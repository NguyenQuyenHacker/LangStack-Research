---
title: Langfuse — Tổng quan nghiên cứu
doc_source: https://langfuse.com/docs
accessed: 2026-07-31
version: v4
status: draft
---

# Langfuse — Tổng quan nghiên cứu

Repo chỉ đào sâu **hai mảng**: **Docs** và **Integrations**. Năm khu còn lại trên menu chỉ nêu là gì và để link, đọc khi cần chứ không nghiên cứu chuyên sâu.

---

## Bảy khu trên menu langfuse.com

| # | Tab | Là gì | URL | Phạm vi |
|---|-----|-------|-----|---------|
| 1 | **Docs** | Tài liệu tra cứu từng tính năng, cú pháp, cách bật/tắt | https://langfuse.com/docs | ✅ Trong |
| 2 | **Integrations** | Cách cắm Langfuse vào công cụ khác: LangChain, OpenAI SDK, LlamaIndex, LiteLLM, OpenTelemetry | https://langfuse.com/integrations | ✅ Trong |
| 3 | Self-Hosting | Hướng dẫn tự cài Langfuse lên máy chủ của mình (Docker / Kubernetes / VM) thay vì dùng bản Cloud | https://langfuse.com/self-hosting | ❌ Ngoài |
| 4 | Guides | Cookbook — công thức làm đúng một việc cụ thể theo tình huống | https://langfuse.com/guides | ❌ Ngoài |
| 5 | Academy | Khóa học có lộ trình, đi từ số 0 | https://langfuse.com/academy | ❌ Ngoài |
| 6 | Workshop | Buổi thực hành theo chủ đề, làm bài tập tay | https://langfuse.com/workshop | ❌ Ngoài |
| 7 | Library | Bài viết kiến thức chung về làm AI, không riêng Langfuse | https://langfuse.com/library | ❌ Ngoài |

---

## Cấu trúc repo

```
Langfuse/
├── Overall.md
├── Docs/            
│   ├── README.md
│   ├── SOURCES.md
│   ├── 01-observability/
│   ├── 02-prompt-management/
│   ├── 03-evaluation/
│   ├── 04-more/
│   ├── 05-platform/
│   ├── 06-glossary/
│   └── 07-integrations/
└── Integrations/  
```

---

## Định vị Langfuse

Nền tảng vận hành và kiểm soát chất lượng cho ứng dụng LLM — đứng *cạnh* bot để theo dõi, đo chi phí, quản prompt, chấm điểm. **Không viết ra bot** và **không chạy bot** thay mình.

---

## Ghi chú

- Tab **Docs** đào sâu các mục 01–06; mục 07 là link chéo sang Integrations.
- Tab **Integrations** có nội dung riêng ở thư mục `Integrations/` tại gốc — soạn sau.
- Năm tab ngoài phạm vi: đọc theo URL ở bảng trên khi cần, không tổng hợp lại trong repo.