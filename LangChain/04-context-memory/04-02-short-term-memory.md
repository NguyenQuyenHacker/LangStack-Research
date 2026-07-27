---
title: Short-term memory
doc_source: https://docs.langchain.com/oss/python/langchain/short-term-memory
accessed: 2026-07-25
lc_version: unknown
status: draft
lab:
related:
  - ./memory.md
  - ./long-term-memory.md
---

# Short-term memory (`checkpointer`)

> Trí nhớ trong phạm vi một thread: agent nhớ được các lượt trước của cùng một cuộc hội thoại, nhưng không mang sang cuộc khác.
> Vì sao có hai loại trí nhớ và long-term khác gì — xem [memory](./memory.md). Nhớ xuyên cuộc — xem [long-term-memory](./long-term-memory.md).

---

## 1. Tổng quan

Short-term memory cho ứng dụng nhớ lại các lượt tương tác trong **một** thread. Một *thread* gom nhiều lượt trong một phiên, giống email gom thư vào một cuộc trao đổi.

Cơ chế: LangChain quản lý short-term memory như một phần trạng thái (state) của agent. State được lưu xuống cơ sở dữ liệu (hoặc bộ nhớ) qua một *checkpointer* — thứ chịu trách nhiệm lưu và nạp lại trạng thái — để thread chạy tiếp bất cứ lúc nào. State cập nhật mỗi khi agent được gọi hoặc một bước (như một lần gọi tool) hoàn tất, và được đọc lại ở đầu mỗi bước.

```python
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver          # bộ lưu state trong RAM, dùng để thử

def get_user_info() -> str:
    """Look up information about the current user."""
    return "No user profile on file."

agent = create_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[get_user_info],
    checkpointer=InMemorySaver(),                              # bật short-term memory bằng cách gắn checkpointer
)

thread_config = {"configurable": {"thread_id": "1"}}           # thread_id định danh cuộc hội thoại; cùng id là cùng thread
response = agent.invoke(
    {"messages": [{"role": "user", "content": "Hi! My name is Bob."}]},
    thread_config,
)["messages"][-1].content
print(response)                                                # "Hi Bob! Nice to see you here. How are you doing?"

response = agent.invoke(
    {"messages": [{"role": "user", "content": "What's my name?"}]},
    thread_config,                                             # vẫn thread_id="1" nên agent còn nhớ tên Bob
)["messages"][-1].content
print(response)                                                # "You are Bob!"
```

**Kết quả in ra:**

```
Hi Bob! Nice to see you here. How are you doing?     ← lượt 1
You are Bob!                                         ← lượt 2 vẫn nhớ, vì cùng thread_id
```

Đây là output lấy nguyên từ tài liệu, không dựng lại. Không có checkpointer thì lượt 2 sẽ không biết tên Bob.

**Quan hệ với long-term memory.** Short-term chết theo thread: đổi `thread_id` là mất sạch. Muốn nhớ xuyên thread, phải dùng long-term ([long-term-memory](./long-term-memory.md)) — lưu vào store thay vì vào state.

---

## 2. Checkpointer khi lên production

`InMemorySaver` lưu vào RAM, mất khi tắt tiến trình — chỉ hợp để thử. Lên production dùng checkpointer gắn cơ sở dữ liệu:

```shell
pip install langgraph-checkpoint-postgres
```

```python
from langchain.agents import create_agent
from langgraph.checkpoint.postgres import PostgresSaver        # checkpointer lưu xuống PostgreSQL

def get_user_info() -> str:
    """Look up information about the current user."""
    return "No user profile on file."

DB_URI = "postgresql://postgres:postgres@localhost:5432/postgres?sslmode=disable"
with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    checkpointer.setup()                                       # tự tạo bảng trong PostgreSQL ở lần đầu
    agent = create_agent(
        "gpt-5.5",
        tools=[get_user_info],
        checkpointer=checkpointer,
    )
```

Ngoài Postgres còn SQLite, Azure Cosmos DB. Danh sách đầy đủ các checkpointer nằm ở trang Persistence (`/oss/python/langgraph/checkpointers`), không thuộc phạm vi trang này.

---

## 3. Mở rộng state của agent

**Khái niệm.** Mặc định agent dùng `AgentState` để quản short-term memory, cụ thể là lịch sử hội thoại qua khóa `messages`. Có thể kế thừa `AgentState` để thêm trường riêng, rồi truyền lược đồ mới cho `create_agent` qua tham số `state_schema`.

**Vai trò.** Khi cần lưu thêm dữ liệu ngoài tin nhắn — ID người dùng, sở thích, kết quả trung gian — mà vẫn muốn nó nằm trong state của thread.

**Triển khai.**

```python
from langchain.agents import create_agent, AgentState
from langgraph.checkpoint.memory import InMemorySaver

class CustomAgentState(AgentState):                            # kế thừa AgentState, giữ nguyên khóa messages sẵn có
    user_id: str                                              # thêm trường riêng
    preferences: dict

agent = create_agent(
    "gpt-5.5",
    tools=[get_user_info],
    state_schema=CustomAgentState,                            # khai báo lược đồ state mở rộng cho agent
    checkpointer=InMemorySaver(),
)

result = agent.invoke(                                        # trường riêng truyền vào ngay trong invoke
    {
        "messages": [{"role": "user", "content": "Hello"}],
        "user_id": "user_123",
        "preferences": {"theme": "dark"},
    },
    {"configurable": {"thread_id": "1"}},
)
```

Tài liệu không in kết quả cho ví dụ này.

---

## 4. Quản lý lịch sử tin nhắn

Bật short-term memory rồi thì hội thoại dài có thể vượt context window của model. Trang tài liệu đưa ba cách gọt, cộng một hướng "tự chế" không có ví dụ.

### 4.1 Cắt bớt tin nhắn — trim

**Khái niệm.** Giữ lại N tin nhắn đầu hoặc cuối, bỏ phần giữa, trước khi gọi model. Cách quyết định khi nào cắt: đếm token trong lịch sử, gần chạm giới hạn thì cắt.

**Vai trò.** Ép lịch sử vừa context window mà vẫn giữ tin nhắn hệ thống đầu và vài lượt gần nhất.


### 4.2 Xóa tin nhắn — delete

**Khái niệm.** Xóa hẳn tin nhắn khỏi state của graph, khác với cắt ở chỗ đây là thao tác xóa trực tiếp bằng `RemoveMessage`.

**Vai trò.** Khi muốn bỏ vài tin nhắn cụ thể hoặc xóa toàn bộ lịch sử.

### 4.3 Tóm tắt tin nhắn — summarize

**Khái niệm.** Thay vì cắt/xóa (làm mất thông tin), dùng một chat model tóm tắt phần lịch sử cũ rồi thay bằng bản tóm tắt.

**Vai trò.** Giữ được ý của các lượt cũ trong khi vẫn thu gọn token — bù đúng cái mà cắt và xóa làm mất.

**Triển khai.** Dùng middleware dựng sẵn `SummarizationMiddleware`:

---

## 5. Đọc và ghi state trong tool

State của agent (chính là short-term memory) đọc và ghi được từ bên trong tool qua tham số `runtime`, kiểu `ToolRuntime`.

### 5.1 Đọc state trong tool

**Khái niệm.** Tool nhận thêm tham số `runtime` (kiểu `ToolRuntime`) để chạm vào state. Tham số này **bị giấu khỏi chữ ký tool** nên model không nhìn thấy, nhưng tool vẫn đọc được state qua nó.

**Vai trò.** Tool cần dữ liệu đang nằm trong state (ví dụ `user_id` đã truyền lúc invoke) mà không muốn model phải tự điền.

**Triển khai.**

```python
from langchain.agents import create_agent, AgentState
from langchain.tools import tool, ToolRuntime

class CustomState(AgentState):
    user_id: str

@tool
def get_user_info(runtime: ToolRuntime) -> str:               # runtime bị giấu khỏi model, không tính là tham số tool
    """Look up user info."""
    user_id = runtime.state["user_id"]                        # đọc trường user_id trong state ra
    return "User is John Smith" if user_id == "user_123" else "Unknown user"

agent = create_agent(model="gpt-5-nano", tools=[get_user_info], state_schema=CustomState)
result = agent.invoke({"messages": "look up user information", "user_id": "user_123"})
print(result["messages"][-1].content)                         # > User is John Smith.
```

**Kết quả in ra:**

```
User is John Smith.                                  ← vì user_id trong state khớp "user_123"
```

### 5.2 Ghi state từ tool

**Khái niệm.** Tool sửa được state trong lúc chạy bằng cách trả về một `Command` chứa phần cập nhật.

**Vai trò.** Lưu kết quả trung gian, hoặc để tool sau / prompt sau đọc được cái tool này vừa tính ra.

**Triển khai.** Hai tool phối hợp: `update_user_info` ghi tên vào state, `greet` đọc tên đó ra:

```python
from langchain.tools import tool, ToolRuntime
from langchain.messages import ToolMessage
from langchain.agents import create_agent, AgentState
from langgraph.types import Command
from pydantic import BaseModel

class CustomState(AgentState):
    user_name: str

class CustomContext(BaseModel):
    user_id: str

@tool
def update_user_info(runtime: ToolRuntime[CustomContext, CustomState]) -> Command:
    """Look up and update user info."""
    user_id = runtime.context.user_id                         # user_id lấy từ context, không phải state
    name = "John Smith" if user_id == "user_123" else "Unknown user"
    return Command(update={                                   # trả Command để ghi vào state
        "user_name": name,
        "messages": [
            ToolMessage("Successfully looked up user information", tool_call_id=runtime.tool_call_id)
        ],
    })

@tool
def greet(runtime: ToolRuntime[CustomContext, CustomState]) -> str | Command:
    """Use this to greet the user once you found their info."""
    user_name = runtime.state.get("user_name", None)          # đọc cái tool kia vừa ghi
    if user_name is None:
        return Command(update={                              # chưa có tên thì nhắc model gọi tool kia trước
            "messages": [
                ToolMessage(
                    "Please call the 'update_user_info' tool it will get and update the user's name.",
                    tool_call_id=runtime.tool_call_id,
                )
            ]
        })
    return f"Hello {user_name}!"

agent = create_agent(
    model="gpt-5-nano",
    tools=[update_user_info, greet],
    state_schema=CustomState,
    context_schema=CustomContext,
)
agent.invoke(
    {"messages": [{"role": "user", "content": "greet the user"}]},
    context=CustomContext(user_id="user_123"),
)
```

Tài liệu không in kết quả cho ví dụ này.

---

## 6. Đọc state trong prompt và middleware

Ngoài tool, còn ba chỗ nữa chạm được state: prompt động, `@before_model`, `@after_model`.

### 6.1 Prompt động

**Khái niệm.** Dùng `@dynamic_prompt` để dựng system prompt dựa trên state hoặc context của cuộc hội thoại.

**Vai trò.** Đổi lời hệ thống theo từng người dùng mà không sửa code agent.

**Triển khai.**

```python
from langchain.agents import create_agent
from typing import TypedDict
from langchain.agents.middleware import dynamic_prompt, ModelRequest

class CustomContext(TypedDict):
    user_name: str

def get_weather(city: str) -> str:
    """Get the weather in a city."""
    return f"The weather in {city} is always sunny!"

@dynamic_prompt
def dynamic_system_prompt(request: ModelRequest) -> str:
    user_name = request.runtime.context["user_name"]          # lấy tên từ context để chèn vào prompt
    return f"You are a helpful assistant. Address the user as {user_name}."

agent = create_agent(
    model="gpt-5-nano",
    tools=[get_weather],
    middleware=[dynamic_system_prompt],
    context_schema=CustomContext,
)
result = agent.invoke(
    {"messages": [{"role": "user", "content": "What is the weather in SF?"}]},
    context=CustomContext(user_name="John Smith"),
)
for msg in result["messages"]:
    msg.pretty_print()
```

**Kết quả in ra** (rút gọn, lấy từ tài liệu):

```
================================ Human Message =================================
What is the weather in SF?
================================== Ai Message ==================================
Tool Calls:
  get_weather (...)                                  ← model tự gọi tool thời tiết
    Args: city: San Francisco
================================= Tool Message =================================
The weather in San Francisco is always sunny!        ← kết quả tool
================================== Ai Message ==================================
Hi John Smith, the weather in San Francisco is always sunny!   ← xưng "John Smith" đúng như prompt động đặt
```

### 6.2 Trước / sau khi gọi model — `before_model` và `after_model`

**Khái niệm.** `@before_model` là middleware chạy *trước* mỗi lần gọi model; `@after_model` chạy *sau*. Cả hai đều đọc và sửa được state.

**Vai trò.** `before_model` để xử lý tin nhắn trước khi đưa vào model (ví dụ cắt lịch sử — chính là [mục 4.1](#41-cắt-bớt-tin-nhắn--trim)). `after_model` để xử lý sau khi model trả lời (ví dụ chặn câu trả lời chứa từ nhạy cảm).

Luồng chạy (theo sơ đồ trong tài liệu):

```
before_model:  __start__ → before_model → model → (tools → before_model) / __end__
after_model:   __start__ → model → after_model → (tools → model) / __end__
```

**Triển khai `after_model`** — chặn câu trả lời lộ từ khóa nhạy cảm:

```python
from langchain.messages import RemoveMessage
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import after_model
from langgraph.runtime import Runtime

@after_model
def validate_response(state: AgentState, runtime: Runtime) -> dict | None:
    """Remove messages containing sensitive words."""
    STOP_WORDS = ["password", "secret"]
    last_message = state["messages"][-1]                      # chỉ soi câu trả lời vừa sinh
    if any(word in last_message.content for word in STOP_WORDS):
        return {"messages": [RemoveMessage(id=last_message.id)]}  # dính từ cấm thì xóa câu đó
    return None

agent = create_agent(
    model="gpt-5-nano",
    tools=[],
    middleware=[validate_response],
    checkpointer=InMemorySaver(),
)
```

Tài liệu không in kết quả cho ví dụ `after_model` này. Code `before_model` ở [mục 4.1](#41-cắt-bớt-tin-nhắn--trim) chính là ví dụ đọc state trong `@before_model`, không lặp lại ở đây.

---

## 7. Bốn cách chạm state — chọn cái nào

| Cách | Chạy ở đâu | Đọc state | Ghi state | Dùng khi |
|---|---|---|---|---|
| Tool + `ToolRuntime` | Trong lúc gọi tool | Có | Có (trả `Command`) | Tool cần dữ liệu state hoặc lưu kết quả cho tool sau |
| `@dynamic_prompt` | Ngay trước khi dựng prompt | Có (qua context/state) | Không | Đổi lời hệ thống theo người dùng |
| `@before_model` | Trước mỗi lần gọi model | Có | Có | Gọt lịch sử trước khi vào model |
| `@after_model` | Sau mỗi lần gọi model | Có | Có | Kiểm/chặn/xóa câu trả lời vừa sinh |

---

## 8. Tham chiếu chéo

- [memory](./memory.md) — vì sao có hai loại trí nhớ; ba kiểu trí nhớ dài hạn; hai thời điểm ghi.
- [long-term-memory](./long-term-memory.md) — nhớ xuyên thread bằng store; đối chiếu trực tiếp: ở đây dữ liệu vào **state**, bên đó vào **store**.
- Trang tài liệu khác được nêu tên trong nguồn (chưa nghiên cứu ở đây): middleware (`/oss/python/langchain/middleware`), Tools / `ToolRuntime`, Persistence & checkpointers (`/oss/python/langgraph/checkpointers`), reducers (`/oss/python/langgraph/graph-api#reducers`).