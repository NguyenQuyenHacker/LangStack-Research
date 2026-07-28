---
title: Runtime
doc_source: https://docs.langchain.com/oss/python/langchain/runtime
accessed: 2026-07-25
version: "unknown"
status: draft
lab:
related:
  - ./03-03-middleware/03-03-middleware-overview.md
  - ./03-02-tools.md
  - ../04-context-memory/04-03-long-term-memory.md
---

# Runtime — tiêm phụ thuộc vào agent lúc chạy (`Runtime`, `ToolRuntime`)

> `Runtime` là đối tượng LangGraph gắn kèm mỗi lần gọi agent, chứa thông tin tĩnh và tiện ích mà tool và middleware đọc được trong lúc chạy.
> `create_agent` của LangChain chạy trên runtime của LangGraph, nên mọi agent đều có sẵn đối tượng này.

---

## 1. Tổng quan

`Runtime` là chỗ chứa những thứ một lần gọi agent cần biết nhưng không nằm trong lời nhắn của người dùng: người dùng là ai, kết nối cơ sở dữ liệu nào, cấu hình gì. Tool và middleware đọc `Runtime` để lấy những thứ đó.

**Vấn đề nó giải quyết**: Một tool tự nó không biết đang phục vụ khách nào, nối vào cơ sở dữ liệu nào. Nếu viết cứng "user_id = 123" vào tool thì tool đó chỉ chạy được cho một người. Runtime cho phép tiêm những thứ đó từ ngoài vào lúc gọi agent (gọi là dependency injection), nên cùng một tool dùng lại được cho mọi khách chỉ bằng cách đổi giá trị truyền vào.

Đưa `Runtime` vào bằng hai bước: khai kiểu dữ liệu của phần `context` khi tạo agent (`context_schema`), rồi truyền giá trị `context` khi gọi.

```python
from dataclasses import dataclass
from langchain.agents import create_agent

@dataclass
class Context:                                    # khai cấu trúc của context: ở đây chỉ có tên người dùng
    user_name: str

agent = create_agent(
    model="gpt-5-nano",
    tools=[...],
    context_schema=Context                        # gắn kiểu context vào agent
)

agent.invoke(
    {"messages": [{"role": "user", "content": "What's my name?"}]},
    context=Context(user_name="John Smith")       # truyền giá trị context cho lần gọi này
)
```

**Kết quả** : giá trị `user_name="John Smith"` được nạp vào `Runtime` của lần gọi này. Bất kỳ tool hay middleware nào đọc `runtime.context.user_name` đều nhận được `"John Smith"`.

---

## 2. Năm nhóm thông tin trong `Runtime`

`Runtime` chứa 5 nhóm thông tin:

| Nhóm | Mô tả |
|---|---|
| `context` | Thông tin tĩnh của một lần gọi: user id, kết nối DB, hoặc phụ thuộc khác |
| `store` | Một bản `BaseStore` dùng cho long-term memory |
| Stream writer | Đối tượng để gửi thông tin qua chế độ stream `"custom"` |
| `execution_info` | Định danh và thông tin thử lại của lần chạy hiện tại: thread ID, run ID, số lần thử |
| `server_info` | Metadata riêng của server khi chạy trên LangGraph Server: assistant ID, graph ID, người dùng đã xác thực |

Chỉ `context` là thứ mình chủ động khai và truyền vào (mục 1). Bốn nhóm còn lại do hệ thống điền: `store` và Stream writer là tiện ích trỏ sang cơ chế ở trang khác (long-term memory, custom stream); `execution_info` và `server_info` là thông tin chỉ-đọc về lần chạy.

Trang này đi sâu vào cách **đọc** các nhóm này từ hai chỗ: bên trong tool (mục 4) và bên trong middleware (mục 5). Cơ chế của `store` và Stream writer không thuộc phạm vi trang này.

---

## 3. Đọc `Runtime` bên trong tool (`ToolRuntime`)

### Khái niệm

Thêm một tham số kiểu `ToolRuntime` vào hàm tool để lấy đối tượng `Runtime` ngay trong thân tool.

### Vai trò

Tool tự nó không biết người dùng là ai hay nối vào DB nào. `ToolRuntime` là đường để tool đọc `context`, đọc/ghi long-term memory, và ghi vào custom stream — mà không cần biến toàn cục.

### Áp dụng thực tế

Tool tra sở thích viết email của khách hàng. Tool không thể viết cứng một `user_id` vì mỗi lần gọi phục vụ một khách khác nhau. Nó đọc `user_id` từ `context` do agent tiêm vào, rồi lấy sở thích đã lưu của đúng khách đó từ store.

### Triển khai — đọc context và long-term memory

```python
from dataclasses import dataclass
from langchain.tools import tool, ToolRuntime

@dataclass
class Context:
    user_id: str

@tool
def fetch_user_email_preferences(runtime: ToolRuntime[Context]) -> str:   # ToolRuntime[Context] để lấy Runtime kèm đúng kiểu context
    """Fetch the user's email preferences from the store."""
    user_id = runtime.context.user_id                                     # đọc user_id agent đã tiêm vào

    preferences: str = "The user prefers you to write a brief and polite email."   # giá trị mặc định nếu chưa có gì lưu
    if runtime.store:                                                     # store có thể vắng; kiểm trước khi dùng
        if memory := runtime.store.get(("users",), user_id):             # lấy bản ghi đã lưu của đúng user_id này
            preferences = memory.value["preferences"]

    return preferences
```

**Kết quả** : nếu store đã có bản ghi cho `user_id`, tool trả sở thích đã lưu; nếu chưa, tool trả câu mặc định. Cơ chế `store.get` và cấu trúc `memory.value` thuộc trang long-term memory ([long-term-memory.md](../04-context-memory/04-03-long-term-memory.md)), trang này chỉ cho thấy tool lấy `store` từ đâu.

**!Note:** `runtime.store` có thể là `None` — luôn kiểm `if runtime.store` trước khi gọi. Bỏ kiểm mà store vắng thì tool ném lỗi ngay dòng `store.get`.

### Triển khai — đọc `execution_info` và `server_info`

```python
from langchain.tools import tool, ToolRuntime

@tool
def context_aware_tool(runtime: ToolRuntime) -> str:
    """A tool that uses execution and server info."""
    info = runtime.execution_info                              # định danh lần chạy
    print(f"Thread: {info.thread_id}, Run: {info.run_id}")     # thread_id, run_id để lần vết log

    server = runtime.server_info                               # metadata server, chỉ có khi chạy trên LangGraph Server
    if server is not None:                                     # ngoài server thì server_info là None
        print(f"Assistant: {server.assistant_id}")
        if server.user is not None:
            print(f"User: {server.user.identity}")             # danh tính người dùng đã xác thực

    return "done"
```

**Kết quả in ra** (dựng lại):

```
Thread: some_id, Run: 7f3a...          ← luôn in được, execution_info có ở mọi môi trường
Assistant: asst_...                    ← chỉ in khi chạy trên LangGraph Server
User: john@company.com                 ← chỉ in khi có người dùng đã xác thực
```

**!Note:**: Chạy ở máy cá nhân (không phải LangGraph Server) thì `server_info` là `None`, hai dòng cuối không in.

---

## 4. Đọc `Runtime` bên trong middleware

### Khái niệm

Middleware cũng đọc `Runtime` để dựng prompt động, sửa tin nhắn, hoặc điều khiển agent theo thông tin người dùng. Cách lấy `Runtime` khác nhau theo kiểu hook:

- Hook kiểu node (node-style): nhận thẳng một tham số `Runtime`.
- Hook kiểu wrap (wrap-style): `Runtime` nằm trong tham số `ModelRequest`, đọc qua `request.runtime`.


### Vai trò

Cho phép câu system prompt và hành vi agent đổi theo người dùng đang phục vụ — cùng một agent, chào mỗi người bằng đúng tên họ, hoặc đổi giọng theo phân quyền.

### Áp dụng thực tế

Agent tư vấn xưng hô đúng tên khách trong system prompt, và ghi log trước/sau mỗi lần gọi model để lần vết phiên làm việc của từng khách.

### Triển khai — prompt động và hook ghi log

```python
from dataclasses import dataclass
from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import dynamic_prompt, ModelRequest, before_model, after_model
from langgraph.runtime import Runtime

@dataclass
class Context:
    user_name: str

@dynamic_prompt                                                       # hook dựng system prompt ngay trước khi gọi model
def dynamic_system_prompt(request: ModelRequest) -> str:
    user_name = request.runtime.context.user_name                     # hook kiểu wrap: đọc runtime qua request
    return f"You are a helpful assistant. Address the user as {user_name}."

@before_model                                                         # hook chạy trước mỗi lần gọi model
def log_before_model(state: AgentState, runtime: Runtime[Context]) -> dict | None:   # hook kiểu node: nhận thẳng runtime
    print(f"Processing request for user: {runtime.context.user_name}")
    return None                                                       # trả None: không đổi gì, chỉ ghi log

@after_model                                                          # hook chạy sau mỗi lần gọi model
def log_after_model(state: AgentState, runtime: Runtime[Context]) -> dict | None:
    print(f"Completed request for user: {runtime.context.user_name}")
    return None

agent = create_agent(
    model="gpt-5-nano",
    tools=[...],
    middleware=[dynamic_system_prompt, log_before_model, log_after_model],
    context_schema=Context
)

agent.invoke(
    {"messages": [{"role": "user", "content": "What's my name?"}]},
    context=Context(user_name="John Smith")
)
```

**Kết quả in ra** (dựng lại):

```
Processing request for user: John Smith   ← log_before_model in, đọc từ context đã tiêm
Completed request for user: John Smith    ← log_after_model in sau khi model trả lời
```

Hai dòng này in được chắc chắn vì chuỗi ghép thẳng từ `user_name="John Smith"`. Ngoài ra system prompt do `dynamic_system_prompt` sinh sẽ bảo model xưng hô khách là "John Smith", nên câu trả lời cuối gọi đúng tên .

---

## Tham chiếu chéo

- [03-03 Middleware](./03-03-middleware/03-03-middleware-overview.md) — phân biệt hook kiểu node và kiểu wrap, và `ModelRequest`
- [03-02 Tools](./03-02-tools.md) — cách viết tool và tham số `ToolRuntime`
- [04-03 Long-term memory](../04-context-memory/04-03-long-term-memory.md) — cơ chế `store` (`BaseStore`) mà tool đọc ở mục 3
- Custom stream (`"custom"` mode): `https://docs.langchain.com/oss/python/langchain/streaming#custom-updates`
- Runtime API reference: `https://reference.langchain.com/python/langgraph/runtime/Runtime`