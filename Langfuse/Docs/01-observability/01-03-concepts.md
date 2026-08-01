---
title: Observability — Concepts
doc_source: https://langfuse.com/docs/observability/data-model
accessed: 2026-07-31
version: v4
status: draft
related:
  - https://langfuse.com/docs/observability/overview
  - https://langfuse.com/docs/observability/features/observation-types
---

# Langfuse Observability — Mô hình dữ liệu

Langfuse là nền tảng observability mã nguồn mở, thiết kế riêng cho ứng dụng LLM. File này tập trung vào cách Langfuse tổ chức dữ liệu — ba tầng cốt lõi: observation, trace, session — và cơ chế thu thập dữ liệu phía sau.

---

## 1. Tổng quan

Ứng dụng LLM vốn không tất định (non-deterministic): cùng một prompt, hai lần gọi cho hai kết quả khác nhau. Debug mà không có observability thì gần như đoán mò.

Langfuse giải quyết bằng cách ghi lại **structured log** cho mỗi request: prompt gửi đi, response nhận về, token tiêu hao, độ trễ, các bước trung gian (gọi tool, truy xuất dữ liệu, xử lý logic). Tất cả được tổ chức thành **trace** — và trace chính là đơn vị trung tâm của toàn bộ hệ thống.

---

## 2. Ba tầng dữ liệu: Observation → Trace → Session

Langfuse tổ chức dữ liệu theo ba tầng lồng nhau, từ nhỏ tới lớn:

```
Session
  └── Trace
        └── Observation
        └── Observation
              └── Observation (lồng nhau)
  └── Trace
        └── Observation
```

Mỗi tầng trả lời một câu hỏi khác nhau:

- **Observation** — Bước này đang làm gì?
- **Trace** — Request này đã đi qua những bước nào?
- **Session** — Chuỗi tương tác này diễn ra như thế nào?

### 2.1. Observation — đơn vị nhỏ nhất

Observation là một bước xử lý trong ứng dụng, chẳng hạn một lần gọi LLM, truy xuất dữ liệu hoặc gọi tool. Các observation có thể **lồng nhau (nested)** để phản ánh đúng luồng thực thi.

Langfuse định nghĩa 10 observation type, mỗi loại mang ngữ nghĩa riêng:

| Type | Dùng cho |
|---|---|
| `event` | Sự kiện rời rạc, không có khoảng thời gian |
| `span` | Một đoạn xử lý có thời lượng (duration) |
| `generation` | Lệnh gọi LLM — ghi kèm prompt, token usage, chi phí |
| `agent` | Agent điều phối luồng ứng dụng, quyết định gọi tool nào |
| `tool` | Lệnh gọi công cụ bên ngoài (API thời tiết, database...) |
| `chain` | Liên kết giữa các bước — truyền context từ retriever sang LLM |
| `retriever` | Truy xuất dữ liệu (vector store, database) |
| `evaluator` | Hàm đánh giá chất lượng output của LLM |
| `embedding` | Gọi LLM để tạo embedding — ghi model, token, chi phí |
| `guardrail` | Kiểm tra nội dung nguy hại hoặc jailbreak |

Khi tích hợp với framework (LangChain, LlamaIndex...), type được gán tự động — ví dụ method đánh dấu `@tool` sẽ thành observation type `tool`. Khi dùng SDK trực tiếp, ta gán bằng tham số `as_type` (Python) hoặc `asType` (TypeScript).

**!Note:** `event` và `span` là hai type nền tảng. `event` không có duration — chỉ ghi lại "chuyện này đã xảy ra". `span` có duration — ghi lại "chuyện này chạy mất bao lâu". Các type còn lại (`generation`, `agent`, `tool`...) về bản chất là span được gắn thêm ngữ nghĩa chuyên biệt.

### 2.2. Trace — nhóm các observation thành một request

Trace đại diện cho **một request hoàn chỉnh** — ví dụ một lượt chat từ câu hỏi người dùng đến câu trả lời cuối cùng. Mọi observation thuộc cùng request đều chia sẻ chung một `trace_id`.

Về lưu trữ, Langfuse chỉ có **một bảng observations**. Mỗi observation ngoài dữ liệu của chính nó (`id`, `type`, `latency`...) còn chứa cả thông tin của trace (`trace_id`, `trace_name`, `user_id`, `session_id`). Nhờ đó, việc truy vấn và thống kê không cần join nhiều bảng.


Ví dụ cụ thể — bảng observations trông thế này:

```
| id    | type       | name         | latency | trace_id | trace_name    | user_id | session_id |
|-------|------------|--------------|---------|----------|---------------|---------|------------|
| obs-1 | span       | handle-chat  | 3.1s    | abc123   | chat-request  | u-42    | s-7        |
| obs-2 | span       | retrieval    | 0.4s    | abc123   | chat-request  | u-42    | s-7        |
| obs-3 | generation | llm-call     | 2.6s    | abc123   | chat-request  | u-42    | s-7        |
| obs-4 | span       | build-report | 1.2s    | def789   | export-report | u-17    | s-9        |
```

Ba observation đầu (`obs-1` → `obs-3`) thuộc cùng trace `abc123` — tức cùng một lượt chat. Các cột `user_id`, `session_id` lặp lại trên mỗi dòng, đó chính là bản sao trace-level attribute.

### 2.3. Session — nhóm các trace thành chuỗi tương tác

Session gom nhiều trace lại khi chúng thuộc cùng một chuỗi tương tác. Ví dụ điển hình: một thread chat nhiều lượt — mỗi lượt là một trace, cả thread là một session.

Session là **tùy chọn** (optional). Ứng dụng single-turn (hỏi một câu, trả lời xong là xong) không cần session. Chỉ nên bật khi ứng dụng có multi-turn conversation hoặc workflow nhiều bước.

---

## 3. Enrichment — gắn attribute bổ sung

Sau khi có trace và observation, ta gắn thêm các attribute để phục vụ lọc, phân nhóm, phân tích:

| Attribute | Mục đích |
|---|---|
| Environments | Tách dữ liệu theo môi trường: `production`, `staging`, `development` |
| Tags | Nhãn linh hoạt — phân loại theo feature, API endpoint, workflow |
| User | Gắn end-user nào đã trigger trace |
| Metadata | Key-value tùy ý cho thông tin đặc thù |
| Releases & Versions | Theo dõi phiên bản ứng dụng và thay đổi component |

Đây không phải dữ liệu cấu trúc bắt buộc — ta chọn gắn attribute nào tùy nhu cầu phân tích.

---

## 4. Cơ chế thu thập dữ liệu

### 4.1. Nền tảng OpenTelemetry

Langfuse xây trên [OpenTelemetry](https://opentelemetry.io/) — chuẩn mở cho telemetry data. Hệ quả thực tế: ta không bị vendor lock-in vào SDK riêng của Langfuse. Có thể gửi trace đồng thời tới nhiều đích — Langfuse cho LLM observability, Datadog cho infrastructure monitoring — mà không phải instrument lại.

Thuật ngữ liên quan: **instrumentation** là quá trình thêm code vào ứng dụng để ghi lại hoạt động. Sau khi instrument, Langfuse (qua OpenTelemetry) tự động capture các sự kiện và tổ chức thành trace/observation.

### 4.2. Xử lý bất đồng bộ

Langfuse không gửi trace ngay lập tức khi tạo — làm vậy sẽ block ứng dụng. Thay vào đó, SDK gom trace thành batch ở local rồi gửi nền (background), không ảnh hưởng tới response time.

Cơ chế này hoạt động tốt với **ứng dụng chạy dài** (web server, API service) vì background exporter có đủ thời gian flush.

Với **ứng dụng chạy ngắn** (script xử lý xong rồi tắt), có rủi ro process tắt trước khi batch kịp gửi. Giải pháp: gọi `flush()` trước khi exit.

**!Note:** Quên gọi `flush()` trong ứng dụng short-lived thì trace mất mà không có lỗi, không có cảnh báo — ứng dụng vẫn chạy đúng, chỉ là Langfuse không nhận được dữ liệu. Đây là lỗi im lặng (silent failure) cần lưu tâm khi triển khai.

---

## 5. Cách gán observation type trong code

Hai cách phổ biến:

**Python** — dùng decorator `@observe` hoặc context manager:

```python
from langfuse import observe

@observe(as_type="agent")                    # gán type ngay tại decorator
def run_agent_workflow(query):
    return process_with_tools(query)

@observe(as_type="tool")                     # tool call cũng tương tự
def call_weather_api(location):
    return weather_service.get_weather(location)
```

Yêu cầu Python SDK `>= 3.3.1`.

**TypeScript** — dùng `startActiveObservation` hoặc wrapper `observe`:

```typescript
import { startActiveObservation } from "@langfuse/tracing";

await startActiveObservation(
  "agent-workflow",
  async (obs) => {
    obs.update({ input: { query } });       # ghi input
    const result = await processWithTools(query);
    obs.update({ output: result });          # ghi output
  },
  { asType: "agent" }                       # gán type qua option
);
```

Yêu cầu TypeScript SDK `>= 4.0.0`.

Observation có thể lồng nhau: bên trong một `agent` observation, ta tạo thêm `tool` observation, `generation` observation — cấu trúc cây phản ánh đúng luồng thực thi.

---

## Tham chiếu chéo

| Chủ đề | Trang |
|---|---|
| Hướng dẫn bắt đầu | [Get Started](https://langfuse.com/docs/observability/get-started) |
| Sessions chi tiết | [Sessions](https://langfuse.com/docs/observability/features/sessions) |
| Token & Cost Tracking | [Token & Cost](https://langfuse.com/docs/observability/features/token-and-cost-tracking) |
| Queuing & Batching | [Queuing/Batching](https://langfuse.com/docs/observability/features/queuing-batching) |
| OpenTelemetry integration | [OTel Guide](https://langfuse.com/integrations/native/opentelemetry) |
| Làm việc với bảng observations (v4) | [Observations table](https://langfuse.com/faq/all/explore-observations-in-v4) |