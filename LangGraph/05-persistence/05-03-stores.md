---
title: Store
doc_source: https://docs.langchain.com/oss/python/langgraph/stores
accessed:
lc_version: unknown
status: draft
lab:
related:
  - ./05-02-checkpointers.md
  - ./05-04-add-memory.md
---

# Store

<!-- CÂU HỎI FILE NÀY TRẢ LỜI: Dữ liệu cần sống lâu hơn một thread thì lưu bằng interface nào -->

## 1. Vấn đề phần này giải quyết

<!-- Checkpointer gắn với thread. Thứ cần nhớ xuyên thread phải có chỗ khác. Tối đa 5 câu, vào thẳng, không lời dẫn. -->

## 2. Khái niệm và API chính

<!-- `BaseStore`, namespace/key, `list_namespaces`, semantic search và chọn field để embed, gắn store vào graph, tự viết store. -->

## 3. Cơ chế bên dưới

<!-- Namespace phân tách dữ liệu ra sao; semantic search embed cái gì. (dựng lại) -->

## 4. Ví dụ chạy được

<!-- Code tối giản đã đối chiếu docs, chú thích tiếng Việt, ghi rõ output kỳ vọng. -->

## 5. Ranh giới và đánh đổi

<!-- Chi phí embedding. Khi nào dùng database thường thay vì store. -->

## 6. Câu hỏi còn mở

<!-- Điểm chưa chắc chắn, chỗ docs không nêu rõ, đích cross-link chưa viết. -->

## 7. Tham chiếu

<!-- - [Tên trang](https://docs.langchain.com/oss/python/langgraph/stores) — truy cập YYYY-MM-DD -->

---

## Tham chiếu chéo

- [04-03 Long-term memory](../../LangChain/04-context-memory/04-03-long-term-memory.md) — đọc/ghi store trong tool đã ở đó — ở đây viết interface `BaseStore` và semantic search
