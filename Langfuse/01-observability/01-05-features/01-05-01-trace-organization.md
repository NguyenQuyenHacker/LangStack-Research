---
title: Observability — Features — Tổ chức & định danh trace
doc_source:
  - https://langfuse.com/docs/observability/features/sessions
  - https://langfuse.com/docs/observability/features/users
  - https://langfuse.com/docs/observability/features/trace-ids-and-distributed-tracing
accessed: 2026-08-01
version: v4
status: draft
lab:
related:
  - ./01-05-00-index.md
---

# Tổ chức & định danh trace

Nhóm ba tính năng quy định cách trace data được gán khóa định danh và gom nhóm, để về sau tra cứu và phân tích theo phiên hội thoại, theo người dùng, hoặc theo một request chạy xuyên nhiều service.

## Tổng quan

Điểm chung khiến ba tính năng này được gom lại: mỗi cái là một **khóa định danh gắn lên trace data** phục vụ việc tổ chức và truy xuất, không phải nội dung của bản thân observation. `Sessions` gom nhiều trace của một chuỗi hội thoại vào một phiên để xem lại. `User Tracking` gắn trace vào một người dùng để tổng hợp metric theo người. `Trace IDs & Distributed Tracing` định danh một trace và cho phép gộp operation của nhiều service vào cùng một trace, hoặc liên kết trace với ID của hệ thống ngoài.

Một phân biệt cần nắm: Sessions gom *nhiều trace* lại với nhau; Trace IDs gom *operation của nhiều service vào một trace duy nhất* — hai hướng gom ngược chiều nhau.

## 1. Sessions

**Khái niệm.** Cơ chế gom nhiều observation nằm rải trên nhiều trace — thuộc cùng một chuỗi tương tác (hội thoại, thread) — vào một session, và xem lại toàn bộ chuỗi dưới dạng session replay. Cơ chế vận hành dựa trên Attribute Propagation: gán và lan truyền thuộc tính `sessionId` qua các observation bằng `propagate_attributes`. Mọi observation mang cùng `sessionId`, kể cả trace bao ngoài, được gom về một session. `sessionId` là chuỗi US-ASCII dài dưới 200 ký tự; vượt 200 ký tự thì bị drop. Giá trị không hợp lệ bị bỏ kèm một warning.

**Vai trò.** Debug và phân tích ứng dụng hội thoại nhiều lượt, nơi mỗi lượt hỏi-đáp là một trace riêng nhưng cần nhìn như một mạch liền.

**Ví dụ.** Một chatbot tạo một trace cho mỗi lượt hỏi-đáp; propagate `sessionId="chat-session-123"` để 20 lượt của cùng một cuộc hội thoại gom về một session, xem lại toàn bộ để tìm chính lượt nào model trả lời sai.

**!Note:** `propagate_attributes` phải được gọi **sớm** trong trace. Nếu gọi muộn, những observation đã tạo trước đó không mang `sessionId` → chúng bị loại khỏi metric cấp session. Code chạy trơn tru, không báo lỗi, nhưng số liệu session thiếu chính xác một cách âm thầm.

Chi tiết cấu hình: https://langfuse.com/docs/observability/features/sessions

## 2. User Tracking

**Khái niệm.** Cơ chế gắn định danh người dùng lên trace data để Langfuse tổng hợp metric theo từng người: chi phí LLM, lượng token, số trace, feedback. Vận hành giống Sessions — propagate thuộc tính `userId` qua observation bằng `propagate_attributes`, chịu cùng ràng buộc (string ≤ 200 ký tự, gọi sớm, giá trị sai bị bỏ kèm warning). `userId` có thể là username, email, hay bất kỳ định danh duy nhất nào; đây là thuộc tính optional. UI cung cấp Users view gồm danh sách toàn bộ user và màn chi tiết từng user, deep link theo URL dạng `.../project/{projectId}/users/{userId}`.

**Vai trò.** Phân tách chi phí, khối lượng dùng và feedback về từng người dùng cuối; segment người dùng theo token, số trace, hoặc feedback.

**Ví dụ.** Một ứng dụng nhiều khách hàng dùng chung một backend; propagate `userId="user_12345"` để biết mỗi khách tiêu bao nhiêu token và chi phí trong kỳ, phát hiện một user chiếm phần lớn chi phí LLM.

Chi tiết cấu hình: https://langfuse.com/docs/observability/features/users

## 3. Trace IDs & Distributed Tracing

**Khái niệm.** Trace ID là định danh duy nhất đi theo một request suốt vòng đời của nó qua hệ thống; trong hệ phân tán, nó cho phép correlate các operation ở nhiều service và dựng lại toàn bộ request lifecycle. Mặc định Langfuse cấp trace ID ngẫu nhiên 32 hexchar và observation ID 16 hexchar. Có ba thao tác can thiệp: (1) sinh trace ID **deterministic** từ một seed bằng `create_trace_id(seed=...)` — cùng seed cho ra cùng ID, dùng để map ID của hệ ngoài (ví dụ support ticket) sang trace Langfuse; (2) đặt **custom trace ID** khi bọc code, qua `trace_context={"trace_id": ...}` (phải đúng 32 hex chars) hoặc qua decorator với `langfuse_trace_id=...`; (3) truy xuất ID hiện hành bằng `get_current_trace_id()` và `get_current_observation_id()`. Khi khởi tạo một trace mới với traceId định trước, phải cấp thêm một parent span ID 16-hexchar hợp lệ bất kỳ — giá trị của nó không quan trọng, chỉ dùng cho việc kế thừa trace ID của observation được tạo.

**Vai trò.** Gộp các operation nằm rải ở nhiều service vào một trace duy nhất, và liên kết trace Langfuse với ID của hệ thống ngoài để về sau tra cứu hoặc chấm điểm đúng trace đó.

**Ví dụ.** Một request đi qua API gateway → service RAG → service gọi LLM ở ba tiến trình khác nhau; sinh trace ID deterministic từ seed `req_12345` để cả ba service ghi observation vào cùng một trace, và về sau dùng lại chính seed đó để chấm điểm đúng trace mà không cần lưu trace ID.

**!Note:** Đặt `parentSpanContext` (hay parent span id) sẽ **tách** span vừa tạo khỏi active span context hiện hành — nó không còn kế thừa từ span đang active. Nếu không lường trước, span mới bị detach âm thầm khỏi cây trace hiện tại; trace vẫn được ghi nhưng cấu trúc phân cấp không như mong đợi.

Chi tiết cấu hình: https://langfuse.com/docs/observability/features/trace-ids-and-distributed-tracing

## Tham chiếu chéo

- Sessions và User Tracking dùng chung cơ chế Attribute Propagation (`propagate_attributes`). Ràng buộc cắt ngang cho cả hai: giá trị phải là string ≤ 200 ký tự và phải propagate sớm trong trace; gọi muộn thì các observation tạo trước không mang thuộc tính, kéo theo metric cấp session và cấp user cùng thiếu chính xác mà không có lỗi phát ra.
- Chọn đúng hướng gom: cần gom **nhiều trace** của một chuỗi hội thoại → Sessions; cần gom **operation nhiều service vào một trace** → Trace IDs & Distributed Tracing (nêu tại mục Related Resources của docs Sessions).
- Index nhóm feature: [./01-05-00-index.md](./01-05-00-index.md)