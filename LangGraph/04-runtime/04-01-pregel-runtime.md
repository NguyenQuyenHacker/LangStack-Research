---
title: Runtime Pregel
doc_source: https://docs.langchain.com/oss/python/langgraph/pregel
accessed:
lc_version: unknown
status: draft
lab:
related:
  - ../02-graph-api/02-02-graph-api.md
  - ./04-02-fault-tolerance.md
---

# Runtime Pregel

<!-- CÂU HỎI FILE NÀY TRẢ LỜI: Engine chạy graph hoạt động ra sao — actor, channel, super-step -->

## 1. Vấn đề phần này giải quyết

<!-- Không nắm super-step thì không giải thích được thứ tự chạy node song song và lúc nào state được cập nhật. Tối đa 5 câu, vào thẳng, không lời dẫn. -->

## 2. Khái niệm và API chính

<!-- Actor, channel, super-step; ba pha plan – execution – update; quan hệ giữa runtime này và API mức cao. -->

## 3. Cơ chế bên dưới

<!-- Một super-step đi qua đâu, reducer gọi ở pha nào, node song song đọc bản state nào. (dựng lại — đối chiếu graph-api) -->

## 4. Ví dụ chạy được

<!-- Code tối giản đã đối chiếu docs, chú thích tiếng Việt, ghi rõ output kỳ vọng. -->

## 5. Ranh giới và đánh đổi

<!-- Mô hình BSP làm gì với node chạy lâu; giới hạn của việc gom mọi ghi vào cuối bước. -->

## 6. Câu hỏi còn mở

<!-- Điểm chưa chắc chắn, chỗ docs không nêu rõ, đích cross-link chưa viết. -->

## 7. Tham chiếu

<!-- - [Tên trang](https://docs.langchain.com/oss/python/langgraph/pregel) — truy cập YYYY-MM-DD -->

---

## Tham chiếu chéo

- [03-08 Runtime](../../LangChain/03-harness/03-08-runtime.md) — TRÙNG TÊN, KHÁC VẬT — phải phân biệt ngay mục 1: trang này là *engine* chạy graph, `03-08` là *object* `Runtime` mà tool/middleware đọc được
