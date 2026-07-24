---
title: Agents
doc_source: https://docs.langchain.com/oss/python/langchain/agents
accessed: 2026-07-22
lc_version: "1.x"
status: draft
lab:
related:
  - ./models.md
  - ./tools.md
  - ./streaming.md
  - ./structured-output.md
  - ./messages.md
---

# Agents (`create_agent`)

> `create_agent` là hàm dựng agent sẵn dùng của LangChain v1: ghép một model với một bộ tool rồi cho chạy vòng lặp cho tới khi đạt điều kiện dừng.
> Nó dựng graph trên nền LangGraph, nên mọi phương thức của Graph API (`invoke`, `stream`) đều dùng được. Chi tiết từng thành phần nằm ở [models](./models.md), [tools](./tools.md), [structured-output](./structured-output.md).

---


## 1. Agent là gì

### Là gì

Agent là model cộng với một bộ tool, chạy trong vòng lặp: model quyết định gọi tool nào, đọc kết quả trả về, rồi quyết định tiếp. Vòng lặp dừng khi model đưa ra câu trả lời cuối hoặc chạm giới hạn số vòng lặp.

### Dùng để làm gì

Giải quyết loại việc mà người viết code không biết trước cần bao nhiêu bước. Tra một sản phẩm rồi mới biết phải tra tiếp tồn kho hay không — cái đó model quyết lúc chạy, không phải mình viết cứng `if/else`.

### Đoạn code ngắn nhất chạy được

```python
from langchain.agents import create_agent

agent = create_agent("openai:gpt-5.4", tools=tools)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "What's the weather in San Francisco?"}]}
)
```

### Bên trong nó là một graph

```
        ┌──────────────┐
  vào → │  model node  │ ── không gọi tool ──→ trả lời cuối → dừng
        └──────┬───────┘
               │ có tool call
               ▼
        ┌──────────────┐
        │  tools node  │
        └──────┬───────┘
               │ kết quả tool đẩy ngược vào messages
               └──────────────→ quay lại model node
```

Node là một bước, edge là đường nối. Middleware chen thêm node vào giữa các bước này. Doc không vẽ sơ đồ, phần hình trên là **suy luận** từ mô tả "the agent moves through this graph, executing nodes like the model node, the tools node, or middleware".

---

## 2. Model — bộ phận suy luận

Model là thứ quyết định gọi tool nào và khi nào dừng. Có hai cách chỉ định: cố định từ lúc tạo agent, hoặc chọn lúc chạy.

### 2.1 Static model — cố định

**Là gì.** Khai báo một lần lúc tạo agent, không đổi trong suốt lượt chạy. Đây là cách phổ biến.

**Hai lối khai báo:**

| Lối | Code | Khi nào dùng |
|---|---|---|
| Chuỗi định danh | `create_agent("openai:gpt-5.4", tools=tools)` | Chỉ cần chạy được, không cần chỉnh gì |
| Instance của provider | `ChatOpenAI(model="gpt-5.4", temperature=0.1, ...)` | Cần chỉnh `temperature`, `max_tokens`, `timeout`, `base_url` |

```python
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

model = ChatOpenAI(
    model="gpt-5.4",
    temperature=0.1,
    max_tokens=1000,
    timeout=30,
)
agent = create_agent(model, tools=tools)
```

Chuỗi định danh tự suy ra provider: viết `"gpt-5.4"` thì hiểu là `"openai:gpt-5.4"`.

### 2.2 Dynamic model — chọn lúc chạy

**Là gì.** Model được chọn tại thời điểm chạy, dựa vào State và context hiện tại.

**Dùng để làm gì.** Tiết kiệm tiền và định tuyến. Việc dễ giao model rẻ, việc khó mới đẩy lên model đắt.

**Bài toán cụ thể.** Chatbot hỗ trợ khách. Vài câu đầu thường là câu hỏi đơn giản — dùng `gpt-5.4-mini`. Hội thoại kéo dài quá 10 lượt tức là vấn đề rắc rối — chuyển sang `gpt-5.4`.

```python
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse

basic_model = ChatOpenAI(model="gpt-5.4-mini")
advanced_model = ChatOpenAI(model="gpt-5.4")

@wrap_model_call
def dynamic_model_selection(request: ModelRequest, handler) -> ModelResponse:
    message_count = len(request.state["messages"])
    model = advanced_model if message_count > 10 else basic_model
    return handler(request.override(model=model))

agent = create_agent(
    model=basic_model,      # model mặc định
    tools=tools,
    middleware=[dynamic_model_selection],
)
```

Cách đọc đoạn này: `request` là yêu cầu sắp gửi cho model, `handler` là hành động gửi thật. `request.override(model=...)` tạo bản sao của yêu cầu với model khác, rồi mới đưa cho `handler`.

**Bẫy doc nói rõ.** Model pre-bound (đã gọi `bind_tools`) không dùng được cùng structured output. Nếu vừa muốn đổi model động vừa muốn structured output, phải đưa model chưa bind vào middleware.

---

## 3. Tools — bộ phận hành động

Doc liệt kê 5 thứ agent làm được mà model gắn tool trần không làm được:

- gọi nhiều tool nối tiếp nhau chỉ từ một câu hỏi
- gọi song song khi hợp lý
- chọn tool tiếp theo dựa vào kết quả tool trước
- thử lại và xử lý lỗi tool
- giữ State xuyên suốt các lần gọi tool

### 3.1 Static tools — cố định

**Là gì.** Danh sách tool đưa vào lúc tạo agent, không đổi.

Tool là hàm Python thường (hoặc coroutine), bọc bằng decorator `@tool`. Docstring của hàm chính là phần mô tả model đọc để biết khi nào nên gọi — viết docstring cẩu thả thì model gọi sai.

```python
from langchain.tools import tool
from langchain.agents import create_agent

@tool
def search(query: str) -> str:
    """Search for information."""
    return f"Results for: {query}"

@tool
def get_weather(location: str) -> str:
    """Get weather information for a location."""
    return f"Weather in {location}: Sunny, 72°F"

agent = create_agent(model, tools=[search, get_weather])
```

Truyền danh sách rỗng thì agent thu về đúng một node LLM, không còn khả năng gọi tool.

### 3.2 Dynamic tools — đổi bộ tool lúc chạy

**Vì sao cần.** Nhồi quá nhiều tool thì model rối và gọi sai; để quá ít thì agent làm được ít việc. Bộ tool nên co giãn theo trạng thái đăng nhập, quyền của user, feature flag, hoặc giai đoạn hội thoại.

Doc chia làm hai nhánh, khác nhau ở chỗ **đã biết trước danh sách tool hay chưa**.

#### Nhánh A — Lọc bộ tool đã đăng ký sẵn

Đăng ký hết vào `create_agent`, rồi mỗi lượt gọi model thì lọc bớt trước khi gửi. Nguồn để lọc có ba, đây là chỗ dễ lẫn nhất của trang này:

| Nguồn | Đọc bằng | Dữ liệu sống bao lâu | Ví dụ dùng để lọc |
|---|---|---|---|
| **State** | `request.state` | Trong một lượt chạy | Đã xác thực chưa, hội thoại đã dài chưa |
| **Store** | `request.runtime.store` | Lâu dài, xuyên phiên | User này được bật những tính năng nào |
| **Runtime Context** | `request.runtime.context` | Do người gọi truyền vào lúc `invoke` | Vai trò: admin / editor / viewer |

Lọc theo State — chỉ mở tool nhạy cảm sau khi đăng nhập:

```python
@wrap_model_call
def state_based_tools(request: ModelRequest, handler) -> ModelResponse:
    state = request.state
    is_authenticated = state.get("authenticated", False)
    message_count = len(state["messages"])

    if not is_authenticated:
        tools = [t for t in request.tools if t.name.startswith("public_")]
        request = request.override(tools=tools)
    elif message_count < 5:
        tools = [t for t in request.tools if t.name != "advanced_search"]
        request = request.override(tools=tools)

    return handler(request)

agent = create_agent(
    model="gpt-5.4",
    tools=[public_search, private_search, advanced_search],
    middleware=[state_based_tools],
)
```

Lọc theo Runtime Context — phân quyền:

```python
@dataclass
class Context:
    user_role: str

@wrap_model_call
def context_based_tools(request: ModelRequest, handler) -> ModelResponse:
    if request.runtime is None or request.runtime.context is None:
        user_role = "viewer"          # không có context thì lấy quyền thấp nhất
    else:
        user_role = request.runtime.context.user_role

    if user_role == "admin":
        pass                           # admin giữ nguyên toàn bộ tool
    elif user_role == "editor":
        tools = [t for t in request.tools if t.name != "delete_data"]
        request = request.override(tools=tools)
    else:
        tools = [t for t in request.tools if t.name.startswith("read_")]
        request = request.override(tools=tools)

    return handler(request)

agent = create_agent(
    model="gpt-5.4",
    tools=[read_data, write_data, delete_data],
    middleware=[context_based_tools],
    context_schema=Context,
)
```

Bản lọc theo Store dùng cùng khuôn, chỉ khác chỗ lấy dữ liệu: `request.runtime.store.get(("features",), user_id)`.

Hợp với trường hợp: biết hết tool từ lúc khởi động, chỉ cần bật/tắt theo quyền hoặc trạng thái.

#### Nhánh B — Đăng ký tool ngay lúc chạy

Dùng khi tool chỉ xuất hiện lúc chạy: nạp từ MCP server, sinh ra từ dữ liệu của user, lấy từ registry ở xa.

Nhánh này cần **hai** hook, không phải một:

1. `wrap_model_call` — nhét tool mới vào yêu cầu để model biết nó tồn tại
2. `wrap_tool_call` — dạy agent cách chạy tool đó khi model gọi tới

```python
class DynamicToolMiddleware(AgentMiddleware):
    def wrap_model_call(self, request: ModelRequest, handler):
        updated = request.override(tools=[*request.tools, calculate_tip])
        return handler(updated)

    def wrap_tool_call(self, request: ToolCallRequest, handler):
        if request.tool_call["name"] == "calculate_tip":
            return handler(request.override(tool=calculate_tip))
        return handler(request)

agent = create_agent(
    model="gpt-4o",
    tools=[get_weather],          # chỉ tool tĩnh đăng ký ở đây
    middleware=[DynamicToolMiddleware()],
)
```

Thiếu `wrap_tool_call` thì model gọi được tên tool nhưng agent không biết chạy hàm nào. Doc nhấn mạnh chỗ này.

**Chốt hai nhánh:**

| | Nhánh A — lọc | Nhánh B — đăng ký lúc chạy |
|---|---|---|
| Tool có sẵn từ đầu? | Có | Không |
| Hook cần dùng | `wrap_model_call` | `wrap_model_call` + `wrap_tool_call` |
| Tình huống điển hình | Phân quyền, feature flag | MCP server, tool sinh động |

### 3.3 Xử lý lỗi tool

Bọc bằng `@wrap_tool_call`, bắt exception rồi trả về `ToolMessage` chứa lời nhắn cho model thay vì để agent chết.

```python
@wrap_tool_call
def handle_tool_errors(request, handler):
    try:
        return handler(request)
    except Exception as e:
        return ToolMessage(
            content=f"Tool error: Please check your input and try again. ({str(e)})",
            tool_call_id=request.tool_call["id"],
        )
```

Kết quả nằm trong dòng messages:

```
ToolMessage(
    content="Tool error: Please check your input and try again. (division by zero)",
    tool_call_id="..."
)
```

Model đọc được câu này và có cơ hội thử lại với đầu vào khác.

### 3.4 Vòng lặp ReAct trông như thế nào

Prompt: tìm tai nghe không dây đang phổ biến nhất và kiểm tra còn hàng không.

```
================================ Human Message =================================
Find the most popular wireless headphones right now and check if they're in stock
```

Nghĩ: độ phổ biến thay đổi theo thời gian, phải tra. Làm: gọi `search_products`.

```
================================== Ai Message ==================================
Tool Calls:
  search_products (call_abc123)
  Args:
    query: wireless headphones

================================= Tool Message =================================
Found 5 products matching "wireless headphones". Top 5 results: WH-1000XM5, ...
```

Nghĩ: chưa biết còn hàng không. Làm: gọi `check_inventory`.

```
================================== Ai Message ==================================
Tool Calls:
  check_inventory (call_def456)
  Args:
    product_id: WH-1000XM5

================================= Tool Message =================================
Product WH-1000XM5: 10 units in stock
```

Nghĩ: đủ dữ kiện. Làm: trả lời.

```
================================== Ai Message ==================================
I found wireless headphones (model WH-1000XM5) with 10 units in stock...
```

Hai vòng lặp, hai lần model tự quyết. Không có dòng `if` nào của người viết code trong đó.

---

## 4. System prompt

**Là gì.** Câu chỉ dẫn định hình cách agent tiếp cận công việc. Truyền qua tham số `system_prompt`, nhận `str` hoặc `SystemMessage`.

Không truyền thì agent tự đoán việc phải làm từ đám messages.

```python
agent = create_agent(
    model,
    tools,
    system_prompt="You are a helpful assistant. Be concise and accurate.",
)
```

Dùng `SystemMessage` khi cần các tính năng riêng của provider. Ví dụ prompt caching của Anthropic: đánh dấu `cache_control` cho khối văn bản dài để lần gọi sau không phải trả tiền và chờ xử lý lại từ đầu.

```python
literary_agent = create_agent(
    model="google_genai:gemini-3.1-pro-preview",
    system_prompt=SystemMessage(
        content=[
            {"type": "text", "text": "You are an AI assistant tasked with analyzing literary works."},
            {
                "type": "text",
                "text": "<the entire contents of 'Pride and Prejudice'>",
                "cache_control": {"type": "ephemeral"},
            },
        ]
    ),
)
```

### Dynamic system prompt

**Dùng để làm gì.** Đổi lời chỉ dẫn theo người dùng thay vì viết một prompt chung chung cho tất cả.

**Bài toán cụ thể.** Cùng câu hỏi "explain machine learning", user đánh dấu `expert` cần câu trả lời kỹ thuật, user `beginner` cần giải thích không thuật ngữ.

```python
@dynamic_prompt
def user_role_prompt(request: ModelRequest) -> str:
    user_role = request.runtime.context.get("user_role", "user")
    base_prompt = "You are a helpful assistant."

    if user_role == "expert":
        return f"{base_prompt} Provide detailed technical responses."
    elif user_role == "beginner":
        return f"{base_prompt} Explain concepts simply and avoid jargon."
    return base_prompt

result = agent.invoke(
    {"messages": [{"role": "user", "content": "Explain machine learning"}]},
    context={"user_role": "expert"},
)
```

---

## 5. Name

Đặt tên agent bằng tham số `name`. Tên này dùng làm định danh node khi agent bị nhét vào hệ multi-agent như một subgraph.

```python
agent = create_agent(model, tools, name="research_assistant")
```

Viết `snake_case`. Tên có dấu cách hoặc ký tự lạ bị một số provider từ chối thẳng. Quy tắc này áp cho cả tên tool.

---

## 6. Gọi agent

Gọi bằng cách đẩy một cập nhật vào State. Mọi agent đều có `messages` trong State, nên đẩy message mới là đủ:

```python
result = agent.invoke(
    {"messages": [{"role": "user", "content": "What's the weather in San Francisco?"}]}
)
```

Agent tuân theo Graph API của LangGraph nên dùng được cả `stream` và các phương thức khác.

---

## 7. Structured output

Ép agent trả về đúng khuôn dữ liệu, khai báo qua tham số `response_format`. Hai chiến lược:

| | `ToolStrategy` | `ProviderStrategy` |
|---|---|---|
| Cách làm | Dựng một tool giả, model "gọi" tool đó để nộp dữ liệu | Dùng tính năng structured output có sẵn của provider |
| Điều kiện | Model biết gọi tool là được | Provider phải hỗ trợ |
| Độ tin cậy | Thấp hơn | Cao hơn |

```python
class ContactInfo(BaseModel):
    name: str
    email: str
    phone: str

agent = create_agent(
    model="gpt-5.4-mini",
    tools=[search_tool],
    response_format=ToolStrategy(ContactInfo),
)

result["structured_response"]
# ContactInfo(name='John Doe', email='john@example.com', phone='(555) 123-4567')
```

Từ `langchain 1.0`, truyền thẳng schema (`response_format=ContactInfo`) thì thư viện tự chọn `ProviderStrategy` nếu provider hỗ trợ, không thì lùi về `ToolStrategy`. Nói cách khác, phần lớn trường hợp không phải chọn tay.

Chi tiết hai chiến lược xem [structured-output](./structured-output.md).

---

## 8. Memory — State tuỳ biến

Agent tự giữ lịch sử hội thoại trong `messages`. Muốn nhớ thêm thứ khác thì mở rộng State — đây là **trí nhớ ngắn hạn**, sống trong phạm vi một lượt chạy.

State tuỳ biến bắt buộc kế thừa `AgentState` và phải là `TypedDict`.

**Hai cách khai báo, doc ưu tiên cách 1:**

```python
# Cách 1 — qua middleware (ưu tiên)
class CustomState(AgentState):
    user_preferences: dict

class CustomMiddleware(AgentMiddleware):
    state_schema = CustomState
    tools = [tool1, tool2]

    def before_model(self, state: CustomState, runtime) -> dict[str, Any] | None:
        ...

agent = create_agent(model, tools=tools, middleware=[CustomMiddleware()])
```

```python
# Cách 2 — qua state_schema (lối tắt, chỉ khi State chỉ dùng cho tool)
agent = create_agent(model, tools=[tool1, tool2], state_schema=CustomState)
```

Lý do doc ưu tiên cách 1: State mở rộng nằm chung chỗ với middleware và tool dùng nó, không vương vãi ra ngoài. Cách 2 giữ lại để tương thích ngược.

**Đổi từ v1.0:** State tuỳ biến bắt buộc là `TypedDict`. Pydantic model và dataclass không còn dùng được — tài liệu cũ trên mạng viết theo lối cũ sẽ lỗi.

Trí nhớ dài hạn xuyên phiên là chuyện khác, xem long-term memory.

---

## 9. Streaming

`invoke` chỉ trả kết quả cuối. Agent chạy nhiều bước thì phải chờ lâu, không thấy gì. `stream` đẩy từng chặng ra ngay khi có.

```python
for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "Search for AI news and summarize the findings"}]},
    stream_mode="values",
):
    latest_message = chunk["messages"][-1]
    ...
```

`stream_mode="values"` trả về **toàn bộ State** tại mỗi chặng, nên phải tự lấy `messages[-1]` để biết vừa có gì mới. Chi tiết các stream_mode xem [streaming](./streaming.md).

---

## 10. Middleware — bảng các hook xuất hiện trong trang này

| Hook | Chen vào chỗ nào | Trang này dùng để |
|---|---|---|
| `@wrap_model_call` | Bọc lần gọi model | Đổi model động, lọc tool, nhét tool mới |
| `@wrap_tool_call` | Bọc lần chạy tool | Bắt lỗi tool, chạy tool đăng ký lúc chạy |
| `@dynamic_prompt` | Sinh system prompt | Đổi prompt theo vai trò user |
| `@before_model` | Trước khi gọi model | Cắt bớt message, chèn context |
| `@after_model` | Sau khi model trả lời | Guardrail, lọc nội dung |

Middleware chen vào luồng chạy mà không phải sửa lõi agent. Danh sách đầy đủ nằm ở trang Middleware.

---

## 11. Tham số của `create_agent` gặp trong trang này

| Tham số | Nhận gì | Mục |
|---|---|---|
| `model` | chuỗi định danh hoặc instance | 2 |
| `tools` | list tool | 3 |
| `system_prompt` | `str` hoặc `SystemMessage` | 4 |
| `middleware` | list middleware | 2, 3, 4 |
| `response_format` | schema, `ToolStrategy`, `ProviderStrategy` | 7 |
| `state_schema` | `TypedDict` kế thừa `AgentState` | 8 |
| `context_schema` | dataclass hoặc `TypedDict` | 3.2 |
| `store` | ví dụ `InMemoryStore()` | 3.2 |
| `name` | chuỗi `snake_case` | 5 |

Đây là danh sách rút từ các ví dụ trong trang, **không phải** chữ ký đầy đủ của hàm.

---

## Cần kiểm chứng thêm

- [ ] Điều kiện dừng "iteration limit". Doc nói agent chạy tới khi model trả lời cuối **hoặc** chạm giới hạn số vòng lặp, nhưng không nói giới hạn mặc định là bao nhiêu và đặt ở đâu. Xác minh: đọc reference `create_agent` và trang Middleware (có thể là một middleware riêng).
- [ ] `request.override()` nhận được những tham số nào. Trang này thấy `model=`, `tools=`, `tool=` — chưa rõ còn gì khác. Xác minh: reference của `ModelRequest` và `ToolCallRequest`.
- [ ] Cấu trúc namespace của Store. Ví dụ viết `store.get(("features",), user_id)` — tuple đầu là namespace, nhưng doc không giải thích quy tắc đặt. Xác minh: trang Long-term memory hoặc reference LangGraph Store.
- [ ] Kết hợp dynamic model với `response_format`. Doc chỉ nói pre-bound model không dùng được với structured output, chưa xác nhận model chưa bind thì chắc chắn chạy được. Xác minh: chạy thử.
- [ ] Tên model trong ví dụ (`gpt-5.4`, `gemini-3.1-pro-preview`). Chưa rõ có thật hay chỉ là placeholder của bản doc. Xác minh: đối chiếu reference `init_chat_model`.
- [ ] Sơ đồ graph ở mục 1 là **suy luận** từ mô tả chữ, doc không vẽ hình. Xác minh: đọc trang Graph API của LangGraph.
- [ ] Middleware chạy theo thứ tự nào khi truyền nhiều cái vào list. Trang này im lặng. Xác minh: trang Middleware.

---

## Tham chiếu chéo

| File | Bổ sung cho mục nào |
|---|---|
| [models](./models.md) | Mục 2 — tham số model, `init_chat_model` |
| [tools](./tools.md) | Mục 3 — cách viết `@tool`, schema đối số |
| [messages](./messages.md) | Mục 3.3, 4 — `ToolMessage`, `SystemMessage` |
| [structured-output](./structured-output.md) | Mục 7 — `ToolStrategy` vs `ProviderStrategy` |
| [streaming](./streaming.md) | Mục 9 — các `stream_mode` |