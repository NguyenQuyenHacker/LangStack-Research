---
title: Unit testing
doc_source: https://docs.langchain.com/oss/python/langchain/test/unit-testing
accessed: 2026-07-25
lc_version: unknown
status: draft
lab:
related:
  - ./08-01-testing-overview.md
  - ./08-03-integration-testing.md
---

# Unit testing (`GenericFakeChatModel`, `InMemorySaver`)

> Kiểm thử logic của agent mà không gọi API: thay model thật bằng model giả và lưu trạng thái trong RAM.
> Đây là cách nhanh, miễn phí, lặp lại được — bù lại chỉ kiểm được logic đã kịch bản hóa sẵn, không kiểm được model thật (phần đó xem [08-03](./08-03-integration-testing.md)).

---

## 1. Tổng quan

Unit test là tách riêng phần logic của agent ra để kiểm, không đụng tới model thật. 

Cách làm: thay model thật bằng một *mô hình giả do chính mình dựng*, đã ghi sẵn nó sẽ trả lời gì — nói câu nào, gọi tool nào, khi nào báo lỗi. 

-> Vì mọi câu trả lời đều do mình định trước nên test chạy trong tích tắc, không tốn tiền, không cần API key, và lần nào chạy cũng ra kết quả y hệt.

Hai công cụ được dùng: `GenericFakeChatModel` (giả model) và `InMemorySaver` (giả nơi lưu trạng thái).

---

## 2. `GenericFakeChatModel` — model giả trả lời theo kịch bản

### Khái niệm

`GenericFakeChatModel` là model giả dùng để dựng sẵn phản hồi của model, hỗ trợ cho việc kiểm thử các quy trình phức tạp (chains), agent, và đặc biệt là tính năng gọi công cụ (tool calling / function calling) mà không cần tốn token hay gọi API thật.

### Áp dụng thực tế

Bạn viết một agent tra cứu thời tiết. Bạn muốn kiểm: "khi model quyết định gọi tool `get_weather`, agent có chạy đúng tool và ráp kết quả vào không". Bạn không quan tâm model thật có gọi tool hay không — bạn cắm sẵn một câu trả lời chứa tool call, rồi khẳng định agent xử lý đúng. Test này chạy trong mili-giây, không tốn một đồng API nào.

### Triển khai
 
Dựng một agent thời tiết rồi cắm model giả vào. Làm hai nhịp: chạy để xem nó đi thế nào, rồi biến thành test bằng vài dòng khẳng định.
 
**Nhịp 1 — chạy để xem.**
 
```python
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.messages.tool import ToolCall
 
@tool
def get_weather(city: str):
    """Tra thời tiết một thành phố."""
    return f"{city}: 25 độ, nắng."
 
# Model giả: soạn sẵn 2 câu cho tình huống "hỏi thời tiết SF"
model = GenericFakeChatModel(messages=iter([
    AIMessage(content="", tool_calls=[                       # câu 1: ra lệnh gọi get_weather cho "SF"
        ToolCall(name="get_weather", args={"city": "SF"}, id="call_1")
    ]),
    "Ở SF đang 25 độ, nắng.",                                # câu 2: câu chốt cuối
]))
 
agent = create_agent(model, tools=[get_weather])
kq = agent.invoke({"messages": [HumanMessage("Thời tiết ở SF thế nào?")]})
 
print(kq["messages"][-1].content)                            # in câu trả lời cuối
```
 
**Kết quả in ra** :
 
```
Ở SF đang 25 độ, nắng.
```
 
Bên trong, `kq["messages"]` giữ lại cả quá trình — bốn message theo đúng thứ tự agent đã đi:
 
```
[
  HumanMessage("Thời tiết ở SF thế nào?"),        ← câu hỏi vào
  AIMessage("", tool_calls=[get_weather(SF)]),    ← câu 1 model giả: ra lệnh gọi tool
  ToolMessage("SF: 25 độ, nắng."),                ← agent ĐÃ chạy get_weather thật → kết quả
  AIMessage("Ở SF đang 25 độ, nắng."),            ← câu 2 model giả: chốt lại
]
```
 
**Nhịp 2 — biến thành test.** Thay `print` bằng khẳng định để máy tự chấm đúng/sai:
 
```python
tool_calls = kq["messages"][1].tool_calls                    # message thứ 2 là lượt model ra lệnh gọi tool
 
assert tool_calls[0]["name"] == "get_weather"                # agent gọi ĐÚNG tool
assert tool_calls[0]["args"] == {"city": "SF"}               # ĐÚNG tham số
assert "25 độ" in kq["messages"][-1].content                 # kết quả tool đã ráp vào câu cuối
```
 
Ba dòng `assert` này chính là chỗ nói rõ **đang test** liệu **agent có nhận lệnh gọi tool, chạy đúng tool với đúng tham số, rồi ráp kết quả vào câu trả lời không**. S

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

---

## Tham chiếu chéo

- [08-01 Testing — tổng quan](./08-01-testing-overview.md) — vị trí unit test trong ba cách kiểm thử
- [08-03 Integration testing](./08-03-integration-testing.md) — bước tiếp theo: kiểm với API model thật
- Tài liệu gốc: `https://docs.langchain.com/oss/python/langchain/test/unit-testing`
- Tham chiếu `GenericFakeChatModel`: `https://reference.langchain.com/python/langchain-core/language_models/fake_chat_models/GenericFakeChatModel`
- Tham chiếu `InMemorySaver`: `https://reference.langchain.com/python/langgraph/checkpoints/`