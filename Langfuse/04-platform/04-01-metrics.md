---
title: Platform — Metrics
doc_source:
- https://langfuse.com/docs/metrics/overview
- https://langfuse.com/docs/metrics/features/custom-dashboards
- https://langfuse.com/docs/metrics/features/monitors
- https://langfuse.com/docs/metrics/features/metrics-api
accessed: 2026-07-31
version: v4
status: draft
---

# Platform — Metrics

## Tổng quan

**Định nghĩa.** Metrics (chỉ số) là các con số đo lường rút ra từ dữ liệu vận hành và đánh giá của ứng dụng LLM — tức từ *trace* (bản ghi mỗi lượt ứng dụng xử lý một yêu cầu) và *score* (điểm chất lượng gắn vào các lượt đó).

**Ba nhóm chỉ số chính.**

| Nhóm | Đo cái gì |
|---|---|
| Chất lượng (Quality) | Ứng dụng trả lời tốt tới đâu — đo qua phản hồi người dùng, chấm bằng model, chấm tay, hoặc điểm tùy chỉnh. |
| Chi phí & Độ trễ (Cost & Latency) | Tốn bao nhiêu tiền và mất bao lâu cho mỗi lượt xử lý. |
| Khối lượng (Volume) | Số lượt xử lý và số *token* (đơn vị văn bản model đọc/sinh ra) đã dùng. |

**Chiều phân tích (Dimension) — cách tách nhỏ chỉ số để soi.** Theo tên use case (trace name), theo người dùng (userId), theo nhãn (tag), theo phiên bản ứng dụng (release/version). Ví dụ: xem chi phí tách theo từng model, hoặc độ trễ theo từng tính năng.

**Ba cách khai thác.** Xem trực quan bằng Dashboard (mục 1); đặt cảnh báo tự động bằng Monitor (mục 2); tự lấy số liệu bằng code qua Metrics API (mục 3).

Nếu muốn tìm hiểu thêm hãy tham khảo thông qua https://langfuse.com/docs/metrics/overview

## 1. Custom Dashboards (Bảng thống kê tùy chỉnh)

**Định nghĩa.** Dashboard là màn hình tổng hợp nhiều biểu đồ (mỗi biểu đồ gọi là *widget*) để trực quan hóa dữ liệu ứng dụng, tự dựng theo nhu cầu, không cần code.

**Mục tiêu.** Theo dõi đúng các chỉ số nhóm quan tâm — độ trễ, chi phí, chất lượng, hành vi người dùng — trên một màn hình; cập nhật gần thời gian thực và chia sẻ trong nhóm.

**Cách dựng (hai bước).**

| Bước | Nội dung |
|---|---|
| Tạo widget | Chọn nguồn dữ liệu (trace / observation / điểm số) → chọn chỉ số đo (số lượng, độ trễ, chi phí, điểm...) → chọn chiều nhóm (theo người dùng, model, thời gian...) → lọc → chọn kiểu biểu đồ. |
| Ghép dashboard | Đặt tên → thêm các widget → kéo-thả sắp xếp, chỉnh kích thước. |

**Điểm đáng chú ý.**

| Khả năng | Nội dung |
|---|---|
| Dashboard dựng sẵn (curated) | Có sẵn bảng về Độ trễ, Chi phí, Mức dùng để bắt đầu ngay; sửa được. Lần chỉnh đầu tiên hệ thống tạo một bản sao riêng, không đụng bản gốc. |
| Trang Home | Trang chủ dự án cũng là một dashboard; chọn được dashboard nào hiển thị làm mặc định cho cả nhóm. |
| Sao chép & chia sẻ | Copy-paste widget giữa các dashboard; xuất/nhập widget và dashboard dạng file JSON để dùng lại giữa các dự án. |
| Lọc nâng cao | Lọc theo metadata, khoảng thời gian, thuộc tính người dùng, model, tag, ngưỡng điểm. |
| Quản lý bằng code | Tạo/sửa dashboard qua API, CLI hoặc MCP. |

> !Note: Các endpoint quản lý dashboard bằng code đang ở trạng thái *unstable* (chưa ổn định) và có thể thay đổi.

Nếu muốn tìm hiểu thêm hãy tham khảo thông qua https://langfuse.com/docs/metrics/features/custom-dashboards

## 2. Monitors and Alerts (Giám sát và cảnh báo)

> !Note: Tính năng này chỉ có trên Langfuse Cloud.

**Định nghĩa.** Monitor là quy tắc tự động kiểm tra một chỉ số theo chu kỳ; khi chỉ số vượt ngưỡng đặt trước thì phát cảnh báo và gửi thông báo ra ngoài.

**Mục tiêu.** Phát hiện sớm vấn đề chi phí/chất lượng trước khi ảnh hưởng người dùng, thay vì ngồi canh dashboard thủ công.

**Cấu hình một monitor.**

| Phần | Nội dung |
|---|---|
| Chỉ số theo dõi | Chọn nguồn dữ liệu và phép đo (ví dụ độ trễ trung bình, chi phí ở phân vị p95), kèm bộ lọc. |
| Điều kiện cảnh báo | Toán tử so sánh (>, ≥, <...); ngưỡng cảnh báo (bắt buộc); ngưỡng cảnh báo sớm (tùy chọn); cửa sổ thời gian mỗi lần kiểm tra nhìn lại bao xa (1 giờ, 1 ngày...). |
| Xử lý ca đặc biệt (tùy chọn) | Cách hành xử khi truy vấn không có dữ liệu; có nhắc lại cảnh báo hay không khi tình trạng kéo dài. |
| Kênh thông báo | Gắn với một hoặc nhiều Automation để gửi cảnh báo đi. |

**Mức độ (severity) của monitor.** `OK` (trong ngưỡng), `WARNING` (chạm ngưỡng cảnh báo sớm), `ALERT` (chạm ngưỡng cảnh báo), `NO_DATA` (không có dữ liệu), `PAUSED` (đã tạm dừng). Cảnh báo bắn khi chuyển xấu đi và khi phục hồi về `OK`.

**Automation — kênh gửi cảnh báo.**

| Kênh | Làm gì |
|---|---|
| Slack | Đăng tin cảnh báo vào một kênh Slack. |
| Webhook | Gửi dữ liệu cảnh báo (JSON có ký xác thực) tới một đường dẫn của bạn. |
| GitHub Actions | Kích hoạt một quy trình tự động trên GitHub. |

> !Note: Sau 5 lần gửi thất bại liên tiếp, Langfuse tự tắt automation đó; phải bật lại thủ công sau khi khắc phục endpoint.

Nếu muốn tìm hiểu thêm hãy tham khảo thông qua https://langfuse.com/docs/metrics/features/monitors

## 3. Metrics API

**Định nghĩa.** Metrics API là cổng cho phép lấy chỉ số tổng hợp từ Langfuse bằng code, thay vì xem trên giao diện — dùng cho báo cáo, tính phí, dashboard hoặc giám sát riêng.

**Mục tiêu.** Tự động rút số liệu theo tiêu chí tùy chỉnh (chỉ số, chiều nhóm, bộ lọc, mốc thời gian) để đưa vào hệ thống khác.

**Cách gọi.** Gửi một truy vấn mô tả cần gì — chọn *view* (lớp dữ liệu), chỉ số + phép gộp, chiều nhóm, bộ lọc, khoảng thời gian — hệ thống trả về bảng số.

**Hai phiên bản.**

| Phiên bản | Ghi chú |
|---|---|
| v2 (khuyến nghị) | Nhanh hơn, dùng cho mọi nhu cầu mới. Bỏ view `traces`, thay bằng `observations` (mạnh và nhanh hơn). |
| v1 (cũ) | Còn dùng được cho tích hợp cũ nhưng chậm khi dữ liệu lớn; nên chuyển sang v2. |

**Một số khái niệm trong truy vấn.**

| Khái niệm | Nghĩa |
|---|---|
| View | Lớp dữ liệu truy vấn: `observations` (từng bước xử lý), `scores-numeric / categorical / boolean` (các loại điểm). |
| Metric + Aggregation | Cái cần đo (số lượng, độ trễ, chi phí, token...) và phép gộp: tổng, trung bình, hoặc phân vị p50/p95/p99 (mốc mà X% giá trị nằm dưới). |
| Dimension | Chiều để nhóm kết quả (theo tên, model, prompt...). Các trường quá nhiều giá trị như `userId`, `sessionId` chỉ dùng để lọc, không dùng để nhóm. |
| Filter / Time | Bộ lọc thu hẹp dữ liệu; mốc thời gian bắt buộc (từ — đến). |

> !Note: v2 mặc định trả tối đa 100 dòng mỗi truy vấn, nâng được lên tối đa 1.000 dòng.

Ngoài ra còn một *Daily Metrics API* cũ trả số liệu chi phí/khối lượng theo ngày, giữ lại cho tương thích ngược; nhu cầu mới nên dùng v2.

Nếu muốn tìm hiểu thêm hãy tham khảo thông qua https://langfuse.com/docs/metrics/features/metrics-api