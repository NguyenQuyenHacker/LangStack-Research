---
title: Checkpointers
doc_source: https://docs.langchain.com/oss/python/langgraph/checkpointers
accessed: 2026-07-28
lc_version: unknown
status: draft
lab:
related:
  - ./02-01-add-memory.md
  - ./02-03-stores.md
---

# Checkpointers

> Checkpointer chụp lại state của graph sau mỗi bước, xếp theo thread. File [02-01](./02-01-add-memory.md) nói cách *gắn* checkpointer; file này giảng *cơ chế* và cách đọc/sửa state đã lưu.

---

## 1. Tổng quan

Checkpointer là cơ chế chụp lại (snapshot) toàn bộ trạng thái (State) của Graph sau mỗi bước thực thi, được nhóm lại theo từng thread_id

Khi truyền checkpointer vào compile(), ta sẽ kích hoạt 4 tính năng cốt lõi:

- **Human-in-the-loop** — tạm dừng để con người duyệt/chỉnh sửa State trước khi chạy tiếp.
- **Short-term Memory** — Duy trì ngữ cảnh giữa các lượt chat trong cùng một thread.
- **Time travel** — tua lại các lần chạy cũ để xem/gỡ lỗi, hoặc rẽ nhánh từ một checkpoint bất kỳ.
- **Chịu lỗi** — một node hỏng giữa chừng thì khởi động lại từ bước thành công gần nhất.

Kèm theo là **pending writes**: Nếu 1 node bị lỗi trong khi các node khác chạy song song cùng bước đã hoàn thành, kết quả của các node hoàn thành vẫn được lưu. Khi chạy lại, LangGraph không cần thực thi lại các node thành công đó.

**!Note:** Nếu chạy trên Agent Server, phần checkpointing do server tự lo — không phải tự cấu hình.

---

## 2. Ba khái niệm lõi của checkpointer

Graph tuần tự `START → A → B → END`:

```
[ Thread (thread_id) ]
    ├── step -1 ──> Checkpoint 0: rỗng,        next = START
    ├── step  0 ──> Checkpoint 1: có input,    next = node_a
    ├── step  1 ──> Checkpoint 2: output A,    next = node_b
    └── step  2 ──> Checkpoint 3: output B,    next = () ← hết
```

Graph có nhánh song song `START → A → (B, C) → D → END`:

```
[ Thread (thread_id) ]
    ├── step -1 ──> Checkpoint 0: rỗng,          next = START
    ├── step  0 ──> Checkpoint 1: có input,      next = (node_a,)
    ├── step  1 ──> Checkpoint 2: output A,      next = (node_b, node_c)  ← fan-out: xếp 2 node cho vòng sau
    ├── step  2 ──> Checkpoint 3: output B + C,  next = (node_d,)         ← B,C chạy SONG SONG trong 1 super-step
    └── step  3 ──> Checkpoint 4: output D,      next = ()                ← fan-in: D chờ cả B và C mới chạy
```

### Thread — khoá gom mọi checkpoint

Thread là một ID gán cho chuỗi state tích luỹ của một loạt lần chạy. Gọi graph có checkpointer thì **bắt buộc** truyền `thread_id` trong `configurable`:

`thread_id` là **khoá chính** để checkpointer lưu và nạp checkpoint. Thiếu nó, checkpointer không lưu được state cũng không tiếp tục được sau một interrupt — vì nó dùng chính `thread_id` để nạp state đã lưu.

### Checkpoint — ảnh chụp tại một thời điểm

State của một thread tại một thời điểm gọi là checkpoint, biểu diễn bằng object `StateSnapshot`. Mỗi super-step sinh một checkpoint và có thể dùng để khôi phục thread về đúng thời điểm đó.

### Super-step — ranh giới của một checkpoint

Super-step là một lượt chạy của graph — mọi node xếp cho lượt đó cùng chạy, và lượt chỉ đóng khi tất cả xong. 

Super-step hỗ trợ:

- Fan-out / fan-in — tự chờ nhau. Chia nhánh A, B, C chạy song song rồi gộp về D: D chỉ chạy ở lượt kế, sau khi cả A, B, C ở lượt trước đã xong. Hàng rào lo việc chờ đó.
- Pending writes — chịu lỗi. Một node crash thì lượt chưa đóng, nhưng output các node đã xong đã được ghi lại. Retry chỉ chạy lại đúng node sập, không tốn thời gian/chi phí chạy lại phần đã xong.
- Time travel — tua ngược. Mỗi checkpoint gắn một super-step, nên tua lại hay rẽ nhánh đều về đúng ranh giới giữa các nhịp.

### `checkpoint_ns` — checkpoint này thuộc graph nào

Mỗi checkpoint có trường `checkpoint_ns` chỉ nó thuộc graph cha hay subgraph:

- `""` (chuỗi rỗng) — thuộc graph gốc (cha).
- `"node_name:uuid"` — thuộc subgraph chạy ở node đó. Subgraph lồng nhau nối bằng dấu `|`, ví dụ `"outer:uuid|inner:uuid"`.

---

## 3. Đọc và sửa state đã lưu

**`get_state`** — lấy state mới nhất của thread (thêm checkpoint_id nếu muốn một mốc cũ). Trả về một StateSnapshot.

**`get_state_history`** — lấy cả danh sách checkpoint, xếp mới nhất trước, nối nhau qua parent_config. Dùng để lần lại diễn tiến hoặc lọc tìm một mốc: trước một node nào đó, theo step, chỗ có interrupt, hay các mốc do update_state tạo.

**`Replay`** — gọi lại với checkpoint_id cũ: node trước mốc bị bỏ qua, node sau chạy lại (kể cả gọi LLM/API; interrupt luôn kích lại).

**`update_state`** — tạo checkpoint mới, không đụng cái cũ. Kênh có reducer thì giá trị cộng dồn chứ không ghi đè.
---

## 4. Durability modes

**Khái niệm:** Durability modes chọn thời điểm ghi checkpoint xuống ổ: ghi ngay mỗi bước (an toàn, chậm) hay dồn lại/ghi sau (nhanh, rủi ro mất tiến trình nếu crash).

```python
graph.stream({"input": "test"}, durability="sync")        # đặt ở bất kỳ hàm chạy nào: invoke/stream/batch
```

| Mức | Ghi khi nào | Đánh đổi |
|---|---|---|
| `"exit"` | Chỉ khi graph thoát (xong / lỗi / interrupt) | Nhanh nhất, nhưng crash giữa chừng là mất state dở |
| `"async"` | Ghi bất đồng bộ song song với bước kế | Cân bằng; rủi ro nhỏ mất checkpoint nếu crash đúng lúc |
| `"sync"` | Ghi đồng bộ xong mới sang bước kế | Bền nhất, chậm hơn chút |

## 5. Chọn backend và serializer

### Thư viện checkpointer

Mọi checkpointer tuân theo interface `BaseCheckpointSaver`. Doc liệt kê:

| Thư viện | Backend | Dùng cho |
|---|---|---|
| `langgraph-checkpoint` | `InMemorySaver` (RAM) | Có sẵn trong LangGraph; để thử nghiệm |
| `langgraph-checkpoint-sqlite` | `SqliteSaver` / `AsyncSqliteSaver` | Thử nghiệm, chạy local; cài riêng |
| `langgraph-checkpoint-postgres` | `PostgresSaver` / `AsyncPostgresSaver` | Production (LangSmith dùng); cài riêng |
| `langchain-azure-cosmosdb` | `CosmosDBSaver` | Production trên Azure, có Entra ID; cài riêng |

Chạy graph bất đồng bộ (`ainvoke`/`astream`/`abatch`) thì dùng `InMemorySaver` hoặc bản async của Sqlite/Postgres. Bốn method của interface: `.put`, `.put_writes`, `.get_tuple`, `.list`.

### Serializer — cách đóng gói state để lưu

Langgraph hỗ trợ 2 thư viện để đóng gói state để lưu 

Mặc định là `JsonPlusSerializer` (dùng ormsgpack + JSON): tự đóng gói phần lớn kiểu dữ liệu (datetime, enum, Pydantic...), thường không phải chỉnh gì.

```python
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

graph.compile(
    checkpointer=InMemorySaver(serde=JsonPlusSerializer(pickle_fallback=True))   # rơi về pickle khi cần
)
```
**!Note**: pickle_fallback=True — bật khi có kiểu lạ msgpack không nuốt được (Pandas DataFrame), để rơi về pickle cho riêng object đó.

Truyền `EncryptedSerializer` : thay khi cần mã hoá state lúc lưu (đóng gói + mã hoá, tự giải mã khi đọc).

```python
from langgraph.checkpoint.serde.encrypted import EncryptedSerializer
from langgraph.checkpoint.postgres import PostgresSaver

serde = EncryptedSerializer.from_pycryptodome_aes()          # đọc LANGGRAPH_AES_KEY
checkpointer = PostgresSaver.from_conn_string("postgresql://...", serde=serde)
checkpointer.setup()
```

Trên LangSmith, chỉ cần có `LANGGRAPH_AES_KEY` là mã hoá tự bật.

### Tối ưu dung lượng — `DeltaChannel`

 Mặc định mỗi super-step ghi **toàn bộ** giá trị mọi kênh. Thread dài, kênh cộng dồn nhiều (như `messages`) thì dung lượng phình theo thời gian.

-> `DeltaChannel` chỉ lưu **phần tăng thêm** thay vì cả giá trị tích luỹ, giảm mạnh kích thước checkpoint cho các kênh kiểu append.


---

## 6. Tự viết checkpointer — chỉ khi làm backend riêng

Phần này dành cho người tự dựng một storage backend, không phải kiến thức dùng graph hằng ngày. Nếu chỉ dùng Postgres/Sqlite/Redis có sẵn thì **bỏ qua mục này**.

Cốt lõi doc nêu, gói gọn: persistence dựa trên **hai bảng** — `checkpoints` (một dòng mỗi super-step) và `writes` (một dòng mỗi output node trong super-step). Kế thừa `BaseCheckpointSaver` và cài đủ năm method: `aput`, `aput_writes`, `aget_tuple`, `alist`, `adelete_thread` — thiếu method nền nào là lỗi runtime.

Một điểm doc nhấn mạnh vì dễ sai âm thầm: `get_tuple` **phải** tra được checkpoint theo `checkpoint_id` cụ thể, không chỉ lấy bản mới nhất. Đường tra theo id vừa phục vụ time travel, vừa phục vụ dựng lại state của DeltaChannel mỗi lần chạy; tra hỏng thì DeltaChannel dựng ra rỗng mà không báo lỗi.

Chi tiết schema SQL, hỗ trợ delta channel, và bộ `langgraph-checkpoint-conformance` để kiểm thử — đọc thẳng mục "Build a custom checkpointer" trong trang doc gốc khi cần.

---

## Tham chiếu chéo

- [02-01 add-memory](./02-01-add-memory.md) — cách gắn checkpointer vào graph và quản lý trí nhớ ngắn hạn (trim/delete/summarize). File này giảng cơ chế bên dưới.
- [02-03 stores](./02-03-stores.md) — trí nhớ dài hạn xuyên thread; checkpointer bó theo `thread_id`, store bó theo `namespace`.
- Trang doc gốc: `https://docs.langchain.com/oss/python/langgraph/checkpointers`
- Time travel (replay/fork): `https://docs.langchain.com/oss/python/langgraph/use-time-travel`