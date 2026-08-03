---
title: Observability — Get Started with Tracing
doc_source: https://langfuse.com/docs/observability/get-started
accessed: 2026-07-31
version: v4
status: draft
related:
  - ./langfuse-data-model.md
---

# Bắt đầu với Tracing trong Langfuse

> Trang tài liệu này chỉ lo một việc: đưa **trace** đầu tiên vào Langfuse — nền tảng observability (giám sát vận hành) cho ứng dụng LLM.
> Nó không định nghĩa *trace* là gì; phần đó thuộc trang Core Concepts (data-model), mục này chỉ trỏ sang.

---

## 1. Tổng quan

Langfuse là nền tảng observability dành riêng cho ứng dụng LLM. Trang này hướng dẫn ghi lại lần chạy đầu tiên của ứng dụng thành một *trace* để xem lại trên giao diện Langfuse. Một trace ghi lại prompt, model và output của mỗi lần gọi model.

Điểm chung của mọi cách cài đặt: code tracing chạy nền, gom dữ liệu mỗi lần gọi model rồi gửi về project Langfuse — không thay đổi cách viết logic gốc. Đây là đặc điểm phân biệt Langfuse với việc tự ghi log thủ công: ta chỉ bọc hoặc gắn thêm, không viết lại luồng xử lý.

Con đường ngắn nhất là bọc OpenAI SDK (Python):

```python
from langfuse.openai import openai              # bản OpenAI đã được Langfuse bọc sẵn

completion = openai.chat.completions.create(     # gọi model y hệt OpenAI SDK thường
    name="test-chat",                            # tên hiển thị của trace trên Langfuse
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a very accurate calculator. You output only the result of the calculation."},
        {"role": "user", "content": "1 + 1 = "}],
    metadata={"someMetadataKey": "someValue"},   # metadata tùy chọn, đính kèm vào trace
)
```

**Kết quả quan sát được.** Một trace tên `test-chat` xuất hiện trên giao diện Langfuse, ghi lại prompt, model và output. Trang tài liệu minh họa bằng ảnh chụp giao diện, không in output ra console — nên phần này mô tả kết quả trên UI, không dựng ra log giả.

---

## 2. Hai hướng cài đặt

Trang tài liệu tách hai hướng: để coding agent tự dựng, hoặc tự làm thủ công.

### 2.1 Hướng agentic — để coding agent tự dựng

Cài **Langfuse Agent Skill** để agent (coding agent) tự thêm tracing theo best practice. Ba cách cài: bảo agent tự cài từ repo `github.com/langfuse/skills`; dùng Cursor Plugin (đã kèm sẵn skill); hoặc cài qua npm bằng CLI `skills` (`npx skills add langfuse/skills --skill "langfuse"`, thêm `--agent "<agent-id>"` nếu nhắm một agent cụ thể). Sau khi cài, ra lệnh cho agent: *"Add tracing to this application with Langfuse following best practices."*

### 2.2 Hướng thủ công — ba bước

Ba bước dưới đây đúng cho mọi công nghệ; chỉ bước 2 khác nhau tùy con đường tích hợp.

**Bước 1 — Lấy API key.** Tạo tài khoản trên `cloud.langfuse.com`, hoặc tự vận hành (self-host) Langfuse trên hạ tầng riêng nếu cần giữ dữ liệu nội bộ. Sau đó vào project settings tạo cặp API credentials gồm một khóa công khai và một khóa bí mật — đây là thứ để ứng dụng nhận diện đúng project khi gửi dữ liệu về.

**Bước 2 — Gắn tracing.** Chọn một con đường tích hợp hợp với công nghệ đang dùng (bọc client, callback handler, telemetry tự phát, SDK gốc, hoặc OpenTelemetry), rồi thêm ít dòng code để bắt đầu ghi trace. Đây là bước duy nhất khác nhau giữa các công nghệ; mục 3 khai triển bước này.

**Bước 3 — Xem trace.** Chạy ứng dụng như bình thường rồi mở giao diện Langfuse. Mỗi lần chạy hiện thành một trace kèm prompt, model và output để xem lại.

---

## 3. Các framework tích hợp



- **Bọc client (drop-in wrapper).** Thay client OpenAI bằng bản bọc của Langfuse; client bọc hành xử như thường nhưng tự ghi lại mỗi lần gọi model, gần như không đổi code. Áp cho OpenAI SDK, cả Python và JS/TS.
- **Callback handler.** Gắn một handler vào chain LangChain; mỗi khi chain hoặc LLM chạy, LangChain phát sự kiện, handler biến sự kiện thành trace. Áp cho LangChain, cả Python và JS/TS.
- **Telemetry tự phát.** Vercel AI SDK tự phát telemetry qua OpenTelemetry; Langfuse chỉ cần đăng ký integration một lần lúc khởi động.
- **Instrument thủ công (SDK gốc).** Tự đánh dấu từng bước xử lý (*span*) và từng lần gọi model (*generation*); linh hoạt nhất, dùng được với mọi framework. Áp cho Python SDK và JS/TS SDK.
- **OpenTelemetry gốc.** Nếu ứng dụng đã phát OTEL span sẵn, gửi thẳng OTLP về Langfuse — điểm vào cho setup OTEL tùy biến và ngôn ngữ ngoài các SDK của Langfuse.
- **Framework khác có sẵn tích hợp.** LlamaIndex, CrewAI, Ollama, LiteLLM, AutoGen, Google ADK — mỗi cái có trang riêng.

**Bảng tổng hợp các framework tích hợp**

| Con đường | Ngôn ngữ | Cơ chế | Khởi tạo OTEL | Trang tài liệu |
|---|---|---|---|---|
| OpenAI SDK | Python | Bọc client | Không | https://langfuse.com/integrations/model-providers/openai-py |
| OpenAI SDK | JS/TS | Bọc client | Có | https://langfuse.com/integrations/model-providers/openai-js |
| LangChain | Python & JS/TS | Callback handler | Chỉ JS/TS | https://langfuse.com/integrations/frameworks/langchain |
| Vercel AI SDK | JS/TS | Telemetry tự phát | Có | https://langfuse.com/integrations/frameworks/vercel-ai-sdk |
| SDK gốc | Python | Instrument thủ công | Không | https://langfuse.com/docs/sdk/python/sdk-v3 |
| SDK gốc | JS/TS | Instrument thủ công | Có | https://langfuse.com/docs/sdk/typescript/guide |
| OpenTelemetry gốc | Bất kỳ | Gửi thẳng OTLP | (đã có sẵn) | https://langfuse.com/integrations/native/opentelemetry |

---

## 5. Nên chọn framework nào

- Đang dùng **OpenAI SDK** và muốn đổi ít nhất → con đường bọc client.
- Đang dùng **LangChain** → callback handler.
- Đang dùng **Vercel AI SDK** → đăng ký integration telemetry.
- Cần **kiểm soát chi tiết** từng span/generation, hoặc dùng framework không có tích hợp sẵn → SDK gốc.
- Ứng dụng **đã phát OTEL span** → OpenTelemetry gốc.
- Dùng framework có sẵn tích hợp (LlamaIndex, CrewAI, Ollama, LiteLLM, AutoGen, Google ADK) → trang tích hợp riêng.

---

## Tham chiếu chéo

- Observability Overview — trace là gì và vì sao cần: `/docs/observability/overview`
- Core Concepts (data model) — cấu trúc trace/observation, cách xử lý nền, khi nào gọi `flush()`: `/docs/observability/data-model`
- Best practices — một trace tốt trông như thế nào: `/docs/observability/best-practices`
- Tài liệu SDK đầy đủ theo từng con đường: xem cột "Trang tài liệu" ở bảng mục 4.