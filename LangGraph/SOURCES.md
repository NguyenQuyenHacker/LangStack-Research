# SOURCES — ánh xạ file ↔ URL docs gốc

Nguồn chuẩn: `https://docs.langchain.com/oss/python/langgraph/`. Cột "URL docs" ghi link đầy đủ, bấm được.

Sidebar nhánh LangGraph được đối chiếu ngày **2026-07-28** từ chính trang docs (nav nhúng trong HTML) và `sitemap.xml`.

File đánh dấu `[tổng hợp]` không có URL riêng — phải đọc nhiều trang rồi tự tổng hợp, ghi rõ nguồn ở mục 7 của file đó.

Ngày truy cập lấy từ trường `accessed:` trong frontmatter của chính file đó. Ngày trong bảng dưới là ngày đối chiếu sidebar, chưa phải ngày viết note.

**Phiên bản:** docs LangGraph không in banner phiên bản trên trang. Hai mốc đọc được trong thân bài: `graph-api` nói recursion limit mặc định thành 1000 *"starting in version 1.0.6"*; `checkpointers` yêu cầu `langgraph>=1.1.5` cho một số API. Runtime dự án khai là `1.3.14` — giá trị này **chưa** verify được từ docs, nên `lc_version` của từng note phải ghi đúng thứ đọc được lúc fetch, không chép sẵn `1.3.14` vào.

---

## Nguyên tắc chống trùng với `LangChain/`

`LangChain/` mô tả tầng agent (`create_agent`, middleware, tool). `LangGraph/` mô tả **tầng dưới nó** — graph mà `create_agent` compile ra, engine chạy graph, cấu trúc dữ liệu bền vững.

Mỗi khi một chủ đề đã có nguồn chính bên `LangChain/`, note LangGraph viết ở **góc cơ chế/primitive** rồi cross-link, không định nghĩa lại khái niệm mức agent. Các file như vậy được đánh dấu **`[stub-nặng]`** trong bảng.

Cross-link đặt ở mục `## Tham chiếu chéo` cuối file, theo đúng cách các note `LangChain/` đang làm. Đường dẫn tương đối từ note LangGraph sang note LangChain có dạng `../../LangChain/<chương>/<file>.md`.

---

## 01-foundations

LangGraph là gì, đứng ở đâu so với `create_agent`, và tư duy dựng graph.

| File | URL docs | Nội dung trình bày | Ngày truy cập |
|---|---|---|---|
| `01-01-overview.md` | [overview](https://docs.langchain.com/oss/python/langgraph/overview) | Định vị: low-level orchestration framework + runtime; trộn bước tất định với bước LLM trong cùng graph; khi nào dùng thẳng LangGraph thay vì `create_agent` | 2026-07-28 |
| `01-02-thinking-in-langgraph.md` | [thinking-in-langgraph](https://docs.langchain.com/oss/python/langgraph/thinking-in-langgraph) | Quy trình 5 bước biến một quy trình nghiệp vụ thành graph: chia bước rời rạc → xác định việc từng bước → thiết kế state → viết node → nối cạnh | 2026-07-28 |
| `01-03-workflows-vs-agents.md` | [workflows-agents](https://docs.langchain.com/oss/python/langgraph/workflows-agents) | Sáu pattern: prompt chaining, parallelization, routing, orchestrator-worker, evaluator-optimizer, agent. Ranh giới workflow tất định vs agent LLM-driven và cách trộn | 2026-07-28 |
| `01-04-quickstart.md` `[tổng hợp]` | [quickstart](https://docs.langchain.com/oss/python/langgraph/quickstart) + [install](https://docs.langchain.com/oss/python/langgraph/install) + [local-server](https://docs.langchain.com/oss/python/langgraph/local-server) | Cài đặt, graph chạy được đầu tiên, `langgraph dev` mức tối thiểu | 2026-07-28 |

**Tham chiếu chéo**

- `01-01` → `../../LangChain/01-foundations/01-01-overview.md`, `../../LangChain/01-foundations/01-02-component-architecture.md`, `../../LangChain/03-harness/03-01-agents.md` — nêu một câu "`create_agent` compile ra graph", không diễn giải lại vòng lặp agent.
- `01-03` → `../../LangChain/06-multi-agent/06-01-overview.md`, `../../LangChain/06-multi-agent/06-06-custom-workflow.md` — bảng 5 pattern multi-agent đã ở đó; ở đây chỉ nói pattern **mức graph**.
- `01-04` → `../../LangChain/09-production/09-01-studio.md` — `langgraph dev` và `langgraph.json` đã trình bày đầy đủ ở đó (mục 4). File này chỉ nêu đủ để chạy được, rồi link.

---

## 08-graph-api

Phần lõi, chỉ LangGraph có. Docs chỉ tách 1 trang concept + 1 trang how-to nên ở đây cũng không chẻ nhỏ hơn.

| File | URL docs | Nội dung trình bày | Ngày truy cập |
|---|---|---|---|
| `08-01-choosing-apis.md` | [choosing-apis](https://docs.langchain.com/oss/python/langgraph/choosing-apis) | Bảng đối chiếu Graph API vs Functional API, cách trộn hai API, cách migrate qua lại | 2026-07-28 |
| `08-02-graph-api.md` | [graph-api](https://docs.langchain.com/oss/python/langgraph/graph-api) | `StateGraph`, state schema và reducer, node, edge, conditional edge, `Send`, `Command`, node caching, graph migration, recursion limit + `RemainingSteps`, visualization | 2026-07-28 |
| `08-03-use-graph-api.md` | [use-graph-api](https://docs.langchain.com/oss/python/langgraph/use-graph-api) | How-to: input/output schema tách rời, private state giữa hai node, runtime configuration, retry policy, node timeout, xử lý lỗi node, graph-wide defaults | 2026-07-28 |

**Tham chiếu chéo**

- `02-02` mục "Runtime context" → `../../LangChain/03-harness/03-08-runtime.md`; mục "Observability and Tracing" → `../../LangChain/09-production/09-03-observability-hooks.md` và `../../Langfuse/README.md`. Cả hai chỉ link, không viết lại.
- `02-02` phần `Command` → `../../LangChain/06-multi-agent/06-03-handoffs.md` (handoff mức agent dựng trên `Command`).
- `02-03` phần retry/timeout **chồng với** `10-02-fault-tolerance.md` của chính nhánh này → `02-03` viết mức cấu hình node, `04-02` viết mức runtime; hai file link chéo nhau.

---

## 09-functional-api

| File | URL docs | Nội dung trình bày | Ngày truy cập |
|---|---|---|---|
| `09-01-functional-api.md` | [functional-api](https://docs.langchain.com/oss/python/langgraph/functional-api) | `@entrypoint`, `@task`, khi nào cần bọc thành task, serialization, tính tất định, idempotency, các bẫy thường gặp | 2026-07-28 |
| `09-02-use-functional-api.md` | [use-functional-api](https://docs.langchain.com/oss/python/langgraph/use-functional-api) | How-to: chạy song song, gọi graph từ entrypoint, gọi entrypoint khác, streaming, retry policy, timeout, cache task, resume sau lỗi, human-in-the-loop, short/long-term memory | 2026-07-28 |

> Sửa so với dàn ý ban đầu: docs **có** trang how-to riêng `use-functional-api`, không phải chỉ một trang concept.

**Tham chiếu chéo**

- `03-02` phần human-in-the-loop → `04-01-interrupts.md` (cùng nhánh) và `../../LangChain/03-harness/03-07-human-in-the-loop.md`.
- `03-02` phần memory → `02-04-add-memory.md` (cùng nhánh).

---

## 10-runtime

Engine chạy graph và hành vi khi có lỗi.

| File | URL docs | Nội dung trình bày | Ngày truy cập |
|---|---|---|---|
| `10-01-pregel-runtime.md` | [pregel](https://docs.langchain.com/oss/python/langgraph/pregel) | Mô hình Pregel/BSP: actor, channel, super-step; ba pha plan–execution–update; quan hệ giữa runtime này và API mức cao | 2026-07-28 |
| `10-02-fault-tolerance.md` | [fault-tolerance](https://docs.langchain.com/oss/python/langgraph/fault-tolerance) | Retry, timeout (wall-clock vs idle), xử lý lỗi, graph defaults, graceful shutdown (`request_drain`), giới hạn đã biết | 2026-07-28 |

> **Sửa quan trọng so với dàn ý ban đầu:** trang [durable-execution](https://docs.langchain.com/oss/python/langgraph/durable-execution) **không còn tồn tại** — trả `308` redirect về [persistence](https://docs.langchain.com/oss/python/langgraph/persistence) (kiểm tra 2026-07-28). Nội dung durable execution nay nằm rải ở `checkpointers` (mục "Durability modes"), `fault-tolerance` (graceful shutdown) và `use-functional-api` (resume sau lỗi). Vì vậy **không tạo** file `durable-execution` riêng; khái niệm này trình bày ở `04-02` và `05-02`, hai chỗ link nhau.

**Tham chiếu chéo**

- `04-01` → `../../LangChain/03-harness/03-08-runtime.md`. **Bắt buộc phân biệt rõ ngay mục 1:** trang `pregel` nói về *engine* chạy graph; `03-08` nói về *object* `Runtime` mà tool/middleware đọc được. Trùng tên, khác vật.
- `04-02` → `08-03-use-graph-api.md` (cấu hình retry/timeout ở mức node), `02-02-checkpointers.md` (durability mode quyết định resume được tới đâu).

---

## 02-persistence

Substrate lưu trạng thái. Gộp luôn `add-memory` vào đây — trang đó là "cách nối checkpointer + store", đúng một tầng với ba file còn lại, tách ra thành chương riêng sẽ vụn.

| File | URL docs | Nội dung trình bày | Ngày truy cập |
|---|---|---|---|
| `02-01-persistence.md` | [persistence](https://docs.langchain.com/oss/python/langgraph/persistence) | Trang đầu mối: checkpointer khác store ở đâu, chọn cái nào, các lỗi thường gặp khi bật persistence | 2026-07-28 |
| `02-02-checkpointers.md` | [checkpointers](https://docs.langchain.com/oss/python/langgraph/checkpointers) | Thread / checkpoint / `StateSnapshot`; `get_state`, `update_state`, `get_state_history`; durability mode; tối ưu dung lượng checkpoint; thư viện InMemory/SQLite/Postgres; tự viết checkpointer | 2026-07-28 |
| `02-03-stores.md` | [stores](https://docs.langchain.com/oss/python/langgraph/stores) | `BaseStore`, namespace/key, `list_namespaces`, semantic search và chọn field để embed, gắn store vào graph, tự viết store | 2026-07-28 |
| `02-04-add-memory.md` `[stub-nặng]` | [add-memory](https://docs.langchain.com/oss/python/langgraph/add-memory) | **Chỉ cách nối** checkpointer + store cho graph nhớ được; quản lý lịch sử tin nhắn ở mức graph; vận hành database. Khái niệm "hai loại trí nhớ" không viết lại | 2026-07-28 |

**Tham chiếu chéo**

- `05-02` → `../../LangChain/04-context-memory/04-02-short-term-memory.md` — checkpointer *dùng ở mức agent* đã ở đó; ở đây viết cấu trúc dữ liệu và API state bên dưới.
- `05-03` → `../../LangChain/04-context-memory/04-03-long-term-memory.md` — đọc/ghi store trong tool đã ở đó; ở đây viết interface `BaseStore` và semantic search.
- `05-04` → stub + link tới cả ba: `../../LangChain/04-context-memory/04-01-memory.md` (vì sao có hai loại trí nhớ), `04-02`, `04-03`. Phần "quản lý lịch sử tin nhắn" trùng nặng với `04-02` mục 4 (trim/delete/summarize) → **không viết lại**, chỉ nêu chỗ khác biệt khi làm ở mức graph thay vì middleware.
- `05-02`, `05-03` → `10-02-fault-tolerance.md` (cùng nhánh).

---

## 03-streaming

| File | URL docs | Nội dung trình bày | Ngày truy cập |
|---|---|---|---|
| `03-01-streaming.md` `[stub-nặng]` | [streaming](https://docs.langchain.com/oss/python/langgraph/streaming) | Stream mode ở **mức graph**: `values`/`updates`/`messages`/`custom`/`debug`, stream từ subgraph, lọc theo node/tag | 2026-07-28 |
| `03-02-event-streaming.md` `[stub-nặng]` | [event-streaming](https://docs.langchain.com/oss/python/langgraph/event-streaming) | Event streaming mức graph: stream state, stream subgraph, resume sau interrupt, vòng đời channel và protocol event, tự dựng projection | 2026-07-28 |

**Tham chiếu chéo**

- `06-01` → `../../LangChain/02-model-layer/02-04-streaming.md`. Trùng **rất nặng**: file LangChain đã có ba kênh dữ liệu, định dạng v1/v2, `custom` writer, tắt streaming có chọn lọc. LangGraph chỉ viết phần *graph mới có*: `subgraphs=True`, lọc theo node, quan hệ giữa super-step và lần phát dữ liệu.
- `06-02` → `../../LangChain/02-model-layer/02-05-event-streaming.md`. Khái niệm projection và bảng projection đã ở đó → không lặp. Ở đây viết vòng đời channel, protocol event, và cách dựng projection riêng.
- `06-02` → `07-03-custom-stream-channels.md` (cùng nhánh, phía client).

---

## 04-human-in-the-loop

| File | URL docs | Nội dung trình bày | Ngày truy cập |
|---|---|---|---|
| `04-01-interrupts.md` | [interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts) | Primitive `interrupt()` và `Command(resume=)`; resume nhiều interrupt song song cùng lúc; các quy tắc của interrupt (node chạy lại từ đầu); interrupt trong subgraph gọi như hàm; debug | 2026-07-28 |
| `04-02-time-travel.md` | [use-time-travel](https://docs.langchain.com/oss/python/langgraph/use-time-travel) | Replay từ một checkpoint vs fork; tìm checkpoint theo node/step; fork ở giữa hai interrupt | 2026-07-28 |

**Tham chiếu chéo**

- `07-01` → `../../LangChain/03-harness/03-07-human-in-the-loop.md`. Ranh giới rõ: file LangChain viết `interrupt_on` — *cấu hình mức agent* khai tool nào cần duyệt. File này viết *primitive bên dưới*. Nêu một câu rồi link, không lặp bốn loại quyết định.
- `07-02` → `02-02-checkpointers.md` (cùng nhánh — time travel chỉ chạy được khi có checkpointer), `../../LangChain/07-interfaces/07-02-frontend-patterns.md` (pattern time-travel phía UI).

---

## 05-subgraphs

| File | URL docs | Nội dung trình bày | Ngày truy cập |
|---|---|---|---|
| `05-01-subgraphs.md` | [use-subgraphs](https://docs.langchain.com/oss/python/langgraph/use-subgraphs) | Hai kiểu giao tiếp cha–con (chung state schema vs gọi như hàm), persistence của subgraph (kế thừa checkpointer hay tự giữ), đọc state lồng nhau, stream output từ subgraph | 2026-07-28 |

**Tham chiếu chéo**

- → `../../LangChain/06-multi-agent/06-02-subagents.md`. **Phải nói thẳng subgraph ≠ subagent**: subagent là agent con lộ ra thành tool cho model gọi; subgraph là cấu trúc lồng graph, cha gọi tất định. Trang docs `use-subgraphs` có nhắc subagent-as-tool → phần đó stub + link.
- → `../../LangChain/06-multi-agent/06-01-overview.md`, `../../LangChain/06-multi-agent/06-06-custom-workflow.md`.
- → `03-01-streaming.md`, `02-02-checkpointers.md` (cùng nhánh).

---

## 06-production

Chỉ ba trang. `studio`, `ui`, `deploy`, `observability` **không viết** — đã có nguồn chính ở nơi khác.

| File | URL docs | Nội dung trình bày | Ngày truy cập |
|---|---|---|---|
| `06-01-application-structure.md` `[stub-nặng]` | [application-structure](https://docs.langchain.com/oss/python/langgraph/application-structure) | Cấu trúc thư mục một app LangGraph, schema `langgraph.json`, khai báo dependency, khai báo graph, biến môi trường | 2026-07-28 |
| `06-02-test.md` `[stub-nặng]` | [test](https://docs.langchain.com/oss/python/langgraph/test) | Test node và edge riêng lẻ, chạy graph một phần (partial execution) | 2026-07-28 |
| `06-03-backward-compatibility.md` | [backward-compatibility](https://docs.langchain.com/oss/python/langgraph/backward-compatibility) | Tương thích ngược khi sửa graph đã có checkpoint đang chạy: tương thích kỹ thuật, tương thích nghiệp vụ, vấn đề bất định | 2026-07-28 |

**Tham chiếu chéo**

- `09-01` → `../../LangChain/09-production/09-01-studio.md` mục 4.4 đã trình bày `langgraph.json`. File này chỉ viết phần *cấu trúc app* chưa có ở đó, phần config thì link.
- `09-02` → `../../LangChain/08-quality/08-01-testing-overview.md`, `08-02-unit-testing.md`. Chiến lược test đã ở đó; ở đây chỉ viết cái đặc thù graph: test một node, chạy tới node X rồi dừng.
- `09-03` → `02-02-checkpointers.md`, `08-02-graph-api.md` (mục graph migration).
- **Ngoài phạm vi, chỉ link, không tạo file:** [studio](https://docs.langchain.com/oss/python/langgraph/studio) → `../../LangChain/09-production/09-01-studio.md`; [deploy](https://docs.langchain.com/oss/python/langgraph/deploy) → `../../LangChain/09-production/09-02-deploy.md`; [observability](https://docs.langchain.com/oss/python/langgraph/observability) → `../../LangChain/09-production/09-03-observability-hooks.md` và `../../Langfuse/README.md`; [ui](https://docs.langchain.com/oss/python/langgraph/ui) → `07-01-frontend-overview.md`.

---

## 07-frontend

Ba trang này **không** trùng với `LangChain/07-interfaces` ngoài trang overview — `graph-execution` và `custom-stream-channels` là nội dung riêng của LangGraph.

| File | URL docs | Nội dung trình bày | Ngày truy cập |
|---|---|---|---|
| `07-01-frontend-overview.md` `[stub-nặng]` | [frontend/overview](https://docs.langchain.com/oss/python/langgraph/frontend/overview) | Kiến trúc client–agent, vì sao stream một graph khác stream một chat | 2026-07-28 |
| `07-02-graph-execution.md` | [frontend/graph-execution](https://docs.langchain.com/oss/python/langgraph/frontend/graph-execution) | Ánh xạ node → card UI, định tuyến token về đúng node, xác định trạng thái node, thanh tiến trình pipeline, xử lý pipeline động | 2026-07-28 |
| `07-03-custom-stream-channels.md` | [frontend/custom-stream-channels](https://docs.langchain.com/oss/python/langgraph/frontend/custom-stream-channels) | Custom channel hoạt động ra sao, `useExtension` vs `useChannel`, chọn cái nào | 2026-07-28 |

**Tham chiếu chéo**

- `10-01` → `../../LangChain/07-interfaces/07-01-frontend-overview.md`. Kiến trúc và `useStream` đã ở đó → stub một đoạn, link, chỉ viết chỗ khác biệt "stream graph ≠ stream chat".
- `10-02`, `10-03` → `../../LangChain/07-interfaces/07-02-frontend-patterns.md` (đối chiếu xem pattern nào đã có), `03-02-event-streaming.md` (cùng nhánh — phía server của cùng cơ chế).

---

## Không đưa vào nhánh này

| Trang docs | Lý do |
|---|---|
| [changelog-py](https://docs.langchain.com/oss/python/langgraph/changelog-py) | Nhật ký phát hành, không phải khái niệm |
| [agentic-rag](https://docs.langchain.com/oss/python/langgraph/agentic-rag), [sql-agent](https://docs.langchain.com/oss/python/langgraph/sql-agent), [case-studies](https://docs.langchain.com/oss/python/langgraph/case-studies) | Tutorial dựng ứng dụng, không phải cơ chế. Cân nhắc mở chương `11-tutorials` ở phiên sau nếu cần |
| [studio](https://docs.langchain.com/oss/python/langgraph/studio), [ui](https://docs.langchain.com/oss/python/langgraph/ui), [deploy](https://docs.langchain.com/oss/python/langgraph/deploy), [observability](https://docs.langchain.com/oss/python/langgraph/observability) | Nguồn chính ở `LangChain/09-production/` và `Langfuse/` |
| Trang về tool, model, message, middleware, structured output | Nguồn chính ở `LangChain/02-model-layer/` và `LangChain/03-harness/` |

---

## assets

| Thư mục | Nội dung trình bày |
|---|---|
| `assets/images/` | Screenshot và sơ đồ đã render. Đặt tên `<chương>-<mục>-<slug>-<n>.png`, chèn bằng `../assets/images/...` |
| `assets/diagrams/` | File nguồn Mermaid của các sơ đồ phải xuất ra ảnh |
