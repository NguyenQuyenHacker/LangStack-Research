---
title: Observability hooks (cơ chế LangChain)
doc_source: https://docs.langchain.com/oss/python/langchain/observability
accessed: 2026-07-28
lc_version: unknown
status: draft
lab:
related:
  - ../03-harness/03-02-tools.md
---

# Observability — bật tracing qua LangSmith

> Trang này chỉ trả lời một việc: làm sao thấy được agent đã chạy những gì bên trong (gọi tool nào, sinh prompt gì, quyết định ra sao). LangChain không có cơ chế quan sát riêng — nó cắm thẳng vào **LangSmith**, một nền tảng riêng để ghi lại, gỡ lỗi, chấm điểm và theo dõi ứng dụng LLM.
> Cơ chế đầy đủ của LangSmith (trace là gì, đọc trace ra sao, chấm điểm thế nào) nằm ở cây tài liệu `/langsmith/...` — **một nguồn khác**, không thuộc trang này.

> **Về tên file.** Frontmatter ghi "Observability hooks" nhưng trang gốc không nói về *hook*. Nội dung thực tế là bật tracing qua LangSmith. Tên "hooks" nên xem lại khi audit — có thể nhầm với cơ chế `hook` của middleware (`03-05`).

---

## 1. Tổng quan

Agent dựng bằng `create_agent` **tự động** hỗ trợ tracing qua LangSmith. Không phải viết thêm dòng code nào — chỉ cần bật đúng biến môi trường, rồi chạy agent như bình thường.

*Trace* là bản ghi từng bước agent chạy: từ input đầu tiên của người dùng đến câu trả lời cuối, gồm mọi lần gọi tool, mọi lần gọi model, mọi điểm ra quyết định. Bản ghi này dùng để gỡ lỗi, đánh giá hiệu năng trên nhiều input khác nhau, và theo dõi cách dùng khi đã lên production.

Khác với việc tự chèn `print()` khắp nơi: `print()` cho ra một dòng chữ phẳng, mất ngữ cảnh cha–con giữa các bước. Trace giữ nguyên cây thực thi — biết được lần gọi tool này nằm trong lượt suy nghĩ nào của model.

Cụ thể "trace trông ra sao", "cây thực thi hiển thị thế nào" thuộc về giao diện LangSmith, không nằm trong trang này.

---

## 2. Điều kiện cần

Hai thứ, đều thuộc LangSmith:

- Một tài khoản LangSmith (đăng ký miễn phí tại `smith.langchain.com`).
- Một API key của LangSmith (theo hướng dẫn *Create an API key* trong cây `/langsmith/...`).

---

## 3. Bật tracing

### Khái niệm

Tracing tắt mặc định. Bật bằng hai biến môi trường — một cờ bật/tắt, một khóa xác thực.

### Triển khai

```bash
export LANGSMITH_TRACING=true            # cờ bật tracing; không đặt = không ghi gì
export LANGSMITH_API_KEY=<your-api-key>  # khóa để gửi trace lên tài khoản của bạn
```

### Kết quả

Không in ra gì ở terminal. Sau khi bật, mọi lần chạy agent sẽ tự đẩy một trace lên LangSmith.

**!Note:** Đây là **lỗi im lặng** điển hình. Quên đặt `LANGSMITH_TRACING=true` thì agent vẫn chạy trơn tru, không lỗi, không cảnh báo — chỉ là **không có trace nào được ghi**. Người mới thường tưởng đã bật tracing rồi ngồi tìm trace trong LangSmith mà không thấy, vì thiếu đúng một biến môi trường.

---

## 4. Chạy agent (quickstart)

### Vai trò

Cho thấy đúng lời khẳng định "không cần code thêm": cùng một đoạn code agent bình thường, tracing xảy ra ở nền.

### Triển khai

```python
from langchain.agents import create_agent


def send_email(to: str, subject: str, body: str):
    """Send an email to a recipient."""
    # ... logic gửi email
    return f"Email sent to {to}"

def search_web(query: str):
    """Search the web for information."""
    # ... logic tìm kiếm web
    return f"Search results for: {query}"

agent = create_agent(
    model="gpt-5.5",                                    # tên model trong doc — xem !Note
    tools=[send_email, search_web],
    system_prompt="You are a helpful assistant that can send emails and search the web."
)

# Chạy agent — mọi bước được ghi trace tự động, không cần thêm gì
response = agent.invoke({
    "messages": [{"role": "user",
                  "content": "Search for the latest AI news and email a summary to john@example.com"}]
})
```

### Kết quả

Không có output ở console. Trace được ghi vào project mặc định tên `default` trong LangSmith. Muốn đổi tên project, xem mục 6.

**!Note:** `model="gpt-5.5"` là tên trong bản doc, chưa xác minh được đây là tên model có thật hay chỉ là chỗ giữ chỗ. Khi chạy thử phải thay bằng tên model bạn thực sự có quyền dùng.

---

## 5. Chỉ trace một phần

### Khái niệm

`tracing_context` là một context manager của LangSmith. Đặt một khối code bên trong `with ls.tracing_context(...)` để bật hoặc tắt tracing **chỉ cho riêng khối đó**, bất kể biến môi trường đang đặt gì.

### Vai trò

Không phải lúc nào cũng muốn trace tất cả. Cần bật cho một vài lần gọi cụ thể (để soi một bug), hoặc muốn tắt cho phần còn lại. `tracing_context` cho phép chọn từng khối thay vì bật/tắt toàn ứng dụng bằng biến môi trường.

### Áp dụng thực tế

Một agent gửi email chạy hàng nghìn lượt/ngày, không muốn ghi trace tất cả cho đỡ tốn. Nhưng có một khách hàng báo agent gửi sai nội dung. Bọc riêng lượt gọi tái hiện lỗi của khách đó vào `tracing_context(enabled=True)` để chỉ lấy đúng một trace cần soi, phần còn lại vẫn im.

### Triển khai

```python
import langsmith as ls

# Khối NÀY được trace — enabled=True ép bật, kể cả khi biến môi trường chưa đặt
with ls.tracing_context(enabled=True):
    agent.invoke({"messages": [{"role": "user",
                                "content": "Send a test email to alice@example.com"}]})

# Khối này KHÔNG được trace (khi LANGSMITH_TRACING chưa đặt)
agent.invoke({"messages": [{"role": "user", "content": "Send another email"}]})
```

### Kết quả

Chỉ lần `invoke` bên trong `with` sinh ra trace. Lần `invoke` bên ngoài không sinh trace (với điều kiện `LANGSMITH_TRACING` chưa được đặt).

**!Note:** `enabled=True` bên trong `tracing_context` **ép bật** cho riêng khối đó, độc lập với biến môi trường. Ngược lại, khối ngoài chỉ "không trace" **nếu** `LANGSMITH_TRACING` chưa đặt — nếu biến môi trường đã bật ở mục 3 thì khối ngoài vẫn được trace như thường. Nói cách khác `tracing_context` là cái đè lên, không phải cái duy nhất quyết định.

---

## 6. Ghi trace vào project riêng

### Khái niệm

Mặc định trace vào project tên `default`. LangSmith cho đặt tên project khác theo hai cách: đặt tĩnh cho cả ứng dụng, hoặc đặt động cho từng thao tác.

### Cách 1 — tĩnh, cho cả ứng dụng

```bash
export LANGSMITH_PROJECT=my-agent-project   # mọi trace của ứng dụng vào project này
```

### Cách 2 — động, cho từng thao tác

```python
import langsmith as ls

with ls.tracing_context(project_name="email-agent-test", enabled=True):   # đặt tên project cho riêng khối này
    response = agent.invoke({
        "messages": [{"role": "user", "content": "Send a welcome email"}]
    })
```

### Kết quả

Trace hiện dưới đúng tên project đã đặt trong LangSmith, thay vì gom hết vào `default`. Dùng để tách trace theo môi trường (dev/prod) hoặc theo từng thử nghiệm.

---

## 7. Gắn metadata và tags vào trace

### Khái niệm

*Tags* là các nhãn phẳng (chuỗi) để lọc trace. *Metadata* là cặp khóa–giá trị để đính thông tin ngữ cảnh (ai gọi, phiên nào, môi trường nào). Cả hai đính kèm vào trace để về sau lọc và tra trong LangSmith.

### Vai trò

Khi có hàng nghìn trace, cần lọc nhanh: "chỉ xem trace của user_123", "chỉ xem trace bản v1.0 trên production". Không gắn tags/metadata thì mọi trace nhìn như nhau, không lọc được.

### Áp dụng thực tế

Một trợ lý email chạy cho 5.000 người dùng. Khi user_123 khiếu nại, không có cách nào lọc ra đúng các lượt chạy của người đó giữa hàng vạn trace — trừ khi mỗi trace đã được gắn `metadata={"user_id": "user_123"}` ngay lúc gọi. Có metadata thì gõ một bộ lọc là ra.

### Triển khai — cách 1: qua `config` của `invoke`

```python
response = agent.invoke(
    {"messages": [{"role": "user", "content": "Send a welcome email"}]},
    config={
        "tags": ["production", "email-assistant", "v1.0"],   # nhãn phẳng để lọc
        "metadata": {                                        # thông tin ngữ cảnh kèm theo
            "user_id": "user_123",
            "session_id": "session_456",
            "environment": "production"
        }
    }
)
```

### Triển khai — cách 2: qua `tracing_context`

```python
with ls.tracing_context(
    project_name="email-agent-test",
    enabled=True,
    tags=["production", "email-assistant", "v1.0"],
    metadata={"user_id": "user_123", "session_id": "session_456", "environment": "production"}):
    response = agent.invoke(
        {"messages": [{"role": "user", "content": "Send a welcome email"}]}
    )
```

### Kết quả

Tags và metadata dính vào trace tương ứng trong LangSmith, dùng làm điều kiện lọc và tìm kiếm.

Trang này không nói cách hai đường (`config` và `tracing_context`) cư xử ra sao khi cùng đặt tags/metadata cho một lượt chạy — gộp lại hay đè lên nhau. Điểm này bỏ ngỏ, phải chạy thử mới rõ.

---

## Phạm vi trang này dừng ở đâu

Trang này chỉ dạy **bật tracing và gắn nhãn**. Mọi thứ về *đọc* và *khai thác* trace — cách trace hiển thị, cách gỡ lỗi từ trace, cách chấm điểm (evaluate), cách theo dõi (monitor) trên production — đều thuộc cây tài liệu LangSmith `/langsmith/observability`, là **nguồn khác**. Khi trích những phần đó vào vault, phải ghi rõ nguồn LangSmith chứ không phải trang LangChain OSS này.

---

## Tham chiếu chéo

- [03-02 Tools](../03-harness/03-02-tools.md) — trace ghi lại từng lần gọi tool; trang observability liên kết trực tiếp tới trang tools.
- LangSmith Observability (nguồn khác): `docs.langchain.com/langsmith/observability` — cơ chế trace đầy đủ, đọc/gỡ lỗi/chấm điểm/theo dõi.
- LangSmith — tạo API key (nguồn khác): `docs.langchain.com/langsmith/create-account-api-key`.