---
title: Observability — Features — Vận hành
doc_source:
  - https://langfuse.com/docs/observability/features/sampling
  - https://langfuse.com/docs/observability/features/log-levels
  - https://langfuse.com/docs/observability/features/queuing-batching
accessed: 2026-08-03
version: v4
status: draft
related:
  - ./01-05-00-index.md
---

# Vận hành

Nhóm ba tính năng điều khiển cách SDK thu thập, gắn nhãn mức độ, và truyền dữ liệu trace về Langfuse — các đòn bẩy ở tầng pipeline, không phải nội dung nghiệp vụ của từng observation.

## Tổng quan

Điểm chung khiến ba tính năng này được gom lại: cả ba tác động lên hành vi vận hành của SDK/pipeline — bao nhiêu dữ liệu được gửi, dữ liệu được đánh dấu mức quan trọng ra sao, và được đẩy về server theo cơ chế nào — chứ không đổi ý nghĩa nội dung mà một observation ghi lại. `Sampling` quyết định tỷ lệ trace được thu thập. `Event queuing/batching` quyết định cách SDK gom sự kiện thành lô và thời điểm gửi. `Log Levels` gắn nhãn mức độ lên observation để lọc và làm nổi lỗi/cảnh báo.

## 1. Sampling

**Khái niệm.** Cơ chế giới hạn khối lượng trace được thu thập, xử lý ở phía client. Cách vận hành: đặt sample rate qua biến môi trường `LANGFUSE_SAMPLE_RATE` hoặc tham số khởi tạo `sample_rate`/`sampleRate`, giá trị từ 0 đến 1. Mặc định là 1 (thu thập toàn bộ trace); giá trị 0.2 nghĩa là chỉ 20% số trace được thu. Quyết định lấy mẫu diễn ra ở **cấp trace**: nếu một trace được chọn, toàn bộ observation và score trong trace đó cũng được gửi; nếu không, không observation hay score nào của trace đó được gửi về Langfuse. Langfuse tôn trọng quyết định sampling của OpenTelemetry — có thể cấu hình sampler ngay trong OTEL SDK (ví dụ `TraceIdRatioBasedSampler`) thay cho tham số của Langfuse.

**Vai trò.** Kiểm soát chi phí và giảm nhiễu ở ứng dụng lưu lượng cao bằng cách chỉ giữ lại một phần trace.

**Ví dụ.** Một API phục vụ 1 triệu request/ngày; đặt `sample_rate=0.2` để chỉ 20% trace được gửi, cắt khối lượng dữ liệu và chi phí observability xuống còn một phần năm mà vẫn đủ mẫu theo dõi xu hướng lỗi.

**!Note:** Lấy mẫu ở cấp trace nghĩa là khi một trace bị loại, mọi observation và score bên trong nó biến mất khỏi Langfuse. Với `sample_rate` thấp, dữ liệu thiếu là do thiết kế; nhưng nếu quên rằng đã bật sampling, ta sẽ tưởng một số request "không chạy" trong khi thực ra chúng chỉ không được ghi. Code không báo gì.

Chi tiết cấu hình: https://langfuse.com/docs/observability/features/sampling

## 2. Event queuing/batching

**Khái niệm.** Cơ chế SDK gom (queue) các sự kiện trace ở nền và gửi theo lô (batch) để tiết kiệm số lần gọi API và thời gian mạng. Lô được xác định bởi kết hợp thời gian và kích thước (số sự kiện và dung lượng lô). Cách điều chỉnh: `flush_at`/`LANGFUSE_FLUSH_AT` (`flushAt` ở JS) đặt số sự kiện tối đa gom trước khi gửi; `flush_interval`/`LANGFUSE_FLUSH_INTERVAL` tính bằng giây (`flushInterval` ở JS) đặt thời gian tối đa chờ trước khi gửi một lô. Đặt `flushAt=1` để gửi ngay mỗi sự kiện, `flushInterval=1` để gửi mỗi giây. Gửi lô thủ công bằng `flush()`; khi thoát ứng dụng dùng `shutdown()` để chờ mọi request được đẩy đi trước khi tiến trình kết thúc. Khi gặp sự cố mạng, `flush` sẽ log lỗi và thử lại lô, không bao giờ ném exception.

**Vai trò.** Giảm số lần gọi API và độ trễ mạng lúc chạy; đồng thời cung cấp điểm chốt (`flush`/`shutdown`) để không mất dữ liệu ở môi trường vòng đời ngắn.

**Ví dụ.** Một AWS Lambda xử lý mỗi request rồi đóng băng runtime ngay sau đó; gọi `langfuse.flush()` (hoặc `forceFlush()` với `LangfuseSpanProcessor`) trước khi handler trả về, để lô sự kiện đang chờ trong hàng đợi được gửi hết thay vì mất khi tiến trình dừng.

**!Note:** Ở môi trường serverless (Vercel Functions, AWS Lambda), nếu không flush trước khi tiến trình thoát hoặc bị đóng băng, các sự kiện còn trong hàng đợi bị mất. Code không báo lỗi — trace chỉ đơn giản không xuất hiện trên Langfuse.

Chi tiết cấu hình: https://langfuse.com/docs/observability/features/queuing-batching

## 3. Log Levels

**Khái niệm.** Thuộc tính `level` gắn trên observation để phân biệt mức độ quan trọng, điều tiết độ chi tiết của trace và làm nổi lỗi/cảnh báo. Bốn mức: `DEBUG`, `DEFAULT`, `WARNING`, `ERROR`. Kèm theo có thể đặt `statusMessage` để bổ sung ngữ cảnh. Đặt `level`/`statusMessage` khi tạo observation, hoặc cập nhật sau (ví dụ `update_current_span(level=..., status_message=...)`). Khi xem một trace, có thể lọc observation theo log level. Với tích hợp OpenAI SDK và LangChain, `level` và `statusMessage` được đặt tự động theo phản hồi API / từng bước trong pipeline.

**Vai trò.** Đánh dấu và lọc nhanh những observation bất thường trong một trace nhiều bước, thay vì đọc tuần tự toàn bộ.

**Ví dụ.** Một pipeline RAG nhiều bước; đặt `level="ERROR"` kèm `statusMessage="Model returned malformed output"` tại bước gọi LLM khi phát hiện output hỏng, rồi lọc trace theo mức ERROR để nhảy thẳng tới bước lỗi.

Chi tiết cấu hình: https://langfuse.com/docs/observability/features/log-levels

## Tham chiếu chéo

- Sampling xử lý ở phía client (docs); với JS/TS, Langfuse tôn trọng quyết định của sampler đặt ở tầng OTEL SDK. Cấu hình batching gắn với một `LangfuseSpanProcessor` cụ thể. **(suy luận, theo mô hình processor của OpenTelemetry — cần kiểm chứng khi triển khai):** vì mỗi span processor/exporter trong OTEL độc lập, thiết lập sampling và batching trên processor của Langfuse chỉ áp cho chính nó; nếu hệ thống còn exporter OTEL khác, chúng phải cấu hình riêng.
- Sampling và queuing/batching cùng là đòn bẩy khối lượng/chi phí nhưng ở hai tầng khác nhau: sampling cắt *có gửi trace hay không*, batching quyết định *gửi theo lô thế nào* — hai cái độc lập và phối hợp được.
- Index nhóm feature: [./01-05-00-index.md](./01-05-00-index.md)