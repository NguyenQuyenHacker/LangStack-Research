---
title: Checkpointer
doc_source: https://docs.langchain.com/oss/python/langgraph/checkpointers
accessed:
lc_version: unknown
status: draft
lab:
related:
  - ./05-03-stores.md
  - ../04-runtime/04-02-fault-tolerance.md
  - ../07-human-in-the-loop/07-02-time-travel.md
---

# Checkpointer

<!-- CÂU HỎI FILE NÀY TRẢ LỜI: Trạng thái graph được lưu dưới dạng gì và đọc/sửa lại bằng API nào -->

## 1. Vấn đề phần này giải quyết

<!-- Không có checkpointer thì không có resume, không có human-in-the-loop, không có time travel. Tối đa 5 câu, vào thẳng, không lời dẫn. -->

## 2. Khái niệm và API chính

<!-- Thread / checkpoint / `StateSnapshot`; `get_state`, `update_state`, `get_state_history`; durability mode; tối ưu dung lượng checkpoint; thư viện InMemory/SQLite/Postgres; tự viết checkpointer. -->

## 3. Cơ chế bên dưới

<!-- Một checkpoint chứa gì, ghi lúc nào trong super-step, và durability mode đổi thời điểm ghi ra sao. (dựng lại) -->

## 4. Ví dụ chạy được

<!-- Code tối giản đã đối chiếu docs, chú thích tiếng Việt, ghi rõ output kỳ vọng. -->

## 5. Ranh giới và đánh đổi

<!-- Đánh đổi giữa các durability mode. Chi phí lưu trữ và cách dọn checkpoint cũ. -->

## 6. Câu hỏi còn mở

<!-- Điểm chưa chắc chắn, chỗ docs không nêu rõ, đích cross-link chưa viết. -->

## 7. Tham chiếu

<!-- - [Tên trang](https://docs.langchain.com/oss/python/langgraph/checkpointers) — truy cập YYYY-MM-DD -->

---

## Tham chiếu chéo

- [04-02 Short-term memory](../../LangChain/04-context-memory/04-02-short-term-memory.md) — checkpointer *dùng ở mức agent* đã ở đó — ở đây viết cấu trúc dữ liệu và API state bên dưới
