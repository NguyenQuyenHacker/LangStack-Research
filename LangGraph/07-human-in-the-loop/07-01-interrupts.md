---
title: Interrupt
doc_source: https://docs.langchain.com/oss/python/langgraph/interrupts
accessed:
lc_version: unknown
status: draft
lab:
related:
  - ./07-02-time-travel.md
  - ../05-persistence/05-02-checkpointers.md
---

# Interrupt

<!-- CÂU HỎI FILE NÀY TRẢ LỜI: Primitive dừng graph chờ người và tiếp tục lại hoạt động ra sao -->

## 1. Vấn đề phần này giải quyết

<!-- Cần người duyệt giữa chừng nhưng tiến trình không thể ngồi chờ mãi. Tối đa 5 câu, vào thẳng, không lời dẫn. -->

## 2. Khái niệm và API chính

<!-- `interrupt()` và `Command(resume=)`; resume nhiều interrupt song song cùng lúc; các quy tắc interrupt docs nêu; interrupt trong subgraph gọi như hàm; cách debug. -->

## 3. Cơ chế bên dưới

<!-- Vì sao node chạy lại từ đầu sau khi resume, và hệ quả với side effect. (dựng lại) -->

## 4. Ví dụ chạy được

<!-- Code tối giản đã đối chiếu docs, chú thích tiếng Việt, ghi rõ output kỳ vọng. -->

## 5. Ranh giới và đánh đổi

<!-- Side effect trước `interrupt()` sẽ chạy hai lần — cách né. -->

## 6. Câu hỏi còn mở

<!-- Điểm chưa chắc chắn, chỗ docs không nêu rõ, đích cross-link chưa viết. -->

## 7. Tham chiếu

<!-- - [Tên trang](https://docs.langchain.com/oss/python/langgraph/interrupts) — truy cập YYYY-MM-DD -->

---

## Tham chiếu chéo

- [03-07 Human-in-the-loop](../../LangChain/03-harness/03-07-human-in-the-loop.md) — RANH GIỚI — file đó viết `interrupt_on`, cấu hình mức agent khai tool nào cần duyệt; file này viết primitive bên dưới. Nêu một câu rồi link, không lặp bốn loại quyết định
- [02-04 Streaming](../../LangChain/02-model-layer/02-04-streaming.md) — mục 4.3 — nhận interrupt qua stream
