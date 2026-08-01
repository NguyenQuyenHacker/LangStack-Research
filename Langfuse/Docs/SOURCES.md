# Langfuse Docs — Bảng URL nguồn

Phiên bản: **v4** | Accessed: **2026-07-31**

---

## Trong phạm vi nghiên cứu

| File | URL nguồn | Ghi chú |
|------|-----------|---------|
| *(trang chủ Docs)* | https://langfuse.com/docs | Trang index chính |
| *(roadmap)* | https://langfuse.com/docs/roadmap | Lộ trình phát triển |
| `01-observability/01-01-overview.md` | https://langfuse.com/docs/observability/overview | |
| `01-observability/01-02-get-started.md` | https://langfuse.com/docs/observability/get-started | |
| `01-observability/01-03-concepts.md` | https://langfuse.com/docs/observability/data-model | ⚠️ URL là `data-model`, không phải `concepts` |
| `01-observability/01-04-best-practices.md` | https://langfuse.com/docs/observability/best-practices | |
| `01-observability/01-05-features.md` | *(nhóm — xem ghi chú)* | Nhóm không có trang overview. Các trang con dưới `/docs/observability/features/`: sessions, environments, tags, trace-ids-and-distributed-tracing, token-and-cost-tracking, queuing-batching, user-feedback |
| `01-observability/01-06-sdks.md` | https://langfuse.com/docs/observability/sdk/overview | |
| `01-observability/01-07-troubleshooting.md` | https://langfuse.com/docs/observability/troubleshooting-and-faq | |
| `02-prompt-management/02-01-overview.md` | https://langfuse.com/docs/prompt-management/overview | |
| `02-prompt-management/02-02-get-started.md` | https://langfuse.com/docs/prompt-management/get-started | |
| `02-prompt-management/02-03-concepts.md` | https://langfuse.com/docs/prompt-management/data-model | ⚠️ URL là `data-model`, không phải `concepts` |
| `02-prompt-management/02-04-features.md` | *(nhóm — xem ghi chú)* | Nhóm không có trang overview. Các trang con dưới `/docs/prompt-management/features/`: caching, link-to-traces, prompt-version-control, playground |
| `02-prompt-management/02-05-troubleshooting.md` | https://langfuse.com/docs/prompt-management/troubleshooting-and-faq | |
| `03-evaluation/03-01-overview.md` | https://langfuse.com/docs/evaluation/overview | |
| `03-evaluation/03-02-concepts.md` | https://langfuse.com/docs/evaluation/core-concepts | ⚠️ URL là `core-concepts`, không phải `concepts` |
| `03-evaluation/03-03-scores.md` | https://langfuse.com/docs/evaluation/scores/overview | Nhóm Scores có trang overview riêng |
| `03-evaluation/03-04-evaluation-methods.md` | *(nhóm — xem ghi chú)* | Nhóm không có trang overview. Các trang con dưới `/docs/evaluation/evaluation-methods/`: llm-as-a-judge, code-evaluators, annotation-queues, scores-via-ui, scores-via-sdk |
| `03-evaluation/03-05-experiments.md` | *(nhóm — xem ghi chú)* | Nhóm không có trang overview. Các trang con dưới `/docs/evaluation/experiments/`: data-model, datasets, experiments-via-sdk, experiments-via-ui, experiments-ci-cd |
| `04-more/04-01-agent-access.md` | https://langfuse.com/docs/evaluation/agentic-access | ⚠️ URL là `agentic-access` (thuộc nhánh Evaluation) |
| `04-more/04-02-guides.md` | https://langfuse.com/guides#evaluation-tutorials | ⚠️ Ngoài `/docs` — trỏ tới trang Guides |
| `04-more/04-03-troubleshooting.md` | https://langfuse.com/docs/evaluation/troubleshooting-and-faq | Thuộc nhánh Evaluation |
| `05-platform/05-01-metrics.md` | https://langfuse.com/docs/metrics/overview | |
| `05-platform/05-02-api-data-platform.md` | https://langfuse.com/docs/api-and-data-platform/overview | ⚠️ URL là `api-and-data-platform` |
| `05-platform/05-03-assistant.md` | https://langfuse.com/docs/langfuse-assistant | ⚠️ URL là `langfuse-assistant`, không nằm dưới một nhóm |
| `05-platform/05-04-administration.md` | *(nhóm — xem ghi chú)* | Nhóm không có trang overview. Các trang con dưới `/docs/administration/`: authentication-and-sso, rbac, scim-and-org-api, audit-logs, data-deletion, data-retention, llm-connection, spend-alerts, billable-units, troubleshooting-and-faq |
| `05-platform/05-05-security-guardrails.md` | https://langfuse.com/docs/security-and-guardrails | ⚠️ URL là `security-and-guardrails` |
| `05-platform/05-06-versions-compatibility.md` | https://langfuse.com/docs/compatibility | ⚠️ URL là `compatibility` |
| `06-glossary/06-01-glossary.md` | https://langfuse.com/docs/glossary | |
| `07-integrations/07-01-overview.md` | https://langfuse.com/integrations | Link chéo — nội dung gốc ở tab Integrations |

---

## Ngoài phạm vi (đọc khi cần)

| URL | Ghi chú |
|-----|---------|
| https://langfuse.com/self-hosting | Tự host Langfuse |
| https://langfuse.com/guides | Hướng dẫn thực hành |
| https://langfuse.com/academy | Khóa học |
| https://langfuse.com/workshop | Workshop |
| https://langfuse.com/library | Thư viện bài viết |

---

## Ghi chú quan trọng

> **Integrations ↗** trong sidebar Docs là **link chéo** → nội dung thực nằm ở tab riêng `Integrations` trên langfuse.com. Trong repo này, mục `07-integrations/` chỉ ghi tổng quan và dẫn link, **không viết trùng** với nội dung trong `Langfuse/Integrations/`.
>
> **URL không suy được từ tên thư mục.** Các dòng đánh dấu ⚠️ có URL lệch khỏi tên file — ví dụ `concepts` → `data-model`/`core-concepts`, `agent-access` → `agentic-access`, `assistant` → `langfuse-assistant`. Không ghép chuỗi URL từ cấu trúc thư mục; phải kiểm URL thật.
>
> **Năm mục là nhóm, không phải một trang** (Observability Features, Prompt Features, Evaluation Methods, Experiments, Administration): Langfuse không có trang overview riêng cho các nhóm này. Mỗi file note tương ứng sẽ tổng hợp từ nhiều trang con — danh sách trang con đã ghi ở cột Ghi chú. Riêng nhóm **Scores** thì có trang overview (`/docs/evaluation/scores/overview`).
>
> **`04-more/` thuộc nhánh Evaluation**, không phải một sản phẩm riêng — ba trang Agent Access, Guides, Troubleshooting nằm trong mục "More" của Evaluation trên sidebar.