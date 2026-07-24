---
title: Middleware — tổng quan
doc_source: https://docs.langchain.com/oss/python/langchain/middleware/overview
accessed: 2026-07-22
lc_version: "1.x"
status: draft
lab:
related:
  - ./agents.md
  - ./tools.md
  - ./middleware-built-in.md
  - ./middleware-custom.md
---

# Middleware — tổng quan

> Middleware là cách chen logic riêng vào giữa các bước của agent mà không phải sửa lõi agent.
> Trang này là trang cổng: nó nói middleware dùng để làm gì, chạy ở đâu, rồi đẩy sang hai trang con là [built-in](./middleware-built-in.md) và [custom](./middleware-custom.md). Nội dung ít, phần lớn giá trị nằm ở hai sơ đồ hình ảnh.

**Cảnh báo về file này.** Trang gốc truyền tải bộ hook bằng **hai file ảnh**, không bằng chữ. Bảng hook ở mục 2 vì thế lấy từ trang Custom middleware và blog chính thức của LangChain, không phải từ trang này. Đã ghi rõ tại chỗ.

---

## 0. Từ điển thuật ngữ

| Từ | Nghĩa dễ hiểu |
|---|---|
| **hook** | Điểm móc. Một chỗ trong luồng chạy được để sẵn cho mình chèn code vào. |
| **node-style hook** | Loại chạy **giữa** hai bước: `before_model`, `after_model`. Nhận `state`, trả về phần cập nhật State. |
| **wrap-style hook** | Loại **bọc quanh** một bước: `wrap_model_call`, `wrap_tool_call`. Nhận `request` và `handler`, tự quyết gọi `handler` lúc nào, mấy lần. |
| **agent loop** | Vòng lặp lõi: gọi model → model chọn tool → chạy tool → quay lại model; hết tool call thì dừng. |
| **guardrail** | Chốt chặn. Luật kiểm tra đầu vào hoặc đầu ra, vi phạm thì chặn. |
| **PII** | Thông tin định danh cá nhân: tên, số điện thoại, email, số tài khoản. |
| **interrupt** | Dừng giữa chừng, chờ người thật quyết rồi mới chạy tiếp. |
| **HITL** | Human-in-the-loop. Có người duyệt xen vào luồng máy chạy. |
| **`StateGraph`** | Graph tự dựng của LangGraph. Mình tự khai node và đường đi. |
| **subgraph** | Một graph được nhét làm một node bên trong graph khác. |
| **checkpointer** | Bộ lưu trạng thái giữa chừng. Không có nó thì dừng xong không khôi phục lại được. |

---

## 1. Middleware là gì và dùng để làm gì

### Là gì

Lớp chen giữa các bước của agent. Nó không thay đổi lõi `create_agent`, chỉ bọc lấy hoặc xen vào giữa các bước.

### Bốn nhóm việc doc liệt kê

- **Quan sát** — logging, analytics, debug hành vi agent
- **Biến đổi** — sửa prompt, chọn lọc tool, định dạng đầu ra
- **Điều khiển luồng** — retry, fallback sang model khác, dừng sớm
- **Chặn** — rate limit, guardrail, phát hiện PII

Bốn nhóm này chính là bốn thứ mà code nghiệp vụ hay phải làm nhưng không nên nhét vào lõi agent.

### Cách gắn

```python
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware, HumanInTheLoopMiddleware

agent = create_agent(
    model="gpt-5.5",
    tools=[...],
    middleware=[
        SummarizationMiddleware(...),
        HumanInTheLoopMiddleware(...),
    ],
)
```

Truyền một list vào tham số `middleware`. Hết.

---

## 2. Hook chen vào chỗ nào

Vòng lặp lõi — gọi model, để model chọn tool, dừng khi model không gọi tool nữa:

```
        ┌──────────┐
  vào → │  model   │ ── không còn tool call ──→ ra
        └────┬─────┘
             │ có tool call
             ▼
        ┌──────────┐
        │  tools   │
        └────┬─────┘
             └────────→ quay lại model
```

(dựng lại — trang gốc vẽ bằng ảnh `core_agent_loop.png`, tôi không đọc được nội dung ảnh)

Middleware để hook ở trước và sau mỗi bước trên.

### Bảng hook

**Nguồn của bảng này không phải trang overview.** Trang overview chỉ đưa ảnh `middleware_final.png`. Tên hook lấy từ trang Custom middleware và bài blog *How Middleware Lets You Customize Your Agent Harness* của LangChain. Cần đối chiếu lại khi đọc trang Custom middleware.

| Hook | Kiểu | Chạy khi nào | Việc hay dùng |
|---|---|---|---|
| `before_agent` | node-style | Một lần, đầu mỗi lượt `invoke` | Nạp trí nhớ, mở kết nối, kiểm tra đầu vào |
| `before_model` | node-style | Trước **mỗi** lần gọi model | Cắt bớt lịch sử, che PII trước khi gửi đi |
| `wrap_model_call` | wrap-style | Bọc quanh lần gọi model | Cache, retry, đổi model, lọc tool |
| `wrap_tool_call` | wrap-style | Bọc quanh lần chạy tool | Bắt lỗi tool, chặn tool, sửa kết quả |
| `after_model` | node-style | Sau mỗi lần model trả lời | Kiểm duyệt đầu ra, guardrail |
| `after_agent` | node-style | Một lần, cuối lượt chạy | Dọn dẹp, ghi log tổng kết |
| `dynamic_prompt` | tiện dụng | Khi sinh system prompt | Đổi prompt theo context |

### Khác nhau giữa hai kiểu

Node-style nhận `(state, runtime)` và trả về dict cập nhật State — nó **đứng cạnh** bước chính. Wrap-style nhận `(request, handler)` — nó **cầm quyền gọi** bước chính, nên làm được retry (gọi `handler` nhiều lần) và cache (không gọi `handler` lần nào).

### Thứ tự chạy khi có nhiều middleware

Các hook `before_*` chạy xuôi theo thứ tự trong list; các hook `after_*` chạy **ngược** lại. Giống lớp vỏ: đi vào lột từ ngoài vào trong, đi ra bọc từ trong ra ngoài.

Điểm này lấy từ nguồn ngoài, trang overview không nói. Xem mục "Cần kiểm chứng thêm".

---

## 3. Middleware không phải một runtime riêng

Đây là câu đáng nhớ nhất của trang: hook chạy **bên trong** graph LangGraph mà `create_agent` biên dịch ra, không phải một tầng chạy song song bên cạnh.

Hệ quả trực tiếp: nhét cả agent (kèm toàn bộ middleware) vào một `StateGraph` lớn hơn làm node hoặc subgraph thì mọi hook vẫn chạy nguyên. Interrupt của HITL, tóm tắt, che PII, retry, hook tự viết — tất cả đi theo node đó.

### Dùng khi nào

Khi topology bên ngoài phức tạp hơn "lặp cho tới khi xong":

- phân loại đầu vào rồi định tuyến sang một trong nhiều agent
- rẽ việc chạy song song
- xen agent với các bước tất định

### Bài toán cụ thể

Hệ xử lý email. Một node phân loại thư đến trước, xong mới định tuyến. Agent email được phép đọc thư tự do nhưng **gửi** thư thì phải có người duyệt.

```python
email_agent = create_agent(
    model="claude-sonnet-4-6",
    tools=[read_email, send_email],
    middleware=[HumanInTheLoopMiddleware(interrupt_on={"send_email": True})],
)

graph = (
    StateGraph(AgentState)
    .add_node("classify", classify_node)
    .add_node("email_agent", email_agent)
    .add_edge(START, "classify")
    .add_conditional_edges("classify", route)
    .compile()
)
```

`email_agent` nằm làm một node trong graph lớn, middleware vẫn hoạt động.

**Chi tiết dễ vấp.** `HumanInTheLoopMiddleware` khớp theo `.name` của tool. Với Python, hàm bọc `@tool` lấy tên từ tên hàm — nên khoá là `"send_email"`, đúng bằng tên hàm. Đặt lại tên tool bằng `@tool("gui_thu")` thì khoá phải đổi theo, không còn là tên hàm nữa.

---

## 4. Built-in middleware được nhắc tên trong trang này

Trang overview không mô tả cái nào, chỉ trỏ link. Danh sách rút từ các link đó:

| Middleware | Việc nó làm |
|---|---|
| `SummarizationMiddleware` | Tóm tắt lịch sử khi sắp tràn context |
| `HumanInTheLoopMiddleware` | Dừng chờ người duyệt trước tool nguy hiểm |
| LLM tool selector | Dùng một model nhanh để lọc tool nào liên quan trước khi gọi model chính |
| Tool retry | Thử lại tool khi lỗi |
| Model fallback | Model chính hỏng thì lùi sang model dự phòng |
| Model call limit | Giới hạn số lần gọi model |
| PII detection | Phát hiện và che thông tin cá nhân |

Mô tả đầy đủ nằm ở [built-in](./middleware-built-in.md).

---

## 5. Bản đồ các trang con

| Trang | Đọc để biết |
|---|---|
| Built-in middleware | Danh sách middleware có sẵn và tham số của từng cái |
| Custom middleware | Cách tự viết bằng decorator hoặc kế thừa `AgentMiddleware` |
| Middleware API reference | Chữ ký đầy đủ |
| Middleware integrations | Middleware riêng của Anthropic, AWS, OpenAI |
| Testing agents | Test agent bằng LangSmith |

---

## Cần kiểm chứng thêm

- [ ] Toàn bộ mục 2. Trang gốc dùng hai file ảnh (`core_agent_loop.png`, `middleware_final.png`) mà tôi không đọc được nội dung. Bảng hook và sơ đồ đều dựng từ nguồn khác. Xác minh: đọc trang Custom middleware, đối chiếu từng tên hook và vị trí.
- [ ] Thứ tự chạy `before_*` xuôi / `after_*` ngược. Lấy từ blog LangChain, trang này không nói. Xác minh: trang Custom middleware hoặc chạy thử với hai middleware in log.
- [ ] `wrap_tool_call` (middleware) và `handle_tool_errors` (của `ToolNode`, xem [tools](./tools.md) mục 5.1) — chồng lấn hay hai tầng khác nhau, cái nào chạy trước. Cả trang Tools lẫn trang này đều im lặng. Câu hỏi này treo từ file trước, chưa trả lời được.
- [ ] HITL có cần `checkpointer` và `thread_id` không. Một nguồn ngoài khẳng định là bắt buộc; trang này không nhắc. Xác minh: trang Human-in-the-loop.
- [ ] `dynamic_prompt` thuộc nhóm hook nào. Một nguồn xếp nó vào nhóm thứ ba gọi là "convenience", tách khỏi node-style và wrap-style. Chưa xác nhận từ doc. Xác minh: trang Custom middleware.
- [ ] Middleware có sửa được `response_format` / structured output không. Không trang nào trong ba trang đã đọc nói tới. Xác minh: reference `ModelRequest`.

---

## Tham chiếu chéo

| File | Bổ sung cho mục nào |
|---|---|
| [agents](./agents.md) | Mục 1, 2 — `wrap_model_call` đổi model động, lọc tool, `dynamic_prompt` |
| [tools](./tools.md) | Mục 2 — `wrap_tool_call` so với `handle_tool_errors` |
| [middleware-built-in](./middleware-built-in.md) | Mục 4 — chi tiết từng middleware có sẵn |
| [middleware-custom](./middleware-custom.md) | Mục 2 — bộ hook thật, cần đối chiếu lại bảng |