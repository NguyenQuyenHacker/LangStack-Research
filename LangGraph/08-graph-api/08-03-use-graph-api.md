---
title: Dùng Graph API
doc_source: https://docs.langchain.com/oss/python/langgraph/use-graph-api
accessed: 2026-07-30
lc_version: unknown
status: draft
lab:
related:
  - ./08-02-graph-api.md
  - ../10-runtime/10-02-fault-tolerance.md
---

# Dùng Graph API — cách làm từng việc

---

## 1. Tổng quan

Trang này chỉ cách ghép các mảnh của Graph API thành workflow chạy được: định nghĩa và cập nhật state, dựng chuỗi tuần tự, rẽ nhánh song song, tạo vòng lặp, và dùng `Send`/`Command`. 

Mẫu tối thiểu một node cập nhật state:

```python
from langgraph.graph import StateGraph, START
from langchain.messages import AIMessage
from typing_extensions import TypedDict

class State(TypedDict):
    messages: list
    extra_field: int

def node(state: State):
    return {"messages": state["messages"] + [AIMessage("Hello!")], "extra_field": 10}

graph = StateGraph(State).add_node(node).set_entry_point("node").compile()
```

**!Note:** Node phải **trả về phần update**, không được sửa trực tiếp (mutate) đối tượng state. Node cũng chỉ cần trả về những khóa nó đổi, không cần trả cả schema.

---

## 2. Định nghĩa và cập nhật state

**Mục đích.** State lưu toàn bộ dữ liệu được chia sẻ giữa các node trong graph. Để định nghĩa state, có thể sử dụng `TypedDict`, `dataclass` hoặc `Pydantic`. Mỗi khóa trong state có thể gắn một **reducer** để quyết định cách hợp nhất (`merge`) các giá trị do nhiều node trả về.

- Không khai báo reducer → giá trị mới **ghi đè** giá trị cũ.
- Có reducer → giá trị mới được hợp nhất theo logic của reducer.

> Chi tiết cơ chế reducer xem tại [08-02 mục 2.2](./08-02-graph-api.md).

### 2.1 Quản lý lịch sử hội thoại với `add_messages`

**Mục đích.** Với chatbot hoặc AI Agent, state thường cần lưu lịch sử hội thoại. Thay vì dùng reducer thông thường, LangGraph cung cấp `add_messages` để quản lý danh sách message.

`add_messages` sẽ:

- Thêm (`append`) message mới.
- Ghi đè message cũ nếu trùng `id`.
- Tự động deserialize từ dạng `dict` sang `Message` của LangChain.

Nếu state chỉ cần lưu lịch sử hội thoại, có thể kế thừa trực tiếp từ `MessagesState`:

```python
from langgraph.graph import MessagesState

class State(MessagesState):
    extra_field: int
```

Ví dụ, node có thể trả về:

```python
return {
    "messages": [
        {
            "role": "user",
            "content": "Hi"
        }
    ]
}
```

`add_messages` sẽ tự chuyển thành `HumanMessage`, không cần tạo `HumanMessage(...)` bằng tay.

> **!Note:** Nếu dùng reducer `add`, message trùng `id` sẽ bị nối thêm. `add_messages` sẽ cập nhật message cũ thay vì tạo bản sao.

### 2.2 Ghi đè reducer với `Overwrite`

**Mục đích.** Khi một khóa đã gắn reducer nhưng muốn **thay thế hoàn toàn** giá trị hiện tại (thay vì merge), sử dụng `Overwrite`.

```python
from langgraph.types import Overwrite

def replace_messages(state: State):
    return {
        "messages": Overwrite(["replacement message"])
    }
```

Kết quả:

```text
["replacement message"]
```

Toàn bộ danh sách cũ sẽ bị thay thế.

> **!Note:** Trong cùng một super-step, chỉ một node được phép `Overwrite` trên cùng một khóa. Nếu nhiều node cùng ghi đè, LangGraph sẽ ném `InvalidUpdateError`.

### 2.3 Input, Output và Private Schema

**Mục đích.** Khi graph phức tạp, state thường chứa cả dữ liệu đầu vào, kết quả cuối cùng và nhiều dữ liệu trung gian. Việc tách schema giúp **kiểm soát dữ liệu graph nhận vào, trả ra và dữ liệu chỉ dùng nội bộ**.

- `input_schema`: giới hạn dữ liệu được truyền vào graph.
- `output_schema`: giới hạn dữ liệu graph trả về.
- `PrivateState`: chứa các channel chỉ dùng để trao đổi giữa các node.

```python
builder = StateGraph(
    OverallState,
    input_schema=InputState,
    output_schema=OutputState,
)

graph.invoke({"question": "hi"})
# {'answer': 'bye'}
```

> **!Note:** Graph vẫn chỉ có **một state duy nhất** (`OverallState`). Các node vẫn có thể ghi vào mọi channel đã khai báo trong `OverallState`. Ngoài ra, `PrivateState` **không bị ẩn khi streaming**; nếu dùng `stream_mode="values"`, toàn bộ state vẫn được phát ra. Muốn giới hạn dữ liệu stream, sử dụng `output_keys=[...]`.

### 2.4 Pydantic State

**Mục đích.** Có thể sử dụng `Pydantic BaseModel` thay cho `TypedDict` để kiểm tra kiểu dữ liệu đầu vào khi graph bắt đầu chạy.

Ví dụ:

```python
graph.invoke({"a": 123})  # a phải là str
```

Kết quả:

```text
1 validation error for OverallState
a
  Input should be a valid string
```

> **!Note:** Việc validate chỉ diễn ra với **đầu vào của node đầu tiên**. Các node phía sau và giá trị trả về không được validate lại. Với channel `messages`, nên sử dụng `AnyMessage` thay vì `BaseMessage` để đảm bảo serialize và deserialize chính xác.

---

## 3. Cấu hình Runtime

**Mục đích.** Ngoài `state`, LangGraph còn cho phép truyền các tham số chỉ dùng trong **lần thực thi hiện tại** thông qua `runtime.context`. Những dữ liệu này **không thuộc state**, không được lưu, không được truyền giữa các node và cũng không xuất hiện trong kết quả trả về.

Runtime thường dùng để truyền các tham số cấu hình như:

- Model LLM cần sử dụng.
- System prompt.
- API key hoặc endpoint.
- Các cờ cấu hình (debug, temperature,...).

Khai báo schema cho runtime:

```python
from typing_extensions import TypedDict

class ContextSchema(TypedDict):
    model_provider: str
```

Sử dụng trong node:

```python
def node(state: State, runtime: Runtime[ContextSchema]):
    if runtime.context["model_provider"] == "gemini":
        return {"response": "Using Gemini"}

    return {"response": "Using OpenAI"}
```

Truyền giá trị khi chạy graph:

```python
builder = StateGraph(
    State,
    context_schema=ContextSchema,
)

graph.invoke(
    {},
    context={
        "model_provider": "gemini"
    }
)
```

Ở ví dụ trên:

- `state` (input): `{}`.
- `context`: `{"model_provider": "gemini"}`.
- Output của graph:

```python
{
    "response": "Using Gemini"
}
```

`model_provider` chỉ tồn tại trong `runtime.context`; nó **không được lưu vào state** và cũng **không xuất hiện trong output**.

> **!Note:** Chỉ đưa vào `runtime.context` những dữ liệu mang tính cấu hình cho lần chạy hiện tại. Nếu dữ liệu cần được các node cập nhật, chia sẻ hoặc trả về sau khi graph kết thúc, hãy lưu trong `state`.

---

## 4. Chịu lỗi — retry, timeout, error handler

Ba cơ chế này gắn khi `add_node`. Cơ chế đầy đủ (vòng đời timeout, luật kế thừa default) ở [fault-tolerance](../10-runtime/10-02-fault-tolerance.md); đây chỉ là cách gắn nhanh.

**Retry.** `retry_policy=RetryPolicy(...)`. Mặc định retry mọi ngoại lệ **trừ** một nhóm lỗi lập trình (`ValueError`, `TypeError`, `KeyError`/`LookupError`, `RuntimeError`...); với thư viện HTTP như `requests`/`httpx` chỉ retry mã 5xx.

```python
builder.add_node("query_db", query_db, retry_policy=RetryPolicy(retry_on=sqlite3.OperationalError))
builder.add_node("model", call_model, retry_policy=RetryPolicy(max_attempts=5))
```

**Timeout (chỉ node async).** `timeout=` nhận số giây, `timedelta`, hoặc `TimeoutPolicy(run_timeout=..., idle_timeout=...)`. Vượt giờ → `NodeTimeoutError` (kế thừa `TimeoutError`); timeout tính riêng cho mỗi lần thử.

```python
builder.add_node("model", call_model, timeout=1.0)   # đặt trên node sync → lỗi ngay lúc compile
```

**!Note:** Timeout **không dùng cho node sync** — Python sync không hủy an toàn giữa chừng, đặt là lỗi lúc compile. Cần `langgraph>=1.2` cho per-node timeout, error handler, và `set_node_defaults`.

**Error handler.** `error_handler=` chạy sau khi node lỗi và **hết lượt retry**; nhận `NodeError`, định tuyến sang nhánh phục hồi bằng `Command`.

**Default cho cả đồ thị.** `set_node_defaults(retry_policy=..., timeout=..., error_handler=...)` đặt một lần cho mọi node; giá trị đặt riêng trên từng node luôn thắng.

---

## 5. Chuỗi tuần tự

Nối node bằng `add_edge`, hoặc dùng shorthand `add_sequence` :

```python
builder = StateGraph(State).add_sequence([step_1, step_2, step_3])
builder.add_edge(START, "step_1")
```

---

## 6. Rẽ nhánh song song

**Cách làm.** Nhiều edge từ một node. Nhiều edge vào một node. Khóa nào nhiều nhánh cùng ghi thì **phải có reducer** (thường `operator.add`) để tích lũy thay vì ghi đè lẫn nhau.

```python
builder.add_edge("a", "b")    # a fan-out sang b và c
builder.add_edge("a", "c")
builder.add_edge("b", "d")    # b và c fan-in về d
builder.add_edge("c", "d")
```

**Kết quả** với reducer `add` trên khóa `aggregate`:

```
Adding "A" to []                      ← node a chạy trước
Adding "B" to ['A']                   ← b và c cùng super-step, chạy song song
Adding "C" to ['A']                   ← ...nên cùng thấy ['A']
Adding "D" to ['A', 'B', 'C']         ← d đợi cả b và c xong mới chạy
```

**!Note**

- Update từ các nhánh song song **không đảm bảo thứ tự**. Cần thứ tự cố định thì ghi ra một khóa riêng kèm giá trị để sắp xếp.
- Super-step là **giao dịch trọn gói**: một nhánh raise ngoại lệ thì **toàn bộ super-step lỗi**, không update nào được áp. Muốn chịu lỗi cục bộ, bắt lỗi trong node hoặc dùng `retry_policy` (chỉ nhánh lỗi bị thử lại).

**Nhánh dài ngắn khác nhau — `defer=True`.** Khi một nhánh nhiều bước hơn nhánh khác, đặt `defer=True` trên node gộp để nó đợi **mọi tác vụ đang chờ** xong mới chạy:

```python
builder.add_node(d, defer=True)   # d chờ cả nhánh dài (b → b_2) xong mới chạy
```

**Rẽ theo state — conditional edge.** Hàm route đọc state trả về tên node kế; route được tới **nhiều** node cùng lúc bằng cách trả về list.

---

## 7. Map-reduce với `Send`

`Send` được dùng khi **không biết trước số lượng nhánh cần tạo**. Thay vì khai báo cố định các node, LangGraph sẽ tạo **một nhánh cho mỗi phần tử của dữ liệu đầu vào**. Mỗi nhánh có **state riêng** và thực thi độc lập.

```python
def continue_to_jokes(state: OverallState):
    return [
        Send("generate_joke", {"subject": s})
        for s in state["subjects"]
    ]

builder.add_conditional_edges(
    "generate_topics",
    continue_to_jokes,
    ["generate_joke"],
)
```

Ví dụ, nếu:

```python
state["subjects"] = ["AI", "Python", "Football"]
```

thì LangGraph sẽ tạo 3 nhánh:

```text
generate_topics
        |
        v
continue_to_jokes()
        |
   -------------------------
   |           |           |
   v           v           v
generate_joke generate_joke generate_joke
 subject=AI   subject=Python subject=Football
```

Sau khi tất cả các nhánh hoàn thành, kết quả sẽ được **gộp (reduce)** về state chung. Nếu khóa `jokes` sử dụng reducer `operator.add`, các danh sách trả về từ từng nhánh sẽ tự động được nối lại thành một danh sách duy nhất.

> **Tóm lại:** `Send` dùng để thực hiện mô hình **Map-Reduce**: **Map** là tạo nhiều nhánh xử lý song song với state riêng, còn **Reduce** là gộp kết quả của các nhánh vào state chung thông qua reducer.

---

## 8. Vòng lặp và trần đệ quy

**Cách làm.** Tạo vòng bằng edge quay lại, kèm **conditional edge với điều kiện dừng** trỏ về `END`:

```python
def route(state: State) -> Literal["b", END]:
    if len(state["aggregate"]) < 7:      # điều kiện dừng
        return "b"
    return END

builder.add_edge(START, "a")
builder.add_conditional_edges("a", route)
builder.add_edge("b", "a")               # b quay lại a → thành vòng
```

Kiến trúc này giống một ReAct agent: node `a` là model gọi tool, node `b` là tool.

**Trần đệ quy.** Không chắc điều kiện dừng có đạt được không thì đặt `recursion_limit` để chặn:

```python
from langgraph.errors import GraphRecursionError
try:
    graph.invoke({"aggregate": []}, {"recursion_limit": 4})
except GraphRecursionError:
    print("Recursion Error")
```

Muốn **trả về state cuối** thay vì ném lỗi, dùng `RemainingSteps` để dừng chủ động trước khi chạm trần (xem [08-02 mục 8](./08-02-graph-api.md)).

**!Note:** Một "lap" của vòng có nhánh song song tốn **nhiều super-step**. Ví dụ vòng A → B → (C, D song song) là 3 super-step; `recursion_limit=4` chỉ chạy được **một lap**. Đặt trần phải tính theo số super-step mỗi lap, không theo số vòng.

---

## 9. Async

Ba thay đổi để chuyển sync → async: node dùng `async def`, bên trong dùng `await`, gọi đồ thị bằng `.ainvoke`/`.astream`.

```python
async def node(state: MessagesState):
    new_message = await llm.ainvoke(state["messages"])
    return {"messages": [new_message]}

result = await graph.ainvoke({"messages": [input_message]})
```

Async cho cải thiện đáng kể khi chạy nhiều tác vụ I/O đồng thời (nhiều lời gọi API model).

---

## 10. Command — kết hợp cập nhật state và định tuyến

Khái niệm ở [08-02 mục 6](./08-02-graph-api.md). Ở đây là hai công thức hay dùng.

**Trong node — thay cho conditional edge + node cập nhật riêng:**

```python
def node_a(state: State) -> Command[Literal["node_b", "node_c"]]:
    goto = "node_b" if random.choice(["b", "c"]) == "b" else "node_c"
    return Command(update={"foo": goto}, goto=goto)   # vừa đổi state vừa rẽ
```

Đồ thị **không cần** conditional edge — định tuyến nằm trong `Command`.

**Trong tool — cập nhật state từ trong tool:**

```python
@tool
def lookup_user_info(runtime: ToolRuntime):
    user_info = get_user_info(runtime.server_info.user.identity)
    return Command(update={
        "user_info": user_info,
        "messages": [ToolMessage("Looked up", tool_call_id=runtime.tool_call_id)]   # bắt buộc
    })
```

**!Note:** Khi trả `Command` từ tool, **bắt buộc** đưa `messages` vào `update` và list đó **phải chứa một `ToolMessage`** — vì nhà cung cấp LLM yêu cầu message AI có tool call phải được theo sau bởi kết quả tool. Thiếu, lịch sử message thành không hợp lệ. Nên dùng `ToolNode` dựng sẵn để nó tự truyền `Command` từ tool vào state.

**Lên đồ thị cha.** `graph=Command.PARENT` nhảy từ node subgraph sang node đồ thị cha; khóa dùng chung phải có reducer ở state cha.

---

## 11. Trực quan hóa đồ thị

Xuất Mermaid hoặc PNG:

```python
print(app.get_graph().draw_mermaid())          # ra cú pháp Mermaid
display(Image(app.get_graph().draw_mermaid_png()))   # PNG qua Mermaid.Ink (không cần cài thêm)
```

PNG còn dựng được bằng Pyppeteer (`pip install pyppeteer`) hoặc Graphviz (`pip install graphviz`).

---

## Tham chiếu chéo

- [08-02 Graph API](./08-02-graph-api.md) — khái niệm State/reducer/Nodes/Edges/Send/Command
- [08-01 Chọn giữa hai API](./08-01-choosing-apis.md) — Graph API hay Functional API
- Retry / timeout / error / graceful shutdown: `../10-runtime/10-02-fault-tolerance.md`
- Trang gốc: https://docs.langchain.com/oss/python/langgraph/use-graph-api