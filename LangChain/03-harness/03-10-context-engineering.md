---
title: Context engineering
doc_source: https://docs.langchain.com/oss/python/langchain/context-engineering
accessed: 2026-07-25
lc_version: unknown
status: draft
lab:
related:
  - ./03-02-tools.md
  - ./03-03-middleware-overview.md
  - ./03-04-middleware-built-in.md
---

# Context engineering

> Khung tư duy để trả lời một câu hỏi duy nhất: *tại mỗi bước của agent, cái gì được đưa vào cho LLM, và lấy từ đâu.*
> Đây là trang khái niệm đầu mối — phần cơ chế nằm ở các trang [middleware](./03-03-middleware-overview.md) và [tools](./03-02-tools.md), trang này chỉ ráp các mảnh lại.

---

## 1. Tổng quan

**Context engineering là gì.** Là việc cung cấp đúng thông tin và đúng tool, ở đúng định dạng, để LLM hoàn thành được nhiệm vụ.

**Vì sao cần.** Agent chạy được trong bản demo nhưng hỏng khi ra thực tế. Khi hỏng, gần như luôn là do lệnh gọi LLM bên trong agent làm sai. LLM sai vì một trong hai lý do:

1. Model nền không đủ giỏi
2. Context "đúng" không được đưa vào cho model

Phần lớn trường hợp là lý do thứ hai. Nói cách khác: model thường không thiếu năng lực, mà thiếu dữ kiện được đưa vào đúng lúc.

### Vòng lặp agent (agent loop)

Một vòng lặp agent điển hình có hai bước, lặp đến khi model tự quyết định dừng:

1. **Model call** — gọi LLM kèm prompt và danh sách tool; model trả về câu trả lời, hoặc yêu cầu chạy tool
2. **Tool execution** — chạy các tool model yêu cầu, trả kết quả tool về

Context engineering là việc kiểm soát *cái gì xảy ra ở mỗi bước, và cả cái gì xảy ra giữa hai bước.*

### Ba loại context — cái bạn kiểm soát được

| Loại context | Kiểm soát cái gì | Transient hay Persistent |
|---|---|---|
| **Model context** | Cái gì đi vào mỗi lệnh gọi model (chỉ dẫn, lịch sử tin nhắn, tool, định dạng đầu ra) | Transient |
| **Tool context** | Cái gì tool đọc được và ghi ra (đọc/ghi vào state, store, runtime context) | Persistent |
| **Life-cycle context** | Cái gì xảy ra *giữa* lệnh gọi model và tool (tóm tắt, guardrail, ghi log…) | Persistent |

Hai từ trong cột phải là trục phân loại quan trọng nhất của cả trang:

- **Transient** (nhất thời): thứ LLM thấy *cho một lệnh gọi duy nhất*. Bạn sửa tin nhắn, tool, prompt mà **không** đổi cái đang lưu trong state. Hết lệnh gọi là mất.
- **Persistent** (bền): thứ được lưu vào state, tồn tại qua các lượt hội thoại. Life-cycle hook và thao tác ghi của tool sửa cái này *vĩnh viễn*.

### Ba nguồn dữ liệu — context lấy từ đâu

Mọi loại context ở trên đều rút dữ liệu từ ba nguồn sau. Nắm ba nguồn này là nắm được toàn bộ trang, vì mọi ví dụ code chỉ là biến thể của việc đọc/ghi ba nguồn này:

| Nguồn | Còn gọi là | Phạm vi | Ví dụ |
|---|---|---|---|
| **Runtime Context** | Cấu hình tĩnh | Trong một cuộc hội thoại | User ID, API key, kết nối database, quyền hạn, biến môi trường |
| **State** | Bộ nhớ ngắn hạn | Trong một cuộc hội thoại | Tin nhắn hiện tại, file đã upload, trạng thái đăng nhập, kết quả tool |
| **Store** | Bộ nhớ dài hạn | Xuyên nhiều cuộc hội thoại | Sở thích người dùng, insight rút ra, ký ức, dữ liệu lịch sử |

Phân biệt nhanh: **Runtime Context** là thứ cố định bạn nạp vào lúc gọi agent (không đổi trong cuộc hội thoại). **State** đổi liên tục trong cuộc hội thoại. **Store** sống lâu hơn cả cuộc hội thoại.

### Cơ chế bên dưới: middleware

**middleware** là cơ chế khiến context engineering làm được trong thực tế. Đây là một lớp bạn gắn vào để móc (hook) vào bất kỳ bước nào của vòng đời agent, rồi làm một trong hai việc: **cập nhật context**, hoặc **nhảy sang một bước khác** trong vòng đời. Xuyên suốt trang, mọi ví dụ đều dùng API middleware như phương tiện để đạt mục đích context engineering.

Cơ chế chi tiết của middleware nằm ở [trang middleware](./03-03-middleware-overview.md), trang này chỉ dùng nó.

### Ví dụ nhỏ nhất

Ráp một agent có prompt đổi theo độ dài hội thoại — minh họa cả ba mảnh: nguồn dữ liệu (State), middleware (`dynamic_prompt`), và mục đích (đưa đúng chỉ dẫn cho model):

```python
from langchain.agents.middleware import dynamic_prompt, ModelRequest

@dynamic_prompt                                          # decorator biến hàm thành middleware sửa prompt
def state_aware_prompt(request: ModelRequest) -> str:
    message_count = len(request.messages)                # request.messages = lối tắt của request.state["messages"]

    base = "You are a helpful assistant."
    if message_count > 10:                               # hội thoại đã dài
        base += "\nThis is a long conversation - be extra concise."
    return base                                          # chuỗi trả về trở thành system prompt cho lệnh gọi này

agent = create_agent(
    model="gpt-5.5",
    tools=[...],
    middleware=[state_aware_prompt],                     # gắn middleware vào agent
)
```

**Hiệu ứng** (dựng lại): với hội thoại đã hơn 10 tin nhắn, system prompt model nhận được là:

```
You are a helpful assistant.                             ← câu nền, luôn có
This is a long conversation - be extra concise.          ← nhánh thêm vào khi message_count > 10
```

Đây là sửa **transient**: system prompt đổi cho *lệnh gọi này*, state không bị đụng đến.

---

## 2. Model context

Kiểm soát cái gì đi vào **mỗi lệnh gọi model**: chỉ dẫn, tool có sẵn, dùng model nào, định dạng đầu ra. Mọi quyết định ở đây tác động thẳng đến độ tin cậy và chi phí. Toàn bộ Model context là **transient** — sửa cho một lệnh gọi, không đổi state.

Năm thứ điều khiển được, mỗi thứ đều rút từ State / Store / Runtime Context:

### 2.1 System prompt

**Khái niệm.** Chỉ dẫn nền từ lập trình viên gửi cho LLM, đặt hành vi và năng lực của nó.

**Vai trò.** Người dùng khác nhau, ngữ cảnh khác nhau, giai đoạn hội thoại khác nhau cần chỉ dẫn khác nhau. Agent tốt rút từ ký ức, sở thích, cấu hình để đưa đúng chỉ dẫn cho trạng thái hiện tại — thay vì một prompt cứng cho mọi tình huống.

**Áp dụng thực tế.** Cùng một agent hỗ trợ nội bộ: khi người gọi có role `admin` thì thêm câu "bạn được phép thao tác mọi thứ"; khi là `viewer` thì thêm "chỉ hướng dẫn thao tác đọc". Vai trò lấy từ Runtime Context.

**Triển khai.** Dùng `dynamic_prompt` như mục 1. Đọc từ Runtime Context thay vì State:

```python
@dynamic_prompt
def context_aware_prompt(request: ModelRequest) -> str:
    user_role = request.runtime.context.user_role        # đọc role từ Runtime Context
    base = "You are a helpful assistant."
    if user_role == "admin":
        base += "\nYou have admin access. You can perform all operations."
    elif user_role == "viewer":
        base += "\nYou have read-only access. Guide users to read operations only."
    return base
```

Ba cách đọc — State (đếm số tin nhắn), Store (đọc sở thích đã lưu), Runtime Context (đọc role/môi trường) — chỉ khác nhau ở dòng lấy dữ liệu, khung còn lại giống hệt.

### 2.2 Messages

**Khái niệm.** Danh sách tin nhắn (lịch sử hội thoại) tạo nên prompt gửi cho LLM.

**Vai trò.** Quản lý nội dung tin nhắn để đảm bảo model có đúng thông tin mà trả lời tốt. Đây là chỗ chèn thêm ngữ cảnh mà lịch sử gốc không có sẵn.

**Áp dụng thực tế.** Người dùng đã upload ba file trong phiên này. Trước khi hỏi model, chèn một đoạn mô tả các file đó vào cuối danh sách tin nhắn để model biết mình có file nào mà tham chiếu.

**Triển khai.** Dùng `wrap_model_call` — middleware bọc quanh lệnh gọi model, cho phép sửa `request` trước khi chuyển tiếp cho `handler`:

```python
@wrap_model_call
def inject_file_context(request, handler):
    uploaded_files = request.state.get("uploaded_files", [])   # đọc metadata file từ State
    if uploaded_files:
        file_context = "Files you have access to: ..."         # dựng đoạn mô tả file
        messages = [                                           # nối đoạn mô tả vào SAU tin nhắn hiện có
            *request.messages,
            {"role": "user", "content": file_context},
        ]
        request = request.override(messages=messages)          # override = ghi đè cho lệnh gọi này, không đụng state
    return handler(request)                                    # chuyển request đã sửa cho bước tiếp theo
```

Tài liệu lưu ý chèn ngữ cảnh vào *cuối* danh sách, vì model chú ý nhiều hơn đến các tin nhắn cuối.

**!Note:** Các ví dụ ở đây dùng `wrap_model_call` nên là sửa **transient** — chỉ đổi tin nhắn gửi cho model trong một lệnh gọi, **không** đổi cái lưu trong state. Muốn sửa **persistent** (đổi hẳn state) phải: trả về một `ExtendedModelResponse` kèm `Command` từ `wrap_model_call`, hoặc dùng life-cycle hook như `before_model` / `after_model` / `wrap_tool_call`.

### 2.3 Tools

Tool cho model tương tác với database, API, hệ thống ngoài. Cách bạn **định nghĩa** và **chọn** tool quyết định model có làm xong việc không.

**Định nghĩa tool.** Mỗi tool cần tên, mô tả, tên tham số và mô tả tham số rõ ràng. Đây không phải metadata trang trí — chúng dẫn dắt suy luận của model về *khi nào* và *cách nào* dùng tool:

```python
@tool(parse_docstring=True)                              # parse_docstring: đọc mô tả tham số từ docstring
def search_orders(user_id: str, status: str, limit: int = 10) -> str:
    """Search for user orders by status.

    Use this when the user asks about order history or wants to check
    order status. Always filter by the provided status.

    Args:
        user_id: Unique identifier for the user
        status: Order status: 'pending', 'shipped', or 'delivered'
        limit: Maximum number of results to return
    """
    ...
```

**Chọn tool (dynamic tool selection).** Không phải tool nào cũng hợp mọi tình huống. Quá nhiều tool làm model quá tải context và tăng lỗi; quá ít thì giới hạn năng lực. Chọn tool động điều chỉnh bộ tool theo trạng thái đăng nhập, quyền, feature flag, hoặc giai đoạn hội thoại.

**Áp dụng thực tế.** Chỉ mở nhóm tool nhạy cảm sau khi người dùng đăng nhập; trước đó chỉ để lộ các tool tên bắt đầu bằng `public_`.

```python
@wrap_model_call
def state_based_tools(request, handler):
    is_authenticated = request.state.get("authenticated", False)   # đọc trạng thái đăng nhập từ State
    if not is_authenticated:
        tools = [t for t in request.tools if t.name.startswith("public_")]   # lọc còn tool công khai
        request = request.override(tools=tools)                    # ghi đè danh sách tool cho lệnh gọi này
    return handler(request)
```

Trang này chỉ giới thiệu. Cách lọc tool đã đăng ký lẫn cách đăng ký tool lúc chạy (ví dụ từ MCP server) nằm ở [Dynamic tools (phần 7) trong trang tools](./03-02-tools.md).

### 2.4 Model

**Khái niệm.** Chọn model nào (kèm cấu hình) để gọi. Model khác nhau có điểm mạnh, chi phí, và cửa sổ context khác nhau — lựa chọn có thể đổi ngay trong một lần chạy agent.

**Vai trò.** Dùng model nhỏ rẻ cho việc nhẹ, model lớn cho việc nặng, để cân chi phí và chất lượng thay vì cắm cứng một model.

**Áp dụng thực tế.** Hội thoại ngắn (< 10 tin nhắn) dùng model tiết kiệm; dài hơn 20 tin nhắn chuyển sang model có cửa sổ context lớn hơn để không tràn.

```python
large_model = init_chat_model("claude-sonnet-4-6")       # khởi tạo sẵn NGOÀI middleware, tránh tạo lại mỗi lần
efficient_model = init_chat_model("gpt-5.4-mini")

@wrap_model_call
def state_based_model(request, handler):
    message_count = len(request.messages)                # đo độ dài hội thoại từ State
    model = large_model if message_count > 20 else efficient_model
    request = request.override(model=model)              # ghi đè model cho lệnh gọi này
    return handler(request)
```

### 2.5 Response format

**Khái niệm.** Định dạng đầu ra có cấu trúc (structured output) biến văn bản tự do thành dữ liệu đã được kiểm tra và có cấu trúc.

**Vai trò.** Khi cần trích xuất trường cụ thể hoặc trả dữ liệu cho hệ thống phía sau, văn bản tự do không đủ. Cấp một schema làm response format thì câu trả lời cuối của model được đảm bảo khớp schema đó.

Cơ chế: agent chạy vòng lặp model/tool đến khi model gọi tool xong, rồi ép câu trả lời cuối vào đúng định dạng đã cấp.

**Định nghĩa format.** Dùng Pydantic `BaseModel`. Tên trường, kiểu, và mô tả (`Field(description=...)`) chính là thứ dẫn model điền đúng:

```python
class CustomerSupportTicket(BaseModel):
    """Structured ticket information extracted from customer message."""
    category: str = Field(description="Issue category: 'billing', 'technical', 'account', or 'product'")
    priority: str = Field(description="Urgency level: 'low', 'medium', 'high', or 'critical'")
    summary: str = Field(description="One-sentence summary of the customer's issue")
    customer_sentiment: str = Field(description="Customer's emotional tone: 'frustrated', 'neutral', or 'satisfied'")
```

**Chọn format động.** Trả format đơn giản ở đầu hội thoại, format chi tiết khi độ phức tạp tăng — dùng lại `wrap_model_call` với `request.override(response_format=...)`, đọc điều kiện từ State / Store / Runtime Context y như các mục trên.

---

## 3. Tool context

Tool đặc biệt ở chỗ nó vừa **đọc** vừa **ghi** context. Ở dạng cơ bản nhất: tool nhận tham số model yêu cầu, làm việc, trả một tool message về. Nhưng tool còn có thể lấy thêm thông tin cho model, và ghi lại thông tin cho các bước sau. Toàn bộ Tool context là **persistent**.

### 3.1 Reads — tool đọc context

**Khái niệm.** Phần lớn tool thực tế cần nhiều hơn tham số model đưa: cần user ID để truy database, API key cho dịch vụ ngoài, hoặc trạng thái phiên hiện tại để ra quyết định.

**Vai trò.** Tool đọc từ State, Store, Runtime Context để lấy những thứ này — thay vì bắt model phải tự nhét chúng vào tham số.

**Triển khai.** Tool nhận thêm tham số `runtime: ToolRuntime`, rồi đọc qua `runtime.state` / `runtime.store` / `runtime.context`:

```python
@tool
def check_authentication(runtime: ToolRuntime) -> str:
    """Check if user is authenticated."""
    is_authenticated = runtime.state.get("authenticated", False)   # đọc trạng thái phiên từ State
    return "User is authenticated" if is_authenticated else "User is not authenticated"
```

### 3.2 Writes — tool ghi context

**Khái niệm.** Kết quả tool không chỉ trả về cho model, mà còn cập nhật bộ nhớ của agent để các bước sau dùng được.

**Vai trò.** Cho phép tool lưu lại dữ kiện quan trọng (ví dụ: đánh dấu đã đăng nhập, lưu sở thích) — biến kết quả một lần chạy tool thành ngữ cảnh bền cho về sau.

**Triển khai.** Ghi vào **State**: trả về một `Command` với `update=...`. Ghi vào **Store**: gọi `store.put(...)`.

```python
@tool
def authenticate_user(password: str, runtime: ToolRuntime) -> Command:
    """Authenticate user and update State."""
    if password == "correct":
        return Command(update={"authenticated": True})   # ghi vào State: đánh dấu đã đăng nhập
    return Command(update={"authenticated": False})
```

Ghi vào State qua `Command` là ghi trong cuộc hội thoại; ghi vào Store qua `store.put` là ghi bền xuyên nhiều cuộc hội thoại. Ví dụ đầy đủ về đọc/ghi state, store, runtime context trong tool nằm ở [trang tools](./03-02-tools.md).

---

## 4. Life-cycle context

Kiểm soát cái gì xảy ra **giữa** các bước lõi của agent — chen vào luồng dữ liệu để làm những việc cắt ngang như tóm tắt, guardrail, ghi log. Life-cycle context là **persistent**.

Như đã thấy ở Model context và Tool context, **middleware** là cơ chế thực hiện. Móc vào bất kỳ bước nào của vòng đời agent, rồi:

1. **Cập nhật context** — sửa state và store để lưu thay đổi, cập nhật lịch sử hội thoại, lưu insight
2. **Nhảy trong vòng đời** — chuyển sang bước khác tùy context (ví dụ: bỏ qua bước chạy tool nếu thỏa điều kiện, hoặc gọi lại model với context đã sửa)

### Ví dụ: tóm tắt hội thoại (SummarizationMiddleware)

**Khái niệm.** Một trong những mẫu life-cycle phổ biến nhất: tự động cô đọng lịch sử hội thoại khi nó quá dài.

**Vai trò.** Khác với việc cắt tin nhắn kiểu transient ở mục 2.2, tóm tắt **cập nhật state bền** — thay hẳn các tin nhắn cũ bằng một bản tóm tắt được lưu lại cho mọi lượt sau. Giải quyết bài toán hội thoại dài làm tràn cửa sổ context và đội chi phí token.

**Triển khai.** Dùng middleware dựng sẵn:

```python
from langchain.agents.middleware import SummarizationMiddleware

agent = create_agent(
    model="gpt-5.5",
    tools=[...],
    middleware=[
        SummarizationMiddleware(
            model="gpt-5.4-mini",        # dùng model rẻ hơn CHỈ để tóm tắt
            trigger={"tokens": 4000},    # vượt ngưỡng token này thì kích hoạt tóm tắt
            keep={"messages": 20},       # giữ nguyên 20 tin nhắn gần nhất
        ),
    ],
)
```

Khi hội thoại vượt ngưỡng token, `SummarizationMiddleware` tự động: tóm tắt các tin nhắn cũ bằng một lệnh gọi LLM riêng, thay chúng bằng một tin nhắn tóm tắt trong State (vĩnh viễn), và giữ nguyên các tin nhắn gần đây. Từ đó về sau các lượt sẽ thấy bản tóm tắt thay vì tin nhắn gốc.

Danh sách đầy đủ middleware dựng sẵn, các hook có thể móc vào, và cách viết middleware riêng nằm ở [trang middleware](./03-04-middleware-built-in.md).

---

## Tham chiếu chéo

- [03-02-tools.md](./03-02-tools.md) — định nghĩa tool, `ToolRuntime`, đọc/ghi state–store–runtime context, dynamic tool selection (mục 2.3 và 3 của file này chỉ giới thiệu, chi tiết ở đó)
- [03-03-middleware-overview.md](./03-03-middleware-overview.md) — cơ chế middleware, `wrap_model_call`, `dynamic_prompt` (nền cho toàn bộ ví dụ ở file này)
- [03-04-middleware-built-in.md](./03-04-middleware-built-in.md) — danh sách middleware dựng sẵn, gồm `SummarizationMiddleware` ở mục 4
- [03-05-middleware-custom.md](./03-05-middleware-custom.md) — State updates: cách sửa persistent từ `wrap_model_call` (liên quan !Note mục 2.2)
- Trang models của tài liệu gốc (`docs.langchain.com/oss/python/langchain/models`) — Dynamic model selection; **chưa có file tương ứng trong bộ, cần bổ sung**
- Trang concept context (`docs.langchain.com/oss/python/concepts/context`) — phân loại các loại context và khi nào dùng; tài liệu gốc khuyên đọc trước trang này