---
title: Fault tolerance
doc_source: https://docs.langchain.com/oss/python/langgraph/fault-tolerance
accessed:
lc_version: unknown
status: draft
lab:
related:
  - ../02-persistence/02-02-checkpointers.md
  - ../08-graph-api/08-03-use-graph-api.md
---

# Fault tolerance

<!-- CÂU HỎI FILE NÀY TRẢ LỜI: Graph gặp lỗi, timeout hoặc bị tắt giữa chừng thì runtime xử lý thế nào -->

## 1. Vấn đề phần này giải quyết

<!-- Graph chạy dài gặp lỗi mạng, tiến trình bị kill — không có cơ chế này thì mất toàn bộ tiến độ. Tối đa 5 câu, vào thẳng, không lời dẫn. -->

## 2. Khái niệm và API chính

<!-- Retry, timeout (wall-clock vs idle), xử lý lỗi, graph defaults, graceful shutdown (`request_drain`), các giới hạn docs tự nêu. -->

## 3. Cơ chế bên dưới

<!-- Durable execution: cái gì được ghi lại trước khi lỗi xảy ra, resume bắt đầu từ đâu. (dựng lại — nối checkpointers mục durability modes) -->

## 4. Ví dụ chạy được

<!-- Code tối giản đã đối chiếu docs, chú thích tiếng Việt, ghi rõ output kỳ vọng. -->

## 5. Ranh giới và đánh đổi

<!-- Retry làm hỏng tính idempotency ở đâu. Giới hạn docs tự thừa nhận. -->

## 6. Câu hỏi còn mở

<!-- LƯU Ý RANH GIỚI: Trang `durable-execution` đã bị gộp (308 → persistence) — khái niệm durable execution trình bày ở đây và ở `05-02`, hai chỗ link nhau, không tạo file thứ ba. -->
<!-- Điểm chưa chắc chắn, chỗ docs không nêu rõ, đích cross-link chưa viết. -->

## 7. Tham chiếu

<!-- - [Tên trang](https://docs.langchain.com/oss/python/langgraph/fault-tolerance) — truy cập YYYY-MM-DD -->

---

## Tham chiếu chéo

<!-- Chưa có đích cross-link ra ngoài nhánh. Bổ sung khi viết nội dung. -->
