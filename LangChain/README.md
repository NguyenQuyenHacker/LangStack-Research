# LangChain — Research Notes

**Nền tảng là gì**: LangChain là framework Python cho lớp harness của agent LLM — nó chuẩn hoá cách gọi model, khai báo tool, và điều khiển vòng lặp suy luận (system prompt → gọi model → gọi tool → lặp) qua `create_agent` và middleware, thay vì để mỗi dự án tự viết lại phần lặp lại này. Nó không tự quản lý orchestration đồ thị bậc thấp — đó là việc của LangGraph, framework nó dùng làm engine bên dưới — và không tự làm observability/dashboard — đó là việc của Langfuse. Điểm mạnh của LangChain nằm ở bộ nguyên liệu dựng sẵn: hàng trăm tool tích hợp, middleware xử lý các vấn đề lặp lại (tóm tắt hội thoại, PII, retry, human-in-the-loop), và một API model thống nhất bất kể provider.

**Bộ note này dùng để làm gì**: Nghiên cứu LangChain v1 (Python) theo docs chính thức `https://docs.langchain.com/oss/python/langchain/`, viết cho kỹ sư đã biết Python và dùng LangChain cơ bản (đã gọi được `create_agent`) nhưng chưa nắm cơ chế bên dưới — vì sao middleware chạy theo thứ tự đó, streaming khác gì giữa `stream()` và `stream_events()`, tool error được xử lý ra sao. Cấu trúc thư mục chia theo mô hình khái niệm của v1 (model layer tách khỏi harness, mọi thứ liên quan context window gom một chỗ) thay vì bám mục lục docs gốc, và dừng lại ở mức API + cơ chế của riêng LangChain: orchestration đồ thị bậc thấp thuộc `LangGraph/`, dashboard/scoring/tracing thuộc `Langfuse/`.

## Cấu trúc thư mục

### 01-foundations (LangChain là gì, các thành phần lắp thành agent)
| File | Nội dung |
|---|---|
| `01-01-overview.md` | Định nghĩa LangChain qua công thức "Agent = Model + Harness" (system prompt, tools, middleware), ví dụ tối thiểu dùng `create_agent`. |
| `01-02-component-architecture.md` | Bảy nhóm thành phần (models, tools, agents, memory, retrievers, document processing, vector stores) và ba kiến trúc thường gặp (RAG, agent-với-tool, multi-agent). |

### 02-model-layer (gọi model, định dạng message, ép output có cấu trúc, streaming)
| File | Nội dung |
|---|---|
| `02-01-models.md` | Khởi tạo chat model bằng `init_chat_model`, bảng tham số hay dùng, ba cách gọi model (invoke/stream/batch). |
| `02-02-messages.md` | Bốn loại message (System/Human/AI/Tool) là đơn vị context của model stateless, cấu trúc Role + Content + Metadata. |
| `02-03-structured-output.md` | Tham số `response_format` ép model trả JSON theo schema, hai chiến lược ProviderStrategy vs ToolStrategy. |
| `02-04-streaming.md` | API streaming cấp thấp `stream`/`astream` kế thừa từ Pregel của LangGraph, ba `stream_mode`, khác biệt v1/v2. |
| `02-05-event-streaming.md` | API `stream_events` (khuyến nghị từ v1.3), khái niệm "projection" — nhánh dữ liệu đã phân loại sẵn, so với `stream()` thô. |

### 03-harness (vòng lặp agent, tool, middleware, guardrail, runtime)
| File | Nội dung |
|---|---|
| `03-01-agents.md` | Agent = model gọi tool trong vòng lặp; bảng tham số đầy đủ của `create_agent`. |
| `03-02-tools.md` | Khai báo tool bằng decorator `@tool`, lấy dữ liệu runtime, kiểu giá trị trả về, xử lý lỗi tool. |
| `03-06-guardrails.md` | Dùng middleware kiểm soát nội dung tại bốn điểm chặn quanh model/tool call, phân biệt luật cứng vs LLM xét. |
| `03-07-human-in-the-loop.md` | `HumanInTheLoopMiddleware` chặn agent chờ người duyệt tool call, bốn loại quyết định (approve/edit/reject/respond). |
| `03-08-runtime.md` | `Runtime`/`ToolRuntime` tiêm phụ thuộc vào agent lúc chạy qua `context_schema`. |
| `03-09-context-engineering.md` | Khung trả lời "tại mỗi bước, cái gì được đưa cho LLM và lấy từ đâu", ba loại context (model/tool/life-cycle). |

**03-03-middleware/** (cơ chế hook can thiệp vào vòng lặp agent)
| File | Nội dung |
|---|---|
| `03-03-middleware-overview.md` | Middleware can thiệp vào các hook trước/sau mỗi bước vòng lặp agent, bốn nhóm việc middleware đảm nhận. |
| `03-04-middleware-built-in.md` | 16+3 bản middleware dựng sẵn (Summarization, HITL, PII, ToolRetry...) kèm nhà cung cấp hỗ trợ. |
| `03-05-middleware-custom.md` | Tự viết middleware theo hai trục: node-style/wrap-style hook và decorator/class. |

### 04-context-memory (nhớ trong một phiên vs nhớ xuyên phiên)
| File | Nội dung |
|---|---|
| `04-01-memory.md` | Phân biệt short-term vs long-term memory theo phạm vi nhớ lại — file tổng quan cho nhánh này. |
| `04-02-short-term-memory.md` | Trí nhớ trong một thread bằng `checkpointer` (ví dụ `InMemorySaver`), state lưu/nạp qua `thread_id`. |
| `04-03-long-term-memory.md` | Trí nhớ xuyên thread bằng LangGraph `store`, dữ liệu lưu theo namespace/key, khác checkpointer ở phạm vi sống. |

### 05-MCP (nối tool từ MCP server ngoài)
| File | Nội dung |
|---|---|
| `05-01-mcp.md` | `MultiServerMCPClient` kết nối MCP server, chuyển tool MCP thành tool LangChain, session và interceptor `wrap_tool_call` riêng cho MCP. |

### 06-multi-agent (nhiều agent phối hợp theo năm khuôn mẫu)
| File | Nội dung |
|---|---|
| `06-01-overview.md` | Ba nhu cầu đẩy sang multi-agent, bảng năm pattern (Subagents/Handoffs/Skills/Router/Custom workflow) và khi nào chọn pattern nào — file tổng quan cho nhánh này. |
| `06-02-subagents.md` | Agent chính (supervisor) gọi agent con stateless như tool, cô lập ngữ cảnh. |
| `06-03-handoffs.md` | Chuyển quyền điều khiển giữa các agent ngang hàng qua biến trạng thái (`current_step`) đổi bằng `Command`. |
| `06-04-skills.md` | Một agent duy nhất nạp prompt chuyên biệt theo yêu cầu qua tool `load_skill`. |
| `06-05-router.md` | Bước phân loại đầu vào rồi định tuyến tới một agent (`Command`) hoặc nhiều agent song song (`Send`). |
| `06-06-custom-workflow.md` | Tự dựng luồng LangGraph `StateGraph`, nhúng agent `create_agent` làm một chặng trong đồ thị. |

### 07-interfaces (nối agent với UI qua streaming)
| File | Nội dung |
|---|---|
| `07-01-frontend-overview.md` | Kiến trúc hai mảnh (backend streaming API + hook `useStream` frontend) và các trạng thái `useStream` cung cấp — file tổng quan cho nhánh này. |
| `07-02-frontend-patterns.md` | 11 mẫu UI dựng sẵn gom bốn nhóm (tin nhắn/tool call/interrupt/lịch sử). |
| `07-03-frontend-integrations.md` | Bốn thư viện UI bên thứ ba cắm vào `useStream` (CopilotKit, AI Elements, assistant-ui, OpenUI). |

### 08-quality (kiểm thử agent)
| File | Nội dung |
|---|---|
| `08-01-testing-overview.md` | Ba cách kiểm thử agent (unit/integration/evals), lý do agent nghiêng về integration test — file tổng quan cho nhánh này. |
| `08-02-unit-testing.md` | Kiểm thử logic agent bằng model giả (`GenericFakeChatModel`) và checkpointer trong RAM, không gọi API thật. |
| `08-03-integration-testing.md` | Kiểm thử với API model thật: marker pytest, quản key, khẳng định theo cấu trúc, cassette HTTP. |
| `08-04-evals.md` | Chấm điểm quỹ đạo thực thi (trajectory) agent bằng đối chiếu tất định hoặc LLM-as-judge (`agentevals`). |

### 09-production (đưa agent lên môi trường thật)
| File | Nội dung |
|---|---|
| `09-01-studio.md` | LangSmith Studio (`langgraph dev`) — giao diện web debug agent local, kiến trúc UI cloud kết nối server local. |
| `09-02-deploy.md` | Đưa agent lên production qua LangSmith Cloud managed hosting; ba lựa chọn khác (Hybrid/Standalone/Self-hosted) chỉ nêu tên. |
| `09-03-observability-hooks.md` | Bật tracing qua LangSmith bằng biến môi trường `LANGSMITH_TRACING` — LangChain không có cơ chế observability riêng. |

### assets
Screenshot và sơ đồ minh hoạ (`assets/images/`, `assets/diagrams/`) được các note ở trên nhúng vào.

## Thứ tự đọc gợi ý

1. **01 — Foundations** trước: nắm mô hình Agent = Model + Harness.
2. **02 — Model layer**: cách gọi model, message, structured output, streaming — nền cho mọi phần sau.
3. **03 — Harness**: vòng lặp agent, tool, middleware — phần lõi của LangChain.
4. **04 — Context & memory**: nối bộ nhớ vào agent.
5. **06 — Multi-agent**: mở rộng từ một agent sang nhiều agent phối hợp.
6. **07 — Interfaces**, **08 — Quality**, **09 — Production**: đọc khi cần triển khai UI, viết test, hoặc đưa lên production.
7. **05 — MCP**: tra cứu khi cần nối tool ngoài qua MCP.

## Quy ước

- `status: draft` trong frontmatter — toàn bộ 36 file đang ở trạng thái draft, chưa có file nào `reviewed`.
- `(dựng lại)` — đánh dấu nội dung không lấy trực tiếp từ docs (chủ yếu khối "Kết quả in ra" tự suy luận), xuất hiện ở 14 file.
- `!Note` — cảnh báo lỗi im lặng, hành vi dễ nhầm, hoặc giới hạn API; xuất hiện dày đặc, tập trung ở `03-02-tools.md`, `05-01-mcp.md`, `09-01-studio.md`, `09-03-observability-hooks.md`.

## Nguồn

Ánh xạ URL docs gốc ở [`SOURCES.md`](SOURCES.md).
