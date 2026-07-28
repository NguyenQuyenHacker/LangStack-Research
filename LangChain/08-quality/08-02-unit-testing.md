---
title: Unit testing
doc_source: https://docs.langchain.com/oss/python/langchain/test/unit-testing
accessed: 2026-07-25
lc_version: unknown
status: draft
lab:
related:
  - ./test-01-tong-quan.md
  - ./test-03-integration-testing.md
---

# Unit testing (`GenericFakeChatModel`, `InMemorySaver`)

> Kiểm thử logic của agent mà không gọi API: thay model thật bằng model giả và lưu trạng thái trong RAM.
> Đây là cách nhanh, miễn phí, lặp lại được — bù lại chỉ kiểm được logic đã kịch bản hóa sẵn, không kiểm được model thật (phần đó xem [test-03](./test-03-integration-testing.md)).

---

## 1. Tổng quan

Unit test đây nghĩa là tách từng mảnh nhỏ tất định của agent ra chạy riêng. Mấu chốt: thay LLM thật bằng một **bản giả trong RAM** (tài liệu gọi là *fixture*) mà mình tự viết kịch bản trả lời — từng câu chữ, từng tool call, từng lỗi. Nhờ vậy test chạy nhanh, không tốn tiền, không cần API key, và cho cùng kết quả mỗi lần chạy.

Hai công cụ được dùng: `GenericFakeChatModel` (giả model) và `InMemorySaver` (giả nơi lưu trạng thái).

---

## 2. `GenericFakeChatModel` — model giả trả lời theo kịch bản

### Khái niệm

`GenericFakeChatModel` là một model giả nhận vào một iterator các câu trả lời và **trả về một câu mỗi lần gọi**. Mỗi phần tử là một `AIMessage` hoặc một chuỗi. Nó dùng được cả kiểu gọi thường lẫn kiểu chảy dần.

### Vai trò

Không có nó thì mỗi lần test phải gọi model thật: chậm, tốn tiền, và câu trả lời đổi mỗi lần chạy nên không khẳng định chính xác được. `GenericFakeChatModel` cho phép **cố định trước** model sẽ nói gì, để phần logic quanh model (agent điều phối tool, xử lý message) được kiểm một cách tất định.

### Áp dụng thực tế

Bạn viết một agent tra cứu thời tiết. Bạn muốn kiểm: "khi model quyết định gọi tool `get_weather`, agent có chạy đúng tool và ráp kết quả vào không". Bạn không quan tâm model thật có gọi tool hay không — bạn cắm sẵn một câu trả lời chứa tool call, rồi khẳng định agent xử lý đúng. Test này chạy trong mili-giây, không tốn một đồng API nào.

### Triển khai

```python
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel

model = GenericFakeChatModel(messages=iter([                                     # iter() biến list thành iterator: mỗi lần gọi lấy 1 phần tử
    AIMessage(content="", tool_calls=[ToolCall(name="foo", args={"bar": "baz"}, id="call_1")]),  # phần tử 1: một AIMessage rỗng chữ nhưng có 1 tool call
    "bar"                                                                        # phần tử 2: một chuỗi (sẽ được tự bọc thành AIMessage)
]))

model.invoke("hello")                                                            # chuỗi "hello" bị bỏ qua — fake không đọc input, chỉ nhả phần tử kế tiếp
```

**Kết quả in ra** (tài liệu có sẵn):

```
AIMessage(content='', ..., tool_calls=[{'name': 'foo', 'args': {'bar': 'baz'}, 'id': 'call_1', 'type': 'tool_call'}])   ← đúng phần tử 1 của iter, bất kể "hello" là gì
```

Gọi lần nữa thì nó trả về phần tử tiếp theo trong iterator:

```python
model.invoke("hello, again!")                                                    # lần gọi thứ 2 → lấy phần tử 2
```

**Kết quả in ra** (tài liệu có sẵn):

```
AIMessage(content='bar', ...)   ← phần tử 2; chuỗi "bar" đã được bọc thành AIMessage với content="bar"
```

**!Note:** Đoạn code trên **thiếu import** `AIMessage` và `ToolCall` — tài liệu không viết dòng import cho hai class này, người chạy thử phải tự thêm (thường là `from langchain_core.messages import AIMessage` và `from langchain_core.messages.tool import ToolCall`; đường dẫn chính xác cần đối chiếu khi chạy thử vì trang này không nêu).

**!Note:** Iterator cạn thì hỏng. Vì dùng `iter()`, gọi model quá số phần tử đã nạp sẽ ném `StopIteration` — test dừng vì lỗi Python chứ không phải vì khẳng định sai. Đây là hệ quả trực tiếp của việc dùng iterator (căn cứ: `iter()` sinh iterator, đọc hết thì cạn), tài liệu không nói thẳng nhưng suy ra được. Nạp đủ số câu trả lời cho số lần agent sẽ gọi model.

---

## 3. `InMemorySaver` — nơi lưu trạng thái trong RAM

### Khái niệm

`InMemorySaver` là một `checkpointer` — nơi lưu trạng thái hội thoại — nhưng lưu trong RAM thay vì ổ đĩa hay database. Cắm nó vào agent để mô phỏng nhiều lượt hội thoại và kiểm hành vi phụ thuộc trạng thái.

### Vai trò

Nhiều hành vi của agent chỉ lộ ra khi có **lịch sử**: lượt sau phải nhớ lượt trước. Muốn test điều đó mà không dựng database thật, dùng `InMemorySaver`: nó giữ message của các lượt trong cùng một phiên, đủ để kiểm "agent có nhớ và dùng lại thông tin cũ không", rồi tự biến mất khi tiến trình tắt.

### Áp dụng thực tế

Agent trợ lý cá nhân. Lượt 1 người dùng khai "tôi ở Sydney". Lượt 2 hỏi "mấy giờ rồi ở chỗ tôi?". Bạn cần kiểm: agent có lôi lại được thông tin Sydney từ lượt 1 để trả lời lượt 2 không. `InMemorySaver` giữ message lượt 1 lại, hai lượt gắn cùng một `thread_id` nên lượt 2 "thấy" được lượt 1.

### Triển khai

```python
from langgraph.checkpoint.memory import InMemorySaver

agent = create_agent(
    model,                                                                       # dùng lại model giả ở mục 2
    tools=[],
    checkpointer=InMemorySaver()                                                 # lưu trạng thái trong RAM; mất khi tắt tiến trình
)

agent.invoke(                                                                    # lượt 1
    {"messages": [HumanMessage(content="I live in Sydney, Australia")]},
    config={"configurable": {"thread_id": "session-1"}}                          # thread_id gom các lượt vào cùng 1 phiên
)

agent.invoke(                                                                    # lượt 2, cùng thread_id
    {"messages": [HumanMessage(content="What's my local time?")]},
    config={"configurable": {"thread_id": "session-1"}}                          # cùng "session-1" → lượt 2 thấy lại message lượt 1 (Sydney)
)
```

**Kết quả in ra** (dựng lại):

```
# sau lượt 2, state của thread "session-1" chứa lịch sử dồn lại:
{'messages': [
    HumanMessage(content='I live in Sydney, Australia'),        ← còn lại từ lượt 1, nhờ checkpointer giữ
    AIMessage(content=...),                                       ← câu model giả nhả ở lượt 1
    HumanMessage(content="What's my local time?"),               ← câu mới ở lượt 2
    AIMessage(content=...),                                       ← câu model giả nhả ở lượt 2
]}
```

> **Về khối kết quả in ra ở mục này.** Trang tài liệu gốc **không in** kết quả cho ví dụ `InMemorySaver`. Khối trên tôi tự dựng lại từ cách checkpointer hoạt động (dồn message các lượt vào cùng `thread_id`). Cần đối chiếu khi chạy thử.

**!Note:** Ví dụ này lẫn hai loại model. Comment trong tài liệu gốc nói "model trả về giờ GMT+10" như thể model tự suy ra múi giờ từ chữ "Sydney" — nhưng ở đây `model` là `GenericFakeChatModel`, nó chỉ nhả đúng câu đã kịch bản, **không tự tính** gì cả. Muốn test thật hành vi Sydney→GMT+10 thì phải kịch bản hóa sẵn câu trả lời lượt 2 của model giả cho đúng ý. Căn cứ: chính trang này (mục 2) định nghĩa model giả trả lời theo iterator cố định. Điểm này là chỗ ví dụ của tài liệu diễn đạt lỏng, không phải hành vi thực của `GenericFakeChatModel`.

**!Note:** Đoạn trên cũng thiếu import `create_agent` và `HumanMessage` (tài liệu không viết) — người chạy thử tự thêm.

---

## Tham chiếu chéo

- [test-01-tong-quan.md](./test-01-tong-quan.md) — vị trí unit test trong ba cách kiểm thử
- [test-03-integration-testing.md](./test-03-integration-testing.md) — bước tiếp theo: kiểm với API model thật
- Tài liệu gốc: `https://docs.langchain.com/oss/python/langchain/test/unit-testing`
- Tham chiếu `GenericFakeChatModel`: `https://reference.langchain.com/python/langchain-core/language_models/fake_chat_models/GenericFakeChatModel`
- Tham chiếu `InMemorySaver`: `https://reference.langchain.com/python/langgraph/checkpoints/`