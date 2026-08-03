# Langfuse — SOURCES

Bảng ánh xạ file note ↔ URL docs gốc của nhánh Langfuse (docs phiên bản v4), dùng để truy vết nguồn, phát hiện lệch URL, và kiểm tra trước khi tạo file note mới.

**Ghi chú chung**
- Phiên bản docs: **v4**. Bản gốc chỉ ghi một ngày truy cập chung cho toàn bộ đợt fetch (**2026-07-31**), không có ngày riêng theo từng file — cột Ngày truy cập bên dưới áp giá trị này cho mọi dòng.
- **Integrations ↗** trong sidebar Docs là link chéo → nội dung thực nằm ở tab riêng `Integrations` trên langfuse.com. Mục `06-integrations/` trong repo chỉ ghi tổng quan và dẫn link, không đào sâu.
- **URL không suy được từ tên thư mục**: các dòng đánh dấu ⚠️ trong bảng có URL lệch khỏi tên file (ví dụ `concepts` → `data-model`/`core-concepts`, `agent-access` → `agentic-access`). Không ghép chuỗi URL từ cấu trúc thư mục.
- **Bốn mục là nhóm nhiều trang, không phải một trang overview riêng**: Observability Features, Prompt Features, Evaluation Methods, Experiments. Riêng nhóm Scores có trang overview (`/docs/evaluation/scores/overview`).
- `01-observability/01-07-troubleshooting.md`: không thấy file này trên đĩa ở lần rà soát gần nhất — có thể đã gộp/xoá, cần xác nhận.
- `02-prompt-management/`: nhánh này có dấu hiệu đang tái cấu trúc riêng (đổi tên/xoá file ngoài phạm vi lần sửa này) — các dòng `02-02-get-started.md`, `02-03-concepts.md`, `02-04-troubleshooting.md` bên dưới giữ nguyên như bảng gốc, chưa đối chiếu lại với đĩa.

## Bảng ánh xạ nguồn

| File | URL docs gốc | Ngày truy cập | Ghi chú |
|---|---|---|---|
| `00-Overview/00-Overview.md` | *(chưa xác định)* | — | File có trên đĩa nhưng chưa từng có dòng trong SOURCES.md gốc — cần bổ sung URL nguồn. |
| `01-observability/01-01-overview.md` | https://langfuse.com/docs/observability/overview | 2026-07-31 | |
| `01-observability/01-02-get-started.md` | https://langfuse.com/docs/observability/get-started | 2026-07-31 | |
| `01-observability/01-03-concepts.md` | https://langfuse.com/docs/observability/data-model | 2026-07-31 | ⚠️ URL thật là `data-model`, không phải `concepts`. |
| `01-observability/01-04-best-practices.md` | https://langfuse.com/docs/observability/best-practices | 2026-07-31 | |
| `01-observability/01-05-features/01-05-00-index.md` | https://langfuse.com/docs/observability/overview | 2026-07-31 | File bản đồ tự tổng hợp, không phải trang nguồn riêng. |
| `01-observability/01-05-features/01-05-01-trace-organization.md` | features/sessions, features/users, features/trace-ids-and-distributed-tracing | 2026-07-31 | Prefix chung: `https://langfuse.com/docs/observability/`. |
| `01-observability/01-05-features/01-05-02-labeling-attributes.md` | features/environments, features/tags, features/metadata, features/releases-and-versioning | 2026-07-31 | |
| `01-observability/01-05-features/01-05-03-structure-content.md` | features/observation-types, features/agent-graphs, features/multi-modality, features/token-and-cost-tracking | 2026-07-31 | |
| `01-observability/01-05-features/01-05-04-data-masking.md` | features/masking | 2026-07-31 | |
| `01-observability/01-05-features/01-05-05-operations.md` | features/sampling, features/log-levels, features/queuing-batching | 2026-07-31 | |
| `01-observability/01-05-features/01-05-06-annotation-feedback.md` | features/comments, features/corrections, features/user-feedback | 2026-07-31 | |
| `01-observability/01-05-features/01-05-07-search-integrations.md` | features/filter-search-bar, features/full-text-search, features/events-table-charts, features/mcp-tracing, features/url | 2026-07-31 | Prefix chung: `https://langfuse.com/docs/observability/`. |
| `01-observability/01-06-sdks.md` | https://langfuse.com/docs/observability/sdk/overview | 2026-07-31 | |
| `01-observability/01-07-troubleshooting.md` | https://langfuse.com/docs/observability/troubleshooting-and-faq | 2026-07-31 | Xem ghi chú chung — không thấy trên đĩa ở lần rà soát gần nhất. |
| `02-prompt-management/02-01-overview.md` | https://langfuse.com/docs/prompt-management/overview | 2026-07-31 | |
| `02-prompt-management/02-02-get-started.md` | https://langfuse.com/docs/prompt-management/get-started | 2026-07-31 | Xem ghi chú chung về 02-prompt-management. |
| `02-prompt-management/02-03-concepts.md` | https://langfuse.com/docs/prompt-management/data-model | 2026-07-31 | ⚠️ URL thật là `data-model`, không phải `concepts`. Xem ghi chú chung về 02-prompt-management. |
| `02-prompt-management/02-03-features/02-03-00-index.md` | https://langfuse.com/docs/prompt-management/overview | 2026-07-31 | File bản đồ tự tổng hợp, theo mẫu `01-05-features/01-05-00-index.md`. |
| `02-prompt-management/02-03-features/02-03-01-dynamic-authoring.md` | features/variables, features/message-placeholders, features/composability, features/config | 2026-07-31 | Prefix chung: `https://langfuse.com/docs/prompt-management/`. |
| `02-prompt-management/02-03-features/02-03-02-versioning-deployment.md` | features/prompt-version-control, features/a-b-testing, features/folders | 2026-07-31 | ⚠️ Tên hiển thị "Version Control" nhưng URL là `prompt-version-control`. |
| `02-prompt-management/02-03-features/02-03-03-runtime-reliability.md` | features/caching, features/guaranteed-availability | 2026-07-31 | |
| `02-prompt-management/02-03-features/02-03-04-iteration-observability.md` | features/playground, features/link-to-traces | 2026-07-31 | Cross-ref Prompt Experiments sang `03-05-experiments.md`, không viết sâu ở đây. |
| `02-prompt-management/02-03-features/02-03-05-automation-integrations.md` | features/agentic-access, features/mcp-server, features/webhooks-slack-integrations, features/github-integration, features/n8n-node | 2026-07-31 | ⚠️ Tên hiển thị "Webhooks" nhưng URL là `webhooks-slack-integrations`. ⚠️ URL `mcp-server` trả về cùng nội dung với `agentic-access`, không có trang kỹ thuật riêng. |
| `02-prompt-management/02-04-troubleshooting.md` | https://langfuse.com/docs/prompt-management/troubleshooting-and-faq | 2026-07-31 | Xem ghi chú chung về 02-prompt-management. |
| `03-evaluation/03-01-overview.md` | https://langfuse.com/docs/evaluation/overview | 2026-07-31 | |
| `03-evaluation/03-02-concepts.md` | https://langfuse.com/docs/evaluation/core-concepts | 2026-07-31 | ⚠️ URL thật là `core-concepts`, không phải `concepts`. |
| `03-evaluation/03-03-scores.md` | https://langfuse.com/docs/evaluation/scores/overview | 2026-07-31 | Nhóm Scores có trang overview riêng, khác các nhóm feature còn lại. |
| `03-evaluation/03-04-evaluation-methods.md` | nhóm — trang con dưới `/docs/evaluation/evaluation-methods/`: llm-as-a-judge, code-evaluators, annotation-queues, scores-via-ui, scores-via-sdk | 2026-07-31 | Không có trang overview riêng. |
| `03-evaluation/03-05-experiments.md` | nhóm — trang con dưới `/docs/evaluation/experiments/`: data-model, datasets, experiments-via-sdk, experiments-via-ui, experiments-ci-cd | 2026-07-31 | Không có trang overview riêng. |
| `04-platform/04-01-metrics.md` | https://langfuse.com/docs/metrics/overview | 2026-07-31 | |
| `04-platform/04-02-api-data-platform.md` | https://langfuse.com/docs/api-and-data-platform/overview | 2026-07-31 | ⚠️ URL thật là `api-and-data-platform`. |
| `04-platform/04-03-security-guardrails.md` | https://langfuse.com/docs/security-and-guardrails | 2026-07-31 | ⚠️ URL thật là `security-and-guardrails`. |
| `05-glossary/05-01-glossary.md` | https://langfuse.com/docs/glossary | 2026-07-31 | |
| `06-integrations/06-01-overview.md` | https://langfuse.com/integrations | 2026-07-31 | Link chéo — nội dung gốc ở tab Integrations, ngoài phạm vi `/docs`. |
