---
title: Streaming mức graph
doc_source: https://docs.langchain.com/oss/python/langgraph/streaming
accessed:
lc_version: unknown
status: draft
lab:
related:
  - ./06-02-event-streaming.md
  - ../04-runtime/04-01-pregel-runtime.md
---

# Streaming mức graph

<!-- CÂU HỎI FILE NÀY TRẢ LỜI: Stream một graph khác stream một model ở chỗ nào -->

## 1. Vấn đề phần này giải quyết

<!-- Graph có nhiều node; người dùng cần biết dữ liệu đang đến từ node nào. Tối đa 5 câu, vào thẳng, không lời dẫn. -->

## 2. Khái niệm và API chính

<!-- STUB NẶNG — stream mode ở mức graph: `values` / `updates` / `messages` / `custom` / `debug`, `subgraphs=True`, lọc theo node và tag. -->

## 3. Cơ chế bên dưới

<!-- Quan hệ giữa một super-step và một lần phát dữ liệu. (dựng lại — nối với `04-01`) -->

## 4. Ví dụ chạy được

<!-- Code tối giản đã đối chiếu docs, chú thích tiếng Việt, ghi rõ output kỳ vọng. -->

## 5. Ranh giới và đánh đổi

<!-- Stream `values` tốn băng thông hơn `updates` ra sao. -->

## 6. Câu hỏi còn mở

<!-- LƯU Ý RANH GIỚI: KHÔNG viết lại: ba kênh dữ liệu, định dạng v1/v2, `custom` writer, tắt streaming chọn lọc — đã kín ở LangChain `02-04`. -->
<!-- Điểm chưa chắc chắn, chỗ docs không nêu rõ, đích cross-link chưa viết. -->

## 7. Tham chiếu

<!-- - [Tên trang](https://docs.langchain.com/oss/python/langgraph/streaming) — truy cập YYYY-MM-DD -->

---

## Tham chiếu chéo

- [02-04 Streaming](../../LangChain/02-model-layer/02-04-streaming.md) — nguồn chính về stream mode và định dạng — ở đây chỉ viết phần graph mới có
