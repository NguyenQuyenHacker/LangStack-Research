---
title: Platform — Security & Guardrails
doc_source: https://langfuse.com/docs/security-and-guardrails
accessed: 2026-07-31
version: v4
status: draft
---

# Platform — Security & Guardrails

Cách Langfuse tham gia vào bài toán an toàn của ứng dụng LLM: không chặn tại chỗ, mà quan sát và đánh giá hiệu quả của các lớp chặn.

## Vấn đề

Ứng dụng LLM đối mặt vài rủi ro an toàn đặc thù: prompt injection (người dùng nhét chỉ dẫn vào input để lái mô hình chệch lệnh hệ thống), rò rỉ PII (thông tin định danh cá nhân — tên, số thẻ, email, SSN, IP...), nội dung độc hại. Khi sự cố xảy ra còn cần điều tra được nó đã đi qua những bước nào.

## Khái niệm

LLM Security là tập biện pháp bảo vệ mô hình và hạ tầng của nó khỏi truy cập trái phép, lạm dụng và tấn công đối kháng, giữ tính toàn vẹn và bảo mật của cả mô hình lẫn dữ liệu.

Cần tách hai vai, vì đây là chỗ dễ hiểu sai vị trí của Langfuse:
- **Guardrail** là lớp chặn chạy *lúc run-time*, nằm ở tầng ứng dụng, chặn/lọc input và output trước và sau khi gọi mô hình. Việc này do thư viện chuyên dụng làm, không phải Langfuse.
- **Langfuse** đứng *sau* các lớp chặn đó, làm nhiệm vụ quan sát (tracing) và đánh giá *ex-post* — kiểm xem lớp chặn có hoạt động đúng không.

## Cách hoạt động ở mức tổng quan

An toàn được xử lý bằng tổ hợp hai thành phần, mỗi thành phần một vai:

**1. Lớp chặn run-time (thư viện ngoài).** Các thư viện như LLM Guard, Prompt Armor, NeMo Guardrails, Azure AI Content Safety, Lakera đảm nhận ba việc: chặn prompt có hại trước khi gửi vào mô hình; che (redact) PII trước khi gửi rồi phục hồi (un-redact) ở response; chấm input/output theo độ độc hại, độ liên quan, mức nhạy cảm ngay lúc chạy và chặn response nếu cần.

**2. Giám sát và đánh giá (Langfuse).** Trace của Langfuse phủ lên từng bước của cơ chế an toàn, cho thấy bước nào đã kích hoạt và kết quả ra sao. Trên nền trace đó có bốn workflow:

- **Điều tra thủ công** — mở trace để truy vết một sự cố an toàn cụ thể.
- **Theo dõi điểm an toàn theo thời gian** — xem security score trên dashboard để biết rủi ro nào đang phổ biến.
- **Kiểm định lớp chặn** — dùng score của Langfuse để đo hiệu quả công cụ an toàn, theo hai hướng: gắn nhãn thủ công một phần trace production làm mốc so sánh (annotation queue), hoặc chạy đánh giá tự động bằng LLM-as-a-judge quét trace tìm độc hại/nhạy cảm.
- **Đo latency** — một số lớp chặn phải chờ xong mới gọi được mô hình, số khác chặn response tới người dùng, nên chúng là nguồn latency đáng kể. Trace tách được thời gian từng lớp chặn để cân nhắc lớp nào đáng giữ.

## Thành phần chính

- **Thư viện guardrail bên ngoài** — nơi thực thi việc chặn. Ví dụ trong docs là LLM Guard (mã nguồn mở của Protect AI): có input scanner (phát hiện prompt injection, che PII, phát hiện độc hại, cấm chủ đề) và output scanner (kiểm duyệt nội dung, phát hiện thiên kiến, phát hiện URL độc, phục hồi dữ liệu đã che).
- **Tracing** — lớp ghi lại từng bước chặn để nhìn được.
- **Scores** — đơn vị định lượng hiệu quả lớp chặn, sinh từ annotation (người) hoặc đánh giá tự động (máy).
- **Dashboard / Annotation queue** — nơi tổng hợp điểm theo thời gian và nơi con người rà soát trace bị gắn cờ.

## Lưu ý ảnh hưởng đến việc hiểu tính năng

- Langfuse không thay thế guardrail. Bỏ thư viện chặn mà chỉ bật Langfuse thì không có gì chặn rủi ro — Langfuse chỉ cho thấy điều đã xảy ra, không ngăn nó xảy ra.
- Guardrail bổ trợ cho, không thay thế, phần huấn luyện an toàn ở tầng mô hình. Hai lớp khác nhau.
- Không có lớp phòng thủ đơn lẻ nào chặn được 100% (docs nêu rõ với prompt injection). Hướng khuyến nghị là defense-in-depth — nhiều lớp cộng giám sát — chứ không dựa vào một công cụ.
- Ví dụ triển khai trong docs (ẩn/hiện PII cho bản tóm tắt biên bản tòa) dùng LLM Guard + tích hợp OpenAODK, nhưng docs nói rõ mọi ví dụ chuyển sang thư viện khác được — chọn thư viện là quyết định của ứng dụng, không phải ràng buộc của Langfuse.

## Hướng dẫn triển khai

Xem hướng dẫn đầy đủ tại: https://langfuse.com/docs/security-and-guardrails