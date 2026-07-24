---
title: Agents
doc_source: https://docs.langchain.com/oss/python/langchain/agents
accessed: 2026-07-22
lc_version: "1.x"
status: draft
lab:
---

# Agents (`create_agent`)

> Trang này định nghĩa agent và giới thiệu `create_agent` — một *harness* cấu hình được. Nó nêu bốn thành phần lõi, cách gọi agent, cách nhận tiến độ, và sáu nhóm năng lực mở rộng bằng middleware.
> Trang cố tình viết ngắn: mỗi mục chỉ vài câu kèm một khối code rồi trỏ sang trang chuyên sâu. Note này giữ đúng độ sâu đó.

> **Về các khối kết quả in ra.** Trang gốc không in kết quả cho khối code nào; chỗ duy nhất có là dòng chú thích `# Answer(summary=..., confidence=...)`. Ba khối kết quả trong file này tôi dựng lại từ mô tả của trang, đều gắn nhãn `(dựng lại)`. Cần đối chiếu khi chạy thử.
>
> Code trên trang có bảy tab theo nhà cung cấp model. Note này lấy tab Google; đổi chuỗi model là chạy được với nhà cung cấp khác.

---

## 1. Tổng quan

Agent là một model gọi tool trong một vòng lặp, cho tới khi nhiệm vụ được giao hoàn thành.

Cách trang này đóng khung vấn đề, và cũng là điểm khác so với cách nghĩ "agent = model thông minh hơn":

> **Agent = Model + Harness**
>
> Việc của harness: đưa cho model đúng bối cảnh, vào đúng lúc, cho nhiệm vụ đang làm.

Harness là toàn bộ những gì bao quanh vòng lặp — model, prompt của nó, tool của nó, và mọi middleware định hình hành vi. Model chỉ là một mảnh; phần còn lại quyết định model nhìn thấy gì tại mỗi lượt.

`create_agent` là một harness cấu hình được ở mức cao. Bản đơn giản nhất:

```python
from langchain.agents import create_agent

agent = create_agent(model="google_genai:gemini-3.5-flash", tools=tools)   # đủ để có một agent chạy được
```

Từ đó, ba tham số `model=`, `tools=`, `system_prompt=` lo phần cơ bản. Năng lực sâu hơn thì mở rộng harness bằng middleware (mục 5).

---

## 2. Bảng tham số của `create_agent`

Chỉ những tham số xuất hiện trên trang này.

| Tham số | Nhận gì | Dùng để |
|---|---|---|
| `model` | chuỗi `"nhà_cung_cấp:model"`, hoặc một bản model đã khởi tạo | Chọn model |
| `tools` | danh sách callable Python, tool của LangChain, hoặc tool dạng dict | Cho agent khả năng hành động |
| `system_prompt` | `str` hoặc `SystemMessage` | Định hình cách agent tiếp cận nhiệm vụ |
| `response_format` | một schema (ví dụ lớp Pydantic) | Ép agent trả về dữ liệu đã kiểm tra theo schema |
| `checkpointer` | ví dụ `InMemorySaver()` | Điều kiện để `thread_id` giữ được lịch sử hội thoại |
| `context_schema` | dataclass | Khai hình dạng dữ liệu truyền theo từng lần chạy |
| `middleware` | danh sách middleware | Mở rộng harness (mục 5) |
| `name` | `str` | Định danh agent khi nhúng làm agent con |

---

## 3. Bốn thành phần lõi

### 3.1 Model

**Khái niệm.** Model được chọn bằng một chuỗi định danh dạng `"nhà_cung_cấp:model"`, hoặc bằng một bản model đã khởi tạo sẵn.

**Vai trò.** Đây là phần suy luận của agent. Chuỗi định danh đủ cho phần lớn trường hợp; cần chỉnh tham số của model thì truyền bản đã khởi tạo.

```python
from langchain.agents import create_agent

agent = create_agent(model="google_genai:gemini-3.5-flash", tools=tools)
```

Tham số của model, cách khai báo nhà cung cấp và cách chọn model động đều nằm ở trang Models, không thuộc trang này.

### 3.2 Tools

**Khái niệm.** Truyền cho agent bất kỳ callable Python nào, một tool của LangChain, hoặc một tool dạng dict.

**Vai trò.** Tool là chỗ agent chạm được vào thế giới bên ngoài. Không có tool thì agent chỉ sinh chữ.

```python
from langchain.agents import create_agent
from langchain.tools import tool


@tool                                                    # decorator biến hàm thường thành tool
def search(query: str) -> str:
    """Search for information."""                        # docstring là mô tả model đọc để quyết định gọi
    return f"Results for: {query}"


agent = create_agent(model="google_genai:gemini-3.5-flash", tools=[search])
```

Cách định nghĩa tool, cách tool đọc bối cảnh, và cách chọn tool động nằm ở trang Tools.

### 3.3 System prompt

**Khái niệm.** Tham số nhận một chuỗi hoặc một `SystemMessage`.

**Vai trò.** Định hình cách agent tiếp cận nhiệm vụ.

```python
agent = create_agent(
    model="google_genai:gemini-3.5-flash",
    tools=tools,
    system_prompt="You are a helpful assistant. Be concise and accurate.",
)
```

Prompt sinh ra lúc chạy thì dùng middleware — trang này chỉ đặt link, không mô tả cách làm.

### 3.4 Structured output

**Khái niệm.** Tham số `response_format=` nhận một schema; agent trả về dữ liệu đã được kiểm tra theo schema đó.

**Vai trò.** Đầu ra vào thẳng hệ thống khác thay vì phải bóc tách từ văn bản tự do.

**Áp dụng thực tế.** Agent đọc bản tin thị trường rồi đẩy kết quả vào một bảng theo dõi: cần đúng hai trường tóm tắt và mức tin cậy, không cần đoạn văn.

```python
from pydantic import BaseModel
from langchain.agents import create_agent


class Answer(BaseModel):                                 # schema mô tả hình dạng dữ liệu cần lấy
    summary: str
    confidence: float


agent = create_agent(model="google_genai:gemini-3.5-flash", tools=tools, response_format=Answer)
result = agent.invoke({"messages": [{"role": "user", "content": "Summarize AI trends"}]})
result["structured_response"]                            # dữ liệu có cấu trúc nằm ở khóa riêng, không ở messages
```

**Kết quả in ra:**

```
Answer(summary=..., confidence=...)     ← đối tượng Python đã kiểm tra theo schema, dùng được ngay
```

Các chiến lược sinh đầu ra có cấu trúc nằm ở trang Structured output.

---

## 4. Gọi agent

### 4.1 Gọi kèm `thread_id`

**Khái niệm.** Gọi agent bằng một message. Bên dưới, message đó là một bản cập nhật vào trạng thái của agent. Kèm theo là `thread_id` để agent lưu lại và nối tiếp được lịch sử hội thoại.

**Vai trò.** Không có `thread_id`, mỗi lần gọi là một cuộc nói chuyện mới. Có `thread_id`, lượt sau biết lượt trước đã nói gì.

```python
from langchain.agents import create_agent
from langchain_core.utils.uuid import uuid7
from langgraph.checkpoint.memory import InMemorySaver

agent = create_agent(
    model="google_genai:gemini-3.5-flash",
    tools=[],
    checkpointer=InMemorySaver(),                        # thiếu dòng này thì thread_id không giữ được gì
)

config = {"configurable": {"thread_id": str(uuid7())}}   # thread_id nằm trong config, không phải tham số riêng

result = agent.invoke(
    {"messages": [{"role": "user", "content": "What's the weather in San Francisco?"}]},
    config=config,
)

# A follow-up turn on the same conversation: reuse the same thread_id to keep history
result = agent.invoke(
    {"messages": [{"role": "user", "content": "What about tomorrow?"}]},
    config=config,                                       # dùng lại đúng config nên agent hiểu "tomorrow" của cái gì
)
```

**Kết quả in ra** (dựng lại):

```
{'messages': [...]}     ← trả về toàn bộ trạng thái; lượt hai chứa cả lịch sử lượt một
```

**!Note:** Giữ lịch sử bằng `thread_id` đòi hỏi agent phải có checkpointer. Chạy trên LangSmith thì checkpointer được cấp tự động; chạy tại máy thì phải truyền tay, ví dụ `create_agent(..., checkpointer=InMemorySaver())`. Quên thì code vẫn chạy, chỉ là mỗi lượt agent không nhớ gì.

### 4.2 Gọi kèm `context`

**Khái niệm.** Dữ liệu cấu hình riêng cho từng lần chạy — mã người dùng, khóa API, cờ tính năng — truyền qua `context`, đi cùng `config`. Hình dạng của nó khai bằng `context_schema`, và tool cùng middleware đọc nó qua `runtime.context`.

**Vai trò.** Có những thứ không thuộc về nội dung hội thoại nhưng tool vẫn cần biết. Nhét chúng vào message là làm bẩn hội thoại; để trong `context` thì tách bạch.

**Áp dụng thực tế.** Cùng một agent phục vụ nhiều chuyên viên; tool tra cứu phải biết người đang hỏi là ai để lọc đúng danh mục khách hàng họ phụ trách.

```python
from dataclasses import dataclass

from langchain.agents import create_agent
from langchain_core.utils.uuid import uuid7
from langgraph.checkpoint.memory import InMemorySaver


@dataclass
class Context:                                           # khai trước hình dạng dữ liệu bối cảnh
    user_id: str


agent = create_agent(
    model="google_genai:gemini-3.5-flash",
    tools=[],
    context_schema=Context,                              # gắn schema vào agent
    checkpointer=InMemorySaver(),
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "What's the weather in San Francisco?"}]},
    config={"configurable": {"thread_id": str(uuid7())}},
    context=Context(user_id="user-123"),                 # truyền lúc gọi, không phải lúc dựng agent
)
```

### 4.3 Phân biệt `thread_id` và `context`

| | `thread_id` | `context` |
|---|---|---|
| Khoanh vùng cái gì | Cuộc hội thoại: lịch sử message, checkpoint | Từng lần chạy |
| Chứa gì | Nội dung đã trao đổi | Mã người dùng, khóa API, cờ tính năng |
| Ai đọc | Bản thân agent | Tool và middleware, qua `runtime.context` |
| Truyền ở đâu | Trong `config` | Tham số `context` |

Hai thứ này thường đi cùng nhau. Chi tiết nằm ở trang Tools (mục bối cảnh của tool) và trang Runtime.

---

## 5. Streaming — hiện tiến độ giữa chừng

**Khái niệm.** `invoke` chỉ trả về kết quả cuối, khi cả lần chạy đã xong. Streaming đẩy ra message trung gian và hoạt động của tool ngay khi chúng xảy ra.

**Vai trò.** Agent gọi nhiều tool thì lần chạy kéo dài; người dùng cần thấy tiến độ trước khi có kết quả cuối.

```python
from langchain.messages import AIMessage, HumanMessage


stream = agent.stream_events(
    {"messages": [{"role": "user", "content": "Search for AI news and summarize the findings"}]},
    version="v3",                                                # bắt buộc ghi rõ phiên bản
)
for snapshot in stream.values:                                   # mỗi snapshot là toàn bộ trạng thái tại thời điểm đó
    latest_message = snapshot["messages"][-1]                    # lấy message mới nhất
    if latest_message.content:
        if isinstance(latest_message, HumanMessage):
            print(f"User: {latest_message.content}")
        elif isinstance(latest_message, AIMessage):
            print(f"Agent: {latest_message.content}")
    elif latest_message.tool_calls:                              # content rỗng thì đây là lượt gọi tool
        print(f"Calling tools: {[tc['name'] for tc in latest_message.tool_calls]}")
```

**Kết quả in ra** (dựng lại):

```
User: Search for AI news and summarize the findings     ← snapshot đầu, trạng thái mới chỉ có câu hỏi
Calling tools: ['search']                               ← lượt model không có content nên rơi vào nhánh tool_calls
Agent: Here are the main AI news items ...              ← lượt cuối có content, lần chạy kết thúc
```

Vì mỗi snapshot chứa trạng thái đầy đủ chứ không phải phần chênh lệch, đoạn code trên luôn lấy phần tử cuối của `messages` thay vì tự ghép dần.

Các chế độ stream, loại sự kiện và cách dựng giao diện nằm ở trang Streaming.

---

## 6. Cấu hình harness bằng middleware

Middleware là đơn vị mở rộng của `create_agent`: mỗi mảnh lo đúng một việc, cắm vào vòng lặp agent tại đúng thời điểm, và ghép tự do với mảnh khác. Lấy đúng thứ cần, bỏ phần còn lại.

Những mẫu hay gặp đã được dựng sẵn thành middleware hạng nhất. Ngoài ra thì tự viết middleware riêng.

Thời điểm từng móc kích hoạt và cách chồng middleware hoạt động thuộc trang Middleware overview — trang này chỉ liệt kê năng lực theo sáu nhóm.

`create_deep_agent` lắp sẵn cả chồng này cho việc lập trình và nghiên cứu chạy dài, mặc định gồm filesystem, tóm tắt, agent con và prompt caching.

### 6.1 Môi trường thi hành

**Khái niệm.** Không gian làm việc của agent: tool để gọi, một filesystem để đọc ghi file xuyên qua các lượt, và khả năng chạy script hoặc lệnh shell.

**Vai trò.** Agent hữu ích khi làm được việc chứ không chỉ sinh chữ. Filesystem còn giải quyết chuyện dữ liệu quá dài: ghi ra file rồi đọc lại, thay vì nhồi hết vào hội thoại.

```python
from langchain.agents import create_agent
from deepagents.backends import StateBackend
from deepagents.middleware import FilesystemMiddleware

agent = create_agent(
    model="google_genai:gemini-3.5-flash",
    tools=[search],
    middleware=[FilesystemMiddleware(backend=StateBackend())],   # backend quyết định file nằm ở đâu
)
```

**!Note:** Khối code này nhập từ `deepagents`, không phải `langchain`. Đây là gói riêng, và `search` trong ví dụ là biến đã có từ trước, trang không khai lại.

Xem thêm `FilesystemMiddleware`, Sandboxes, Interpreters.

### 6.2 Quản trị bối cảnh

**Khái niệm.** Ba việc khác nhau nhằm giữ cửa sổ bối cảnh không tràn: tóm tắt nén lịch sử lại trước khi tràn; memory nạp chỉ dẫn cố định lúc khởi động để kiến thức đi xuyên các phiên; skills đưa kiến thức chuyên môn ra khi cần thay vì nạp hết từ đầu.

**Vai trò.** Mỗi lần gọi model có một cửa sổ bối cảnh cố định. Agent chạy càng lâu, cửa sổ càng đầy lịch sử, kết quả tool và các bước trung gian.

```python
from deepagents.backends import StateBackend
from deepagents.middleware import FilesystemMiddleware, MemoryMiddleware, SkillsMiddleware, SummarizationMiddleware

backend = StateBackend()
model="google_genai:gemini-3.5-flash"

agent = create_agent(
    model=model,
    tools=[search],
    middleware=[
        FilesystemMiddleware(backend=backend),                       # nơi đọc ghi file
        SummarizationMiddleware(model=model, backend=backend),       # tóm tắt cũng cần một model để chạy
        MemoryMiddleware(backend=backend, sources=["./AGENTS.md"]),  # chỉ dẫn cố định lấy từ file
        SkillsMiddleware(backend=backend, sources=["./skills/"]),    # kiến thức chuyên môn lấy từ thư mục
    ],
)
```

Bốn middleware dùng chung một `backend`, nên phải tạo biến `backend` trước rồi truyền lại cho từng cái.

Xem thêm `SummarizationMiddleware`, `MemoryMiddleware`, Skills, Context engineering.

### 6.3 Lập kế hoạch và giao việc

**Khái niệm.** Agent chính chia nhỏ công việc, giao cho các agent con, mỗi agent con chạy trong bối cảnh riêng biệt của nó.

**Vai trò.** Nhiệm vụ phức tạp thường vượt quá sức chứa của một cửa sổ bối cảnh. Giao việc giúp agent chính tập trung điều phối thay vì tự làm; việc chạy song song được, và bối cảnh của agent chính không bị bẩn.

```python
from deepagents.backends import StateBackend
from deepagents.middleware import FilesystemMiddleware
from deepagents.middleware.subagents import SubAgentMiddleware
from langchain.agents import create_agent
from langchain.agents.middleware import TodoListMiddleware
from langchain.tools import tool


@tool
def search(query: str) -> str:
    """Search for a query and return a short summary."""
    return f"Search results for: {query}"


backend = StateBackend()

agent = create_agent(
    model="google_genai:gemini-3.5-flash",
    tools=[search],
    middleware=[
        FilesystemMiddleware(backend=backend),
        TodoListMiddleware(),                                # danh sách việc cần làm của agent chính
        SubAgentMiddleware(
            backend=backend,
            subagents=[
                {
                    "name": "researcher",                    # tên agent con
                    "description": "Searches and returns a structured summary.",   # agent chính đọc mô tả này để biết khi nào giao việc
                    "system_prompt": "Use the search tool to research the question and summarize key points.",
                    "tools": [search],                       # agent con có bộ tool riêng
                    "model": "anthropic:claude-sonnet-4-6",  # và model riêng, khác agent chính
                    "middleware": [],
                }
            ],
        ),
    ],
)
```

Agent con khai bằng dict, mỗi cái tự chọn model, tool, prompt và middleware của nó.

Xem thêm Subagents.

### 6.4 Đặt tên agent

**Khái niệm.** Một định danh tùy chọn cho agent.

**Vai trò.** Cần đến khi nhúng agent làm quy trình con trong hệ nhiều agent.

```python
agent = create_agent(model="google_genai:gemini-3.5-flash", tools=tools, name="research_assistant")
```

### 6.5 Chịu lỗi

**Khái niệm.** Middleware xử lý các hỏng hóc ở tầng hạ tầng: chạm giới hạn tần suất gọi, model hết thời gian chờ, lỗi API thoáng qua.

**Vai trò.** Những lỗi này hiếm khi xuất hiện lúc phát triển nhưng gặp thường xuyên khi chạy thật. Đưa chúng về tầng hạ tầng thì tool và logic nghiệp vụ không phải bọc `try/catch` quanh từng lệnh gọi.

```python
from langchain.agents import create_agent
from langchain.agents.middleware import ModelRetryMiddleware, ToolRetryMiddleware
from langchain.tools import tool


@tool
def search(query: str) -> str:
    """Search for a query and return a short summary."""
    return f"Search results for: {query}"


agent = create_agent(
    model="google_genai:gemini-3.5-flash",
    tools=[search],
    middleware=[
        ModelRetryMiddleware(max_retries=3),                 # thử lại khi lỗi đến từ phía model
        ToolRetryMiddleware(max_retries=2),                  # thử lại khi lỗi đến từ phía tool
    ],
)
```

Hai loại lỗi tách riêng nên số lần thử lại đặt riêng cho từng bên.

Xem thêm `ModelRetryMiddleware`, `ToolRetryMiddleware`, Prebuilt middleware.

### 6.6 Guardrails

**Khái niệm.** Middleware chặn dữ liệu trên đường nó chảy qua vòng lặp agent, áp quy tắc tuân thủ hoặc chính sách nội dung trước khi kết quả tool chạm tới bối cảnh của model.

**Vai trò.** Có những quy định không thể để trong prompt — chúng phải được thi hành một cách xác định, bất kể model làm gì. Prompt là lời dặn, model có thể lơ; guardrail là chốt chặn.

**Áp dụng thực tế.** Kết quả tool kéo về từ hệ thống nội bộ có kèm địa chỉ email cá nhân của người liên hệ. Che ở tầng guardrail thì dữ liệu đó không bao giờ đi vào bối cảnh model, không phụ thuộc vào việc prompt có dặn hay không.

```python
from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware
from langchain.tools import tool


@tool
def search(query: str) -> str:
    """Search for a query and return a short summary."""
    return f"Search results for: {query}"


agent = create_agent(
    model="google_genai:gemini-3.5-flash",
    tools=[search],
    middleware=[PIIMiddleware("email")],                     # khai loại thông tin cá nhân cần xử lý
)
```

Trang chỉ đưa một loại là `"email"`. Danh sách loại nhận được và cách xử lý từng loại không nằm ở đây — xem `PIIMiddleware` và Prebuilt middleware.

### 6.7 Steering — chốt duyệt của con người

**Khái niệm.** Đặt người vào những điểm quyết định cụ thể mà không phải dựng lại agent. Agent dừng và chờ; người duyệt, sửa, hoặc từ chối; rồi chạy tiếp.

**Vai trò.** Toàn quyền tự chủ không phải lúc nào cũng phù hợp — trước những thao tác ghi đè có tính phá hủy, những lệnh gọi API tốn kém, hoặc bất cứ việc gì cần phán đoán.

**Áp dụng thực tế.** Agent soạn xong bản thảo tờ trình và định ghi đè lên file đang dùng. Đây là chỗ cần một người nhìn qua trước khi file cũ biến mất.

```python
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.tools import tool


@tool
def search(query: str) -> str:
    """Search for a query and return a short summary."""
    return f"Search results for: {query}"


agent = create_agent(
    model="google_genai:gemini-3.5-flash",
    tools=[search],
    middleware=[HumanInTheLoopMiddleware(interrupt_on={"write_file": True})],   # chặn đúng tool có tên write_file
)
```

**!Note:** Ví dụ đặt chốt cho `write_file` trong khi danh sách tool chỉ khai `search`. Trang không nói `write_file` từ đâu ra — theo mục 6.1 thì đó là tool do `FilesystemMiddleware` mang lại, nhưng middleware đó không có mặt trong khối code này. Đây là suy luận, chưa được trang xác nhận; phải chạy thử mới rõ chốt duyệt có kích hoạt hay không khi tên tool không tồn tại.

Xem thêm `HumanInTheLoopMiddleware`, Human-in-the-loop.

---

## 7. Ba trang tra cứu về middleware

| Trang | Trả lời câu hỏi |
|---|---|
| Middleware overview | Chồng middleware hoạt động ra sao, móc kích hoạt lúc nào |
| Prebuilt middleware | Toàn bộ middleware dựng sẵn, kèm ví dụ cấu hình |
| Custom middleware | Cách tự viết móc cho logic nghiệp vụ, che thông tin cá nhân |

---

## Tham chiếu chéo

- [Models](https://docs.langchain.com/oss/python/langchain/models) — tham số model, khai báo nhà cung cấp, chọn model động (mục 3.1)
- [Tools](https://docs.langchain.com/oss/python/langchain/tools) — định nghĩa tool, tool đọc bối cảnh, chọn tool động (mục 3.2, 4.2)
- [Structured output](https://docs.langchain.com/oss/python/langchain/structured-output) — các chiến lược cho mục 3.4
- [Runtime](https://docs.langchain.com/oss/python/langchain/runtime) — `runtime.context` ở mục 4.2
- [Long-term memory](https://docs.langchain.com/oss/python/langchain/long-term-memory) — checkpointer ở mục 4.1
- [Streaming](https://docs.langchain.com/oss/python/langchain/streaming) — chế độ stream và loại sự kiện ở mục 5
- [Middleware overview](https://docs.langchain.com/oss/python/langchain/middleware/overview), [Prebuilt middleware](https://docs.langchain.com/oss/python/langchain/middleware/built-in), [Custom middleware](https://docs.langchain.com/oss/python/langchain/middleware/custom) — mục 6
- [Deep Agents](https://docs.langchain.com/oss/python/deepagents/harness) — `create_deep_agent` lắp sẵn cả chồng middleware ở mục 6
- [Subagents](https://docs.langchain.com/oss/python/langchain/multi-agent/subagents), [Skills](https://docs.langchain.com/oss/python/langchain/multi-agent/skills) — mục 6.2, 6.3
- [Human-in-the-loop](https://docs.langchain.com/oss/python/langchain/human-in-the-loop) — mục 6.7