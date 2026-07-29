---
title: Graph API
doc_source: https://docs.langchain.com/oss/python/langgraph/graph-api
accessed:
lc_version: unknown
status: draft
lab:
related:
  - ./08-03-use-graph-api.md
  - ../10-runtime/10-01-pregel-runtime.md
---

# Graph API

<!-- CÂU HỎI FILE NÀY TRẢ LỜI: Các primitive dựng nên một graph là gì và ghép với nhau ra sao -->

## 1. Vấn đề phần này giải quyết

<!-- Đây là phần lõi chỉ LangGraph có. Không nắm state/reducer thì mọi thứ phía sau đều đoán mò. Tối đa 5 câu, vào thẳng, không lời dẫn. -->

## 2. Khái niệm và API chính

<!-- `StateGraph`, state schema và reducer, node, edge, conditional edge, `Send`, `Command`, node caching, graph migration, recursion limit và `RemainingSteps`, visualization. -->

## 3. Cơ chế bên dưới

<!-- Reducer chạy lúc nào trong một super-step, và vì sao ghi song song vào cùng key cần reducer. (dựng lại — đối chiếu với trang pregel) -->

## 4. Ví dụ chạy được

<!-- Code tối giản đã đối chiếu docs, chú thích tiếng Việt, ghi rõ output kỳ vọng. -->

## 5. Ranh giới và đánh đổi

<!-- Khi nào `Command` gọn hơn conditional edge và ngược lại. Giá phải trả của node caching. -->

## 6. Câu hỏi còn mở

<!-- Điểm chưa chắc chắn, chỗ docs không nêu rõ, đích cross-link chưa viết. -->

## 7. Tham chiếu

<!-- - [Tên trang](https://docs.langchain.com/oss/python/langgraph/graph-api) — truy cập YYYY-MM-DD -->

---

## Tham chiếu chéo

- [03-08 Runtime](../../LangChain/03-harness/03-08-runtime.md) — mục Runtime context của trang docs — object `Runtime` đã có nguồn chính ở đó
- [06-03 Handoffs](../../LangChain/06-multi-agent/06-03-handoffs.md) — handoff mức agent dựng trên `Command`
- [09-03 Observability hooks](../../LangChain/09-production/09-03-observability-hooks.md) — mục Observability and Tracing — chỉ link
- [Langfuse](../../Langfuse/README.md) — dashboard và scoring nằm ở nhánh này
