# LangChain — SOURCES

Bảng ánh xạ file note ↔ URL docs gốc của nhánh LangChain, dùng để truy vết nguồn, phát hiện lệch URL, và tra cứu trước khi tạo file note mới.

**Ghi chú chung**
- Nguồn chuẩn: `https://docs.langchain.com/oss/python/langchain/`. Danh mục đầy đủ: `https://docs.langchain.com/llms.txt`.
- Nhãn `[tổng hợp]` trong cột Ghi chú: file không có URL riêng, nội dung tổng hợp từ nhiều trang liên quan (URL đã liệt kê đủ ở cột URL docs gốc).
- Ngày truy cập lấy từ trường `accessed:` trong frontmatter của chính file đó.

## Bảng ánh xạ nguồn

| File | URL docs gốc | Ngày truy cập | Ghi chú |
|---|---|---|---|
| `01-foundations/01-01-overview.md` | https://docs.langchain.com/oss/python/langchain/overview | 2026-07-25 | |
| `01-foundations/01-02-component-architecture.md` | https://docs.langchain.com/oss/python/langchain/component-architecture | 2026-07-25 | |
| `02-model-layer/02-01-models.md` | https://docs.langchain.com/oss/python/langchain/models | 2026-07-25 | |
| `02-model-layer/02-02-messages.md` | https://docs.langchain.com/oss/python/langchain/messages | 2026-07-25 | |
| `02-model-layer/02-03-structured-output.md` | https://docs.langchain.com/oss/python/langchain/structured-output | 2026-07-25 | |
| `02-model-layer/02-04-streaming.md` | https://docs.langchain.com/oss/python/langchain/streaming | 2026-07-25 | |
| `02-model-layer/02-05-event-streaming.md` | https://docs.langchain.com/oss/python/langchain/event-streaming | 2026-07-25 | |
| `03-harness/03-01-agents.md` | https://docs.langchain.com/oss/python/langchain/agents | 2026-07-25 | |
| `03-harness/03-02-tools.md` | https://docs.langchain.com/oss/python/langchain/tools | 2026-07-25 | |
| `03-harness/03-03-middleware/03-03-middleware-overview.md` | https://docs.langchain.com/oss/python/langchain/middleware/overview | 2026-07-24 | |
| `03-harness/03-03-middleware/03-04-middleware-built-in.md` | https://docs.langchain.com/oss/python/langchain/middleware/built-in | 2026-07-24 | |
| `03-harness/03-03-middleware/03-05-middleware-custom.md` | https://docs.langchain.com/oss/python/langchain/middleware/custom | 2026-07-24 | |
| `03-harness/03-06-guardrails.md` | https://docs.langchain.com/oss/python/langchain/guardrails | 2026-07-25 | Guardrails triển khai bằng middleware, không phải cơ chế riêng. |
| `03-harness/03-07-human-in-the-loop.md` | https://docs.langchain.com/oss/python/langchain/human-in-the-loop | 2026-07-25 | |
| `03-harness/03-08-runtime.md` | https://docs.langchain.com/oss/python/langchain/runtime | 2026-07-25 | |
| `03-harness/03-09-context-engineering.md` | https://docs.langchain.com/oss/python/langchain/context-engineering | 2026-07-25 | Trang đầu mối; cơ chế thật nằm ở middleware và tools. |
| `04-context-memory/04-01-memory.md` | https://docs.langchain.com/oss/python/concepts/memory | 2026-07-25 | |
| `04-context-memory/04-02-short-term-memory.md` | https://docs.langchain.com/oss/python/langchain/short-term-memory | 2026-07-25 | |
| `04-context-memory/04-03-long-term-memory.md` | https://docs.langchain.com/oss/python/langchain/long-term-memory | 2026-07-25 | |
| `05-MCP/05-01-mcp.md` | https://docs.langchain.com/oss/python/langchain/mcp | 2026-07-25 | |
| `06-multi-agent/06-01-overview.md` | https://docs.langchain.com/oss/python/langchain/multi-agent/index | 2026-07-25 | |
| `06-multi-agent/06-02-subagents.md` | https://docs.langchain.com/oss/python/langchain/multi-agent/subagents | 2026-07-25 | |
| `06-multi-agent/06-03-handoffs.md` | https://docs.langchain.com/oss/python/langchain/multi-agent/handoffs | 2026-07-25 | |
| `06-multi-agent/06-04-skills.md` | https://docs.langchain.com/oss/python/langchain/multi-agent/skills | 2026-07-25 | |
| `06-multi-agent/06-05-router.md` | https://docs.langchain.com/oss/python/langchain/multi-agent/router | 2026-07-25 | |
| `06-multi-agent/06-06-custom-workflow.md` | https://docs.langchain.com/oss/python/langchain/multi-agent/custom-workflow | 2026-07-25 | |
| `07-interfaces/07-01-frontend-overview.md` | https://docs.langchain.com/oss/python/langchain/frontend/overview | 2026-07-25 | |
| `07-interfaces/07-02-frontend-patterns.md` | https://docs.langchain.com/oss/python/langchain/frontend/{markdown-messages, tool-calling, headless-tools, human-in-the-loop, branching-chat, reasoning-tokens, structured-output, message-queues, join-rejoin, time-travel, generative-ui} | 2026-07-25 | `[tổng hợp]` 11 trang con, mỗi pattern một mục trong file. |
| `07-interfaces/07-03-frontend-integrations.md` | https://docs.langchain.com/oss/python/langchain/frontend/integrations/{overview, copilotkit, ai-elements, assistant-ui, openui} | 2026-07-25 | `[tổng hợp]` 5 trang con. |
| `08-quality/08-01-testing-overview.md` | https://docs.langchain.com/oss/python/langchain/test/index | 2026-07-25 | |
| `08-quality/08-02-unit-testing.md` | https://docs.langchain.com/oss/python/langchain/test/unit-testing | 2026-07-25 | |
| `08-quality/08-03-integration-testing.md` | https://docs.langchain.com/oss/python/langchain/test/integration-testing | 2026-07-25 | |
| `08-quality/08-04-evals.md` | https://docs.langchain.com/oss/python/langchain/test/evals | 2026-07-25 | |
| `09-production/09-01-studio.md` | https://docs.langchain.com/oss/python/langchain/studio | 2026-07-25 | |
| `09-production/09-02-deploy.md` | https://docs.langchain.com/oss/python/langchain/deploy | 2026-07-28 | |
| `09-production/09-03-observability-hooks.md` | https://docs.langchain.com/oss/python/langchain/observability | 2026-07-28 | Chỉ cơ chế callback/tracing LangChain phơi ra. |

## Chống trùng giữa các nhánh

- `03-harness/03-06-guardrails.md` và `03-harness/03-07-human-in-the-loop.md` đặt trong `03-harness/` vì cả hai được triển khai bằng middleware — không tách folder riêng theo tên gọi.
- `08-quality/`: dashboard, dataset và scoring **không viết ở đây** — thuộc `Langfuse/`, ở đây chỉ đặt link nội bộ.
- `09-production/09-03-observability-hooks.md`: chỉ viết cơ chế callback/tracing mà LangChain phơi ra; dashboard và scoring link sang `Langfuse/`.

## Assets

| Thư mục | Nội dung trình bày |
|---|---|
| `assets/images/` | Screenshot và sơ đồ đã render. Đặt tên `<chương>-<mục>-<slug>-<n>.png`, chèn bằng `../assets/images/...`. |
| `assets/diagrams/` | File nguồn của các sơ đồ phức tạp phải xuất ra ảnh. |
