---
title: Streaming mức graph
doc_source: https://docs.langchain.com/oss/python/langgraph/streaming
accessed: 2026-07-29
lc_version: "≥1.1 (định dạng v2); event-streaming có từ v1.2"
status: draft
lab:
related:
  - ./03-02-event-streaming.md
  - ../10-runtime/10-01-pregel-runtime.md
---

# Streaming mức graph (`stream` / `astream`)

> API streaming dựa trên `stream_mode`: gọi `graph.stream(...)` để nhận dữ liệu graph nhả ra dần trong lúc chạy, thay vì đợi chạy xong.
> Theo docs đây là API cũ hơn so với event-streaming — [03-02 event-streaming](./03-02-event-streaming.md) là bản typed mới (v1.2) tài liệu khuyến nghị cho ứng dụng mới.

---

## 1. Tổng quan

`stream()` (đồng bộ) và `astream()` (bất đồng bộ) trả về một iterator, nhả ra từng mẩu (chunk) ngay khi graph đi qua mỗi bước, để ta hiển thị tiến trình theo thời gian thực.

Cơ chế chọn "muốn nhận loại dữ liệu gì" nằm ở tham số `stream_mode`. Truyền một mode, hoặc một danh sách nhiều mode.

```python
for chunk in graph.stream(              # stream() đồng bộ; bản async là astream()
    {"topic": "ice cream"},             # input khởi tạo state
    stream_mode=["updates", "custom"],  # chọn loại dữ liệu muốn nhận
    version="v2",                       # bật định dạng StreamPart thống nhất (mục 2)
):
    if chunk["type"] == "updates":      # phân nhánh theo loại chunk nhận về
        for node_name, state in chunk["data"].items():
            print(f"Node {node_name} updated: {state}")
    elif chunk["type"] == "custom":
        print(f"Status: {chunk['data']['status']}")
```

**Kết quả in ra:**

```
Status: thinking of a joke...                  ← chunk custom, do node tự phát ra
Node generate_joke updated: {'joke': 'Why did the ice cream go to school? ...'}     ← chunk updates, sau khi node chạy xong
```

Thứ tự phản ánh đúng lúc từng mẩu được sinh ra: node phát `custom` trước khi nó return, nên dòng status hiện trước dòng updates.

---

## 2. `Version="v2"`
 
`version` không đổi *dữ liệu* graph nhả ra, nó đổi **hình dạng cái vỏ bọc quanh dữ liệu đó** — tức mỗi `chunk` trong vòng lặp `for chunk in graph.stream(...)` trông ra sao.`.
 
### Vấn đề của v1: chunk đổi hình theo cấu hình
 
Ở bản v1, cấu trúc của chunk bị tráo đổi linh hoạt tùy thuộc vào số lượng stream_mode hoặc việc bạn có sử dụng Subgraph hay không.
 
| Cấu hình stream | `chunk` v1 trả về | Code phải bóc |
|---|---|---|
| Một mode | `{'refine_topic': {...}}` — dict thô | `data = chunk` |
| Nhiều mode | `('updates', {...})` — tuple 2 | `mode, data = chunk` |
| Bật subgraph | `(('node_2:abc',), {...})` — tuple 2 | `ns, data = chunk` |
| Nhiều mode + subgraph | `(('node_2:abc',), 'updates', {...})` — bộ ba | `ns, mode, data = chunk` |
 
🚨 Hậu quả: Code xử lý phía Client phải viết rất nhiều câu lệnh if/else hoặc kiểm tra độ dài len(chunk) để đoán xem mình đang cầm kiểu dữ liệu nào. Chỉ cần thay đổi cấu hình từ 1 mode sang 2 mode, hệ thống sẽ bị vỡ code ngay lập tức.

Thấy rõ nhất khi in thẳng `chunk` ra, dùng graph hai node ở [mục 4.1](#41-lấy-trạng-thái-graph--values-và-updates) (`refine_topic → generate_joke`). Chỉ thêm một mode thứ hai, hình dạng đổi hẳn:

 ---
```python
# Một mode — in mỗi chunk:
for chunk in graph.stream({"topic": "ice cream"}, stream_mode="updates"):
    print(chunk)

```

Output — một mode, `chunk` là **dict thô**:
 
```
{'refine_topic': {'topic': 'ice cream and cats'}}                  ← không có chỗ nào ghi đây là mode 'updates'
{'generate_joke': {'joke': 'This is a joke about ice cream and cats'}}
```
 
 ---

```python
# Hai mode — vẫn graph đó, chỉ thêm "values":
for chunk in graph.stream({"topic": "ice cream"}, stream_mode=["updates", "values"]):
    print(chunk)
```

Output — hai mode, `chunk` biến thành **tuple** :
 
```
('values',  {'topic': 'ice cream', 'joke': ''})                    ← phần tử [0] giờ là tên mode
('updates', {'refine_topic': {'topic': 'ice cream and cats'}})     ← cùng graph, chỉ thêm 1 mode, cấu trúc đã khác hẳn
('values',  {'topic': 'ice cream and cats', 'joke': ''})           ← dòng `data = chunk` viết cho case trên giờ sập
...
```

### Cách v2 chữa: một vỏ cố định `StreamPart`
 
Khi truyền thêm version="v2", mọi chunk trả về — bất kể cấu hình 1 hay nhiều mode, có Subgraph hay không — đều tuân theo một Dictionary 3 khóa cố định gọi là StreamPart:
 
```python
{
    "type": "values" | "updates" | "messages" | "custom" | "checkpoints" | "tasks" | "debug",
    "ns":   (),     # namespace: rỗng () ở graph gốc, có giá trị khi chunk đến từ subgraph
    "data": ...,    # dữ liệu thật; kiểu bên trong thay đổi theo từng mode
}
```
 
Vì vỏ luôn giống nhau, code đọc lúc nào cũng viết một kiểu — lấy `chunk["type"]` để biết loại, lấy `chunk["data"]` để dùng, không phải đoán tuple hay dict:
 
```python
for chunk in graph.stream(inputs, version="v2"):
    if chunk["type"] == "messages":                  # chunk["type"] cho biết mode nào tạo mẩu này
        print("Token:", chunk["data"])               # chunk["data"] là dữ liệu thật, luôn nằm ở đây
    elif chunk["type"] == "updates":
        print("Cập nhật:", chunk["data"])
```
 
Chạy lại đúng hai-mode ở trên nhưng thêm `version="v2"`, in `chunk` ra để so với tuple lúc nãy:
 
```python
for chunk in graph.stream(
    {"topic": "ice cream"}, stream_mode=["updates", "values"], version="v2",
):
    print(chunk)
```
 
Output — mọi chunk cùng một vỏ, dù mode nào (dựng lại):
 
```
{'type': 'values',  'ns': (), 'data': {'topic': 'ice cream', 'joke': ''}}                          ← type ghi rõ mode; data nằm cố định
{'type': 'updates', 'ns': (), 'data': {'refine_topic': {'topic': 'ice cream and cats'}}}           ← đổi mode, vỏ không đổi
{'type': 'values',  'ns': (), 'data': {'topic': 'ice cream and cats', 'joke': ''}}                  ← vẫn type/ns/data
...
```
 
Trước cầm hai mode phải bóc `mode, data = chunk`, giờ chỉ đọc `chunk["data"]`; thêm subgraph cũng không đổi dòng nào — chỉ khi cần phân biệt gốc/subgraph mới ngó thêm `chunk["ns"]` (dùng ở [mục 4.4](#44-lấy-output-từ-subgraph--subgraphstrue)).
 
---

## 3. Bảng bảy stream mode

| Mode | Kiểu payload | Trả về gì |
|---|---|---|
| `values` | `ValuesStreamPart` | Toàn bộ state sau mỗi bước | 
| `updates` | `UpdatesStreamPart` | Chỉ phần state bị đổi sau mỗi bước; nhiều update trong cùng bước nhả riêng từng cái | |
| `messages` | `MessagesStreamPart` | Tuple `(token LLM, metadata)` từ các lần gọi LLM | |
| `custom` | `CustomStreamPart` | Dữ liệu tự định nghĩa, node phát qua `get_stream_writer` | |
| `checkpoints` | `CheckpointStreamPart` | Sự kiện checkpoint (cùng định dạng `get_state()`) |
| `tasks` | `TasksStreamPart` | Sự kiện task bắt đầu/kết thúc, kèm kết quả và lỗi |
| `debug` | `DebugStreamPart` | Gộp `checkpoints` + `tasks` + metadata bổ sung |

Dùng thường xuyên là bốn mode đầu. Ba mode cuối phục vụ gỡ lỗi và quan sát vòng đời task — nếu ứng dụng không cần nhìn sâu vào runtime thì bỏ qua.

---

## 4. Cách lấy từng loại dữ liệu
 
> Phần này chỉ nêu khái niệm: mỗi mode cho ta cái gì, khi nào dùng, có điều kiện gì. Code khai báo chạy được và output thật cho từng mode nằm ở folder ví dụ `./examples/`.
 
### 4.1 Lấy trạng thái graph — `values` và `updates`
 
Cả hai cùng cho thấy state của graph, khác nhau ở chỗ "toàn bộ hay chỉ phần vừa đổi".
 
`updates` nhả **phần state mà node vừa thay đổi**, kèm tên node tạo ra thay đổi đó. Sau mỗi node, ta nhận đúng những key nó vừa ghi, không kèm phần state cũ. Hợp khi chỉ quan tâm "bước này đổi cái gì" — ví dụ log tiến trình theo từng node. Nếu trong một bước có nhiều node cùng cập nhật, mỗi cập nhật nhả riêng một chunk.
 
`values` nhả **toàn bộ state** sau mỗi bước — mỗi chunk là ảnh chụp đầy đủ của state tại thời điểm đó. Hợp khi cần hiển thị "trạng thái mới nhất" hoàn chỉnh, hoặc muốn thấy state lớn dần qua từng node.
 
Nói gọn: chọn `updates` khi cần biết "cái gì vừa đổi"; chọn `values` khi cần "toàn cảnh hiện tại".
 
### 4.2 Lấy token LLM — `messages`
 
Vấn đề: model sinh câu trả lời mất vài giây; đợi xong mới hiện thì người dùng thấy trễ. `messages` nhả **từng token** LLM ngay khi model sinh ra, gom từ mọi lần gọi LLM ở bất kỳ đâu trong graph (node, tool, subgraph, task) — để chữ chảy dần ra màn hình như ChatGPT.
 
Mỗi mẩu là cặp `(message_chunk, metadata)`: `message_chunk` là mẩu chữ, `metadata` là dict cho biết token này đến từ node nào (`langgraph_node`) và từ lần gọi LLM nào (qua `tags`). Token vẫn phát **kể cả khi node gọi model bằng `.invoke` chứ không phải `.stream`** — không cần đổi cách gọi model để có streaming.
 
Khi graph gọi LLM nhiều lần mà chỉ muốn lấy token ở một số chỗ, lọc qua `metadata`:
 
- **Theo lần gọi:** gắn tag lúc khởi tạo model (vd `tags=["joke"]`), rồi chỉ giữ chunk có tag đó.
- **Theo node:** chỉ giữ chunk có `metadata["langgraph_node"]` bằng tên node cần.
- **Loại hẳn khỏi stream (`nostream`):** gắn tag `nostream` cho model — model vẫn chạy và vẫn cho ra kết quả, nhưng token của nó **không** xuất hiện trong `messages`. Dùng khi LLM chỉ phục vụ xử lý nội bộ (vd tạo structured output) mà không muốn đẩy ra client, hoặc tránh trùng nội dung khi đã stream qua kênh khác.
**!Note:** Với **Python < 3.11 chạy async**, phải truyền `RunnableConfig` thẳng vào lời gọi LLM async (`ainvoke`), nếu không callback không lan truyền và **không token nào chảy ra** — code vẫn chạy trơn, hỏng trong im lặng. Xem mục 6.
 
### 4.3 Gửi dữ liệu tự định nghĩa — `custom`
 
Vấn đề: đôi khi cần báo tiến trình của thứ *không phải* LLM — vd một tool đang query DB "đã lấy 40/100 bản ghi". Không mode nào có sẵn thông tin này vì nó do logic của ta sinh ra.
 
Cơ chế: trong node hoặc tool, lấy hàm ghi bằng `get_stream_writer()` rồi gọi nó với bất kỳ dict nào cần đẩy ra ngoài. Phía nhận đặt `stream_mode="custom"` để nhận đúng các dict đó. Khi ghép nhiều mode, **ít nhất một mode phải là `custom`** thì kênh này mới hoạt động.
 
### 4.4 Lấy output từ subgraph — `subgraphs=True`
 
Mặc định stream chỉ nhả sự kiện của graph gốc; sự kiện bên trong subgraph bị ẩn. Đặt `subgraphs=True` để nhận thêm cả sự kiện từ subgraph.
 
Với v2, chunk từ subgraph vẫn là `StreamPart` bình thường — phân biệt bằng trường `ns`: rỗng `()` là graph gốc, có giá trị (dạng `("tên_node:<task_id>",)`) là đến từ subgraph. Nhờ vậy vừa nhận được tiến trình bên trong, vừa biết nó thuộc subgraph nào.
 
Cấu trúc subgraph (định nghĩa, cách compile lồng nhau) không thuộc trang này — xem tài liệu use-subgraphs.
 
### 4.5 Nhìn sâu vào runtime — `checkpoints`, `tasks`, `debug`
 
Ba mode này **cần một checkpointer** (vd `MemorySaver`) khi compile graph, vì chúng đọc dữ liệu vòng đời mà chỉ tầng lưu trạng thái mới có.
 
`checkpoints` nhả sự kiện checkpoint, cùng định dạng với `get_state()`. `tasks` nhả sự kiện task bắt đầu/kết thúc, kèm node nào đang chạy, kết quả và lỗi. `debug` gộp cả hai lại và thêm metadata — dùng khi muốn tối đa thông tin; chỉ cần một phần thì lấy thẳng `checkpoints` hoặc `tasks` cho gọn.
 
Cơ chế checkpointer và task thuộc [10-01 pregel-runtime](../10-runtime/10-01-pregel-runtime.md), ở đây chỉ nêu mode để lấy chúng ra qua stream.
 
---

## 5. Nhiều mode cùng lúc

Truyền một list vào `stream_mode`. Với v2, mọi chunk vẫn là một `StreamPart` — chỉ cần rẽ nhánh theo `chunk["type"]`, không phải giải nén tuple như v1.

```python
for chunk in graph.stream(inputs, stream_mode=["updates", "custom"], version="v2"):
    if chunk["type"] == "updates":
        for node_name, state in chunk["data"].items():
            print(f"Node `{node_name}` updated: {state}")
    elif chunk["type"] == "custom":
        print(f"Custom event: {chunk['data']}")
```

---

## 6. Vài tình huống nâng cao

**Dùng với LLM bất kỳ.** Nếu model không theo chuẩn LangChain chat model, không có mode `messages`, ta vẫn stream được bằng `custom`: trong node, lặp qua client streaming của mình và đẩy từng mẩu bằng `writer(...)`. Cách này biến `custom` thành đường ống chung cho mọi nguồn token.

**Tắt streaming cho model cụ thể.** Khi trộn model hỗ trợ và không hỗ trợ streaming, đặt `streaming=False` lúc khởi tạo model để tắt. Nếu integration không nhận tham số `streaming`, dùng `disable_streaming=True` — tham số này có ở mọi chat model qua lớp cơ sở.

**Async trên Python < 3.11.** Do asyncio task ở bản này không mang được `context`, LangGraph không tự lan truyền được. Hệ quả: (1) phải truyền `RunnableConfig` thẳng vào các lời gọi LLM async như `ainvoke()`; (2) **không** dùng được `get_stream_writer` trong node/tool async — phải khai báo tham số `writer: StreamWriter` trong hàm để LangGraph tự truyền vào. Bỏ qua hai điều này thì streaming im lặng hỏng, không báo lỗi.

**`invoke` ở định dạng v2.** Truyền `version="v2"` vào `invoke()`/`ainvoke()` thì kết quả là một `GraphOutput` có `.value` (output thật) và `.interrupts` (tuple các interrupt, rỗng nếu không có) — tách bạch state khỏi metadata interrupt. Truy cập kiểu dict cũ (`result["key"]`, `result["__interrupt__"]`) vẫn chạy nhưng **đã deprecated**, sẽ bỏ ở bản sau. Ngoài ra, khi state là Pydantic model hoặc dataclass, mode `values` của v2 tự ép output về đúng kiểu đó thay vì trả dict thô.

---

## 7. Chuyển từ v1 sang v2

| Tình huống | v1 (mặc định) | v2 (`version="v2"`) |
|---|---|---|
| Một stream mode | Data thô (dict) | `StreamPart` dict có `type`, `ns`, `data` |
| Nhiều stream mode | Tuple `(mode, data)` | Cùng `StreamPart`, lọc theo `chunk["type"]` |
| Stream subgraph | Tuple `(namespace, data)` | Cùng `StreamPart`, kiểm `chunk["ns"]` |
| Nhiều mode + subgraph | Bộ ba `(namespace, mode, data)` | Cùng `StreamPart` |
| Kiểu trả về của `invoke()` | Dict thô (state) | `GraphOutput` có `.value` và `.interrupts` |
| Vị trí interrupt (stream) | Key `__interrupt__` trong dict state | Trường `interrupts` trên chunk `values` |
| Vị trí interrupt (invoke) | Key `__interrupt__` trong dict kết quả | Thuộc tính `.interrupts` trên `GraphOutput` |
| Output Pydantic/dataclass | Trả dict thô | Ép về đúng model/dataclass |

---

## 8. Nên dùng cái này hay event-streaming

Dùng **stream-mode API (trang này)** khi: cần truy cập trực tiếp sự kiện runtime của graph (`checkpoints`, `tasks`, `debug`), hoặc cần output của một `stream_mode` cụ thể, hoặc đang duy trì code cũ đã viết theo `stream_mode`.

Dùng **[event-streaming (03-02)](./03-02-event-streaming.md)** cho ứng dụng mới: đó là API typed-projection (từ v1.2) tài liệu khuyến nghị, cho từng iterator riêng theo loại (messages, values, subgraphs, output) để tiêu thụ độc lập, thay vì rẽ nhánh trên `stream_mode` chunk.

Một điểm chưa rõ ranh giới: chính trang này ở ví dụ `nostream` lại gọi `graph.stream_events(initial_state, version="v3")` — tức API event-streaming với `version="v3"`, không phải `stream()`. Tài liệu không giải thích chỗ lệch này. Cần đối chiếu [03-02](./03-02-event-streaming.md) khi triển khai để chọn đúng API và đúng `version`.

---

## Tham chiếu chéo

- [03-02 event-streaming](./03-02-event-streaming.md) — API typed-projection mới (v1.2), bản khuyến nghị; trang này là API stream-mode cũ hơn.
- [10-01 pregel-runtime](../10-runtime/10-01-pregel-runtime.md) — "mỗi bước", superstep, checkpointer, task: cơ chế runtime đứng sau các mode `checkpoints`/`tasks`/`debug`.
- Trang nguồn: `https://docs.langchain.com/oss/python/langgraph/streaming`