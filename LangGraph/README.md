# LangGraph — Research

Nghiên cứu LangGraph (Python) theo docs chính thức `https://docs.langchain.com/oss/python/langgraph/`. Nhánh này giữ tầng orchestration bậc thấp — graph mà `create_agent` compile ra, engine chạy graph, cấu trúc dữ liệu bền vững bên dưới. Chỗ nào `LangChain/` đã trình bày ở mức agent thì ở đây chỉ viết cơ chế rồi cross-link.

Cấu trúc chia theo tầng cơ chế (API dựng graph → engine chạy → substrate lưu trạng thái → giao diện), không bám mục lục docs.

Quy ước viết ở [`../CONVENTIONS.md`](../CONVENTIONS.md). Thuật ngữ ở [`../GLOSSARY.md`](../GLOSSARY.md). Ánh xạ nguồn và bản đồ chống trùng ở [`SOURCES.md`](SOURCES.md).

## Mục lục

### 01 — Foundations
- [01-01 Tổng quan LangGraph](01-foundations/01-01-overview.md)
- [01-02 Tư duy theo LangGraph](01-foundations/01-02-thinking-in-langgraph.md)
- [01-03 Workflow và agent](01-foundations/01-03-workflows-vs-agents.md)

### 02 — Graph API
- [02-01 Chọn giữa Graph API và Functional API](08-graph-api/08-01-choosing-apis.md)
- [02-02 Graph API](08-graph-api/08-02-graph-api.md)
- [02-03 Dùng Graph API](08-graph-api/08-03-use-graph-api.md)

### 03 — Functional API
- [03-01 Functional API](09-functional-api/09-01-functional-api.md)
- [03-02 Dùng Functional API](09-functional-api/09-02-use-functional-api.md)

### 04 — Runtime
- [04-01 Runtime Pregel](10-runtime/10-01-pregel-runtime.md)
- [04-02 Fault tolerance](10-runtime/10-02-fault-tolerance.md)

### 05 — Persistence
- [05-01 Persistence](02-persistence/02-01-persistence.md)
- [05-02 Checkpointer](02-persistence/02-02-checkpointers.md)
- [05-03 Store](02-persistence/02-03-stores.md)
- [05-04 Nối trí nhớ vào graph](02-persistence/02-04-add-memory.md)

### 06 — Streaming
- [06-01 Streaming mức graph](03-streaming/03-01-streaming.md)
- [06-02 Event streaming mức graph](03-streaming/03-02-event-streaming.md)

### 07 — Human-in-the-loop
- [07-01 Interrupt](04-human-in-the-loop/04-01-interrupts.md)
- [07-02 Time travel](04-human-in-the-loop/04-02-time-travel.md)

### 08 — Subgraphs
- [08-01 Subgraph](05-subgraphs/05-01-subgraphs.md)

### 09 — Frontend
- [09-01 Frontend — tổng quan](06-frontend/06-01-frontend-overview.md)
- [09-02 Graph execution trên UI](06-frontend/06-02-graph-execution.md)
- [09-03 Custom stream channel](06-frontend/06-03-custom-stream-channels.md)

### 10 — Production
- [10-01 Cấu trúc ứng dụng](07-production/07-01-application-structure.md)
- [10-02 Test graph](07-production/07-02-test.md)
- [10-03 Tương thích ngược](07-production/07-03-backward-compatibility.md)

### assets
- [`assets/images/`](assets/images/) — screenshot và sơ đồ đã render
- [`assets/diagrams/`](assets/diagrams/) — file nguồn của sơ đồ

## Bảng tiến độ

Mọi file hiện là **khung rỗng** — có frontmatter, 7 heading của template và ghi chú ranh giới, chưa có nội dung. `accessed` để trống và `lc_version: unknown` cho tới khi fetch trang tương ứng.

| Nhóm | Số file | Trạng thái |
|---|---|---|
| 01 — Foundations | 4 | khung |
| 02 — Graph API | 3 | khung |
| 03 — Functional API | 2 | khung |
| 04 — Runtime | 2 | khung |
| 05 — Persistence | 4 | khung |
| 06 — Streaming | 2 | khung |
| 07 — Human-in-the-loop | 2 | khung |
| 08 — Subgraphs | 1 | khung |
| 09 — Frontend | 3 | khung |
| 10 — Production | 3 | khung |
| **Tổng** | **26** | **khung** |

## Không viết ở nhánh này

`studio`, `ui`, `deploy`, `observability`, `changelog-py` và các trang tutorial (`agentic-rag`, `sql-agent`, `case-studies`) — lý do và đích cross-link ghi ở [`SOURCES.md`](SOURCES.md) mục cuối.
