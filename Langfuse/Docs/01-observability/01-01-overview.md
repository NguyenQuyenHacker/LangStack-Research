---
title: Langfuse — Observability Overview
doc_source: https://langfuse.com/docs/observability/overview
accessed: 2026-07-31
version: "v4"
status: draft
lab:
related:
  - ./langfuse-get-started.md
  - ./langfuse-data-model.md
---

# Langfuse Observability — nhật ký cho ứng dụng LLM

> Trang tổng quan giới thiệu observability và tracing của Langfuse — công cụ ghi lại
> toàn bộ những gì xảy ra bên trong một ứng dụng LLM để gỡ lỗi và theo dõi.
> Cơ chế chi tiết (traces/sessions/observations) nằm ở [Concepts](https://langfuse.com/docs/observability/data-model); cách cài đặt và code đầu tiên nằm ở [Get Started](https://langfuse.com/docs/observability/get-started).

---

## 1. Tổng quan

Langfuse Observability là công cụ ghi lại (tracing) và theo dõi hành vi của ứng dụng LLM — nó chụp lại từng request: prompt đã gửi, câu model trả về, số token, độ trễ, và mọi bước tool hay truy xuất dữ liệu ở giữa.

Khác với công cụ giám sát ứng dụng thông thường ở một điểm: Langfuse được làm riêng cho LLM, nên hiểu sẵn những khái niệm đặc thù như token, tham số model, cặp prompt/completion, điểm đánh giá.


---

## 2. Vì sao ứng dụng LLM cần observability

Model LLM chạy không tất định : cùng một đầu vào có thể ra kết quả khác nhau. Gỡ lỗi một ứng dụng như vậy mà không có công cụ quan sát thì gần như đoán mò — không biết bên trong đã xảy ra chuyện gì, và vì sao lại ra kết quả đó.

Đây là vấn đề mà observability sinh ra để lo: cho ta công cụ nhìn vào bên trong ứng dụng và hiểu *cái gì đang diễn ra, vì sao*.

Lõi của observability chính là **application tracing** — mục 3.

---

## 3. Tracing — biên bản đầy đủ vòng đời một request

**Vấn đề.** Một request đi qua ứng dụng LLM không phải một lệnh gọi đơn lẻ: nó có thể gọi model, truy xuất dữ liệu, chạy vài tool, rồi tổng hợp lại. Khi kết quả sai, ta cần biết chính xác bước nào hỏng — không có bản ghi thì không truy được.

**Định nghĩa.** Application tracing ghi lại trọn vòng đời của một request khi nó chạy qua hệ thống. Mỗi trace chụp mọi thao tác — lệnh gọi LLM, bước truy xuất, lần chạy tool, và logic tùy biến — kèm thời gian, đầu vào, đầu ra, metadata.

Một điểm quan trọng: tracing giữ lại **quan hệ nhân quả** giữa các thao tác — thao tác nào gọi ra thao tác nào, lồng trong nhau ra sao. Đây là thứ phân biệt tracing với việc ghi log rời rạc.

Ví dụ một trace trên giao diện Langfuse: các thao tác lồng nhau gồm một lệnh gọi model ban đầu, nhiều lần chạy tool, và một bước tổng hợp cuối. Mỗi thao tác kèm thời gian, đầu vào, đầu ra, và chi phí.

---

## 4. Phân biệt Observability và tracing 

Hai từ này thường bị coi là một, nhưng tài liệu tách rạch ròi.

**Observability** là năng lực rộng: hiểu trạng thái bên trong hệ thống thông qua đầu ra của nó. Nó bao gồm ba thứ — tracing, metrics (số liệu), và logging (ghi log).

**Tracing** là một kỹ thuật cụ thể *nằm trong* observability: ghi lại luồng đi của một request qua hệ thống, giữ nguyên quan hệ nhân quả giữa các thao tác.

Với ứng dụng LLM, tracing là công cụ observability quan trọng nhất, vì nó chụp trọn bối cảnh của mỗi request — prompt, câu trả lời, lệnh gọi tool, và quan hệ giữa chúng.

---

## 5. Langfuse khác công cụ tracing thông thường ở đâu

Điểm phân biệt gốc: Langfuse làm riêng cho ứng dụng LLM, nên hiểu sẵn các khái niệm mà công cụ APM đa dụng không có — token, tham số model, cặp prompt/completion, điểm đánh giá.

Trên nền đó, Langfuse có thêm các tính năng dành riêng cho kỹ thuật AI:

- Chấm điểm bằng [LLM-as-a-Judge](https://langfuse.com/docs/evaluation/evaluation-methods/llm-as-a-judge) — dùng một model để đánh giá đầu ra
- [Prompt management](https://langfuse.com/docs/prompt-management/overview) — quản lý prompt
- [Experiments và datasets](https://langfuse.com/docs/evaluation/experiments/datasets) — chạy thử nghiệm trên bộ dữ liệu
- [Custom dashboards](https://langfuse.com/docs/metrics/features/custom-dashboards) — bảng theo dõi tự dựng

Ngoài ra Langfuse là mã nguồn mở và có thể [tự vận hành trên hạ tầng riêng](https://langfuse.com/self-hosting) (self-host).

---

## 6. Langfuse có làm chậm ứng dụng không

Không. SDK của Langfuse gửi dữ liệu tracing bất đồng bộ (asynchronous) ở nền — các sự kiện được xếp hàng tại chỗ (queue) rồi đẩy đi theo lô (batch). Nhờ vậy thời gian phản hồi của ứng dụng không bị ảnh hưởng.

Cơ chế queue và batch chi tiết nằm ở trang [queuing & batching](https://langfuse.com/docs/observability/features/queuing-batching) — ngoài phạm vi trang overview.

---

## 7. Bắt đầu từ đâu

Tài liệu gợi ý lộ trình sau khi đã dựng được trace đầu tiên:

- [Dựng trace đầu tiên](https://langfuse.com/docs/observability/get-started) — bước khởi đầu
- [Nắm khái niệm nền: traces, sessions, observations](https://langfuse.com/docs/observability/data-model)
- [Gom trace thành session cho ứng dụng nhiều lượt hội thoại](https://langfuse.com/docs/observability/features/sessions)
- [Tách trace theo môi trường (dev/staging/prod)](https://langfuse.com/docs/observability/features/environments)
- [Gắn thuộc tính vào trace để lọc về sau](https://langfuse.com/docs/observability/features/tags)
- [Dùng trace ID tùy biến cho distributed tracing](https://langfuse.com/docs/observability/features/trace-ids-and-distributed-tracing)
- [Theo dõi chi phí và lượng token](https://langfuse.com/docs/observability/features/token-and-cost-tracking)

---

## Khoảng trống của trang này

- **Không có code.** Trang overview thuần khái niệm; ví dụ chạy được đặt ở Get Started.
- **Mô hình dữ liệu chỉ nhắc tên.** Ba khái niệm trace/session/observation được nêu nhưng không định nghĩa ở đây — trang Concepts mới là chỗ giảng.
- **So sánh với APM để ngỏ.** Tài liệu nói Langfuse khác "công cụ APM đa dụng" nhưng không nêu tên công cụ cụ thể nào để đối chiếu trực tiếp.

---

## Tham chiếu chéo

- [Get Started](https://langfuse.com/docs/observability/get-started) — cài đặt và trace đầu tiên (chưa có file note riêng)
- [Concepts / Data model](https://langfuse.com/docs/observability/data-model) — traces, sessions, observations (chưa có file note riêng)
- [Best Practices](https://langfuse.com/docs/observability/best-practices)