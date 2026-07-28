---
title: Nối trí nhớ vào graph
doc_source: https://docs.langchain.com/oss/python/langgraph/add-memory
accessed:
lc_version: unknown
status: draft
lab:
related:
  - ./05-02-checkpointers.md
  - ./05-03-stores.md
---

# Nối trí nhớ vào graph

<!-- CÂU HỎI FILE NÀY TRẢ LỜI: Ghép checkpointer và store vào graph thế nào để nó nhớ được -->

## 1. Vấn đề phần này giải quyết

<!-- Có đủ hai thành phần rồi nhưng nối sai chỗ thì graph vẫn quên. Tối đa 5 câu, vào thẳng, không lời dẫn. -->

## 2. Khái niệm và API chính

<!-- STUB NẶNG — chỉ viết *cách nối*: gắn checkpointer, gắn store, truyền context lúc invoke, vận hành database. -->

## 3. Cơ chế bên dưới

<!-- Đường đi của một lượt hội thoại qua checkpointer rồi qua store. (dựng lại) -->

## 4. Ví dụ chạy được

<!-- Code tối giản đã đối chiếu docs, chú thích tiếng Việt, ghi rõ output kỳ vọng. -->

## 5. Ranh giới và đánh đổi

<!-- Chỗ khác biệt khi quản lý lịch sử ở mức graph thay vì bằng middleware. -->

## 6. Câu hỏi còn mở

<!-- LƯU Ý RANH GIỚI: KHÔNG viết lại: khái niệm hai loại trí nhớ, và trim/delete/summarize — cả hai đã kín ở LangChain `04-01` và `04-02` mục 4. -->
<!-- Điểm chưa chắc chắn, chỗ docs không nêu rõ, đích cross-link chưa viết. -->

## 7. Tham chiếu

<!-- - [Tên trang](https://docs.langchain.com/oss/python/langgraph/add-memory) — truy cập YYYY-MM-DD -->

---

## Tham chiếu chéo

- [04-01 Memory](../../LangChain/04-context-memory/04-01-memory.md) — vì sao có hai loại trí nhớ, ba kiểu trí nhớ dài hạn — nguồn chính
- [04-02 Short-term memory](../../LangChain/04-context-memory/04-02-short-term-memory.md) — trim / delete / summarize ở mục 4 — không lặp
- [04-03 Long-term memory](../../LangChain/04-context-memory/04-03-long-term-memory.md) — namespace/key và đọc–ghi trong tool
