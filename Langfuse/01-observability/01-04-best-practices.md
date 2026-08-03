---
title: Observability — Best Practices
doc_source: https://langfuse.com/docs/observability/best-practices
accessed: 2026-07-31
version: v4
status: draft
related:
  - ./langfuse-observability-concepts.md
---

# Langfuse Observability — Best Practices

Trace xuất hiện trên Langfuse rồi, nhưng cấu trúc có tốt không thì là chuyện khác. Trang này **hệ thống hoá** các quy tắc thiết kế trace sao cho debug nhanh, evaluator chạy đúng, dashboard không vỡ khi ứng dụng thay đổi.

Mạch trình bày đi theo đúng thứ tự ta phải ra quyết định khi instrument: xác định phạm vi trace → kiểm tra cấu trúc cây → đặt tên → thiết kế input/output → gắn attribute bổ sung.

---

## 1. Phạm vi của một trace

Một trace đại diện cho **một đơn vị công việc khép kín**. Ba ví dụ điển hình:

- Một lượt chatbot: người dùng gửi câu hỏi → ứng dụng truy xuất context → gọi LLM → trả response.
- Một lượt agent: agent nhận task → suy luận → gọi tool → trả kết quả.
- Một pipeline: tài liệu đi vào → chunk → embedding → lưu trữ.

Nếu nhiều đơn vị nối tiếp nhau (multi-turn chat, nhiều agent chạy nối tiếp cho một báo cáo), mỗi đơn vị vẫn là một trace riêng — dùng session để gom chúng lại. Với chatbot nghĩa là: mỗi lượt là một trace, cả cuộc hội thoại là một session. Lý do: ta không biết trước cuộc hội thoại kết thúc khi nào, và trace nhỏ thì dễ duyệt hơn trong session view.

Quy tắc này không chỉ giúp giao diện gọn gàng — cấu trúc trace ảnh hưởng trực tiếp tới khả năng vận hành: LLM-as-a-judge evaluator nhắm observation theo tên và type, dashboard lọc metric theo observation name, dataset experiment so sánh input/output giữa các lần chạy. Trace cấu trúc sai thì các tính năng này vỡ im lặng.

---

## 2. Kiểm tra cấu trúc trace tree
<div align="center">
    <img src="../../assets/image/image.png" width="800" align="center">
</div>

Khi mở một trace trên UI, ta thấy trace tree — cây phân cấp các observation. Ba điều cần kiểm tra:

### 2.1. Các bước có đúng type không

Mỗi observation phải mang đúng type phản ánh bản chất của nó. Lệnh gọi LLM phải là `generation` (vì `generation` mới ghi được token usage, chi phí, thông tin model). Tool call phải là `tool` (để evaluator có thể lọc riêng). Framework integration thường gán type tự động; nếu instrument thủ công thì gán qua `as_type` (Python) hoặc `asType` (TypeScript).

Nhìn vào ví dụ: các bước `ai.streamText.doStream` hiện rõ token và chi phí (`1,053 → 81`, $0.000974) — dấu hiệu chúng được gán đúng type `generation`. Còn `getLangfuseOverview` và `searchLangfuseDocs` mang icon riêng, được nhận là `tool`. Nếu một lệnh gọi LLM lại không hiện token/chi phí, gần như chắc chắn nó bị gán sai type. Framework integration thường gán tự động; instrument thủ công thì gán qua `as_type` (Python) hoặc `asType` (TypeScript).


### 2.2. Cây có lồng đúng không

Tool call phải nằm **bên trong** agent hoặc span đang điều phối bước đó, ngang hàng với generation đã yêu cầu nó — không phải trôi nổi ở gốc trace. Cây lồng đúng thì nhìn vào biết ngay bước nào thuộc bước nào. Framework integration thường xử lý đúng; instrument thủ công thì cần chú ý nesting.

Trong ví dụ, `searchLangfuseDocs` (5.13s) nằm lồng dưới `ai.streamText`, ngay cạnh các `ai.streamText.doStream` — đúng vị trí, vì chính generation đó đã kích hoạt tool. Agent graph bên phải xác nhận luồng này: `get-langfuse-prompt` → `ai.streamText` → phân nhánh sang `getLangfuseOverview` và `searchLangfuseDocs` rồi quay lại `ai.streamText.doStream`. Nếu tool call trôi lên gốc trace, cây sẽ không cho biết bước nào gọi nó. Framework integration thường xử lý đúng; instrument thủ công thì cần chú ý nesting.


### 2.3. Có observation thừa không

HTTP span, database query, framework internal — những thứ này thường chỉ tạo nhiễu mà không giúp hiểu ứng dụng làm gì. Nếu trace tree bị "rác" bởi các observation kiểu này, lọc chúng ra. Tài liệu hướng dẫn lọc tại [unwanted-http-database-spans](https://langfuse.com/faq/all/unwanted-http-database-spans).

Ví dụ trace `QA-Chatbot` khá sạch: mọi node trên cây đều là bước có nghĩa nghiệp vụ (nhận message, lấy prompt, tạo MCP client, gọi LLM, gọi tool). Không có span HTTP hay truy vấn database lẫn vào. Đây là trạng thái ta muốn hướng tới. Nếu trace tree bị "rác" bởi các observation kỹ thuật kiểu đó, lọc chúng ra. Tài liệu hướng dẫn lọc tại [unwanted-http-database-spans](https://langfuse.com/faq/all/unwanted-http-database-spans).

---

## 3. Quy tắc đặt tên

Observation name và trace name xuất hiện ở nhiều nơi: cấu hình evaluator, truy vấn dashboard, bộ lọc trên bảng tracing. Vì vậy, tên phải được xem như **API** — đổi tên thì evaluator, dashboard, saved filter đang nhắm tên cũ sẽ ngừng match mà không báo lỗi.

Ba quy tắc:

**Dùng động từ mở đầu, mô tả hành động.** `classify-intent`, `retrieve-context`, `generate-response`, `summarize-results`. Trace tree đọc lên như mô tả ứng dụng đã làm gì, và lọc theo bước cụ thể cũng dễ hơn.

**Không nhồi giá trị động vào tên.** Dùng `process-order`, không dùng `process-order-8945` hay `generate-response-retry-2`. Tên xác định loại thao tác, không xác định một lần thực thi cụ thể. Giá trị thay đổi theo từng request thuộc về metadata. Đây cũng là quy tắc low-cardinality mà OpenTelemetry khuyến nghị cho span name.

**Không đặt tên theo model.** `gpt-4o`, `claude-sonnet` — đặt thế thì đổi model là vỡ hết filter, evaluator, dashboard. Model đã là attribute riêng trên `generation` observation, dùng attribute đó thay vì nhồi vào tên.

---

## 4. Thiết kế input và output

Mỗi observation nên có input và/hoặc output. Observation không có cả hai thì tự hỏi: observation đó có cần tồn tại không.

**Root observation** cần chăm chút nhất, vì trace-level input/output được suy từ nó. Chúng hiện trên bảng tracing, được evaluator đọc, được so sánh giữa các lần chạy trong dataset experiment. Đặt input/output sao cho người review nhìn qua là hiểu — với chatbot: input là câu hỏi người dùng, output là câu trả lời. Không phải raw JSON blob chứa function arguments. Payload thô cần cho debug thì đẩy vào metadata.

Với `generation` observation cụ thể, input/output hiển thị tốt nhất khi theo định dạng OpenAI chuẩn: mảng message, mỗi phần tử có `role` và `content`. Tool call hiển thị thành card khi nằm trong mảng `tool_calls` của assistant message, với `arguments` là JSON-encoded string (ví dụ `"{\"location\": \"Paris\"}"`). Nếu input/output hiện raw JSON thay vì conversation format, kiểm tra lại cấu trúc dữ liệu gửi vào.

**!Note:** Input/output của trace trống mà không rõ lý do — tham khảo [why are the input and output of my trace empty?](https://langfuse.com/faq/all/empty-trace-input-and-output). Đây là lỗi phổ biến khi mới instrument.

---

## 5. Gắn attribute bổ sung

Sau khi trace có cấu trúc đúng, tên ổn định, input/output rõ ràng — bước tiếp theo là gắn thêm attribute để phục vụ lọc, phân tích, scoring.

### 5.1. Metadata — key-value linh hoạt

Metadata là nơi chứa thông tin hữu ích nhưng không thuộc về tên hay input/output. Các trường hợp thực tế:

- **Evaluation context:** Ground truth, expected behavior — những thứ LLM-as-a-judge evaluator cần nhưng không phải input/output thực sự. Evaluator có thể map biến từ metadata field.
- **Request context:** Internal request ID, API route, app version, feature flag đang active — để liên kết trace với hệ thống khác và lọc theo rollout.
- **Retrieval context:** Data source, số chunk truy xuất, index nào — hữu ích khi debug tại sao retrieval trả kết quả kém.
- **Raw payload:** Request/response object đầy đủ, quá nặng cho input/output nhưng thỉnh thoảng cần khi debug.

Metadata hỗ trợ lọc theo key trên UI Langfuse.

### 5.2. Model, token, chi phí trên generation

Để phân tích chi phí LLM theo model, theo user, theo feature — cần ba thứ trên mỗi `generation` observation:

| Attribute | Vai trò |
|---|---|
| Model name | Langfuse dùng để tra bảng giá (model pricing table). Tên không khớp → không tính được chi phí tự động |
| Usage details | Input tokens, output tokens, cached tokens (tùy chọn). Là nguồn dữ liệu cho token usage view trên dashboard |
| Cost details | Tùy chọn. Ghi đè pricing tự động khi có thoả thuận giá riêng |

Framework integration thường capture tự động. Instrument thủ công thì xem [token and cost tracking docs](https://langfuse.com/docs/observability/features/token-and-cost-tracking).

### 5.3. Tags — phân loại theo chiều nghiệp vụ

Tags cho phép lọc và breakdown metric theo các chiều mà nghiệp vụ quan tâm: "latency giữa user `web` và `api` khác nhau thế nào?".

Đặc điểm quan trọng: tags **bất biến** (immutable), phải gán lúc tạo observation. Phù hợp cho thông tin biết trước (nguồn request, feature nào). Không phù hợp cho thông tin xác định sau — ví dụ kết quả evaluation. Trường hợp đó dùng [scores](https://langfuse.com/docs/evaluation/overview).

### 5.4. Liên kết prompt version

Nếu quản lý prompt trên Langfuse (Prompt Management), ta có thể liên kết prompt version với generation. Khi thay đổi prompt và muốn so sánh metric giữa các version, liên kết này cho phép truy vết chính xác version nào đã chạy cho trace nào.

### 5.5. Environment

Gán `production`, `staging`, `development` để trace test không lẫn vào dashboard và evaluator của production.

### 5.6. User ID

Gắn user ID để mở khoá per-user view: user nào tốn chi phí nhiều nhất, chất lượng output khác nhau thế nào giữa các user, pattern sử dụng của một user cụ thể ra sao.

### 5.7. Session ID

Dùng khi ứng dụng có nhiều trace thuộc về cùng một chuỗi tương tác: multi-turn chatbot, nhiều agent cộng tác cho một output cuối, workflow nhiều request có human-in-the-loop giữa các bước. Ứng dụng single-request không cần session.

---

## Tham chiếu chéo

| Chủ đề | Trang |
|---|---|
| Mô hình dữ liệu (Observation, Trace, Session) | [Concepts](https://langfuse.com/docs/observability/data-model) |
| Observation types | [Observation Types](https://langfuse.com/docs/observability/features/observation-types) |
| LLM-as-a-judge evaluator | [LLM-as-a-Judge](https://langfuse.com/docs/evaluation/evaluation-methods/llm-as-a-judge) |
| Dataset experiments | [Experiments](https://langfuse.com/docs/evaluation/experiments) |
| Token & Cost tracking | [Token & Cost](https://langfuse.com/docs/observability/features/token-and-cost-tracking) |
| Prompt Management | [Prompt Management](https://langfuse.com/docs/prompt-management) |
| Lọc observation thừa | [Unwanted spans](https://langfuse.com/faq/all/unwanted-http-database-spans) |