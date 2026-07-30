---
title: Time travel
doc_source: https://docs.langchain.com/oss/python/langgraph/use-time-travel
accessed: 2026-07-29
lc_version: unknown
status: draft
lab:
related:
  - ../02-persistence/02-02-checkpointers.md
  - ./04-01-interrupts.md
---

# Time travel

> Cơ chế quay về một checkpoint đã qua để **chạy lại** (replay) hoặc **rẽ nhánh có sửa state** (fork), thay vì chạy lại cả đồ thị từ đầu.
> Dựng hoàn toàn trên checkpoint của persistence — xem [checkpointers](../02-persistence/02-02-checkpointers.md); phần giao với human-in-the-loop xem [interrupts](./04-01-interrupts.md).

---

## 1. Tổng quan

Time travel cho phép quay về một điểm bất kỳ trong quá khứ của một lần chạy đồ thị và tiếp tục từ đó. Có hai cách: **replay** — chạy lại từ checkpoint cũ mà không đổi gì; **fork** — rẽ một nhánh mới từ checkpoint cũ sau khi sửa state.

---

## 2. Checkpoint chia đôi đồ thị — cái gì đóng băng, cái gì chạy lại

**Vấn đề.** Một agent thường chạy nhiều bước nối tiếp: sinh chủ đề → viết nội dung → kiểm duyệt → xuất bản. Chạy tới bước ba mới phát hiện chủ đề chọn ở bước một sai. Không có time travel thì phải chạy lại từ đầu — mỗi lần gọi LLM tốn tiền, tốn thời gian, mà các bước phía trước vốn đã đúng. Ta cần một cách nhảy về đúng chỗ cần sửa, giữ lại phần đã làm đúng.

**Cơ chế.** Mỗi bước thực thi, LangGraph lưu một checkpoint — ảnh chụp toàn bộ state tại thời điểm đó (cơ chế lưu thuộc [persistence](../02-persistence/02-02-checkpointers.md), ở đây chỉ mượn kết quả của nó). Khi quay về một checkpoint, đường ranh giới của nó quyết định mọi thứ:

- Node đã chạy **trước** checkpoint: không chạy lại. Kết quả nằm sẵn trong state đã lưu.
- Node đáng lẽ chạy **sau** checkpoint: chạy lại từ đầu.

"Sau checkpoint" là những node nằm trong trường `next` của checkpoint đó — tuple các node sắp được chạy tiếp. Đây là cái ta dựa vào để định vị điểm cần quay về.

**Cách tìm checkpoint để quay về.** `get_state_history` trả về danh sách các checkpoint của một thread, **theo thứ tự đảo ngược thời gian** (mới nhất đứng đầu). Mỗi phần tử cho ta hai thứ cần dùng: `.next` để biết checkpoint này dừng ngay trước node nào, và `.config` (chứa `checkpoint_id`) để quay về đúng nó.

```python
history = list(graph.get_state_history(config))          # danh sách checkpoint, mới nhất trước
before_joke = next(s for s in history                     # tìm checkpoint dừng ngay trước write_joke
                   if s.next == ("write_joke",))          # .next là tuple node sắp chạy
```

Từ `before_joke.config`, ta đi tiếp bằng replay (mục 3) hoặc fork (mục 4).

---

## 3. Replay — chạy lại từ checkpoint cũ, không đổi state

Replay là gọi lại đồ thị bằng config của một checkpoint cũ để nó chạy tiếp từ đúng điểm đó, giữ nguyên state. Truyền `None` làm input (không thêm dữ liệu mới) kèm config của checkpoint muốn quay về:
 
```python
replay_result = graph.invoke(None, before_joke.config)   # None = không input mới; chạy tiếp từ checkpoint này
# write_joke chạy lại; generate_topic (trước checkpoint) không chạy lại
```
 
**Vai trò.** Dùng khi muốn thực thi lại đúng đoạn đó mà không can thiệp gì vào state: thử lại sau một lỗi tạm thời, hoặc quan sát một chuỗi có thành phần không tất định (LLM) cho ra kết quả khác nhau qua từng lần.
 
<div align="center">
  <img src="../assets/images/image copy 5.png" width="800">
</div>


**!Note — replay không đọc cache.** Node sau checkpoint **chạy lại thật**: lệnh gọi LLM, gọi API, interrupt đều fire lại. Nếu chuỗi có LLM, replay hai lần với cùng state đầu vào vẫn có thể ra hai kết quả khác nhau.
 
**!Note — replay từ checkpoint cuối là no-op.** Checkpoint cuối cùng không còn node nào trong `next`, nên không có gì để chạy tiếp. Gọi replay tại đó không làm gì cả.

---

## 4. Fork — rẽ nhánh mới từ checkpoint cũ, có sửa state

Fork tạo một nhánh mới từ một checkpoint quá khứ sau khi sửa state, rồi chạy tiếp trên nhánh đó. Hai bước: `update_state` để tạo nhánh và nhận về config của nhánh mới, rồi `invoke(None, ...)` để chạy tiếp.
 
```python
fork_config = graph.update_state(                        # tạo checkpoint mới rẽ nhánh từ điểm này
    before_joke.config,                                  # checkpoint gốc để rẽ ra
    values={"topic": "chickens"},                        # state đã sửa cho nhánh mới
)
fork_result = graph.invoke(None, fork_config)            # chạy tiếp trên nhánh; write_joke chạy lại với topic mới
```
 
Kết quả: nội dung sinh ra ở nhánh này dựa trên `topic` mới ("chickens"), không phải giá trị cũ.
 
<div align="center">
  <img src="../assets/images/image copy 6.png" width="800">
</div>

**Vai trò.** Dùng khi muốn đổi một quyết định trong quá khứ rồi xem nhánh khác diễn ra thế nào: sửa chủ đề, sửa một tham số, thử một phương án thay thế mà vẫn giữ được lần chạy gốc để đối chiếu.
 
**!Note — `update_state` không cuộn lùi thread.** Nó **không** xóa hay lùi lịch sử. Nó tạo một checkpoint **mới** rẽ ra từ điểm chỉ định; lịch sử gốc vẫn nguyên vẹn. Nghĩa là sau khi fork, thread có hai dòng thời gian song song cùng tồn tại — nhánh gốc và nhánh đã sửa.
 
### `as_node` — coi update này như do node nào tạo ra
 
Khi gọi `update_state`, LangGraph cần biết **coi bản update này như thể node nào vừa tạo ra nó**. Điều đó quyết định hai việc: giá trị được áp qua writer/reducer của node nào ([reducers](https://docs.langchain.com/oss/python/langgraph/graph-api#reducers) thuộc phạm vi file graph-api, chỉ trỏ sang), và graph sẽ chạy tiếp từ **node kế sau** node đó.
 
Mặc định LangGraph tự suy `as_node` từ lịch sử phiên bản của checkpoint. Khi fork từ một checkpoint cụ thể, suy luận này gần như luôn đúng — thường không cần chỉ định.
 
Phải chỉ `as_node` rõ ràng trong ba trường hợp:
 
| Trường hợp | Vì sao cần chỉ rõ |
|---|---|
| Nhánh song song | Nhiều node cùng update state trong một step, LangGraph không xác định được node nào cuối → báo `InvalidUpdateError` |
| Không có lịch sử thực thi | Dựng state trên thread mới toanh (hay gặp khi [test](https://docs.langchain.com/oss/python/langgraph/test)) nên không có gì để suy |
| Cố tình bỏ qua node | Đặt `as_node` thành một node phía sau để đánh lừa graph rằng node đó đã chạy — nó sẽ bị skip |
 
```python
fork_config = graph.update_state(
    before_joke.config,
    values={"topic": "chickens"},
    as_node="generate_topic",                            # coi như generate_topic tạo update → chạy tiếp từ write_joke
)
```

---

## 5. Interrupts luôn kích hoạt lại khi time travel

Nếu đồ thị dùng `interrupt` cho luồng human-in-the-loop, thì **mọi lần time travel đều làm interrupt kích hoạt lại**. Node chứa interrupt chạy lại, và `interrupt()` dừng để chờ một `Command(resume=...)` mới — câu trả lời resume của lần chạy trước không được nhớ lại.

Cơ chế interrupt đầy đủ nằm ở [file interrupts](./04-01-interrupts.md); ở đây chỉ cần nắm điểm giao với time travel: vì phải cấp lại câu trả lời resume, ta có thể replay đúng một điểm HITL nhưng đưa vào một câu trả lời khác để xem kết quả rẽ theo hướng nào.

---

## 6. Subgraphs — độ mịn của time travel phụ thuộc checkpointer

Time travel đi được vào **bên trong** một [subgraph](https://docs.langchain.com/oss/python/langgraph/use-subgraphs) mịn tới đâu là do subgraph đó có checkpointer riêng hay không. Đây là điểm quyết định, nên nắm trước khi thiết kế.

**Mặc định — subgraph kế thừa checkpointer của cha.** Đồ thị cha coi **toàn bộ** subgraph là **một super-step duy nhất**: chỉ có một checkpoint cấp cha cho cả lần chạy subgraph. Hệ quả: quay về trước subgraph sẽ chạy lại **toàn bộ subgraph từ đầu**, và **không thể** time travel tới một điểm nằm giữa các node bên trong subgraph — chỉ time travel được ở cấp cha.

**`checkpointer=True` trên subgraph — subgraph có lịch sử checkpoint riêng.** Lúc này LangGraph tạo checkpoint tại **mỗi bước bên trong** subgraph, nên ta time travel được tới một điểm cụ thể bên trong nó — ví dụ giữa hai interrupt. Cách truy: gọi `get_state(config, subgraphs=True)` để lấy checkpoint riêng của subgraph, rồi fork từ đó.

```python
parent_state = graph.get_state(config, subgraphs=True)   # subgraphs=True để lấy được checkpoint bên trong subgraph
sub_config = parent_state.tasks[0].state.config          # config checkpoint riêng của subgraph
fork_config = graph.update_state(sub_config, {"value": ["forked"]})
result = graph.invoke(None, fork_config)                 # step_b chạy lại, kết quả step_a được giữ
```

Chi tiết cấu hình checkpointer cho subgraph thuộc [subgraph persistence](https://docs.langchain.com/oss/python/langgraph/use-subgraphs#subgraph-persistence).

---

## 7. Replay và Fork — so sánh

| Tiêu chí | Replay | Fork |
|---|---|---|
| Có sửa state không | Không | Có, qua `update_state` |
| Cách gọi | `invoke(None, cp.config)` | `update_state(...)` → `invoke(None, fork_config)` |
| Tạo nhánh mới không | Không | Có |
| Lịch sử gốc | Giữ nguyên | Giữ nguyên (fork thêm một nhánh bên cạnh) |
| Node trước checkpoint | Không chạy lại | Không chạy lại |
| Node sau checkpoint | Chạy lại (LLM/API/interrupt fire lại) | Chạy lại với state đã sửa |

Điểm chung dễ quên: **cả hai đều chạy lại thật** phần phía sau, và **cả hai đều không xóa lịch sử gốc**. Fork chỉ khác replay ở chỗ chèn thêm một bước sửa state trước khi chạy tiếp.

---

## Tham chiếu chéo

- [02-02 Checkpointers](../02-persistence/02-02-checkpointers.md) — cơ chế lưu checkpoint mà time travel dựa vào; trường `next`, `config`, `checkpoint_id`.
- [04-01 Interrupts](./04-01-interrupts.md) — cơ chế `interrupt` và `Command(resume=...)`; time travel luôn kích hoạt lại interrupt.
- Trang tài liệu gốc: `https://docs.langchain.com/oss/python/langgraph/use-time-travel`