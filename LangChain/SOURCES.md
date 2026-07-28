# SOURCES — ánh xạ file ↔ URL docs gốc

Nguồn chuẩn: `https://docs.langchain.com/oss/python/langchain/` (viết tắt `B`). Danh mục đầy đủ: `https://docs.langchain.com/llms.txt`.

File đánh dấu `[tổng hợp]` không có URL riêng — phải đọc nhiều trang liên quan rồi tự tổng hợp, ghi rõ nguồn ở mục Tham chiếu của file đó.

Ngày truy cập lấy từ trường `accessed:` trong frontmatter của chính file đó.

---

## 01-foundations

Trả lời câu hỏi "LangChain là cái gì và các thành phần ghép với nhau ra sao". Đọc xong nhóm này phải nắm được công thức `Agent = Model + Harness`.

| File | URL docs | Nội dung trình bày | Ngày truy cập |
|---|---|---|---|
| `01-01-overview.md` | `B`overview | Bức tranh tổng thể, công thức Agent = Model + Harness, `create_agent` là gì | 2026-07-25 |
| `01-02-component-architecture.md` | `B`component-architecture | Các thành phần ghép với nhau ra sao, ranh giới trách nhiệm | 2026-07-25 |

---

## 02-model-layer

Tầng giao tiếp trực tiếp với LLM. Đặc điểm chung của cả nhóm: **dùng được kể cả khi không có agent**.

| File | URL docs | Nội dung trình bày | Ngày truy cập |
|---|---|---|---|
| `02-01-models.md` | `B`models | Interface chuẩn hóa giữa các provider, cách đổi model mà không sửa code | 2026-07-25 |
| `02-02-messages.md` | `B`messages | Hệ thống message và content blocks — cấu trúc dữ liệu đi vào/ra khỏi model | 2026-07-25 |
| `02-03-structured-output.md` | `B`structured-output | Ép model trả về schema xác định, các cơ chế triển khai bên dưới và đánh đổi | 2026-07-25 |
| `02-04-streaming.md` | `B`streaming | Stream token, cách dữ liệu chảy qua từng lớp | 2026-07-25 |
| `02-05-event-streaming.md` | `B`event-streaming | Stream ở mức sự kiện — khác gì stream token, dùng khi nào | 2026-07-25 |

---

## 03-harness

Toàn bộ những gì bao quanh model: vòng lặp agent, tools, middleware. Guardrails và human-in-the-loop nằm ở đây vì cả hai **đều được triển khai bằng middleware** — xếp chúng ra folder riêng là chia theo tên gọi chứ không theo cơ chế. Ba file middleware gom vào thư mục con `03-03-middleware/`.

| File | URL docs | Nội dung trình bày | Ngày truy cập |
|---|---|---|---|
| `03-01-agents.md` | `B`agents | `create_agent`, vòng lặp model → tool → model, điều kiện dừng | 2026-07-25 |
| `03-02-tools.md` | `B`tools | Định nghĩa tool, schema tham số, `ToolRuntime`, xử lý lỗi khi tool fail | 2026-07-25 |
| `03-03-middleware/03-03-middleware-overview.md` | `B`middleware/overview | Middleware là gì, chèn vào đâu trong vòng lặp | 2026-07-24 |
| `03-03-middleware/03-04-middleware-built-in.md` | `B`middleware/built-in | Danh mục middleware có sẵn, mỗi cái giải quyết vấn đề gì | 2026-07-24 |
| `03-03-middleware/03-05-middleware-custom.md` | `B`middleware/custom | Tự viết middleware, các hook được phép cài đặt, thứ tự chạy hook | 2026-07-24 |
| `03-06-guardrails.md` | `B`guardrails | Chặn input/output không hợp lệ; chỉ rõ nó là middleware ở dạng nào | 2026-07-25 |
| `03-07-human-in-the-loop.md` | `B`human-in-the-loop | Dừng chờ người duyệt, cơ chế interrupt và resume | 2026-07-25 |
| `03-08-runtime.md` | `B`runtime | Đối tượng runtime truyền qua các lớp, chứa gì và ai đọc được | 2026-07-25 |
| `03-09-context-engineering.md` | `B`context-engineering | Chiến lược nạp/cắt/nén context, chi phí token đi kèm — trang đầu mối, cơ chế nằm ở middleware và tools | 2026-07-25 |

---

## 04-context-memory

Ba file cùng trả lời một câu hỏi: **model nhìn thấy gì trong context window**. Khác nhau ở phạm vi thời gian — trong một phiên, xuyên phiên.

| File | URL docs | Nội dung trình bày | Ngày truy cập |
|---|---|---|---|
| `04-01-memory.md` | `https://docs.langchain.com/oss/python/concepts/memory` | Vì sao có hai loại trí nhớ, ba kiểu trí nhớ dài hạn, hai thời điểm ghi | 2026-07-25 |
| `04-02-short-term-memory.md` | `B`short-term-memory | Lịch sử hội thoại trong một thread: checkpointer, state, cắt/xóa/tóm tắt | 2026-07-25 |
| `04-03-long-term-memory.md` | `B`long-term-memory | Ghi nhớ xuyên thread bằng store: namespace/key, đọc–ghi trong tool | 2026-07-25 |

---

## 05-MCP

Nạp tool từ hệ thống ngoài qua Model Context Protocol.

| File | URL docs | Nội dung trình bày | Ngày truy cập |
|---|---|---|---|
| `05-01-mcp.md` | `B`mcp | Nạp tool từ MCP server, interceptor (`MCPToolCallRequest`), elicitation — khác gì tool định nghĩa tại chỗ | 2026-07-25 |

---

## 06-multi-agent

Năm pattern phối hợp nhiều agent, mỗi file một pattern; file đầu là bảng đối chiếu để biết khi nào chọn cái nào.

| File | URL docs | Nội dung trình bày | Ngày truy cập |
|---|---|---|---|
| `06-01-overview.md` | `B`multi-agent/index | Vì sao cần nhiều agent, chi phí phải trả, bảng so sánh 5 pattern | 2026-07-25 |
| `06-02-subagents.md` | `B`multi-agent/subagents | Agent cha gọi agent con như gọi tool | 2026-07-25 |
| `06-03-handoffs.md` | `B`multi-agent/handoffs | Chuyển quyền điều khiển giữa các agent ngang hàng | 2026-07-25 |
| `06-04-skills.md` | `B`multi-agent/skills | Đóng gói năng lực thành đơn vị tái dùng, hé lộ dần | 2026-07-25 |
| `06-05-router.md` | `B`multi-agent/router | Định tuyến truy vấn tới agent phù hợp | 2026-07-25 |
| `06-06-custom-workflow.md` | `B`multi-agent/custom-workflow | Tự dựng luồng khi 4 pattern trên không vừa | 2026-07-25 |

---

## 07-interfaces

Nối agent với giao diện người dùng.

| File | URL docs | Nội dung trình bày | Ngày truy cập |
|---|---|---|---|
| `07-01-frontend-overview.md` | `B`frontend/overview | Mô hình kết nối agent với UI, hook `useStream` | 2026-07-25 |
| `07-02-frontend-patterns.md` | `B`frontend/{markdown-messages, tool-calling, headless-tools, human-in-the-loop, branching-chat, reasoning-tokens, structured-output, message-queues, join-rejoin, time-travel, generative-ui} | 11 pattern UI, gom thành một file với mỗi pattern một mục | 2026-07-25 |
| `07-03-frontend-integrations.md` | `B`frontend/integrations/{overview, copilotkit, ai-elements, assistant-ui, openui} | Thư viện UI có sẵn, mức độ trừu tượng của từng cái | 2026-07-25 |

---

## 08-quality

Kiểm chứng agent hoạt động đúng. Phần dashboard, dataset và scoring **không viết ở đây** — thuộc `Langfuse/`, ở đây chỉ đặt link nội bộ.

| File | URL docs | Nội dung trình bày | Ngày truy cập |
|---|---|---|---|
| `08-01-testing-overview.md` | `B`test/index | Chiến lược test cho hệ thống có LLM: cái gì test được xác định, cái gì không | 2026-07-25 |
| `08-02-unit-testing.md` | `B`test/unit-testing | Test thành phần đơn lẻ, cách mock model | 2026-07-25 |
| `08-03-integration-testing.md` | `B`test/integration-testing | Test luồng thật có gọi model, quản key, chập chờn, chi phí | 2026-07-25 |
| `08-04-evals.md` | `B`test/evals | Chấm điểm quỹ đạo bằng đối chiếu tất định hoặc LLM chấm | 2026-07-25 |

---

## 09-production

Đưa agent lên môi trường thật và giữ nó chạy được.

| File | URL docs | Nội dung trình bày | Ngày truy cập |
|---|---|---|---|
| `09-01-studio.md` | `B`studio | `langgraph dev` — quan sát và debug agent trực quan trước khi deploy | 2026-07-25 |
| `09-02-deploy.md` | `B`deploy | Các phương án triển khai, kiến trúc từng phương án | 2026-07-28 |
| `09-03-observability-hooks.md` | `B`observability | **Chỉ cơ chế callback/tracing LangChain phơi ra**; dashboard và scoring link sang `Langfuse/` | 2026-07-28 |

---

## assets

| Thư mục | Nội dung trình bày |
|---|---|
| `assets/images/` | Screenshot và sơ đồ đã render. Đặt tên `<chương>-<mục>-<slug>-<n>.png`, chèn bằng `../assets/images/...` |
| `assets/diagrams/` | File nguồn của các sơ đồ phức tạp phải xuất ra ảnh |
