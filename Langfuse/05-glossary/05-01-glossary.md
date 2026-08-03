---
title: Glossary
doc_source:
  - https://langfuse.com/docs/glossary
accessed: 2026-07-31
version: v4
status: draft
---

# Glossary — Từ điển thuật ngữ Langfuse

Định nghĩa ngắn của mọi khái niệm dùng xuyên suốt docs; mỗi thuật ngữ trỏ về nơi giảng chi tiết, không lặp lại nội dung đã có ở note riêng.

## Tổng quan

Đây là chỉ mục tra cứu, không phải nơi giảng: mỗi mục chỉ đủ để nhận diện thuật ngữ là gì và thuộc miền nào, phần cấu hình và cách dùng nằm ở URL. Trang gốc gom thuật ngữ theo category (Observability, Evaluation, Prompts, Platform, API, SDK); ở đây ta gom lại theo chức năng để thấy quan hệ phụ thuộc: đối tượng cốt lõi của tracing → các loại observation → thuộc tính gắn lên trace → công cụ xem dữ liệu → đánh giá → dataset/experiment → prompt → nền tảng quản trị → API/SDK. Một tập lớn thuật ngữ Observability thực chất là các **loại observation** dùng chung một trang, nên tách riêng thành một nhóm.

## 1. Đối tượng cốt lõi của tracing

| Thuật ngữ | Khái niệm | Chi tiết |
|---|---|---|
| Trace | Một request/thao tác đơn lẻ trong ứng dụng LLM; chứa input, output, metadata tổng và các observation lồng bên trong. | https://langfuse.com/docs/observability/data-model |
| Observation | Một bước đơn trong trace; có nhiều loại (span, generation, event, tool…), lồng nhau để biểu diễn workflow phân cấp. | https://langfuse.com/docs/observability/data-model |
| Tracing | Quá trình ghi log có cấu trúc cho mọi request — prompt, response, token, latency, các bước trung gian. | https://langfuse.com/docs/observability/overview |
| Session | Gom các trace thuộc cùng một lượt tương tác của user (hội thoại nhiều lượt, chat thread). | https://langfuse.com/docs/observability/features/sessions |
| Environment | Tách trace/observation/score theo ngữ cảnh triển khai (production, staging, development) trong cùng một project. | https://langfuse.com/docs/observability/features/environments |

## 2. Các loại observation

Tất cả trỏ về cùng một trang: https://langfuse.com/docs/observability/features/observation-types

| Thuật ngữ | Khái niệm |
|---|---|
| Span | Loại observation biểu diễn khoảng thời gian một đơn vị công việc; loại mặc định. |
| Generation | Loại observation ghi output từ model AI (prompt, completion, token, chi phí); loại phổ biến nhất cho lệnh gọi LLM. |
| Event | Loại observation cơ bản đánh dấu sự kiện rời rạc; đơn vị dựng nền của tracing. |
| Tool | Loại observation biểu diễn một lệnh gọi tool (gọi API thời tiết, truy vấn database). |
| Agent | Loại observation biểu diễn workflow agent AI — suy luận nhiều bước, điều phối tool, ra quyết định tự chủ. |
| Chain | Loại observation biểu diễn liên kết giữa các bước ứng dụng (chuyển context từ retriever sang lệnh gọi LLM). |
| Retriever | Loại observation biểu diễn bước truy xuất dữ liệu (gọi vector store, database trong RAG). |
| Embedding | Loại observation biểu diễn lệnh gọi LLM sinh embedding; kèm model, token, chi phí. |
| Evaluator | Loại observation biểu diễn hàm đánh giá độ liên quan/chính xác/hữu ích của output LLM; cũng chỉ hàm chấm điểm kết quả experiment. |
| Guardrail | Loại observation biểu diễn thành phần chặn nội dung độc hại, jailbreak, rủi ro bảo mật. |

## 3. Thuộc tính & tổ chức trace

| Thuật ngữ | Khái niệm | Chi tiết |
|---|---|---|
| Tags | Nhãn tự do gán lên trace/observation để phân loại và lọc theo feature, endpoint, workflow. | https://langfuse.com/docs/observability/features/tags |
| User Tracking | Gắn trace với user qua `userId` để phân tích, theo dõi chi phí và lọc theo từng user. | https://langfuse.com/docs/observability/features/users |
| Token | Đơn vị text cơ bản LLM xử lý; số token quyết định chi phí API và giới hạn context. Langfuse theo dõi token input/output. | https://langfuse.com/docs/observability/features/token-and-cost-tracking |
| Model Definition | Cấu hình lưu giá của một model LLM (chi phí mỗi token input/output) để Langfuse tự tính giá generation theo token. | https://langfuse.com/docs/observability/features/token-and-cost-tracking |

## 4. Xem & phân tích dữ liệu

| Thuật ngữ | Khái niệm | Chi tiết |
|---|---|---|
| Custom Dashboards | Dashboard phân tích tự phục vụ; nhiều loại biểu đồ, lọc và tổng hợp nhiều tầng trên metric của ứng dụng. | https://langfuse.com/docs/metrics/features/custom-dashboards |
| Filter Search Bar | Thanh truy vấn một dòng lọc bảng Observations/Traces bằng cú pháp `field:value`; hỗ trợ toán tử, wildcard, phủ định, nút Ask AI dựng filter từ mô tả ngôn ngữ tự nhiên. | https://langfuse.com/docs/observability/features/filter-search-bar |
| Log View | Hiển thị mọi observation nối tiếp nhau, để quét nhanh. | https://langfuse.com/docs/observability/overview |
| Agent Graph | Biểu diễn trực quan workflow agent nhiều bước trong một trace, giúp debug luồng observation. | https://langfuse.com/docs/observability/features/agent-graphs |

## 5. Đánh giá (Evaluation)

| Thuật ngữ | Khái niệm | Chi tiết |
|---|---|---|
| Score | Kết quả của annotation hoặc đánh giá tự động; dạng numeric/categorical/boolean/text; gán cho trace, observation, session, dataset run. | https://langfuse.com/docs/evaluation/scores/data-model#scores |
| Score Config | Cấu hình định nghĩa cách tính và diễn giải score — kiểu dữ liệu, ràng buộc giá trị, danh mục. | https://langfuse.com/docs/evaluation/scores/data-model#score-config |
| Evaluation Method | Hàm chấm điểm trace/observation/session/dataset run; gồm LLM-as-a-Judge, Annotation Queue, chấm qua UI, chấm qua API/SDK. | https://langfuse.com/docs/evaluation/core-concepts#evaluation-methods |
| LLM-as-a-Judge | Phương pháp đánh giá dùng một LLM chấm output theo tiêu chí tùy chỉnh, có suy luận chain-of-thought. | https://langfuse.com/docs/evaluation/evaluation-methods/llm-as-a-judge |
| Annotation Queue | Phương pháp đánh giá thủ công cho chuyên gia review, thêm score và comment vào trace/observation/session; dựng ground truth. | https://langfuse.com/docs/evaluation/evaluation-methods/annotation-queues |
| Offline Evaluation | Kiểm thử ứng dụng trên dataset cố định trước khi deploy; validate thay đổi, bắt regression. | https://langfuse.com/docs/evaluation/core-concepts#the-evaluation-loop |
| Online Evaluation | Chấm điểm trace production trực tiếp để bắt vấn đề trên traffic thật. | https://langfuse.com/docs/evaluation/core-concepts#online-evaluation |

## 6. Dataset & Experiment

| Thuật ngữ | Khái niệm | Chi tiết |
|---|---|---|
| Dataset | Tập test case (dataset item) để kiểm thử và benchmark ứng dụng LLM; chứa input và (tùy chọn) expected output. | https://langfuse.com/docs/evaluation/experiments/datasets |
| Dataset Item | Một test case trong dataset; gồm input và (tùy chọn) expected output. | https://langfuse.com/docs/evaluation/experiments/data-model#datasetitem-object |
| Dataset Experiment (Dataset Run) | Lần chạy dataset qua ứng dụng, sinh output để đánh giá; liên kết dataset item với trace tương ứng. | https://langfuse.com/docs/evaluation/experiments/data-model#datasetrun-experiment-run |
| Task | Định nghĩa hàm xử lý dataset item trong experiment; đại diện code ứng dụng cần kiểm thử. | https://langfuse.com/docs/evaluation/experiments/data-model#task |
| Remote Experiment | Trigger dạng webhook cho phép chạy SDK experiment từ UI; cấu hình webhook URL và config mặc định. | https://langfuse.com/docs/evaluation/experiments/experiments-via-sdk#optional-trigger-sdk-experiment-from-ui |

## 7. Prompt

| Thuật ngữ | Khái niệm | Chi tiết |
|---|---|---|
| Prompt Management | Cách lưu, đánh version, truy xuất prompt có hệ thống; tách cập nhật prompt khỏi deploy code. | https://langfuse.com/docs/prompt-management/overview |
| Text Prompt (String Prompt) | Prompt là một chuỗi đơn; hợp với ca đơn giản hoặc chỉ cần system message. | https://langfuse.com/docs/prompt-management/data-model#text-vs-chat-prompts |
| Chat Prompt (Message Prompt) | Prompt là mảng message có role (system, user, assistant); quản lý cấu trúc hội thoại và lịch sử chat. | https://langfuse.com/docs/prompt-management/data-model#text-vs-chat-prompts |
| Prompt Variables | Placeholder trong prompt được điền động lúc runtime; tạo template prompt tái dùng. | https://langfuse.com/docs/prompt-management/features/variables |
| Prompt Label | Nhãn gán cho một version prompt; đánh dấu production/staging để fetch qua SDK/API. | https://langfuse.com/docs/prompt-management/features/prompt-version-control |
| Protected Prompt Label | Hạn chế quyền gán một số label (vd production) vào version mới, chỉ admin/owner; chặn sửa nhầm hoặc trái phép. | https://langfuse.com/docs/prompt-management/features/prompt-version-control |
| Playground | Nơi test, lặp và so sánh prompt/model trực tiếp trong Langfuse, không cần viết code. | https://langfuse.com/docs/prompt-management/features/playground |

## 8. Nền tảng & quản trị (Platform)

| Thuật ngữ | Khái niệm | Chi tiết |
|---|---|---|
| Organization | Thực thể cấp cao nhất chứa project; quản lý billing, thành viên, cấu hình SSO. | https://langfuse.com/docs/administration/rbac |
| Project | Container gom mọi dữ liệu Langfuse trong một organization; cho phép RBAC chi tiết và tách dữ liệu theo ứng dụng. | https://langfuse.com/docs/administration/rbac |
| RBAC | Kiểm soát truy cập theo vai trò; các vai trò Owner, Admin, Member, Viewer, None với scope riêng. | https://langfuse.com/docs/administration/rbac |
| API Key | Credential xác thực với API/SDK; gồm public key và secret key, gắn với một project. | https://langfuse.com/docs/administration/rbac |
| LLM Connection | Cấu hình API key để Langfuse gọi model LLM trong Playground hoặc cho LLM-as-a-Judge; hỗ trợ OpenAI, Anthropic, Google. | https://langfuse.com/docs/administration/llm-connection |
| Langfuse Assistant | Trợ lý AI trong sản phẩm (beta trên Langfuse Cloud) để khám phá dữ liệu project bằng ngôn ngữ tự nhiên qua Langfuse MCP server. | https://langfuse.com/docs/langfuse-assistant |
| Billable Unit | Đơn vị tính giá Langfuse Cloud; bằng tổng trace + observation + score nạp vào trong kỳ billing. | https://langfuse.com/docs/administration/billable-units |

## 9. API & SDK

| Thuật ngữ | Khái niệm | Chi tiết |
|---|---|---|
| Public API | REST API truy cập mọi dữ liệu và tính năng Langfuse; dùng cho tích hợp, workflow, truy cập lập trình. | https://langfuse.com/docs/api-and-data-platform/features/public-api |
| Metrics API | Endpoint lấy analytics tùy chỉnh; chỉ định dimension, metric, filter, độ chi tiết thời gian để dựng report/dashboard. | https://langfuse.com/docs/metrics/features/metrics-api |
| MCP Server | Server Model Context Protocol cho phép công cụ AI tương tác với dữ liệu Langfuse. | https://langfuse.com/docs/api-and-data-platform/features/mcp-server |
| SDK | Bộ công cụ phát triển; Langfuse có SDK native cho Python và JavaScript/TypeScript, lo tracing, prompt management, truy cập API. | https://langfuse.com/docs/observability/sdk/overview |
| Instrumentation | Quá trình thêm code để ghi lại hành vi ứng dụng; gồm context manager, observe wrapper, phương thức observation thủ công. | https://langfuse.com/docs/observability/sdk/instrumentation |
| Flush | Gửi dữ liệu trace đang đệm lên server; quan trọng với ứng dụng đời ngắn để không mất dữ liệu khi tiến trình kết thúc. | https://langfuse.com/docs/observability/sdk/instrumentation#client-lifecycle--flushing |
| OpenTelemetry (OTel) | Chuẩn mở thu thập telemetry; Langfuse xây trên OpenTelemetry để tương thích và giảm khóa nhà cung cấp. | https://langfuse.com/integrations/native/opentelemetry |

