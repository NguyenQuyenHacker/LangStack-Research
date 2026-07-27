---
title: Guardrails
doc_source: https://docs.langchain.com/oss/python/langchain/guardrails
accessed: 2026-07-25
version: "unknown"
status: draft
lab:
related:
  - ./middleware.md
  - ./human-in-the-loop.md
  - ./event-streaming.md
---

# Guardrails — chốt kiểm soát an toàn cho agent

> Guardrails là lớp kiểm tra và lọc nội dung đặt tại các điểm mốc trong lúc agent chạy, để chặn rò rỉ dữ liệu nhạy cảm, chặn nội dung độc hại và ép tuân thủ quy tắc nghiệp vụ trước khi hậu quả xảy ra.
> Tất cả guardrails ở đây đều dựng bằng **middleware** — cơ chế chèn xử lý vào giữa luồng chạy của agent. Cách hoạt động của middleware nằm ở trang riêng: [middleware.md](./middleware.md).

---

## 1. Tổng quan

Guardrails không phải một hàm hay một class riêng. Nó là **cách dùng middleware để kiểm soát nội dung tại bốn điểm chặn**: trước khi agent bắt đầu, sau khi agent kết thúc, quanh lời gọi model, và quanh lời gọi tool.

Khác với việc nhét câu lệnh "hãy an toàn" vào prompt: prompt là lời nhắc, model có thể lờ đi; guardrails là mã chạy tách rời, kiểm tra thật và chặn thật.

Các việc guardrails hay dùng để làm: chặn rò rỉ thông tin cá nhân (PII), chặn tấn công tiêm prompt (prompt injection), chặn nội dung độc hại, ép tuân thủ quy tắc nghiệp vụ, và kiểm tra chất lượng đầu ra.

```python
from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware

agent = create_agent(
    model="gpt-5.5",
    tools=[customer_service_tool],
    middleware=[                                        # danh sách guardrails, chạy theo thứ tự khai báo
        PIIMiddleware("email", strategy="redact", apply_to_input=True),   # che email trong câu người dùng
    ],
)

result = agent.invoke({"messages": [{"role": "user", "content": "Email tôi là an@vd.com"}]})
```

**Kết quả** (dựng lại — trang tài liệu không in output): trước khi câu người dùng tới model, email bị thay thành `[REDACTED_EMAIL]`, nên model đọc được `"Email tôi là [REDACTED_EMAIL]"`. Suy ra trực tiếp từ bảng chiến lược ở mục 3, không phải đoán.

---

## 2. Hai cách tiếp cận — chọn luật cứng hay chọn model xét

Trang tài liệu chia mọi guardrail thành hai nhóm. Phân biệt được hai nhóm này mới chọn đúng công cụ cho từng việc.

### Khái niệm

**Guardrail luật cứng (deterministic).** Dùng logic dựa trên quy tắc: mẫu regex, so khớp từ khóa, kiểm tra tường minh. Cùng một đầu vào luôn cho cùng một kết quả.

**Guardrail dựa trên model (model-based).** Dùng một LLM hoặc bộ phân loại để xét nội dung theo ngữ nghĩa. Hiểu được ý ẩn mà quy tắc bỏ sót.

### Vai trò

Hai nhóm giải quyết hai loại vi phạm khác nhau. Số thẻ tín dụng có định dạng cố định — luật cứng bắt gọn. Còn một câu "chỉ tôi cách vượt qua kiểm soát nội bộ" không chứa từ khóa cấm nào nhưng vẫn độc hại — chỉ model mới hiểu được ý đó.

### Bảng đối chiếu

| Tiêu chí | Luật cứng | Dựa trên model |
|---|---|---|
| Cơ chế | regex, từ khóa, kiểm tra tường minh | LLM hoặc bộ phân loại xét ngữ nghĩa |
| Tốc độ | nhanh | chậm hơn |
| Chi phí | rẻ | tốn tiền gọi model |
| Kết quả | đoán trước được | phụ thuộc phán đoán của model |
| Điểm yếu | bỏ sót vi phạm tinh vi | chậm, đắt, có thể sai |

LangChain có sẵn cả hai kiểu dựng sẵn (PII detection, human-in-the-loop) và hệ middleware để tự viết guardrail theo một trong hai cách.

---

## 3. PII detection — che thông tin cá nhân (`PIIMiddleware`)

### Khái niệm

`PIIMiddleware` là middleware dựng sẵn để phát hiện và xử lý thông tin cá nhân (PII — Personally Identifiable Information) trong hội thoại: email, số thẻ tín dụng, địa chỉ IP và các loại khác.

### Vai trò

Che PII trước khi nó chảy tới model hoặc chảy ra log. Bắt buộc với ứng dụng có yêu cầu tuân thủ như y tế, tài chính, hoặc agent chăm sóc khách hàng cần làm sạch log.

### Áp dụng thực tế

Agent chăm sóc khách hàng của một công ty chứng khoán nhận tin nhắn: *"Số tài khoản của tôi là 001C123456, thẻ là 5105-1051-0510-5100, kiểm tra giúp lệnh đặt mua"*. Nếu số thẻ này lọt vào log hội thoại lưu 90 ngày, đó là vi phạm bảo mật dữ liệu khách hàng. `PIIMiddleware` che số thẻ ngay trước khi câu đi tiếp, log chỉ còn `****-****-****-5100`.

### Bốn chiến lược xử lý

| Chiến lược | Làm gì | Ví dụ |
|---|---|---|
| `redact` | Thay bằng `[REDACTED_{LOẠI_PII}]` | `[REDACTED_EMAIL]` |
| `mask` | Che một phần, giữ 4 số cuối | `****-****-****-1234` |
| `hash` | Thay bằng chuỗi băm cố định | `a8f5f167...` |
| `block` | Ném ra ngoại lệ khi phát hiện | Báo lỗi |

Bốn chiến lược khác nhau ở chỗ dữ liệu còn lại gì. `redact` xóa sạch loại PII. `mask` giữ 4 số cuối để nhân viên còn đối chiếu. `hash` cho phép so trùng hai lần xuất hiện mà không lộ giá trị gốc. `block` chặn thẳng — dùng cho thứ tuyệt đối không được xuất hiện như API key.

### Triển khai

```python
from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware

agent = create_agent(
    model="gpt-5.5",
    tools=[customer_service_tool, email_tool],
    middleware=[
        PIIMiddleware(                              # lớp 1: che email trong câu người dùng
            "email",
            strategy="redact",
            apply_to_input=True,                    # chỉ kiểm câu người dùng trước khi vào model
        ),
        PIIMiddleware(                              # lớp 2: che một phần số thẻ, giữ 4 số cuối
            "credit_card",
            strategy="mask",
            apply_to_input=True,
        ),
        PIIMiddleware(                              # lớp 3: chặn thẳng nếu thấy API key
            "api_key",
            detector=r"sk-[a-zA-Z0-9]{32}",         # loại tự định nghĩa, khớp bằng regex riêng
            strategy="block",
            apply_to_input=True,
        ),
    ],
)

result = agent.invoke({
    "messages": [{"role": "user",
        "content": "My email is john.doe@example.com and card is 5105-1051-0510-5100"}]
})
```

**Kết quả** (dựng lại — suy từ bảng chiến lược, trang tài liệu không in):

```
Câu người dùng gốc:  "My email is john.doe@example.com and card is 5105-1051-0510-5100"
Câu model thực nhận: "My email is [REDACTED_EMAIL] and card is ****-****-****-5100"   ← email bị redact, thẻ bị mask giữ 4 số cuối
```

Câu này không có API key nên nhánh `block` không kích hoạt. Nếu có chuỗi khớp `sk-...`, `agent.invoke` sẽ ném ngoại lệ thay vì trả kết quả.

### Các loại PII dựng sẵn và tùy chọn cấu hình

Loại dựng sẵn: `email`, `credit_card` (có kiểm tra Luhn), `ip`, `mac_address`, `url`.

| Tham số | Nghĩa | Mặc định |
|---|---|---|
| `pii_type` | Loại PII cần bắt (dựng sẵn hoặc tự định nghĩa) | Bắt buộc |
| `strategy` | Cách xử lý (`"block"`, `"redact"`, `"mask"`, `"hash"`) | `"redact"` |
| `detector` | Hàm hoặc regex tự định nghĩa để bắt | `None` (dùng bộ dựng sẵn) |
| `apply_to_input` | Kiểm câu người dùng trước khi gọi model | `True` |
| `apply_to_output` | Kiểm câu trả lời của AI sau khi gọi model | `False` |
| `apply_to_tool_results` | Kiểm kết quả tool sau khi tool chạy | `False` |

Ba tham số `apply_to_*` bật/tắt độc lập. Mặc định chỉ kiểm đầu vào; muốn che cả câu AI trả ra thì phải bật `apply_to_output=True` riêng.

**!Note:** Bật `apply_to_output=True` thì `PIIMiddleware` còn che luôn cả dữ liệu gửi dần ra ngoài (wire output) — gồm mẩu chữ chảy dần, tham số lời gọi tool, kết quả tool, và ảnh chụp trạng thái — thông qua một stream transformer đăng ký sẵn. Tính năng này cần `langchain>=1.3.2`. Cơ chế transformer nằm ở trang khác: [event-streaming.md](./event-streaming.md#register-transformers-on-middleware). Quên bật `apply_to_output` thì câu AI trả ra vẫn lộ PII dù đầu vào đã che sạch — lỗi im lặng, code chạy không báo gì.

---

## 4. Human-in-the-loop — chặn chờ người duyệt (`HumanInTheLoopMiddleware`)

### Khái niệm

`HumanInTheLoopMiddleware` là middleware dựng sẵn buộc agent dừng lại chờ người thật phê duyệt trước khi chạy một tool nhạy cảm.

### Vai trò

Đây là guardrail mạnh nhất cho quyết định rủi ro cao. Với thao tác không thể hoàn tác — chuyển tiền, xóa dữ liệu production, gửi thư cho bên ngoài — một lần model quyết sai là mất mát thật. Chặn chờ người duyệt biến quyết định tự động thành quyết định có người gác cổng.

### Áp dụng thực tế

Agent hỗ trợ nghiệp vụ soạn được email thông báo điều chỉnh lãi suất trái phiếu gửi cho 200 nhà đầu tư. Gửi nhầm là sự cố công bố thông tin. Đặt tool `send_email` vào diện chờ duyệt: agent soạn xong thì dừng, chuyên viên đọc lại rồi mới bấm duyệt cho gửi.

### Triển khai

```python
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

agent = create_agent(
    model="gpt-5.5",
    tools=[search_tool, send_email_tool, delete_database_tool],
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={                          # khai báo tool nào cần duyệt, tool nào không
                "send_email": True,                 # gửi email: bắt buộc duyệt
                "delete_database": True,            # xóa dữ liệu: bắt buộc duyệt
                "search": False,                    # tìm kiếm: tự động cho qua
            }
        ),
    ],
    checkpointer=InMemorySaver(),                   # nơi lưu trạng thái để dừng rồi chạy tiếp được
)

config = {"configurable": {"thread_id": "some_id"}}   # mỗi phiên chờ duyệt cần một thread_id riêng

result = agent.invoke(                              # lần gọi 1: agent chạy tới tool nhạy cảm rồi dừng
    {"messages": [{"role": "user", "content": "Send an email to the team"}]},
    config=config
)

result = agent.invoke(                              # lần gọi 2: gửi quyết định duyệt để chạy tiếp
    Command(resume={"decisions": [{"type": "approve"}]}),
    config=config                                   # cùng thread_id mới nối lại đúng phiên đang dừng
)
```

**Kết quả** (dựng lại): lần gọi 1 không chạy `send_email` mà trả về một tín hiệu dừng (interrupt) chờ người duyệt. Lần gọi 2 truyền `Command(resume=...)` với cùng `thread_id`, agent nối lại phiên cũ và chạy tiếp `send_email`. Hình dạng chính xác của tín hiệu dừng và các loại quyết định ngoài `approve` không nằm trong trang này — xem [human-in-the-loop.md](./human-in-the-loop.md).

**!Note:** Thiếu `checkpointer` thì không dừng-rồi-chạy-tiếp được, vì không có nơi lưu trạng thái giữa hai lần gọi. Và hai lần gọi phải cùng `thread_id`; sai `thread_id` thì lần 2 không tìm thấy phiên đang dừng để nối lại.

---

## 5. Guardrail tự viết — chèn kiểm tra trước hoặc sau agent

Khi cần logic riêng, viết middleware tự chạy trước hoặc sau agent. Hai điểm chèn tương ứng hai loại kiểm tra khác nhau.

### 5.1 Kiểm trước agent — chặn ngay từ câu đầu (`before_agent`)

**Khái niệm.** Hook `before_agent` chạy đúng một lần ở đầu mỗi lần gọi, trước khi bất kỳ xử lý nào bắt đầu.

**Vai trò.** Dùng cho kiểm tra ở mức phiên: xác thực, giới hạn số lần gọi, hoặc chặn câu hỏi không hợp lệ trước khi tốn một lời gọi model nào. Chặn ở đây rẻ nhất vì chưa gọi model.

**Áp dụng thực tế.** Chặn câu chứa từ khóa cấm như "hack", "exploit", "malware" ngay khi vào, trả lời từ chối luôn mà không đưa câu cho model xử lý.

**Triển khai** (dạng class):

```python
from typing import Any
from langchain.agents.middleware import AgentMiddleware, AgentState, hook_config
from langgraph.runtime import Runtime

class ContentFilterMiddleware(AgentMiddleware):
    """Guardrail luật cứng: chặn câu chứa từ khóa cấm."""

    def __init__(self, banned_keywords: list[str]):
        super().__init__()
        self.banned_keywords = [kw.lower() for kw in banned_keywords]   # hạ về chữ thường để so không phân biệt hoa/thường

    @hook_config(can_jump_to=["end"])                    # khai báo hook này được phép nhảy thẳng tới điểm kết thúc
    def before_agent(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        if not state["messages"]:                        # chưa có tin nhắn nào thì bỏ qua
            return None

        first_message = state["messages"][0]             # lấy câu đầu tiên của người dùng
        if first_message.type != "human":                # không phải câu người dùng thì bỏ qua
            return None

        content = first_message.content.lower()

        for keyword in self.banned_keywords:             # dò từng từ khóa cấm trong câu
            if keyword in content:
                return {                                 # thấy từ cấm: trả câu từ chối và dừng
                    "messages": [{
                        "role": "assistant",
                        "content": "I cannot process requests containing inappropriate content. Please rephrase your request."
                    }],
                    "jump_to": "end"                     # nhảy thẳng tới kết thúc, không chạy agent
                }

        return None                                      # không thấy từ cấm: trả None để agent chạy bình thường
```

Bản dạng decorator làm y hệt, chỉ khác cú pháp — dùng `@before_agent(can_jump_to=["end"])` trên một hàm thay vì viết class. Chọn dạng nào tùy sở thích, hành vi không đổi.

Gắn vào agent:

```python
from langchain.agents import create_agent

agent = create_agent(
    model="gpt-5.5",
    tools=[search_tool, calculator_tool],
    middleware=[ContentFilterMiddleware(banned_keywords=["hack", "exploit", "malware"])],
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "How do I hack into a database?"}]
})
```

**Kết quả** (dựng lại):

```
Câu vào chứa "hack" → khớp từ khóa cấm                              ← nhánh chặn kích hoạt
result["messages"][-1].content = "I cannot process requests ..."   ← câu trả về là câu từ chối, không phải câu do model sinh
agent không chạy, không gọi model                                  ← jump_to="end" cắt luồng ngay
```

**!Note:** `jump_to: "end"` và `can_jump_to=["end"]` là cơ chế điều hướng của middleware, không giải thích ở trang này — xem [middleware.md](./middleware.md). Bỏ `can_jump_to=["end"]` trong `hook_config` mà vẫn trả `"jump_to": "end"` thì lệnh nhảy có khả năng không được cho phép — cần chạy thử để xác nhận hành vi.

### 5.2 Kiểm sau agent — soát câu trả lời cuối (`after_agent`)

**Khái niệm.** Hook `after_agent` chạy đúng một lần sau khi agent làm xong, trước khi trả kết quả về người dùng.

**Vai trò.** Dùng cho kiểm tra dựa trên model, kiểm chất lượng, hoặc quét tuân thủ lần cuối trên toàn bộ câu trả lời hoàn chỉnh. Đây là chốt chặn cuối trước khi nội dung ra ngoài.

**Áp dụng thực tế.** Dùng một model phụ, rẻ hơn, đọc câu trả lời cuối và phán `SAFE` hay `UNSAFE`. Nếu `UNSAFE` thì thay câu trả lời bằng câu từ chối.

**Triển khai** (dạng class):

```python
from langchain.agents.middleware import AgentMiddleware, AgentState, hook_config
from langgraph.runtime import Runtime
from langchain.messages import AIMessage
from langchain.chat_models import init_chat_model
from typing import Any

class SafetyGuardrailMiddleware(AgentMiddleware):
    """Guardrail dựa trên model: dùng LLM xét độ an toàn của câu trả lời."""

    def __init__(self):
        super().__init__()
        self.safety_model = init_chat_model("gpt-5.4-mini")   # model phụ rẻ hơn, chỉ để phán an toàn

    @hook_config(can_jump_to=["end"])
    def after_agent(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        if not state["messages"]:
            return None

        last_message = state["messages"][-1]                  # lấy câu trả lời cuối cùng
        if not isinstance(last_message, AIMessage):           # không phải câu do AI sinh thì bỏ qua
            return None

        safety_prompt = f"""Evaluate if this response is safe and appropriate.
        Respond with only 'SAFE' or 'UNSAFE'.

        Response: {last_message.content}"""                   # ép model phụ chỉ trả đúng một trong hai nhãn

        result = self.safety_model.invoke([{"role": "user", "content": safety_prompt}])

        if "UNSAFE" in result.content:                        # bị phán không an toàn: ghi đè câu trả lời
            last_message.content = "I cannot provide that response. Please rephrase your request."

        return None                                           # luôn trả None; đã sửa nội dung tại chỗ ở dòng trên
```

Bản decorator tương đương dùng `@after_agent(can_jump_to=["end"])` trên một hàm, hành vi không đổi.

**Kết quả** (dựng lại): với câu hỏi độc hại, câu trả lời cuối bị model phụ phán `UNSAFE`, nội dung `last_message.content` bị ghi đè thành câu từ chối. Với câu bình thường, model phụ trả `SAFE`, không có gì bị đổi.

**!Note:** Hàm này sửa `last_message.content` trực tiếp rồi vẫn `return None` — thay đổi có hiệu lực nhờ sửa tại chỗ, không nhờ giá trị trả về. Model phụ được yêu cầu chỉ trả `SAFE`/`UNSAFE`, nhưng nếu nó trả câu dài chứa chữ "UNSAFE" trong ngữ cảnh khác thì điều kiện `"UNSAFE" in result.content` vẫn kích hoạt nhầm — lỗi im lặng, cần ràng buộc đầu ra chặt hơn khi chạy thật.

### 5.3 Xếp chồng nhiều guardrail

Thêm nhiều guardrail vào mảng `middleware` để dựng phòng thủ nhiều lớp. Chúng chạy **theo đúng thứ tự khai báo**.

```python
from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware, HumanInTheLoopMiddleware

agent = create_agent(
    model="gpt-5.5",
    tools=[search_tool, send_email_tool],
    middleware=[
        ContentFilterMiddleware(banned_keywords=["hack", "exploit"]),   # lớp 1: lọc luật cứng trước agent
        PIIMiddleware("email", strategy="redact", apply_to_input=True),  # lớp 2a: che email ở đầu vào
        PIIMiddleware("email", strategy="redact", apply_to_output=True), # lớp 2b: che email ở đầu ra
        HumanInTheLoopMiddleware(interrupt_on={"send_email": True}),     # lớp 3: chặn chờ người duyệt gửi email
        SafetyGuardrailMiddleware(),                                     # lớp 4: model xét an toàn sau agent
    ],
)
```

Cùng một loại PII (`email`) được khai hai lần — một cho đầu vào, một cho đầu ra — vì `apply_to_input` và `apply_to_output` là hai công tắc độc lập, muốn che cả hai chiều thì phải khai cả hai.

---

## 6. Nên chọn cái nào

Trang tài liệu không xếp hạng, dưới đây là tóm tắt thực dụng theo từng loại việc.

Dùng **PII detection** khi dữ liệu nhạy cảm có định dạng nhận diện được: email, số thẻ, IP, hoặc chuỗi khớp một regex mình định nghĩa.

Dùng **human-in-the-loop** khi thao tác không thể hoàn tác và một quyết định sai gây mất mát thật: chuyển tiền, xóa dữ liệu, gửi thông báo ra ngoài.

Dùng **guardrail luật cứng trước agent** (`before_agent`) khi vi phạm bắt được bằng từ khóa hoặc mẫu — chặn sớm, rẻ, chưa tốn lời gọi model.

Dùng **guardrail dựa trên model sau agent** (`after_agent`) khi vi phạm là ý ẩn mà quy tắc không bắt được — chấp nhận chậm và tốn thêm một lời gọi model.

Ba nhóm này không loại trừ nhau. Cách dùng thực tế là xếp chồng như mục 5.3: lọc luật cứng ở ngoài cùng cho rẻ, model xét ngữ nghĩa ở trong cùng cho kỹ.

---

## Tham chiếu chéo

- [middleware.md](./middleware.md) — cơ chế middleware, các điểm chèn, và `jump_to` / `can_jump_to`
- [human-in-the-loop.md](./human-in-the-loop.md) — hình dạng tín hiệu dừng và các loại quyết định duyệt
- [event-streaming.md](./event-streaming.md#register-transformers-on-middleware) — stream transformer mà `apply_to_output=True` dùng để che dữ liệu gửi dần
- Middleware API reference: `https://reference.langchain.com/python/langchain/middleware/`
- Testing agents: `https://docs.langchain.com/oss/python/langchain/test/`