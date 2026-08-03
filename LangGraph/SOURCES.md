# LangGraph — SOURCES

Bảng ánh xạ file note ↔ URL docs gốc của nhánh LangGraph, dùng để truy vết nguồn, phát hiện lệch URL, và kiểm tra trùng nội dung với `LangChain/`/`Langfuse/` trước khi viết note mới.

**Ghi chú chung**
- Nguồn chuẩn: `https://docs.langchain.com/oss/python/langgraph/`.
- Sidebar nhánh LangGraph đối chiếu ngày **2026-07-28** từ nav HTML của trang docs và `sitemap.xml`.
- Nhãn `[tổng hợp]` trong cột Ghi chú: file không có URL riêng, tổng hợp từ nhiều trang (URL liệt kê đủ ở cột URL docs gốc), nguồn chi tiết ghi ở mục 7 của chính file đó.
- Ngày truy cập lấy từ `accessed:` trong frontmatter của từng file; ngày trong bảng dưới là ngày đối chiếu sidebar, không phải ngày viết note.
- **Phiên bản:** docs LangGraph không in banner version. Hai mốc đọc được trong thân bài: `graph-api` nói recursion limit mặc định 1000 "từ version 1.0.6"; `checkpointers` yêu cầu `langgraph>=1.1.5` cho một số API. Runtime dự án khai `1.3.14` nhưng **chưa verify** được từ docs — `lc_version` từng note phải ghi đúng giá trị đọc được lúc fetch, không chép sẵn `1.3.14`.

## Bảng ánh xạ nguồn

| File | URL docs gốc | Ngày truy cập | Ghi chú |
|---|---|---|---|
| `01-foundations/01-01-overview.md` | https://docs.langchain.com/oss/python/langgraph/overview | 2026-07-28 | |
| `01-foundations/01-02-thinking-in-langgraph.md` | https://docs.langchain.com/oss/python/langgraph/thinking-in-langgraph | 2026-07-28 | |
| `01-foundations/01-03-workflows-vs-agents.md` | https://docs.langchain.com/oss/python/langgraph/workflows-agents | 2026-07-28 | |
| `01-foundations/01-04-quickstart.md` | https://docs.langchain.com/oss/python/langgraph/quickstart + .../install + .../local-server | 2026-07-28 | `[tổng hợp]` 3 trang; **không thấy file này trên đĩa** ở lần rà soát gần nhất — cần xác nhận. |
| `02-persistence/02-01-persistence.md` | https://docs.langchain.com/oss/python/langgraph/persistence | 2026-07-28 | |
| `02-persistence/02-02-checkpointers.md` | https://docs.langchain.com/oss/python/langgraph/checkpointers | 2026-07-28 | |
| `02-persistence/02-03-stores.md` | https://docs.langchain.com/oss/python/langgraph/stores | 2026-07-28 | |
| `02-persistence/02-04-add-memory.md` | https://docs.langchain.com/oss/python/langgraph/add-memory | 2026-07-28 | `[stub-nặng]` — chỉ cách nối checkpointer + store; khái niệm "hai loại trí nhớ" không viết lại. |
| `03-streaming/03-01-streaming.md` | https://docs.langchain.com/oss/python/langgraph/streaming | 2026-07-28 | `[stub-nặng]` — chỉ phần graph mới có; phần đã có ở LangChain không lặp. |
| `03-streaming/03-02-event-streaming.md` | https://docs.langchain.com/oss/python/langgraph/event-streaming | 2026-07-28 | `[stub-nặng]` — không lặp khái niệm projection đã có ở LangChain. |
| `04-human-in-the-loop/04-01-interrupts.md` | https://docs.langchain.com/oss/python/langgraph/interrupts | 2026-07-28 | |
| `04-human-in-the-loop/04-02-time-travel.md` | https://docs.langchain.com/oss/python/langgraph/use-time-travel | 2026-07-28 | |
| `05-subgraphs/05-01-subgraphs.md` | https://docs.langchain.com/oss/python/langgraph/use-subgraphs | 2026-07-28 | |
| `06-frontend/06-01-frontend-overview.md` | https://docs.langchain.com/oss/python/langgraph/frontend/overview | 2026-07-28 | `[stub-nặng]` — kiến trúc client–agent đã ở LangChain, chỉ viết khác biệt "stream graph ≠ stream chat". |
| `06-frontend/06-02-graph-execution.md` | https://docs.langchain.com/oss/python/langgraph/frontend/graph-execution | 2026-07-28 | |
| `06-frontend/06-03-custom-stream-channels.md` | https://docs.langchain.com/oss/python/langgraph/frontend/custom-stream-channels | 2026-07-28 | |
| `07-production/07-01-application-structure.md` | https://docs.langchain.com/oss/python/langgraph/application-structure | 2026-07-28 | `[stub-nặng]` — chỉ phần cấu trúc app chưa có ở LangChain, phần config link sang đó. |
| `07-production/07-02-test.md` | https://docs.langchain.com/oss/python/langgraph/test | 2026-07-28 | `[stub-nặng]` — chỉ cái đặc thù graph; chiến lược test chung đã ở LangChain. |
| `07-production/07-03-backward-compatibility.md` | https://docs.langchain.com/oss/python/langgraph/backward-compatibility | 2026-07-28 | |
| `08-graph-api/08-01-choosing-apis.md` | https://docs.langchain.com/oss/python/langgraph/choosing-apis | 2026-07-28 | |
| `08-graph-api/08-02-graph-api.md` | https://docs.langchain.com/oss/python/langgraph/graph-api | 2026-07-28 | |
| `08-graph-api/08-03-use-graph-api.md` | https://docs.langchain.com/oss/python/langgraph/use-graph-api | 2026-07-28 | |
| `09-functional-api/09-01-functional-api.md` | https://docs.langchain.com/oss/python/langgraph/functional-api | 2026-07-28 | |
| `09-functional-api/09-02-use-functional-api.md` | https://docs.langchain.com/oss/python/langgraph/use-functional-api | 2026-07-28 | Docs có trang how-to riêng — khác dàn ý ban đầu (dự kiến chỉ 1 trang concept). |
| `10-runtime/10-01-pregel-runtime.md` | https://docs.langchain.com/oss/python/langgraph/pregel | 2026-07-28 | |
| `10-runtime/10-02-fault-tolerance.md` | https://docs.langchain.com/oss/python/langgraph/fault-tolerance | 2026-07-28 | Trang `durable-execution` không còn tồn tại (redirect 308 sang `persistence`, kiểm tra 2026-07-28); nội dung nay rải ở `checkpointers`, `fault-tolerance`, `use-functional-api`. |

## Chống trùng giữa các nhánh

**Nguyên tắc**: `LangChain/` mô tả tầng agent (`create_agent`, middleware, tool). `LangGraph/` mô tả tầng dưới nó — graph mà `create_agent` compile ra, engine chạy graph, cấu trúc dữ liệu bền vững. Mỗi khi một chủ đề đã có nguồn chính bên `LangChain/`, note LangGraph viết ở góc cơ chế/primitive rồi cross-link, không định nghĩa lại khái niệm mức agent. File như vậy đánh dấu `[stub-nặng]` trong bảng trên.

**Tham chiếu chéo theo file**

- `01-01-overview.md` → `../../LangChain/01-foundations/01-01-overview.md`, `../../LangChain/01-foundations/01-02-component-architecture.md`, `../../LangChain/03-harness/03-01-agents.md` — nêu một câu "`create_agent` compile ra graph", không diễn giải lại vòng lặp agent.
- `01-03-workflows-vs-agents.md` → `../../LangChain/06-multi-agent/06-01-overview.md`, `../../LangChain/06-multi-agent/06-06-custom-workflow.md` — bảng 5 pattern multi-agent đã ở đó; ở đây chỉ nói pattern mức graph.
- `01-04-quickstart.md` → `../../LangChain/09-production/09-01-studio.md` — `langgraph dev` và `langgraph.json` đã trình bày đầy đủ ở đó; file này chỉ nêu đủ để chạy được rồi link.
- `08-02-graph-api.md` mục "Runtime context" → `../../LangChain/03-harness/03-08-runtime.md`; mục "Observability and Tracing" → `../../LangChain/09-production/09-03-observability-hooks.md` và `../../Langfuse/README.md` (cả hai chỉ link, không viết lại).
- `08-02-graph-api.md` phần `Command` → `../../LangChain/06-multi-agent/06-03-handoffs.md` (handoff mức agent dựng trên `Command`).
- `08-03-use-graph-api.md` phần retry/timeout chồng với `10-02-fault-tolerance.md` (cùng nhánh) → `08-03` viết mức cấu hình node, `10-02` viết mức runtime; hai file link chéo nhau.
- `09-02-use-functional-api.md` phần human-in-the-loop → `04-01-interrupts.md` (cùng nhánh) và `../../LangChain/03-harness/03-07-human-in-the-loop.md`.
- `09-02-use-functional-api.md` phần memory → `02-04-add-memory.md` (cùng nhánh).
- `10-01-pregel-runtime.md` → `../../LangChain/03-harness/03-08-runtime.md`. Phải phân biệt rõ: trang `pregel` nói về *engine* chạy graph; `03-08` của LangChain nói về *object* `Runtime` mà tool/middleware đọc được — trùng tên, khác vật.
- `10-02-fault-tolerance.md` → `08-03-use-graph-api.md` (cấu hình retry/timeout ở mức node), `02-02-checkpointers.md` (durability mode quyết định resume được tới đâu).
- `02-02-checkpointers.md` → `../../LangChain/04-context-memory/04-02-short-term-memory.md` (checkpointer dùng ở mức agent đã ở đó; ở đây viết cấu trúc dữ liệu và API state bên dưới).
- `02-03-stores.md` → `../../LangChain/04-context-memory/04-03-long-term-memory.md` (đọc/ghi store trong tool đã ở đó; ở đây viết interface `BaseStore` và semantic search).
- `02-04-add-memory.md` → stub, link tới cả ba: `../../LangChain/04-context-memory/04-01-memory.md` (vì sao có hai loại trí nhớ), `04-02-short-term-memory.md`, `04-03-long-term-memory.md`. Phần "quản lý lịch sử tin nhắn" trùng nặng với `04-02` mục 4 (trim/delete/summarize) — không viết lại, chỉ nêu khác biệt khi làm ở mức graph thay vì middleware.
- `02-02-checkpointers.md`, `02-03-stores.md` → `10-02-fault-tolerance.md` (cùng nhánh).
- `03-01-streaming.md` → `../../LangChain/02-model-layer/02-04-streaming.md`. Trùng rất nặng: LangChain đã có ba kênh dữ liệu, định dạng v1/v2, `custom` writer, tắt streaming có chọn lọc — LangGraph chỉ viết phần *graph mới có*: `subgraphs=True`, lọc theo node, quan hệ giữa super-step và lần phát dữ liệu.
- `03-02-event-streaming.md` → `../../LangChain/02-model-layer/02-05-event-streaming.md`. Khái niệm projection và bảng projection đã ở đó, không lặp — ở đây viết vòng đời channel, protocol event, cách dựng projection riêng.
- `03-02-event-streaming.md` → `06-03-custom-stream-channels.md` (cùng nhánh, phía client).
- `04-01-interrupts.md` → `../../LangChain/03-harness/03-07-human-in-the-loop.md`. Ranh giới: LangChain viết `interrupt_on` — cấu hình mức agent khai tool nào cần duyệt; file này viết primitive bên dưới, nêu một câu rồi link, không lặp bốn loại quyết định.
- `04-02-time-travel.md` → `02-02-checkpointers.md` (cùng nhánh — time travel chỉ chạy được khi có checkpointer), `../../LangChain/07-interfaces/07-02-frontend-patterns.md` (pattern time-travel phía UI).
- `05-01-subgraphs.md` → `../../LangChain/06-multi-agent/06-02-subagents.md`. Phải nói rõ subgraph ≠ subagent: subagent là agent con lộ ra thành tool cho model gọi; subgraph là cấu trúc lồng graph, cha gọi tất định. Trang docs `use-subgraphs` có nhắc subagent-as-tool → phần đó stub + link.
- `05-01-subgraphs.md` → `../../LangChain/06-multi-agent/06-01-overview.md`, `../../LangChain/06-multi-agent/06-06-custom-workflow.md`.
- `05-01-subgraphs.md` → `03-01-streaming.md`, `02-02-checkpointers.md` (cùng nhánh).
- `06-01-frontend-overview.md` → `../../LangChain/07-interfaces/07-01-frontend-overview.md`. Kiến trúc và `useStream` đã ở đó — stub một đoạn, link, chỉ viết khác biệt "stream graph ≠ stream chat".
- `06-02-graph-execution.md`, `06-03-custom-stream-channels.md` → `../../LangChain/07-interfaces/07-02-frontend-patterns.md` (đối chiếu xem pattern nào đã có), `03-02-event-streaming.md` (cùng nhánh — phía server của cùng cơ chế).
- `07-01-application-structure.md` → `../../LangChain/09-production/09-01-studio.md` mục 4.4 đã trình bày `langgraph.json`; file này chỉ viết phần cấu trúc app chưa có ở đó, phần config thì link.
- `07-02-test.md` → `../../LangChain/08-quality/08-01-testing-overview.md`, `08-02-unit-testing.md`. Chiến lược test đã ở đó; ở đây chỉ viết cái đặc thù graph: test một node, chạy tới node X rồi dừng.
- `07-03-backward-compatibility.md` → `02-02-checkpointers.md`, `08-02-graph-api.md` (mục graph migration).
- Ngoài phạm vi, chỉ link không tạo file: [studio](https://docs.langchain.com/oss/python/langgraph/studio) → `../../LangChain/09-production/09-01-studio.md`; [deploy](https://docs.langchain.com/oss/python/langgraph/deploy) → `../../LangChain/09-production/09-02-deploy.md`; [observability](https://docs.langchain.com/oss/python/langgraph/observability) → `../../LangChain/09-production/09-03-observability-hooks.md` và `../../Langfuse/README.md`; [ui](https://docs.langchain.com/oss/python/langgraph/ui) → `06-01-frontend-overview.md`.

## Assets

| Thư mục | Nội dung trình bày |
|---|---|
| `assets/images/` | Screenshot và sơ đồ đã render. Đặt tên `<chương>-<mục>-<slug>-<n>.png`, chèn bằng `../assets/images/...`. |
| `assets/diagrams/` | File nguồn Mermaid của các sơ đồ phải xuất ra ảnh. |
