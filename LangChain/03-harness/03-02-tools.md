---
title: Tools
doc_source: https://docs.langchain.com/oss/python/langchain/tools
accessed: 2026-07-22
lc_version: "1.x (mục Execution info và Server info yêu cầu langgraph>=1.1.5 hoặc deepagents>=0.5.0)"
status: draft
lab:
related:
  - ./agents.md
  - ./models.md
  - ./messages.md
  - ./streaming.md
---

# Tools (`@tool`, `ToolRuntime`, `ToolNode`)

> Tool là hàm Python có đầu vào và đầu ra khai báo rõ, được đưa cho model để model tự quyết khi nào gọi và gọi với đối số nào.
> Trang này gồm ba lớp: cách viết tool (`@tool`), cách tool đọc dữ liệu xung quanh (`ToolRuntime`), và cách chạy tool trong graph tự dựng (`ToolNode`). Phần agent dùng tool ra sao nằm ở [agents](./agents.md).

---

## 0. Từ điển thuật ngữ

| Từ | Nghĩa dễ hiểu |
|---|---|
| **tool** | Một hàm Python được "giới thiệu" cho model. Model không chạy được nó, chỉ nói ra ý định gọi. |
| **type hint** | Chú thích kiểu trong Python: `query: str`, `limit: int`. Ở đây nó **bắt buộc** vì thư viện dựa vào đó sinh input schema. |
| **input schema** | Bản mô tả tool nhận đối số gì, kiểu gì. Model đọc bản này để biết phải điền gì. |
| **docstring** | Đoạn chú thích trong ngoặc ba nháy ngay dưới tên hàm. Mặc định trở thành mô tả tool cho model đọc. |
| **`args_schema`** | Cách khai báo input schema bằng một class Pydantic riêng thay vì để thư viện tự suy từ type hint. |
| **Pydantic** | Thư viện Python khai báo cấu trúc dữ liệu và kiểm tra ràng buộc. `Field(description=...)` cho phép mô tả từng trường. |
| **`ToolRuntime`** | Một tham số đặc biệt của tool. Khai báo nó thì tool đọc được State, Context, Store... Model không nhìn thấy tham số này. |
| **State** | Sổ ghi của lượt hội thoại đang chạy. Có `messages` và các trường tự thêm. Hết lượt là mất. |
| **Context** | Dữ liệu người gọi truyền vào lúc `invoke`, ví dụ `user_id`. Chỉ đọc, không sửa trong lúc chạy. |
| **Store** | Kho nhớ lâu dài, sống qua nhiều phiên. Tổ chức theo cặp namespace/key. |
| **`Command`** | Giá trị trả về đặc biệt: thay vì chỉ nộp kết quả, tool ra lệnh ghi vào State. |
| **`ToolMessage`** | Message chứa kết quả của một lần gọi tool. Phải gắn `tool_call_id` để biết nó trả lời cho lần gọi nào. |
| **reducer** | Quy tắc gộp khi nhiều tool chạy song song cùng ghi vào một trường State. Giống quy tắc xử lý khi hai người cùng sửa một ô Excel. |
| **`ToolNode`** | Node dựng sẵn chuyên chạy tool trong graph LangGraph tự viết. |
| **`tools_condition`** | Hàm rẽ nhánh sẵn: model có gọi tool thì đi sang node tools, không thì kết thúc. |
| **server-side tool** | Tool chạy ở phía provider (web search, code interpreter). Mình không phải viết và không phải nuôi. |

---

## 1. Tool là gì

### Là gì

Hàm Python có đầu vào và đầu ra định nghĩa rõ, được truyền xuống chat model. Model dựa vào ngữ cảnh hội thoại để quyết định khi nào gọi và điền đối số gì.

Model **không** chạy hàm. Nó chỉ phát ra một tool call — tên hàm kèm đối số. Việc chạy thật do agent hoặc `ToolNode` làm.

### Dùng để làm gì

Mở rộng phạm vi của model ra ngoài đám dữ liệu nó đã học: lấy dữ liệu thời gian thực, chạy code, truy vấn database, thực hiện hành động.

---

## 2. Tạo tool

### 2.1 Cách cơ bản

```python
from langchain.tools import tool

@tool
def search_database(query: str, limit: int = 10) -> str:
    """Search the customer database for records matching the query.

    Args:
        query: Search terms to look for
        limit: Maximum number of results to return
    """
    return f"Found {limit} results for '{query}'"
```

Hai điều doc nhấn mạnh, cùng là chỗ dễ sai:

- **Type hint bắt buộc.** Không có type hint thì không sinh được input schema.
- **Docstring là phần model đọc.** Viết mơ hồ thì model gọi sai lúc, gọi thừa, hoặc bỏ qua tool.

Đặt tên `snake_case`: `web_search`, không phải `Web Search`. Một số provider từ chối thẳng tên có dấu cách hoặc ký tự lạ.

### 2.2 Đổi tên và đổi mô tả

Tên mặc định lấy từ tên hàm, mô tả mặc định lấy từ docstring. Ghi đè khi tên hàm không nói lên việc:

```python
@tool("web_search")
def search(query: str) -> str:
    """Search the web for information."""
    return f"Results for: {query}"

print(search.name)   # web_search
```

```python
@tool("calculator", description="Performs arithmetic calculations. Use this for any math problems.")
def calc(expression: str) -> str:
    """Evaluate mathematical expressions."""
    return str(eval(expression))
```

Ở ví dụ thứ hai, docstring vẫn còn nhưng `description` truyền vào decorator mới là thứ model đọc.

### 2.3 Schema phức tạp — `args_schema`

**Dùng để làm gì.** Khi đối số cần mô tả riêng, giá trị mặc định, hoặc chỉ được nhận vài giá trị cố định. Type hint trần không diễn đạt được những thứ đó.

**Bài toán cụ thể.** Tool tra thời tiết cần biết đơn vị nhiệt độ, và chỉ chấp nhận đúng hai giá trị `celsius` / `fahrenheit`. Để `units: str` thì model có thể điền `"C"`, `"độ C"`, `"Kelvin"`.

```python
from pydantic import BaseModel, Field
from typing import Literal

class WeatherInput(BaseModel):
    """Input for weather queries."""
    location: str = Field(description="City name or coordinates")
    units: Literal["celsius", "fahrenheit"] = Field(
        default="celsius",
        description="Temperature unit preference",
    )
    include_forecast: bool = Field(
        default=False,
        description="Include 5-day forecast",
    )

@tool(args_schema=WeatherInput)
def get_weather(location: str, units: str = "celsius", include_forecast: bool = False) -> str:
    """Get current weather and optional forecast."""
    ...
```

`Literal[...]` khoá tập giá trị. `Field(description=...)` là câu giải thích riêng cho từng đối số, model đọc được.

### 2.4 Hai tên tham số bị cấm

| Tên | Vì sao cấm |
|---|---|
| `config` | Dành cho `RunnableConfig` truyền ngầm vào tool |
| `runtime` | Dành cho tham số `ToolRuntime` |

Đặt trùng hai tên này gây lỗi lúc chạy. Muốn lấy thông tin runtime thì khai báo `ToolRuntime` chứ đừng tự đặt tham số tên `config` hay `runtime` cho mục đích khác.

---

## 3. Truy cập ngữ cảnh — `ToolRuntime`

Thêm tham số `runtime: ToolRuntime` vào chữ ký hàm là tool đọc được dữ liệu xung quanh. Tham số này **được tiêm tự động và ẩn khỏi model** — model chỉ nhìn thấy các đối số còn lại trong schema.

Tám thứ `ToolRuntime` cấp:

| Thành phần | Là gì | Dùng khi nào |
|---|---|---|
| **State** | Trí nhớ ngắn hạn: messages và các trường tự thêm, sửa được | Đọc lịch sử hội thoại, đếm số lần gọi tool |
| **Context** | Cấu hình bất biến truyền lúc `invoke` | Cá nhân hoá theo danh tính người dùng |
| **Store** | Trí nhớ dài hạn, sống qua nhiều phiên | Lưu sở thích user, kho kiến thức |
| **Stream Writer** | Phát cập nhật ra ngoài trong lúc tool đang chạy | Báo tiến độ việc chạy lâu |
| **Execution Info** | thread ID, run ID, lần thử thứ mấy | Ghi log, đổi hành vi khi đang retry |
| **Server Info** | assistant ID, graph ID, user đã xác thực | Chỉ có khi chạy trên LangGraph Server |
| **Config** | `RunnableConfig` của lượt chạy | Lấy callback, tag, metadata |
| **Tool Call ID** | Định danh của chính lần gọi tool này | Gắn vào `ToolMessage`, đối chiếu log |

### 3.1 Ba nguồn dữ liệu dễ lẫn nhất

Bảng này đọc trước sẽ đỡ rối ở các mục sau:

| | State | Context | Store |
|---|---|---|---|
| Đọc bằng | `runtime.state` | `runtime.context` | `runtime.store` |
| Sửa được không | Có, qua `Command` | Không | Có, qua `store.put` |
| Sống bao lâu | Hết lượt là mất | Hết lượt là mất | Qua nhiều phiên |
| Ai đặt vào | Agent và tool trong lúc chạy | Người gọi, lúc `invoke` | Tool hoặc hệ thống, lưu ra ngoài |
| Khai báo ở `create_agent` | `state_schema` | `context_schema` | `store` |

### 3.2 State — đọc

```python
from langchain.tools import tool, ToolRuntime
from langchain.messages import HumanMessage

@tool
def get_last_user_message(runtime: ToolRuntime) -> str:
    """Get the most recent message from the user."""
    messages = runtime.state["messages"]
    for message in reversed(messages):
        if isinstance(message, HumanMessage):
            return message.content
    return "No user messages found"


@tool
def get_user_preference(pref_name: str, runtime: ToolRuntime) -> str:
    """Get a user preference value."""
    preferences = runtime.state.get("user_preferences", {})
    return preferences.get(pref_name, "Not set")
```

Ở tool thứ hai, model chỉ nhìn thấy `pref_name` trong schema. `runtime` bị ẩn.

### 3.3 State — ghi

**Là gì.** Tool trả về `Command` thay vì trả về chuỗi. `Command` mang theo lệnh cập nhật State.

**Dùng để làm gì.** Khi tool không chỉ nộp dữ liệu mà còn phải thay đổi trạng thái của agent.

**Bài toán cụ thể.** User nói "gọi tôi là Ngọc Anh". Tool phải ghi tên vào State để các lượt sau còn dùng, đồng thời phải báo cho model biết là ghi xong.

```python
from langchain.agents import AgentState
from langchain.messages import ToolMessage
from langchain.tools import ToolRuntime, tool
from langgraph.types import Command


class CustomState(AgentState):
    user_name: str


@tool
def set_user_name(new_name: str, runtime: ToolRuntime[None, CustomState]) -> Command:
    """Set the user's name in the conversation state."""
    return Command(
        update={
            "user_name": new_name,
            "messages": [
                ToolMessage(
                    content=f"User name set to {new_name}.",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )
```

Kèm `ToolMessage` vào `update` là bắt buộc nếu muốn model thấy tool đã chạy xong. Không có nó, model chỉ thấy im lặng.

**Bẫy doc cảnh báo.** Model gọi được nhiều tool song song. Hai tool cùng ghi vào một trường State thì cần khai báo **reducer** cho trường đó để quyết cách gộp. Doc không nói mặc định là gì khi thiếu reducer — xem mục "Cần kiểm chứng thêm".

### 3.4 Context

```python
@dataclass
class UserContext:
    user_id: str

@tool
def get_account_info(runtime: ToolRuntime[UserContext]) -> str:
    """Get the current user's account information."""
    user_id = runtime.context.user_id
    ...

agent = create_agent(
    model,
    tools=[get_account_info],
    context_schema=UserContext,
    system_prompt="You are a financial assistant.",
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "What's my current balance?"}]},
    context=UserContext(user_id="user123"),
)
```

Điểm cần thấy: `user_id` do người gọi truyền vào, **không** để model tự điền. Nếu để `user_id` thành đối số thường của tool thì model có thể bịa ra một id khác — đây là chỗ khác biệt về an toàn giữa Context và đối số thường.

### 3.5 Store — trí nhớ dài hạn

Tổ chức theo namespace và key: `store.get(namespace, key)`, `store.put(namespace, key, value)`.

```python
@tool
def get_user_info(user_id: str, runtime: ToolRuntime) -> str:
    """Look up user info."""
    user_info = runtime.store.get(("users",), user_id)
    return str(user_info.value) if user_info else "Unknown user"

@tool
def save_user_info(user_id: str, user_info: dict[str, Any], runtime: ToolRuntime) -> str:
    """Save user info."""
    runtime.store.put(("users",), user_id, user_info)
    return "Successfully saved user info."

agent = create_agent(model, tools=[get_user_info, save_user_info], store=InMemoryStore())
```

Phiên đầu lưu, phiên sau lấy lại được — đó là điểm khác State:

```
# Phiên 1
"Save the following user: userid: abc123, name: Foo, age: 25, email: foo@langchain.dev"

# Phiên 2
"Get user info for user with id 'abc123'"
→ Name: Foo / Age: 25 / Email: foo@langchain.dev
```

`InMemoryStore` chỉ dùng để thử. Chạy thật thì dùng `PostgresStore` hoặc bản lưu bền khác.

### 3.6 Stream writer

**Dùng để làm gì.** Tool chạy lâu thì người dùng ngồi nhìn màn hình trống. `runtime.stream_writer` cho phép đẩy tin tiến độ ra ngoài ngay trong lúc tool chạy.

```python
@tool
def get_weather(city: str, runtime: ToolRuntime) -> str:
    """Get weather for a given city."""
    writer = runtime.stream_writer
    writer(f"Looking up data for city: {city}")
    writer(f"Acquired data for city: {city}")
    return f"It's always sunny in {city}!"
```

Điều kiện: tool phải được gọi bên trong một lượt chạy LangGraph. Gọi hàm trần ngoài graph thì không có chỗ để đẩy tin. Chi tiết xem [streaming](./streaming.md).

### 3.7 Execution info và Server info

`runtime.execution_info` cho `thread_id`, `run_id`, `node_attempt` (đang là lần thử thứ mấy). Dùng để ghi log hoặc đổi hành vi khi đang retry.

`runtime.server_info` cho `assistant_id`, `graph_id`, `user.identity`. Trả về `None` khi tool không chạy trên LangGraph Server — chạy local hay chạy test thì luôn `None`, phải kiểm tra trước khi dùng.

Cả hai yêu cầu `langgraph>=1.1.5` hoặc `deepagents>=0.5.0`.

---

## 4. Tool trả về cái gì

Ba kiểu, khác nhau ở chỗ có động vào State hay không:

| Trả về | Chuyện gì xảy ra | Dùng khi |
|---|---|---|
| `str` | Chuyển thành `ToolMessage`, model đọc rồi quyết bước tiếp | Kết quả vốn là văn bản người đọc được |
| `dict` / object | Được serialize rồi gửi lại, model đọc từng trường | Bước suy luận sau cần trường rõ ràng thay vì văn xuôi |
| `Command` | Ghi vào State qua `update`; State mới dùng được ở các bước sau trong cùng lượt chạy | Tool vừa trả dữ liệu vừa thay đổi trạng thái |

Hai kiểu đầu **không** đụng vào State.

```python
# str
@tool
def get_weather(city: str) -> str:
    """Get weather for a city."""
    return f"It is currently sunny in {city}."

# object
@tool
def get_weather_data(city: str) -> dict:
    """Get structured weather data for a city."""
    return {"city": city, "temperature_c": 22, "conditions": "sunny"}

# Command
@tool
def set_language(language: str, runtime: ToolRuntime) -> Command:
    """Set the preferred response language."""
    return Command(
        update={
            "preferred_language": language,
            "messages": [
                ToolMessage(content=f"Language set to {language}.", tool_call_id=runtime.tool_call_id)
            ],
        }
    )
```

---

## 5. `ToolNode` — chạy tool trong graph tự dựng

### Là gì

Node dựng sẵn chuyên chạy tool. Nó tự lo chạy song song, bắt lỗi, và tiêm State vào tool.

### Dùng để làm gì

`create_agent` đã bọc sẵn `ToolNode` bên trong. Dùng `ToolNode` trực tiếp khi tự dựng graph và cần kiểm soát chi tiết luồng chạy tool — nó là viên gạch nằm dưới agent.

```python
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, MessagesState, START, END

tool_node = ToolNode([search, calculator])

builder = StateGraph(MessagesState)
builder.add_node("tools", tool_node)
```

### 5.1 Xử lý lỗi — `handle_tool_errors`

Năm cách cấu hình, xếp từ mặc định tới chi tiết nhất:

```python
ToolNode(tools)                                              # mặc định: bắt lỗi gọi sai, ném tiếp lỗi lúc chạy
ToolNode(tools, handle_tool_errors=True)                     # bắt hết, trả thông báo lỗi cho model
ToolNode(tools, handle_tool_errors="Something went wrong.")  # thông báo lỗi tự viết
ToolNode(tools, handle_tool_errors=handle_error)             # hàm xử lý riêng
ToolNode(tools, handle_tool_errors=(ValueError, TypeError))  # chỉ bắt vài loại exception
```

Phân biệt hai loại lỗi trong dòng mặc định: **lỗi gọi sai** là model điền thiếu hoặc sai kiểu đối số; **lỗi lúc chạy** là bản thân hàm nổ. Mặc định chỉ bắt loại đầu, loại sau để nổ ra ngoài. Doc không nói rõ ranh giới hơn nữa.

### 5.2 Rẽ nhánh — `tools_condition`

```python
builder.add_edge(START, "llm")
builder.add_conditional_edges("llm", tools_condition)   # đi "tools" hoặc END
builder.add_edge("tools", "llm")
graph = builder.compile()
```

Đây chính là vòng lặp của agent viết tay ra: model → có tool call thì chạy tool → quay lại model; không có thì kết thúc.

### 5.3 Tiêm State

`ToolNode` cũng tự tiêm `ToolRuntime`, y như trong agent:

```python
@tool
def get_message_count(runtime: ToolRuntime) -> str:
    """Get the number of messages in the conversation."""
    return f"There are {len(runtime.state['messages'])} messages."

tool_node = ToolNode([get_message_count])
```

---

## 6. Tool có sẵn và tool chạy phía server

**Prebuilt tools.** LangChain có sẵn một bộ tool và toolkit cho các việc thường gặp: tìm kiếm web, chạy code, truy cập database. Danh sách nằm ở trang integrations, không phải trang này.

**Server-side tool.** Vài chat model có tool tích hợp sẵn do chính provider chạy — web search, code interpreter. Không phải viết logic, không phải nuôi hạ tầng. Cách bật nằm ở trang của từng provider và trang [models](./models.md).

Ranh giới: prebuilt tool vẫn chạy trên máy mình, server-side tool chạy ở phía provider.

---

## Cần kiểm chứng thêm

- [ ] Thiếu reducer thì chuyện gì xảy ra khi hai tool song song cùng ghi một trường State. Doc chỉ khuyên "consider defining a reducer", không nói hành vi mặc định. Xác minh: trang Graph API mục reducers, hoặc chạy thử hai tool cùng ghi.
- [ ] Ranh giới "invocation errors" và "execution errors" trong `ToolNode` mặc định. Doc dùng hai từ này mà không định nghĩa. Xác minh: reference `ToolNode`.
- [ ] `ToolRuntime[None, CustomState]` — hai tham số generic nghĩa là gì. Suy luận từ ví dụ: cái đầu là context schema, cái sau là state schema, nhưng doc **không** khẳng định. Xác minh: reference `ToolRuntime`.
- [ ] Cấu trúc namespace của Store. Ví dụ viết `("users",)` là tuple một phần tử — chưa rõ quy tắc đặt nhiều tầng và cách phân tách theo user. Xác minh: trang Long-term memory.
- [ ] Khi vừa truyền `args_schema` vừa để type hint ở hàm, cái nào thắng nếu hai bên lệch nhau. Doc không nói. Xác minh: chạy thử.
- [ ] Kết quả `writer(...)` của stream writer hiện ra ở `stream_mode` nào. Doc đẩy sang trang Streaming. Xác minh: đối chiếu [streaming](./streaming.md) mục custom stream mode.
- [ ] Trang này không nhắc `wrap_tool_call` (middleware bọc lần chạy tool) trong khi trang Agents dùng nhiều. Chưa rõ quan hệ giữa `wrap_tool_call` và `handle_tool_errors` của `ToolNode` — chồng lấn hay hai tầng khác nhau. Xác minh: trang Middleware.

---

## Tham chiếu chéo

| File | Bổ sung cho mục nào |
|---|---|
| [agents](./agents.md) | Mục 3, 5 — static/dynamic tools, `wrap_tool_call`, vòng lặp ReAct |
| [models](./models.md) | Mục 1, 6 — cơ chế tool calling ở phía model, server-side tool |
| [messages](./messages.md) | Mục 3.3, 4 — `ToolMessage`, `tool_call_id` |
| [streaming](./streaming.md) | Mục 3.6 — stream writer |