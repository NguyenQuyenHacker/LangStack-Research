# LangGraph — Research Notes

**Nền tảng là gì**: LangGraph là engine orchestration bậc thấp của hệ Lang — thay vì mô tả agent bằng một vòng lặp cố định như LangChain, nó cho dựng đồ thị tường minh gồm state (schema dữ liệu dùng chung), node (hàm xử lý một bước), và edge (luồng chuyển giữa các bước), rồi chạy đồ thị đó theo mô hình Pregel/BSP (bulk-synchronous, chạy theo "super-step"). Nó đi kèm hai cơ chế bền vững hoá: checkpointer lưu trạng thái theo từng bước trong một thread (phục vụ resume, time-travel, human-in-the-loop), và store lưu dữ liệu xuyên thread (phục vụ long-term memory). `create_agent` của LangChain thực chất compile xuống một đồ thị LangGraph — nắm LangGraph là nắm cơ chế thật sự chạy bên dưới mọi agent LangChain.

**Bộ note này dùng để làm gì**: Nghiên cứu LangGraph (Python) theo docs chính thức `https://docs.langchain.com/oss/python/langgraph/`, giữ tầng cơ chế mà `LangChain/` không đi sâu: đồ thị mà `create_agent` compile ra, engine Pregel chạy đồ thị đó, và cấu trúc dữ liệu bền vững bên dưới (checkpoint, store). Chỗ nào `LangChain/` đã trình bày ở mức agent thì ở đây chỉ viết cơ chế rồi cross-link, không lặp lại nội dung. Phạm vi dừng ở graph/functional API và runtime — `studio`, `ui`, `deploy`, `observability`, `changelog-py`, và các bài tutorial (agentic-rag, sql-agent, case-studies) nằm ngoài phạm vi nghiên cứu, lý do loại và đích cross-link ghi ở `SOURCES.md`.

## Cấu trúc thư mục

### 01-foundations (LangGraph là gì, tư duy node/state, workflow vs agent)
| File | Nội dung |
|---|---|
| `01-01-overview.md` | LangGraph là gì, vị trí trong hệ Lang (bảng so sánh Deep Agents/LangChain/LangGraph/LangSmith), năm năng lực lõi, khi nào dùng trực tiếp vs qua LangChain agents. |
| `01-02-thinking-in-langgraph.md` | Mô hình node/state/Command qua ví dụ agent xử lý email, bốn loại node, xử lý lỗi theo loại, độ mịn của node. |
| `01-03-workflows-vs-agents.md` | Năm khuôn workflow (prompt chaining, parallelization, routing, orchestrator-worker, evaluator-optimizer) và agent loop với `ToolNode`/`ToolRuntime`. |

### 02-persistence (checkpointer, store, cách nối trí nhớ vào graph)
| File | Nội dung |
|---|---|
| `02-01-persistence.md` | Tổng quan checkpointer vs store, bốn vấn đề thường gặp. |
| `02-02-checkpointers.md` | Thread/checkpoint/super-step, đọc/sửa state, durability modes, chọn backend, tự viết checkpointer. |
| `02-03-stores.md` | Namespace/key/value, `put`/`search`, semantic search, custom store. |
| `02-04-add-memory.md` | Trim/delete/summarize trí nhớ ngắn hạn, quản lý database bộ nhớ. |

### 03-streaming (stream mức graph, event streaming)
| File | Nội dung |
|---|---|
| `03-01-streaming.md` | Bảy stream mode, khác biệt shape v1/v2, cách lấy từng loại dữ liệu. |
| `03-02-event-streaming.md` | `stream_events`, pipeline transformer, các projection (`stream.messages`, `.output`, `.values`...). |

**03-streaming/examples/** (code mẫu chạy được, không phải note)
| File | Nội dung |
|---|---|
| `README.md` | Index ánh xạ 9 script Python + `graph.py` tới các mục tương ứng trong `03-01-streaming.md`. |

### 04-human-in-the-loop (dừng graph chờ người, quay lại quá khứ)
| File | Nội dung |
|---|---|
| `04-01-interrupts.md` | Cơ chế interrupt/resume, quy tắc dùng, năm mẫu dùng thường gặp, subgraph. |
| `04-02-time-travel.md` | Replay vs fork, tham số `as_node`, time travel với subgraph. |

### 05-subgraphs (đồ thị lồng đồ thị)
| File | Nội dung |
|---|---|
| `05-01-subgraphs.md` | Hai cách nối state cha-con, ba chế độ checkpointer cho subgraph, xem state/output subgraph. |

### 06-frontend (nối graph với UI)
| File | Nội dung |
|---|---|
| `06-01-frontend-overview.md` | Kiến trúc frontend SDK, bảng ánh xạ khái niệm runtime sang UX — file tổng quan cho nhánh này. |
| `06-02-graph-execution.md` | `useStream`, `useMessages`, bốn trạng thái node trên UI. |
| `06-03-custom-stream-channels.md` | `useExtension` vs `useChannel` để tự định nghĩa kênh stream. |

### 07-production (cấu trúc ứng dụng, test, tương thích ngược)
| File | Nội dung |
|---|---|
| `07-01-application-structure.md` | Cấu trúc thư mục ứng dụng, ba khóa lõi của `langgraph.json`, dependencies, biến môi trường. |
| `07-02-test.md` | Ba khuôn test graph (full flow, một node, một đoạn giữa). |
| `07-03-backward-compatibility.md` | Trục trặc kỹ thuật/nghiệp vụ khi đổi version, bẫy riêng của Functional API. |

### 08-graph-api (dựng graph tường minh bằng Graph API)
| File | Nội dung |
|---|---|
| `08-01-choosing-apis.md` | So sánh Graph API vs Functional API, khi nào dùng cái nào. |
| `08-02-graph-api.md` | State/schema/reducer, `Send`, `Command`, runtime context, graph migrations. |
| `08-03-use-graph-api.md` | Công thức retry/timeout, chuỗi tuần tự, rẽ nhánh song song, map-reduce, async, trực quan hóa. |

### 09-functional-api (dựng graph bằng decorator thay vì node/edge)
| File | Nội dung |
|---|---|
| `09-01-functional-api.md` | `@entrypoint`/`@task`, determinism, idempotency. |
| `09-02-use-functional-api.md` | Song song, retry/timeout/cache, resume sau lỗi, human-in-the-loop, chatbot nhớ hội thoại. |

### 10-runtime (engine Pregel bên dưới cùng)
| File | Nội dung |
|---|---|
| `10-01-pregel-runtime.md` | Actors/channels, BSP step lifecycle, bốn loại channel (`LastValue`, `Topic`, `BinaryOperatorAggregate`, `DeltaChannel`). |
| `10-02-fault-tolerance.md` | Retry/timeout/error handler, graceful shutdown. |

### assets
`assets/images/` — 9 ảnh PNG được `01-02`, `01-03`, `04-02`, `06-01` nhúng vào; `assets/diagrams/` hiện rỗng.

## Thứ tự đọc gợi ý

Thư mục đánh số theo mục lục gốc của docs, không theo thứ tự đọc hợp lý — nên đi theo tầng cơ chế: API dựng graph → engine chạy → substrate lưu trạng thái → giao diện.

1. **01-foundations** — nắm mô hình node/state/Command trước tiên.
2. **08-graph-api** rồi **09-functional-api** — hai cách dựng graph, đọc `08-01-choosing-apis.md` để biết chọn cái nào.
3. **10-runtime** — engine Pregel chạy graph bên dưới cả hai API.
4. **02-persistence** — checkpointer/store, nền cho human-in-the-loop và memory.
5. **03-streaming**, **04-human-in-the-loop**, **05-subgraphs** — các cơ chế vận hành graph khi đã chạy được.
6. **06-frontend**, **07-production** — tra cứu khi cần nối UI hoặc đưa lên production.

## Quy ước

- `status: draft` trong frontmatter — toàn bộ 24 file nội dung đều draft; nội dung đã viết đầy đủ theo template dù nhãn status chưa phản ánh đúng mức hoàn thiện.
- `(dựng lại)` — đánh dấu nội dung không lấy trực tiếp từ docs, xuất hiện ở 6 file (`01-01-overview.md`, `01-02-thinking-in-langgraph.md`, `03-01-streaming.md`, `08-01-choosing-apis.md`, `08-02-graph-api.md`, `09-02-use-functional-api.md`).
- `!Note` — cảnh báo lỗi im lặng/hành vi tinh vi, xuất hiện ở 17/24 file.

## Nguồn

Ánh xạ nguồn và bản đồ chống trùng ở [`SOURCES.md`](SOURCES.md).
