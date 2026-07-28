---
title: Frontend — tổng quan
doc_source: https://docs.langchain.com/oss/python/langgraph/frontend/overview
accessed:
lc_version: unknown
status: draft
lab:
related:
  - ./10-02-graph-execution.md
  - ./10-03-custom-stream-channels.md
---

# Frontend — tổng quan

<!-- CÂU HỎI FILE NÀY TRẢ LỜI: Nối UI vào một graph khác nối UI vào một chat ở chỗ nào -->

## 1. Vấn đề phần này giải quyết

<!-- Chat chỉ có một dòng token; graph có nhiều node chạy song song. Tối đa 5 câu, vào thẳng, không lời dẫn. -->

## 2. Khái niệm và API chính

<!-- STUB NẶNG — kiến trúc client–agent, điểm khác biệt so với stream một chat. -->

## 3. Cơ chế bên dưới

<!-- Dữ liệu từ node đi tới component nào. (dựng lại) -->

## 4. Ví dụ chạy được

<!-- Code tối giản đã đối chiếu docs, chú thích tiếng Việt, ghi rõ output kỳ vọng. -->

## 5. Ranh giới và đánh đổi

<!--  -->

## 6. Câu hỏi còn mở

<!-- LƯU Ý RANH GIỚI: KHÔNG viết lại kiến trúc `useStream` — đã kín ở LangChain `07-01`. -->
<!-- Điểm chưa chắc chắn, chỗ docs không nêu rõ, đích cross-link chưa viết. -->

## 7. Tham chiếu

<!-- - [Tên trang](https://docs.langchain.com/oss/python/langgraph/frontend/overview) — truy cập YYYY-MM-DD -->

---

## Tham chiếu chéo

- [07-01 Frontend overview](../../LangChain/07-interfaces/07-01-frontend-overview.md) — kiến trúc và `useStream` — nguồn chính, chỉ viết chỗ khác biệt 'stream graph ≠ stream chat'
