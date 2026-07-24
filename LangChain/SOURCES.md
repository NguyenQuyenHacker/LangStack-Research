# SOURCES — ánh xạ file ↔ URL docs gốc

Nguồn chuẩn: `https://docs.langchain.com/oss/python/langchain/` (viết tắt `B`). Danh mục đầy đủ: `https://docs.langchain.com/llms.txt`.

File đánh dấu `[tổng hợp]` không có URL riêng — phải đọc nhiều trang liên quan rồi tự tổng hợp, ghi rõ nguồn ở mục Tham chiếu của file đó.

---

## 01-foundations

Trả lời câu hỏi "LangChain là cái gì và tại sao nó được thiết kế như vậy". Đọc xong nhóm này phải nắm được công thức `Agent = Model + Harness` và biết vì sao LCEL không còn là trung tâm.

| File | URL docs | Nội dung trình bày | Ngày truy cập |
|---|---|---|---|
| `01-01-overview.md` | `B`overview | Bức tranh tổng thể, công thức Agent = Model + Harness, `create_agent` là gì | |
| `01-02-philosophy.md` | `B`philosophy | Nguyên tắc thiết kế: vì sao chọn harness tối giản thay vì framework dày | |
| `01-03-quickstart.md` | `B`quickstart | Agent chạy được đầu tiên, đọc từng dòng để hiểu luồng | |
| `01-04-component-architecture.md` | `B`component-architecture | Các thành phần ghép với nhau ra sao, ranh giới trách nhiệm | |
| `01-05-package-layout.md` | [tổng hợp] | Phân chia `langchain-core` / `langchain` / partner packages / `langgraph`, cái gì nằm ở đâu và vì sao tách | |
| `01-06-v0-vs-v1.md` | `B`changelog-py | LCEL, Chains, `AgentExecutor` đã đi đâu; code v0 cần sửa gì | |

---

## 02-model-layer

Tầng giao tiếp trực tiếp với LLM. Đặc điểm chung của cả nhóm: **dùng được kể cả khi không có agent**. Ranh giới này quan trọng khi so sánh LangChain với việc gọi SDK thuần ở `10-02`.

| File | URL docs | Nội dung trình bày | Ngày truy cập |
|---|---|---|---|
| `02-01-models.md` | `B`models | Interface chuẩn hóa giữa các provider, cách đổi model mà không sửa code | |
| `02-02-messages.md` | `B`messages | Hệ thống message và content blocks — cấu trúc dữ liệu đi vào/ra khỏi model | |
| `02-03-structured-output.md` | `B`structured-output | Ép model trả về schema xác định, các cơ chế triển khai bên dưới và đánh đổi | |
| `02-04-streaming.md` | `B`streaming | Stream token, cách dữ liệu chảy qua từng lớp | |
| `02-05-event-streaming.md` | `B`event-streaming | Stream ở mức sự kiện — khác gì stream token, dùng khi nào | |

---

## 03-harness

Toàn bộ những gì bao quanh model: vòng lặp agent, tools, middleware. Guardrails và human-in-the-loop nằm ở đây vì cả hai **đều được triển khai bằng middleware** — xếp chúng ra folder riêng là chia theo tên gọi chứ không theo cơ chế.

| File | URL docs | Nội dung trình bày | Ngày truy cập |
|---|---|---|---|
| `03-01-agents.md` | `B`agents | `create_agent`, vòng lặp model → tool → model, điều kiện dừng | |
| `03-02-tools.md` | `B`tools | Định nghĩa tool, schema tham số, xử lý lỗi khi tool fail | |
| `03-03-middleware-overview.md` | `B`middleware/overview | Middleware là gì, chèn vào đâu trong vòng lặp | |
| `03-04-middleware-built-in.md` | `B`middleware/built-in | Danh mục middleware có sẵn, mỗi cái giải quyết vấn đề gì | |
| `03-05-middleware-custom.md` | `B`middleware/custom | Tự viết middleware, các hook được phép cài đặt | |
| `03-06-hook-lifecycle.md` | [tổng hợp] + đọc source | Thứ tự thực thi hook, hành vi khi xếp chồng nhiều middleware — phần đào sâu nhất của nhóm | |
| `03-07-guardrails.md` | `B`guardrails | Chặn input/output không hợp lệ; chỉ rõ nó là middleware ở dạng nào | |
| `03-08-human-in-the-loop.md` | `B`human-in-the-loop | Dừng chờ người duyệt, cơ chế interrupt và resume | |
| `03-09-runtime.md` | `B`runtime | Đối tượng runtime truyền qua các lớp, chứa gì và ai đọc được | |

---

## 04-context-memory

Ba file cùng trả lời một câu hỏi: **model nhìn thấy gì trong context window**. Khác nhau ở phạm vi thời gian — trong một lượt, trong một phiên, xuyên phiên.

| File | URL docs | Nội dung trình bày | Ngày truy cập |
|---|---|---|---|
| `04-01-context-engineering.md` | `B`context-engineering | Chiến lược nạp/cắt/nén context, chi phí token đi kèm | |
| `04-02-short-term-memory.md` | `B`short-term-memory | Lịch sử hội thoại trong một phiên, cách cắt khi vượt giới hạn | |
| `04-03-long-term-memory.md` | `B`long-term-memory | Ghi nhớ xuyên phiên, nơi lưu và cách truy xuất lại | |

---

## 05-retrieval

Nạp tri thức ngoài vào context. Chỉ mô tả cơ chế LangChain cung cấp; chiến lược chunking và đánh giá chất lượng gom riêng ở `05-03`.

| File | URL docs | Nội dung trình bày | Ngày truy cập |
|---|---|---|---|
| `05-01-retrieval.md` | `B`retrieval | Interface retriever, luồng từ truy vấn tới tài liệu trả về | |
| `05-02-knowledge-base.md` | `B`knowledge-base | Dựng knowledge base hoàn chỉnh, có code chạy được | |
| `05-03-rag-design-notes.md` | [tổng hợp] | Chunking, citation/source attribution, cách đo chất lượng retrieval | |

---

## 06-multi-agent

Năm pattern phối hợp nhiều agent. Mỗi file mô tả một pattern; file cuối so sánh để biết khi nào chọn cái nào.

| File | URL docs | Nội dung trình bày | Ngày truy cập |
|---|---|---|---|
| `06-01-overview.md` | `B`multi-agent/index | Vì sao cần nhiều agent, chi phí phải trả so với một agent | |
| `06-02-subagents.md` | `B`multi-agent/subagents | Agent cha gọi agent con như gọi tool | |
| `06-03-handoffs.md` | `B`multi-agent/handoffs | Chuyển quyền điều khiển giữa các agent ngang hàng | |
| `06-04-skills.md` | `B`multi-agent/skills | Đóng gói năng lực thành đơn vị tái dùng | |
| `06-05-router.md` | `B`multi-agent/router | Định tuyến truy vấn tới agent phù hợp | |
| `06-06-custom-workflow.md` | `B`multi-agent/custom-workflow | Tự dựng luồng khi 4 pattern trên không vừa | |
| `06-07-pattern-comparison.md` | [tổng hợp] | Bảng so sánh 5 pattern: độ phức tạp, chi phí token, khi nào dùng | |

---

## 07-interfaces

Kết nối agent ra thế giới bên ngoài — tool từ hệ thống khác, và giao diện người dùng.

| File | URL docs | Nội dung trình bày | Ngày truy cập |
|---|---|---|---|
| `07-01-mcp.md` | `B`mcp | Nạp tool từ MCP server, khác gì tool định nghĩa tại chỗ | |
| `07-02-frontend-overview.md` | `B`frontend/overview | Mô hình kết nối agent với UI | |
| `07-03-frontend-patterns.md` | `B`frontend/{markdown-messages, tool-calling, headless-tools, human-in-the-loop, branching-chat, reasoning-tokens, structured-output, message-queues, join-rejoin, time-travel, generative-ui} | 11 pattern UI, gom thành một file với mỗi pattern một mục | |
| `07-04-frontend-integrations.md` | `B`frontend/integrations/{overview, copilotkit, ai-elements, assistant-ui, openui} | Thư viện UI có sẵn, mức độ trừu tượng của từng cái | |

---

## 08-quality

Kiểm chứng agent hoạt động đúng. Phần dashboard, dataset và scoring **không viết ở đây** — thuộc `Langfuse/`, ở đây chỉ đặt link nội bộ.

| File | URL docs | Nội dung trình bày | Ngày truy cập |
|---|---|---|---|
| `08-01-testing-overview.md` | `B`test/index | Chiến lược test cho hệ thống có LLM: cái gì test được xác định, cái gì không | |
| `08-02-unit-testing.md` | `B`test/unit-testing | Test thành phần đơn lẻ, cách mock model | |
| `08-03-integration-testing.md` | `B`test/integration-testing | Test luồng thật có gọi model | |
| `08-04-evals.md` | `B`evals + `B`test/evals | Đánh giá chất lượng đầu ra, thiết kế bộ tiêu chí | |
| `08-05-observability-hooks.md` | `B`observability | **Chỉ cơ chế callback/tracing LangChain phơi ra**; dashboard và scoring link sang `Langfuse/` | |
| `08-06-studio.md` | `B`studio | Công cụ quan sát và debug agent trực quan | |
| `08-07-error-catalog.md` | `B`errors/{INVALID_PROMPT_INPUT, INVALID_TOOL_RESULTS, MESSAGE_COERCION_FAILURE, MODEL_AUTHENTICATION, MODEL_NOT_FOUND, MODEL_RATE_LIMIT, OUTPUT_PARSING_FAILURE} | 7 mã lỗi chuẩn — mỗi mã một mục: nguyên nhân, cách tái hiện, cách xử lý | |

---

## 09-production

Đưa agent lên môi trường thật và giữ nó chạy được.

| File | URL docs | Nội dung trình bày | Ngày truy cập |
|---|---|---|---|
| `09-01-deploy.md` | `B`deploy | Các phương án triển khai, kiến trúc từng phương án | |
| `09-02-cost-and-latency.md` | [tổng hợp] | Nguồn phát sinh chi phí token và độ trễ, cách cắt giảm | |
| `09-03-security.md` | [tổng hợp] | Prompt injection, giới hạn quyền của tool, quản lý secret | |

---

## 10-analysis

Phần đánh giá độc lập, không lấy từ docs. Viết sau khi đã nắm đủ cơ chế ở các nhóm trên.

| File | URL docs | Nội dung trình bày | Ngày truy cập |
|---|---|---|---|
| `10-01-langchain-vs-langgraph.md` | [tổng hợp] | Ranh giới hai framework, khi nào phải xuống LangGraph. **Viết sau cùng**, sau khi xong phần `LangGraph/` | |
| `10-02-vs-other-frameworks.md` | [tổng hợp] | So với LlamaIndex, Semantic Kernel, và gọi SDK thuần | |
| `10-03-criticism-and-tradeoffs.md` | [tổng hợp] | Các chỉ trích phổ biến về LangChain và mức độ hợp lý sau bản v1 | |

---

## 11-case-studies

Hệ thống hoàn chỉnh, xem cách các thành phần ghép lại trong bài toán thật.

| File | URL docs | Nội dung trình bày | Ngày truy cập |
|---|---|---|---|
| `11-01-sql-agent.md` | `B`sql-agent | Agent truy vấn database, xử lý schema và rủi ro câu lệnh sai | |
| `11-02-voice-agent.md` | `B`voice-agent | Agent giọng nói, ràng buộc độ trễ khác gì agent text | |
| `11-03-deep-agent-from-scratch.md` | `B`deep-agent-from-scratch | Dựng deep agent từ primitive, hiểu cái gì được đóng gói sẵn | |
| `11-04-multi-agent-tutorials.md` | `B`multi-agent/{subagents-personal-assistant, handoffs-customer-support, router-knowledge-base, skills-sql-assistant} | 4 tutorial multi-agent, mỗi cái minh họa một pattern ở nhóm 06 | |
| `11-05-own-project.md` | [tổng hợp] | Áp dụng vào dự án riêng — chỉ để khung, điền sau | |

---

## labs

Code chạy được, tách khỏi file note để chạy độc lập. Mỗi thư mục có `README.md`, `main.py`, `.env.example`. Không commit API key thật.

| Thư mục | Nguồn code | Nội dung trình bày |
|---|---|---|
| `lab-01-quickstart/` | `B`quickstart | Agent tối giản chạy được đầu tiên |
| `lab-02-custom-middleware/` | `B`middleware/custom | Middleware tự viết, in ra thứ tự hook để đối chiếu với `03-06` |
| `lab-03-rag-knowledge-base/` | `B`knowledge-base | Pipeline RAG hoàn chỉnh |
| `lab-04-multi-agent-handoff/` | `B`multi-agent/handoffs | Hai agent chuyển quyền cho nhau |

---

## assets

| Thư mục | Nội dung trình bày |
|---|---|
| `assets/images/` | Screenshot và sơ đồ đã render. Đặt tên `<chương>-<mục>-<slug>-<n>.png`, chèn bằng `../assets/images/...` |
| `assets/diagrams/` | File Mermaid nguồn `.mmd` của các sơ đồ phức tạp phải xuất ra ảnh |