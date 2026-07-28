---
title: Subgraph
doc_source: https://docs.langchain.com/oss/python/langgraph/use-subgraphs
accessed:
lc_version: unknown
status: draft
lab:
related:
  - ../05-persistence/05-02-checkpointers.md
  - ../06-streaming/06-01-streaming.md
---

# Subgraph

<!-- CÂU HỎI FILE NÀY TRẢ LỜI: Lồng một graph vào graph khác thì state và checkpoint đi đường nào -->

## 1. Vấn đề phần này giải quyết

<!-- Graph lớn cần chia nhỏ; chia sai thì state rò rỉ hoặc checkpoint xung đột. Tối đa 5 câu, vào thẳng, không lời dẫn. -->

## 2. Khái niệm và API chính

<!-- Hai kiểu giao tiếp cha–con (chung state schema vs gọi như hàm), persistence của subgraph, đọc state lồng nhau, stream output từ subgraph. -->

## 3. Cơ chế bên dưới

<!-- State đi từ cha xuống con và ngược lại theo đường nào trong mỗi kiểu. (dựng lại) -->

## 4. Ví dụ chạy được

<!-- Code tối giản đã đối chiếu docs, chú thích tiếng Việt, ghi rõ output kỳ vọng. -->

## 5. Ranh giới và đánh đổi

<!-- Khi nào tách subgraph là thừa. Xung đột checkpoint khi gọi song song. -->

## 6. Câu hỏi còn mở

<!-- Điểm chưa chắc chắn, chỗ docs không nêu rõ, đích cross-link chưa viết. -->

## 7. Tham chiếu

<!-- - [Tên trang](https://docs.langchain.com/oss/python/langgraph/use-subgraphs) — truy cập YYYY-MM-DD -->

---

## Tham chiếu chéo

- [06-02 Subagents](../../LangChain/06-multi-agent/06-02-subagents.md) — PHẢI NÓI THẲNG subgraph ≠ subagent — subagent lộ ra thành tool cho model gọi, subgraph là cấu trúc lồng, cha gọi tất định. Phần subagent-as-tool của trang docs thì stub + link
- [06-01 Multi-agent overview](../../LangChain/06-multi-agent/06-01-overview.md) — bảng so sánh 5 pattern
- [06-06 Custom workflow](../../LangChain/06-multi-agent/06-06-custom-workflow.md) — tự dựng luồng
