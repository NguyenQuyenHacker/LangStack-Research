---
title: Custom middleware
doc_source: https://docs.langchain.com/oss/python/langchain/middleware/custom
accessed: 2026-07-22
lc_version: "1.x"
status: draft
lab: ../labs/lab-02-custom-middleware/
related:
  - ./middleware-overview.md
  - ./middleware-built-in.md
  - ./agents.md
  - ./tools.md
---

# Custom middleware

> Cách tự viết middleware: chọn hook, viết bằng decorator hoặc class, cập nhật State, nhảy sớm ra khỏi vòng lặp.
> Đây là trang đóng phần lớn các câu hỏi treo từ ba file trước — bộ hook và thứ tự chạy đều được nói bằng chữ ở đây, không phải bằng ảnh.

## Trang này đóng câu hỏi nào

| Câu hỏi treo | Ở file | Kết quả |
|---|---|---|
| Bộ hook đầy đủ gồm những gì | [middleware-overview](./middleware-overview.md) | **Xác nhận đúng** bảng đã dựng: 4 node-style, 2 wrap-style, 1 convenience |
| `before_*` xuôi, `after_*` ngược có đúng không | [middleware-overview](./middleware-overview.md) | **Xác nhận đúng**, doc liệt kê 13 bước, xem mục 2 |
| `dynamic_prompt` thuộc nhóm nào | [middleware-overview](./middleware-overview.md) | **Xác nhận**, doc xếp riêng thành nhóm "Convenience" |
| `wrap_tool_call` so với `handle_tool_errors` của `ToolNode` | [tools](./tools.md), [middleware-built-in](./middleware-built-in.md) | **Vẫn chưa trả lời.** Trang này cũng không nhắc |
| Middleware sửa được `response_format` không | [middleware-overview](./middleware-overview.md) | **Vẫn chưa trả lời.** `request.override()` chỉ thấy `model`, `tools`, `system_message` |

---

## 0. Từ điển thuật ngữ

Các từ State, Store, Context, hook, reducer đã giải thích ở [tools](./tools.md) và [middleware-overview](./middleware-overview.md). Đây là từ mới của trang này.

| Từ | Nghĩa dễ hiểu |
|---|---|
| **handler** | Hàm chạy bước thật. Wrap-style hook nhận nó và tự quyết gọi lúc nào, mấy lần. |
| **short-circuit** | Không gọi `handler` lần nào, trả kết quả tự chế. Dùng cho cache. |
| **nest / lồng nhau** | Middleware ngoài bọc middleware trong, giống các lớp vỏ củ hành. |
| **inner / outer** | Trong / ngoài. Middleware đứng **đầu** list là **outer** — nó bọc tất cả các cái sau. |
| **`NotRequired`** | Đánh dấu một khoá của `TypedDict` là không bắt buộc phải có. |
| **`Annotated[type, reducer]`** | Gắn thêm quy tắc gộp cho một trường State. |
| **`ExtendedModelResponse`** | Vỏ bọc gồm hai phần: kết quả model, và một `Command` ghi State. Dành riêng cho `wrap_model_call`. |
| **`hook_config`** | Decorator khai báo cấu hình cho hook, hiện thấy dùng để xin quyền nhảy (`can_jump_to`). |
| **`jump_to`** | Khoá trả về để nhảy thẳng sang một node khác, bỏ qua phần còn lại. |
| **`content_blocks`** | Cách đọc nội dung message dưới dạng danh sách khối, dù ban đầu nó là chuỗi hay list. |
| **sync / async** | Đồng bộ / bất đồng bộ. Bản async của hook đặt tên thêm chữ `a` ở đầu: `abefore_model`. |

---

## 1. Hai kiểu hook

### Node-style — chạy giữa hai bước

| Hook | Chạy khi nào |
|---|---|
| `before_agent` | Trước khi agent bắt đầu, **một lần** mỗi `invoke` |
| `before_model` | Trước **mỗi** lần gọi model |
| `after_model` | Sau **mỗi** lần model trả lời |
| `after_agent` | Sau khi agent xong, **một lần** mỗi `invoke` |

Chữ ký: `(state, runtime)`. Trả về dict cập nhật State, hoặc `None`.

Dùng cho: ghi log, kiểm tra, cập nhật State — việc tuần tự.

### Wrap-style — bọc quanh một bước

| Hook | Chạy khi nào |
|---|---|
| `wrap_model_call` | Bọc quanh mỗi lần gọi model |
| `wrap_tool_call` | Bọc quanh mỗi lần chạy tool |

Chữ ký: `(request, handler)`. Trả về kết quả của bước đó.

Dùng cho: retry, cache, biến đổi — việc cần điều khiển luồng.

### Khác biệt cốt lõi

Wrap-style **cầm quyền gọi** `handler`. Gọi 0 lần là short-circuit (cache), 1 lần là chạy bình thường, nhiều lần là retry. Node-style không có quyền đó, nó chỉ đứng cạnh bước chính.

```python
@wrap_model_call
def retry_model(request: ModelRequest, handler) -> ModelResponse:
    for attempt in range(3):
        try:
            return handler(request)          # gọi lại tối đa 3 lần
        except Exception as e:
            if attempt == 2:
                raise
            print(f"Retry {attempt + 1}/3 after error: {e}")
```

### Nhóm thứ ba — Convenience

Chỉ có một cái: `@dynamic_prompt`, sinh system prompt động.

Đáng chú ý là ví dụ "Dynamic prompt" trong chính trang này lại **không** dùng `@dynamic_prompt` mà dùng `wrap_model_call` sửa `request.system_message`. Hai đường làm cùng một việc, doc không nói khi nào chọn đường nào. Xem mục 7.1.

---

## 2. Thứ tự chạy khi có nhiều middleware

```python
create_agent(model="gpt-5.4", middleware=[middleware1, middleware2, middleware3], tools=[...])
```

Doc liệt kê đủ 13 bước:

```
1.  middleware1.before_agent()
2.  middleware2.before_agent()
3.  middleware3.before_agent()
    ── vòng lặp agent bắt đầu ──
4.  middleware1.before_model()
5.  middleware2.before_model()
6.  middleware3.before_model()
7.  middleware1.wrap_model_call() → middleware2.wrap_model_call() → middleware3.wrap_model_call() → model
8.  middleware3.after_model()
9.  middleware2.after_model()
10. middleware1.after_model()
    ── vòng lặp agent kết thúc ──
11. middleware3.after_agent()
12. middleware2.after_agent()
13. middleware1.after_agent()
```

Ba luật:

- `before_*` — đầu tới cuối
- `after_*` — cuối tới đầu
- `wrap_*` — lồng nhau, cái đầu tiên bọc tất cả

### Hệ quả thực tế

**Đứng đầu list nghĩa là ở ngoài cùng.** `middleware1` chạy `before_*` sớm nhất, `after_*` muộn nhất, và bọc mọi wrap-style khác. Doc khuyên đặt middleware quan trọng lên đầu.

**Bài toán cụ thể.** Cắm hai cái: một middleware retry và một middleware ghi log số lần gọi model. Đặt log ở ngoài (vị trí 1) thì nó đếm 1 lần cho cả cụm retry. Đặt log ở trong (vị trí 2) thì nó đếm đúng số lần thử. Thứ tự trong list quyết định con số, không phải logic của middleware.

---

## 3. Hai cách viết

| | Decorator | Class |
|---|---|---|
| Số hook | Một | Nhiều hook trong cùng một middleware |
| Cấu hình lúc khởi tạo | Không | Có, qua `__init__` |
| Bản sync và async cho cùng một hook | Không | Có |
| Hợp với | Viết nhanh, thử nghiệm | Dùng lại nhiều dự án |

### Decorator

```python
@before_model
def log_before_model(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    print(f"About to call model with {len(state['messages'])} messages")
    return None

agent = create_agent(model="gpt-5.4", middleware=[log_before_model, retry_model], tools=[...])
```

Truyền thẳng **tên hàm** vào list, không gọi.

### Class

```python
class LoggingMiddleware(AgentMiddleware):
    def before_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        print(f"About to call model with {len(state['messages'])} messages")
        return None

    def after_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        print(f"Model returned: {state['messages'][-1].content}")
        return None

    async def abefore_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        return None

    async def aafter_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        print(f"Model returned: {state['messages'][-1].content}")
        return None

agent = create_agent(model="gpt-5.4", middleware=[LoggingMiddleware()], tools=[...])
```

Truyền **instance** vào list — có ngoặc đơn. Tên hook chính là tên phương thức, không cần decorator.

Bản async đặt tên thêm chữ `a` ở đầu: `abefore_model`, `aafter_model`.

---

## 4. Cập nhật State

Hai kiểu hook cập nhật State bằng hai cơ chế khác nhau.

### 4.1 Node-style — trả về dict

Khoá của dict ánh xạ vào trường State. Dict được gộp vào State qua reducer của graph.

```python
class TrackingState(AgentState):
    model_call_count: NotRequired[int]

@after_model(state_schema=TrackingState)
def increment_after_model(state: TrackingState, runtime: Runtime) -> dict[str, Any] | None:
    return {"model_call_count": state.get("model_call_count", 0) + 1}
```

### 4.2 Wrap-style — trả về `ExtendedModelResponse` hoặc `Command`

Wrap-style phải trả về kết quả của bước chính, nên không trả dict được. Cơ chế:

| Hook | Trả về gì để ghi State |
|---|---|
| `wrap_model_call` | `ExtendedModelResponse(model_response=..., command=Command(update={...}))` |
| `wrap_tool_call` | `Command` trực tiếp |

```python
class UsageTrackingState(AgentState):
    last_model_call_tokens: NotRequired[int]

@wrap_model_call(state_schema=UsageTrackingState)
def track_usage(request: ModelRequest, handler) -> ExtendedModelResponse:
    response = handler(request)
    return ExtendedModelResponse(
        model_response=response,
        command=Command(update={"last_model_call_tokens": 150}),
    )
```

**Dùng khi nào.** Khi giá trị cần ghi chỉ tính được **trong lúc** gọi model hoặc tool: số token đã dùng, ngưỡng kích hoạt tóm tắt, dữ liệu suy ra từ request hoặc response. Node-style đứng ngoài lần gọi nên không thấy được những thứ này.

`Command` đi qua reducer của graph, nên messages được **cộng thêm** chứ không đè lên State cũ.

### 4.3 Nhiều middleware cùng ghi

Ba luật khi nhiều lớp cùng trả `ExtendedModelResponse`:

- **Qua reducer.** Mỗi `Command` là một lần cập nhật riêng. Với `messages`, các lần cộng dồn.
- **Ngoài thắng trong.** Với trường không có reducer, áp cập nhật của lớp trong trước, lớp ngoài sau. Trùng khoá thì giá trị của lớp ngoài cùng thắng.
- **An toàn với retry.** Lớp ngoài gọi `handler()` nhiều lần thì `Command` của các lần trước bị bỏ, không cộng dồn nhầm.

Doc minh hoạ bằng cặp `OuterMiddleware` / `InnerMiddleware` cùng ghi vào `trace_layer` và `messages`. Kết quả: `trace_layer` còn lại `"outer"`, còn `messages` có **cả hai** dòng vì nó dùng reducer cộng dồn.

```python
def _last_wins(_a: str, b: str) -> str:
    return b

class CustomMiddlewareState(AgentState):
    trace_layer: NotRequired[Annotated[str, _last_wins]]
```

---

## 5. State schema riêng

**Dùng để làm gì.** Giữ số đếm và cờ xuyên suốt lượt chạy; chuyển dữ liệu từ `before_model` sang `after_model`; cài rate limit, đếm dung lượng, ghi audit mà không đụng vào lõi agent; dựa vào số liệu tích luỹ để quyết định có nhảy sớm không.

```python
class CustomState(AgentState):
    model_call_count: NotRequired[int]
    user_id: NotRequired[str]

@before_model(state_schema=CustomState, can_jump_to=["end"])
def check_call_limit(state: CustomState, runtime: Runtime) -> dict[str, Any] | None:
    if state.get("model_call_count", 0) > 10:
        return {"jump_to": "end"}
    return None

@after_model(state_schema=CustomState)
def increment_counter(state: CustomState, runtime: Runtime) -> dict[str, Any] | None:
    return {"model_call_count": state.get("model_call_count", 0) + 1}

result = agent.invoke({
    "messages": [HumanMessage("Hello")],
    "model_call_count": 0,
    "user_id": "user-123",
})
```

Bản class khai bằng thuộc tính lớp thay vì tham số decorator:

```python
class CallCounterMiddleware(AgentMiddleware[CustomState]):
    state_schema = CustomState
```

Hai điểm nhỏ: khai `NotRequired` để không bắt buộc phải truyền khoá đó lúc `invoke`; và giá trị khởi tạo vẫn truyền được vào `invoke` như một trường bình thường.

---

## 6. Nhảy sớm — `jump_to`

Trả về dict có khoá `jump_to` để thoát khỏi luồng bình thường.

| Đích | Nhảy tới đâu |
|---|---|
| `end` | Cuối lượt chạy, hoặc hook `after_agent` đầu tiên |
| `tools` | Node tools |
| `model` | Node model, hoặc hook `before_model` đầu tiên |

Phải xin quyền trước bằng `can_jump_to`, không thì không nhảy được.

```python
@after_model
@hook_config(can_jump_to=["end"])
def check_for_blocked(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    last_message = state["messages"][-1]
    if "BLOCKED" in last_message.content:
        return {
            "messages": [AIMessage("I cannot respond to that request.")],
            "jump_to": "end",
        }
    return None
```

Bản class dùng `@hook_config` đặt ngay trên phương thức.

**Doc dùng hai cú pháp khác nhau cho cùng một việc.** Mục "Node-style hooks" viết `@before_model(can_jump_to=["end"])` — truyền thẳng vào decorator hook. Mục "Agent jumps" lại chồng hai decorator: `@after_model` rồi `@hook_config(can_jump_to=["end"])`. Chưa rõ cả hai đều hợp lệ hay một cái đã lỗi thời. Đưa vào mục kiểm chứng.

---

## 7. Năm ví dụ mẫu

### 7.1 Sửa system prompt

`request.system_message` **luôn** là một đối tượng `SystemMessage`, kể cả khi agent được tạo bằng chuỗi `system_prompt="..."`.

```python
@wrap_model_call
def add_context(request: ModelRequest, handler) -> ModelResponse:
    new_content = list(request.system_message.content_blocks) + [
        {"type": "text", "text": "Additional context."}
    ]
    return handler(request.override(system_message=SystemMessage(content=new_content)))
```

Doc nhấn ba điều: luôn đọc qua `content_blocks` để khỏi phải phân biệt nội dung gốc là chuỗi hay list; **cộng thêm** khối mới thay vì ghi đè để giữ cấu trúc cũ; và có thể truyền thẳng `SystemMessage` vào `system_prompt` của `create_agent` cho các trường hợp như cache control.

### 7.2 Đổi model theo độ dài hội thoại

```python
@wrap_model_call
def dynamic_model(request: ModelRequest, handler) -> ModelResponse:
    model = complex_model if len(request.messages) > 10 else simple_model
    return handler(request.override(model=model))
```

Bản ở [agents](./agents.md) đọc `request.state["messages"]`, bản ở đây đọc `request.messages`. Hai đường khác nhau, doc không giải thích chênh lệch.

### 7.3 Lọc tool

```python
@wrap_model_call
def select_tools(request: ModelRequest, handler) -> ModelResponse:
    relevant_tools = select_relevant_tools(request.state, request.runtime)
    return handler(request.override(tools=relevant_tools))

agent = create_agent(model="gpt-5.4", tools=all_tools, middleware=[select_tools])
```

Toàn bộ tool vẫn phải đăng ký từ đầu ở `create_agent`. Đây là bản viết tay của `LLMToolSelectorMiddleware` (xem [middleware-built-in](./middleware-built-in.md) mục 8.1).

Ba lợi ích doc nêu: prompt ngắn hơn, model chọn chính xác hơn khi ít lựa chọn, và lọc được theo quyền của người dùng.

### 7.4 Giám sát tool call

```python
@wrap_tool_call
def monitor_tool(request: ToolCallRequest, handler) -> ToolMessage | Command:
    print(f"Executing tool: {request.tool_call['name']}")
    print(f"Arguments: {request.tool_call['args']}")
    try:
        result = handler(request)
        print("Tool completed successfully")
        return result
    except Exception as e:
        print(f"Tool failed: {e}")
        raise
```

Chữ ký cho biết `handler` của tool trả về `ToolMessage` **hoặc** `Command` — khớp với ba kiểu trả về ở [tools](./tools.md) mục 4.

**Đường import lệch giữa hai trang doc.** Ở đây: `from langchain.tools.tool_node import ToolCallRequest`. Ở trang [agents](./agents.md): `from langchain.agents.middleware import ... ToolCallRequest`. Một trong hai sai, hoặc cả hai đều chạy. Đưa vào mục kiểm chứng.

### 7.5 Prompt caching cho Anthropic

```python
@wrap_model_call
def add_cached_context(request: ModelRequest, handler) -> ModelResponse:
    new_content = list(request.system_message.content_blocks) + [
        {
            "type": "text",
            "text": "Here is a large document to analyze:\n\n<document>...</document>",
            "cache_control": {"type": "ephemeral"},
        }
    ]
    return handler(request.override(system_message=SystemMessage(content=new_content)))
```

Chú thích trong code đáng chú ý: nội dung **tính tới khối này** được cache, không phải chỉ riêng khối này. Vị trí đặt `cache_control` quyết định ranh giới cache.

---

## 8. Bảy điều doc khuyên

1. Mỗi middleware làm đúng một việc
2. Bắt lỗi tử tế, đừng để middleware làm sập agent
3. Chọn đúng kiểu hook: node-style cho việc tuần tự, wrap-style cho điều khiển luồng
4. Ghi tài liệu rõ cho các trường State tự thêm
5. Test riêng middleware trước khi ghép vào agent
6. Cân nhắc thứ tự, đặt cái quan trọng lên đầu list
7. Dùng middleware có sẵn khi được

---

## 9. Việc cho lab

Thư mục: `../labs/lab-02-custom-middleware/`

Bốn thí nghiệm dựng thẳng từ các câu hỏi ở mục dưới:

| Thí nghiệm | Trả lời câu hỏi nào |
|---|---|
| Cắm 3 middleware, mỗi cái in tên trong cả 4 node-style hook, chạy một lượt có gọi tool | Sơ đồ 13 bước ở mục 2 có đúng không, `wrap_tool_call` chen vào bước thứ mấy |
| Một `ToolRetryMiddleware` + một `wrap_tool_call` in log, cho tool ném lỗi | `wrap_tool_call` và retry cái nào chạy trước — câu hỏi treo qua bốn file |
| Hai middleware cùng ghi một trường State không có reducer | Luật "ngoài thắng trong" ở mục 4.3 |
| Viết cùng một hook bằng `@before_model(can_jump_to=[...])` và bằng `@hook_config` | Hai cú pháp ở mục 6 có cùng hợp lệ không |

---

## Cần kiểm chứng thêm

- [ ] **`wrap_tool_call` so với `handle_tool_errors` của `ToolNode` và `ToolRetryMiddleware`.** Ba cơ chế cùng đụng vào lỗi tool, bốn trang doc đã đọc đều không nói cái nào chạy trước. Xác minh: thí nghiệm 2 ở mục 9.
- [ ] **`can_jump_to` có hai cú pháp.** `@before_model(can_jump_to=["end"])` và `@after_model` + `@hook_config(can_jump_to=["end"])`. Xác minh: reference `hook_config` và `before_model`, hoặc thí nghiệm 4.
- [ ] **`ToolCallRequest` import từ đâu.** Trang này lấy từ `langchain.tools.tool_node`, trang Agents lấy từ `langchain.agents.middleware`. Xác minh: chạy thử cả hai.
- [ ] **`request.messages` so với `request.state["messages"]`.** Mục 7.2 dùng cái đầu, trang Agents dùng cái sau. Có phải hai đường tới cùng một chỗ không, hay `request.messages` đã lọc bớt. Xác minh: reference `ModelRequest`.
- [ ] **`request.override()` nhận được gì.** Qua bốn trang đã gom được `model`, `tools`, `system_message`, và `tool` (cho `ToolCallRequest`). Chưa rõ có `response_format` không. Xác minh: reference `ModelRequest`.
- [ ] **`wrap_tool_call` có bản `ExtendedToolResponse` không.** Doc nói `wrap_model_call` trả `ExtendedModelResponse`, còn `wrap_tool_call` trả `Command` trực tiếp — nghĩa là tool không trả được cả kết quả lẫn lệnh ghi State cùng lúc? Nhưng `Command` có `update` chứa `messages` nên có thể vẫn làm được. Xác minh: reference.
- [ ] **`dynamic_prompt` so với sửa `system_message` trong `wrap_model_call`.** Trang này liệt kê `@dynamic_prompt` rồi lại minh hoạ bằng đường kia. Chưa rõ khác nhau chỗ nào. Xác minh: reference `dynamic_prompt`.
- [ ] **Hook async.** Chỉ thấy `abefore_model` và `aafter_model` trong ví dụ. Chưa rõ wrap-style có bản async không, và định nghĩa cả hai bản thì bản nào được gọi. Xác minh: reference `AgentMiddleware`.

---

## Tham chiếu chéo

| File | Bổ sung cho mục nào |
|---|---|
| [middleware-overview](./middleware-overview.md) | Mục 1, 2 — bảng hook dựng từ nguồn ngoài, nay đã đối chiếu xong |
| [middleware-built-in](./middleware-built-in.md) | Mục 7.3 — bản dựng sẵn của việc lọc tool |
| [agents](./agents.md) | Mục 7.2, 7.4 — cùng ví dụ, khác đường import và khác cách đọc messages |
| [tools](./tools.md) | Mục 7.4 — `ToolMessage` và `Command` là hai kiểu trả về của tool |