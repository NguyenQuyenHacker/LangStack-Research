# LangChain — Research

Nghiên cứu LangChain v1 (Python) theo docs chính thức `https://docs.langchain.com/oss/python/langchain/`. Viết cho kỹ sư đã biết Python và đã dùng LangChain cơ bản, nhưng chưa nắm cơ chế bên dưới. Cấu trúc thư mục chia theo mô hình khái niệm của v1 — model layer tách khỏi harness, mọi thứ liên quan tới context window gom một chỗ — thay vì bám theo mục lục docs.

Ánh xạ nguồn ở [`SOURCES.md`](SOURCES.md).

## Mục lục

### 01 — Foundations
- [01-01 Tổng quan](01-foundations/01-01-overview.md)
- [01-02 Kiến trúc thành phần](01-foundations/01-02-component-architecture.md)

### 02 — Model layer
- [02-01 Models](02-model-layer/02-01-models.md)
- [02-02 Messages](02-model-layer/02-02-messages.md)
- [02-03 Structured output](02-model-layer/02-03-structured-output.md)
- [02-04 Streaming](02-model-layer/02-04-streaming.md)
- [02-05 Event streaming](02-model-layer/02-05-event-streaming.md)

### 03 — Harness
- [03-01 Agents](03-harness/03-01-agents.md)
- [03-02 Tools](03-harness/03-02-tools.md)
- [03-03 Middleware — tổng quan](03-harness/03-03-middleware/03-03-middleware-overview.md)
- [03-04 Middleware dựng sẵn](03-harness/03-03-middleware/03-04-middleware-built-in.md)
- [03-05 Middleware tự viết](03-harness/03-03-middleware/03-05-middleware-custom.md)
- [03-06 Guardrails](03-harness/03-06-guardrails.md)
- [03-07 Human-in-the-loop](03-harness/03-07-human-in-the-loop.md)
- [03-08 Runtime](03-harness/03-08-runtime.md)
- [03-09 Context engineering](03-harness/03-09-context-engineering.md)

### 04 — Context & memory
- [04-01 Memory — tổng quan](04-context-memory/04-01-memory.md)
- [04-02 Short-term memory](04-context-memory/04-02-short-term-memory.md)
- [04-03 Long-term memory](04-context-memory/04-03-long-term-memory.md)

### 05 — MCP
- [05-01 Model Context Protocol](05-MCP/05-01-mcp.md)

### 06 — Multi-agent
- [06-01 Tổng quan](06-multi-agent/06-01-overview.md)
- [06-02 Subagents](06-multi-agent/06-02-subagents.md)
- [06-03 Handoffs](06-multi-agent/06-03-handoffs.md)
- [06-04 Skills](06-multi-agent/06-04-skills.md)
- [06-05 Router](06-multi-agent/06-05-router.md)
- [06-06 Custom workflow](06-multi-agent/06-06-custom-workflow.md)

### 07 — Interfaces
- [07-01 Frontend — tổng quan](07-interfaces/07-01-frontend-overview.md)
- [07-02 Frontend patterns](07-interfaces/07-02-frontend-patterns.md)
- [07-03 Frontend integrations](07-interfaces/07-03-frontend-integrations.md)

### 08 — Quality
- [08-01 Testing — tổng quan](08-quality/08-01-testing-overview.md)
- [08-02 Unit testing](08-quality/08-02-unit-testing.md)
- [08-03 Integration testing](08-quality/08-03-integration-testing.md)
- [08-04 Evals](08-quality/08-04-evals.md)

### 09 — Production
- [09-01 Studio](09-production/09-01-studio.md)
- [09-02 Deploy](09-production/09-02-deploy.md)
- [09-03 Observability hooks](09-production/09-03-observability-hooks.md)

### assets
- [`assets/images/`](assets/images/) — screenshot và sơ đồ đã render
- [`assets/diagrams/`](assets/diagrams/) — file nguồn của sơ đồ

## Bảng tiến độ

| Nhóm | Số file | Trạng thái |
|---|---|---|
| 01 — Foundations | 2 | draft |
| 02 — Model layer | 5 | draft |
| 03 — Harness | 9 | draft |
| 04 — Context & memory | 3 | draft |
| 05 — MCP | 1 | draft |
| 06 — Multi-agent | 6 | draft |
| 07 — Interfaces | 3 | draft |
| 08 — Quality | 4 | draft |
| 09 — Production | 3 | draft |
| **Tổng** | **36** | **draft** |
