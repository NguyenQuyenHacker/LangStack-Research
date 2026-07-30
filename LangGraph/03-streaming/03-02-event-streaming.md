---
title: Event streaming mức graph
doc_source: https://docs.langchain.com/oss/python/langgraph/event-streaming
accessed: 2026-07-29
lc_version: unknown
status: draft
lab:
related:
  - ./03-01-streaming.md
  - ../06-frontend/06-03-custom-stream-channels.md
---

# Event streaming mức graph (`graph.stream_events`)

> Cách LangGraph khuyến nghị để đọc dữ liệu chảy ra từ một lần chạy graph: một luồng sự kiện duy nhất, phơi ra thành nhiều "khung nhìn" (projection) có kiểu rõ ràng, nhiều bên đọc song song không giẫm chân nhau.
> Nó đứng **trên** streaming thô ([03-01](./03-01-streaming.md)); phần tự viết projection nằm ở [06-03](../06-frontend/06-03-custom-stream-channels.md).

---

## 1. Tổng quan

Khi một graph chạy, bên trong nó xảy ra rất nhiều thứ cùng lúc: model nhả token, state cập nhật sau từng bước, subgraph con chạy, tool bắn kết quả, thỉnh thoảng dừng lại chờ người duyệt. Muốn hiện bất cứ thứ nào trong số đó lên giao diện hay ghi log, ta phải lấy được các sự kiện này ra.

Event streaming là lớp làm việc đó. Gọi `graph.stream_events(input, version="v3")`, ta nhận về một **run stream object** — không phải một danh sách sự kiện thô, mà một đối tượng phơi ra nhiều projection có kiểu: `stream.messages` cho chữ của model, `stream.values` cho state, `stream.output` cho kết quả cuối, `stream.subgraphs` cho graph con... Mỗi projection là một cách đọc riêng trên **cùng một luồng sự kiện**.

Khác biệt so với streaming thô ([03-01](./03-01-streaming.md)): ở đó ta chọn `stream_mode` rồi tự bóc dict thô, tự ghép chuỗi namespace, tự khớp tool với message. Event streaming chuẩn hóa hết rồi đưa cho ta các khung nhìn gọi theo tên, đúng kiểu dữ liệu, và cho **nhiều bên đọc đồng thời**.

```python
stream = graph.stream_events(                              # trả về run stream object, không phải list
    {"messages": [{"role": "user", "content": "42 * 17 = ?"}]},
    version="v3",                                          # phiên bản giao thức sự kiện, bắt buộc ghi
)

for message in stream.messages:                            # khung nhìn "chữ của model"
    for token in message.text:                             # message.text lặp được: token một
        print(token, end="", flush=True)                   # end="" để chữ nối liền, không xuống dòng

final_state = stream.output                                # đợi lấy kết quả cuối của cả run
```

**Kết quả in ra** :

```
The                                                        ← token đầu, in ngay khi model vừa nhả
 answer                                                    ← các token nối liền nhau nhờ end=""
 is                                                        ← ...
 714.                                                      ← token cuối của câu trả lời
```

**!Note:** `version="v3"` là phiên bản **giao thức sự kiện**, không phải phiên bản thư viện. Đây là tham số bắt buộc trên mọi lời gọi `stream_events`, kể cả khi resume sau interrupt.

---

## 2. Sơ đồ kiến trúc Event Streaming Pipeline

LangGraph cung cấp sẵn trọn bộ Event Streaming Pipeline này, tự động chuyển dữ liệu thô phức tạp thành các dòng sự kiện sạch sẽ (`stream.messages`, `stream.values`...), nhờ đó ta chỉ cần tập trung viết code ứng dụng mà không tốn công bóc tách dữ liệu thủ công.

```text
┌────────────────────────────────────────────────┐
│  Pregel engine — thực thi các bước trong Graph │
└────────────────────────────────────────────────┘
                      │ xả sự kiện thô
                      ▼
┌────────────────────────────────────────────────┐
│  Raw Pregel events                             │
│  updates · values · messages · custom          │
│  checkpoints · tasks · debug                   │
└────────────────────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────┐
│  Event router — điều hướng qua pipeline        │
└────────────────────────────────────────────────┘
                      │
                      ▼
┌───────────────────────────────────────────────┐
│  Stream transformers                          │
│  ValuesTransformer · MessagesTransformer      │
│  Custom transformers                          │
└───────────────────────────────────────────────┘
                      │ chiếu ra projection
                      ▼
┌────────────────────────────────────────────────┐
│  Event Stream — stream.messages, stream.values │
└────────────────────────────────────────────────┘
```

**Diễn giải từng chặng:**

| Chặng | Thành phần | Làm gì |
|---|---|---|
| 1 | **Pregel engine** | Trái tim của LangGraph, thực thi các bước trong Graph. |
| 2 | **Raw Pregel events** | Engine xả ra chuỗi sự kiện thô đủ loại. |
| 3 | **Event router** | Tiếp nhận sự kiện thô, điều hướng qua transformer pipeline. |
| 4 | **Stream transformers** | Phân loại: `ValuesTransformer` (state), `MessagesTransformer` (token văn bản), `Custom transformers` (tự viết). |
| 5 | **Event Stream** | Dòng sự kiện đã chiếu, có kiểu rõ ràng, client dễ tiêu thụ. |
---

## 3. Các projection có sẵn — đọc dữ liệu gì bằng cái gì

Tất cả projection đều đọc trên **cùng một** run stream và đọc song song được. Khác nhau ở chỗ mỗi cái chiếu ra một loại dữ liệu riêng, phục vụ một nhu cầu riêng. Bảng dưới đọc theo ba trục: nó là gì, dùng để làm gì, và khi nào mới cần tới.

| Projection | Là gì / lấy ra cái gì | Khi nào dùng tới |
|---|---|---|
| `stream.messages` | Chữ của chat model, tách nhỏ theo token; kèm reasoning và mảnh tham số tool-call. | **Dùng thường xuyên nhất.** Bất cứ khi nào cần hiện câu trả lời gõ dần lên UI (kiểu ChatGPT). |
| `stream.output` | Chỉ mỗi **kết quả cuối** của run, đợi tới khi chạy xong mới có. | **Dùng thường xuyên.** Khi chỉ cần đáp án cuối, không quan tâm quá trình. |
| `stream.values` | **Ảnh chụp toàn bộ state** sau mỗi bước graph. | Khi cần theo dõi state đổi qua từng bước — debug, hiện tiến trình, ghi log trung gian. |
| `stream.subgraphs` | Hoạt động của các graph con lồng nhau, đã bóc sẵn tên và đường dẫn. | Khi graph có subgraph / hệ multi-agent, muốn biết con nào đang chạy và nó nhả gì. |
| `stream.interrupted` | Một cờ đúng/sai: run có đang dừng chờ người nhập không. | Khi có bước duyệt tay — dùng để rẽ nhánh "có dừng thì xử lý resume". |
| `stream.interrupts` | Payload của điểm dừng: graph đang hỏi gì, chờ quyết định gì. | Đi kèm `interrupted` — để hiện cho người dùng nội dung cần duyệt. |
| `stream` | Bản thân đối tượng run stream; lặp nó ra **mọi** sự kiện giao thức thô. | Chỉ khi các projection có sẵn không đủ, cần tự lọc sự kiện ở mức thấp nhất (xem 4.6). |
| `stream.extensions` | Các projection **do transformer tự viết** tạo ra. | Chỉ khi ta đã viết transformer riêng (xem mục 6). |

Nắm hai dòng đầu là chạy được phần lớn việc: `stream.messages` để hiện chữ, `stream.output` để lấy kết quả. Bốn dòng giữa cho nhu cầu cụ thể hơn. Hai dòng cuối (`stream` thô, `stream.extensions`) là trường hợp đặc biệt.

---

## 4. Cách lấy từng loại dữ liệu


### 4.1 Lấy chữ của model — `stream.messages`
⎘ [docs …#stream-messages](https://docs.langchain.com/oss/python/langgraph/event-streaming#stream-messages)

Tách đầu ra model thành từng message. Mỗi message có `.text` (lặp ra token-một, hoặc `str(.text)` lấy cả câu), `.reasoning` (mảnh suy luận), `.tool_calls` (mảnh tham số tool), và `.output.usage_metadata` (số token). Cần **text + reasoning + tool-call đúng thứ tự đến** thì phải lặp sự kiện thô, đừng đọc ba cái riêng rồi ghép — thứ tự sẽ lệch âm thầm.

### 4.2 Lấy state và kết quả cuối — `stream.values` + `stream.output`
⎘ [docs …#stream-state](https://docs.langchain.com/oss/python/langgraph/event-streaming#stream-state)

`stream.values` cho ảnh chụp toàn bộ state sau mỗi bước; `stream.output` đợi lấy state cuối khi run kết thúc.

### 4.3 Quan sát graph con — `stream.subgraphs`
⎘ [docs …#stream-subgraphs](https://docs.langchain.com/oss/python/langgraph/event-streaming#stream-subgraphs)

Theo dõi graph con lồng nhau qua `subgraph.graph_name`, `subgraph.path`, `subgraph.messages` — đã bóc sẵn, không phải tự phân tích chuỗi namespace.

### 4.4 Đọc nhiều projection đúng thứ tự — `stream.interleave`
⎘ [docs …#stream-multiple-projections](https://docs.langchain.com/oss/python/langgraph/event-streaming#stream-multiple-projections)

`stream.interleave("values", "messages", ...)` trộn nhiều projection, mỗi vòng trả cặp `(name, item)` đúng thứ tự thời gian chúng đến — `name` cho biết item thuộc projection nào.

### 4.5 Dừng chờ người và chạy tiếp — interrupt & resume
⎘ [docs …#resume-after-an-interrupt](https://docs.langchain.com/oss/python/langgraph/event-streaming#resume-after-an-interrupt)

Graph dừng chờ người: kiểm tra `stream.interrupted`, đọc `stream.interrupts` xem nó hỏi gì, rồi gọi lại `stream_events(...)` với `Command(resume=...)` để chạy tiếp. Chỉ chạy được khi graph compile kèm **checkpointer** và config mang **thread ID**.

### 4.6 Lấy toàn bộ sự kiện thô — lặp thẳng `stream`
⎘ [docs …#stream-all-protocol-events](https://docs.langchain.com/oss/python/langgraph/event-streaming#stream-all-protocol-events)

Lặp thẳng `stream` ra mọi `ProtocolEvent` khi projection có sẵn không đủ. Mỗi event có `seq` (**dùng để sắp thứ tự** — không dùng `timestamp` vì đồng hồ có thể trôi), `method` (tên channel), và `params.namespace` (đường dẫn scope phát ra event, gốc là `[]`, mỗi tầng lồng thêm một đoạn `"name:runtime_id"`).

---

## Tham chiếu chéo

- [03-01 Streaming](./03-01-streaming.md) — tầng dưới của ngăn xếp: sự kiện thô theo `stream_mode`. Event streaming đứng trên tầng này.
- [07-03 Custom stream channels](../06-frontend/06-03-custom-stream-channels.md) — chi tiết cơ chế transformer và `StreamChannel` mà mục 6 chỉ nêu tên.
- Trang tài liệu gốc: `https://docs.langchain.com/oss/python/langgraph/event-streaming`
- Sản phẩm liên quan (tài liệu riêng, không thuộc phạm vi file này): LangChain agent streaming, Deep Agents streaming, LangSmith Streaming API cho graph deploy sau Agent Server.