# LangChain — Research

Nghiên cứu LangChain v1 (Python) theo docs chính thức `https://docs.langchain.com/oss/python/langchain/`. Viết cho kỹ sư đã biết Python và đã dùng LangChain cơ bản, nhưng chưa nắm cơ chế bên dưới. Cấu trúc thư mục chia theo mô hình khái niệm của v1 — model layer tách khỏi harness, mọi thứ liên quan tới context window gom một chỗ — thay vì bám theo mục lục docs.

Quy ước viết ở [`../CONVENTIONS.md`](../CONVENTIONS.md). Thuật ngữ ở [`../GLOSSARY.md`](../GLOSSARY.md). Ánh xạ nguồn ở [`SOURCES.md`](SOURCES.md).

## Mục lục

### 01 — Foundations
- [01-01 Tổng quan](01-foundations/01-01-overview.md)
- [01-02 Triết lý thiết kế](01-foundations/01-02-philosophy.md)
- [01-03 Quickstart](01-foundations/01-03-quickstart.md)
- [01-04 Kiến trúc thành phần](01-foundations/01-04-component-architecture.md)
- [01-05 Bố cục package](01-foundations/01-05-package-layout.md)
- [01-06 v0 vs v1](01-foundations/01-06-v0-vs-v1.md)

### 02 — Model layer
- [02-01 Models](02-model-layer/02-01-models.md)
- [02-02 Messages](02-model-layer/02-02-messages.md)
- [02-03 Structured output](02-model-layer/02-03-structured-output.md)
- [02-04 Streaming](02-model-layer/02-04-streaming.md)
- [02-05 Event streaming](02-model-layer/02-05-event-streaming.md)

### 03 — Harness
- [03-01 Agents](03-harness/03-01-agents.md)
- [03-02 Tools](03-harness/03-02-tools.md)
- [03-03 Middleware — tổng quan](03-harness/middleware/03-03-middleware-overview.md)
- [03-04 Middleware dựng sẵn](03-harness/middleware/03-04-middleware-built-in.md)
- [03-05 Middleware tự viết](03-harness/middleware/03-05-middleware-custom.md)
- [03-06 Vòng đời hook](03-harness/03-06-hook-lifecycle.md)
- [03-07 Guardrails](03-harness/03-07-guardrails.md)
- [03-08 Human-in-the-loop](03-harness/03-08-human-in-the-loop.md)
- [03-09 Runtime](03-harness/03-09-runtime.md)

### 04 — Context & memory
- [04-01 Context engineering](04-context-memory/04-01-context-engineering.md)
- [04-02 Short-term memory](04-context-memory/04-02-short-term-memory.md)
- [04-03 Long-term memory](04-context-memory/04-03-long-term-memory.md)

### 05 — Retrieval
- [05-01 Retrieval](05-retrieval/05-01-retrieval.md)
- [05-02 Knowledge base](05-retrieval/05-02-knowledge-base.md)
- [05-03 Ghi chú thiết kế RAG](05-retrieval/05-03-rag-design-notes.md)

### 06 — Multi-agent
- [06-01 Tổng quan](06-multi-agent/06-01-overview.md)
- [06-02 Subagents](06-multi-agent/06-02-subagents.md)
- [06-03 Handoffs](06-multi-agent/06-03-handoffs.md)
- [06-04 Skills](06-multi-agent/06-04-skills.md)
- [06-05 Router](06-multi-agent/06-05-router.md)
- [06-06 Custom workflow](06-multi-agent/06-06-custom-workflow.md)
- [06-07 So sánh pattern](06-multi-agent/06-07-pattern-comparison.md)

### 07 — Interfaces
- [07-01 MCP](07-interfaces/07-01-mcp.md)
- [07-02 Frontend — tổng quan](07-interfaces/07-02-frontend-overview.md)
- [07-03 Frontend patterns](07-interfaces/07-03-frontend-patterns.md)
- [07-04 Frontend integrations](07-interfaces/07-04-frontend-integrations.md)

### 08 — Quality
- [08-01 Testing — tổng quan](08-quality/08-01-testing-overview.md)
- [08-02 Unit testing](08-quality/08-02-unit-testing.md)
- [08-03 Integration testing](08-quality/08-03-integration-testing.md)
- [08-04 Evals](08-quality/08-04-evals.md)
- [08-05 Observability hooks](08-quality/08-05-observability-hooks.md)
- [08-06 Studio](08-quality/08-06-studio.md)
- [08-07 Catalog mã lỗi](08-quality/08-07-error-catalog.md)

### 09 — Production
- [09-01 Deploy](09-production/09-01-deploy.md)
- [09-02 Chi phí & độ trễ](09-production/09-02-cost-and-latency.md)
- [09-03 Bảo mật](09-production/09-03-security.md)

### 10 — Analysis
- [10-01 LangChain vs LangGraph](10-analysis/10-01-langchain-vs-langgraph.md)
- [10-02 So với framework khác](10-analysis/10-02-vs-other-frameworks.md)
- [10-03 Chỉ trích & đánh đổi](10-analysis/10-03-criticism-and-tradeoffs.md)

### 11 — Case studies
- [11-01 SQL agent](11-case-studies/11-01-sql-agent.md)
- [11-02 Voice agent](11-case-studies/11-02-voice-agent.md)
- [11-03 Deep agent from scratch](11-case-studies/11-03-deep-agent-from-scratch.md)
- [11-04 Tutorial multi-agent](11-case-studies/11-04-multi-agent-tutorials.md)
- [11-05 Dự án riêng](11-case-studies/11-05-own-project.md)

### Labs
- [lab-01 Quickstart](labs/lab-01-quickstart/)
- [lab-02 Custom middleware](labs/lab-02-custom-middleware/)
- [lab-03 RAG knowledge base](labs/lab-03-rag-knowledge-base/)
- [lab-04 Multi-agent handoff](labs/lab-04-multi-agent-handoff/)

## Bảng tiến độ

| Nhóm | Số file | Trạng thái |
|---|---|---|
| 01 — Foundations | 6 | scaffold |
| 02 — Model layer | 5 | scaffold |
| 03 — Harness | 9 | scaffold |
| 04 — Context & memory | 3 | scaffold |
| 05 — Retrieval | 3 | scaffold |
| 06 — Multi-agent | 7 | scaffold |
| 07 — Interfaces | 4 | scaffold |
| 08 — Quality | 7 | scaffold |
| 09 — Production | 3 | scaffold |
| 10 — Analysis | 3 | scaffold |
| 11 — Case studies | 5 | scaffold |
| **Tổng** | **55** | **scaffold** |
