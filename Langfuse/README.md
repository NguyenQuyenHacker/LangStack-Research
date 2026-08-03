# Langfuse — Research Notes

**Nền tảng là gì**: Langfuse là nền tảng vận hành và kiểm soát chất lượng cho ứng dụng LLM, gom ba việc thường phải ghép từ nhiều công cụ rời rạc vào một chỗ: observability (ghi lại từng lệnh gọi model/tool thành trace có cấu trúc cây, đo chi phí và độ trễ), quản lý prompt (tách prompt khỏi code, versioning, A/B test), và đánh giá chất lượng (chấm điểm output bằng LLM-as-judge, code evaluator, hoặc con người). Nó đứng cạnh bot để quan sát và đo — không viết ra bot (đó là việc của LangChain) và không tự chạy/orchestrate bot (đó là việc của LangGraph).

**Bộ note này dùng để làm gì**: Nghiên cứu tab Docs chính thức trên langfuse.com (phiên bản v4), viết cho kỹ sư đã biết Python và có kinh nghiệm với LangChain — vì vậy các ví dụ tích hợp thường lấy LangChain làm framework minh hoạ. Cấu trúc thư mục bám theo ba trụ cột Observability/Prompt Management/Evaluation cộng Platform (metrics, API, security) và Glossary, đúng như cách Langfuse tự chia trên docs của họ. Mục Integrations chỉ ghi tổng quan và link chéo sang tab riêng của langfuse.com, không đào sâu — nội dung tích hợp cụ thể (cách gắn Langfuse vào LangChain, OpenAI SDK...) đọc trực tiếp ở nguồn khi cần.

## Cấu trúc thư mục

### 00-Overview (bản đồ ba trụ cột trước khi vào từng phần)
| File | Nội dung |
|---|---|
| `00-Overview.md` | Ba trụ cột Observability/Prompt Management/Evaluation của Langfuse và vì sao mỗi trụ cột tồn tại. |

### 01-observability (theo dõi ứng dụng LLM: trace, span, cost, SDK)
| File | Nội dung |
|---|---|
| `01-01-overview.md` | Observability là gì, phân biệt với tracing, Langfuse khác công cụ APM thông thường ở đâu. |
| `01-02-get-started.md` | Các bước và các con đường tích hợp (wrapper, callback, OTel...) để tạo trace đầu tiên. |
| `01-03-concepts.md` | Mô hình dữ liệu ba tầng Observation → Trace → Session, cơ chế thu thập bất đồng bộ trên nền OpenTelemetry. |
| `01-04-best-practices.md` | Quy tắc thiết kế trace tốt: phạm vi trace, cấu trúc cây, đặt tên, input/output, gắn attribute. |
| `01-06-sdks.md` | SDK Python/JS, ba cách instrument, gắn thuộc tính, trace ID, flush/shutdown, cấu hình nâng cao. |

**01-05-features/** (27 tính năng nhỏ gom theo nhóm liên quan)
| File | Nội dung |
|---|---|
| `01-05-00-index.md` | Bản đồ 27 feature, không viết nội dung riêng — chỉ trỏ sang các file bên dưới. |
| `01-05-01-trace-organization.md` | Sessions, User Tracking, Trace IDs & Distributed Tracing — ba cơ chế định danh/gom trace. |
| `01-05-02-labeling-attributes.md` | Environments, Tags, Metadata, Releases & Versions — bốn thuộc tính gắn nhãn lên trace/observation. |
| `01-05-03-structure-content.md` | Observation Types, Agent Graphs, Multi-Modality, Token & Cost Tracking — nội dung/cấu trúc bên trong observation. |
| `01-05-04-data-masking.md` | Che dữ liệu nhạy cảm phía client trước khi trace rời ứng dụng, hai hook Python, cách dùng với LangChain. |
| `01-05-05-operations.md` | Sampling, event queuing/batching, log levels — các đòn bẩy vận hành khối lượng/gửi dữ liệu. |
| `01-05-06-annotation-feedback.md` | User Feedback, Corrections, Comments — ba cách con người gắn tín hiệu lên trace đã ghi. |
| `01-05-07-search-integrations.md` | Filter search bar, full-text search, chart trên bảng, trace URL, MCP tracing — tìm/xem/chia sẻ trace trên UI. |

### 02-prompt-management (tách prompt khỏi code, versioning, deploy)
| File | Nội dung |
|---|---|
| `02-01-overview.md` | Vì sao tách prompt khỏi code và ba bước đưa một prompt vào dùng. |
| `02-02-concepts.md` | Prompt object, text vs chat, chèn nội dung động, version–label, caching — các khái niệm nền. |

**02-03-features/** (16 tính năng nhỏ gom theo nhóm liên quan)
| File | Nội dung |
|---|---|
| `02-03-00-index.md` | Bản đồ 16 feature, không viết nội dung riêng. |
| `02-03-01-dynamic-authoring.md` | Variables, Message Placeholders, Prompt Composability, Config — tham số hóa nội dung/cấu trúc prompt lúc gọi. |
| `02-03-02-versioning-deployment.md` | Version Control (version/label/protected label), A/B Testing, Folders — quản lý triển khai sau khi soạn. |
| `02-03-03-runtime-reliability.md` | Caching, Guaranteed Availability — đảm bảo `get_prompt()` nhanh và không lỗi khi Langfuse chậm/down. |
| `02-03-04-iteration-observability.md` | Playground, Link to Traces — thử trước khi chạy thật và quan sát hiệu suất sau khi đã chạy. |
| `02-03-05-automation-integrations.md` | Agent Access, MCP Server, Webhooks & Slack, GitHub Integration, n8n Node — tác nhân ngoài đọc/sửa và tự động hoá sự kiện prompt. |

### 03-evaluation (đo chất lượng ứng dụng LLM)
| File | Nội dung |
|---|---|
| `03-01-overview.md` | Vấn đề đo chất lượng LLM app, hai chế độ online/offline, bốn khối khái niệm nền, vòng AI engineering loop. |
| `03-02-concepts.md` | Vòng đánh giá offline/online chi tiết cùng bốn khối Score/Evaluation Method/Experiment/Online Evaluation. |
| `03-03-scores.md` | Score object, bốn kiểu dữ liệu, ScoreConfig, Score vs Tag, Score Analytics. |
| `03-04-evaluation-methods.md` | Năm cách sinh score: LLM-as-a-Judge, Code evaluators, Scores via API/SDK, Scores via UI, Annotation Queues. |
| `03-05-experiments.md` | Mô hình dữ liệu Experiment, Dataset, ba cách chạy experiment (SDK, UI, CI/CD). |

### 04-platform (metrics, API, security)
| File | Nội dung |
|---|---|
| `04-01-metrics.md` | Ba nhóm chỉ số (chất lượng/chi phí-độ trễ/khối lượng), ba cách khai thác: Dashboard, Monitor, Metrics API. |
| `04-02-api-data-platform.md` | Các lối truy cập dữ liệu bằng chương trình: Agent Skill, CLI, MCP Server, export, Public/Observations/Scores API. |
| `04-03-security-guardrails.md` | Vai trò Langfuse là quan sát/đánh giá lớp guardrail chạy runtime, không phải chính guardrail. |

### 05-glossary (tra cứu thuật ngữ)
| File | Nội dung |
|---|---|
| `05-01-glossary.md` | Từ điển tra cứu toàn bộ thuật ngữ Langfuse, gom theo 9 nhóm chức năng, mỗi mục trỏ URL chi tiết. |

### 06-integrations (link chéo sang tab Integrations của langfuse.com)
| File | Nội dung |
|---|---|
| `06-01-overview.md` | Tám nhóm cách nguồn ngoài gửi trace vào Langfuse: Native, Frameworks, Model Providers, Gateways, No-Code, Analytics, Developer Tools, Other. |

### assets
`assets/image/image.png` — ảnh chụp UI trace tree, nhúng trong `01-observability/01-04-best-practices.md`.

## Thứ tự đọc gợi ý

1. **00-Overview** — nắm ba trụ cột trước khi vào chi tiết.
2. **01-observability** — nền tảng: mọi dữ liệu Langfuse đều xuất phát từ trace.
3. **02-prompt-management** — quản lý và versioning prompt.
4. **03-evaluation** — scoring và experiment để đo chất lượng.
5. **04-platform**, **05-glossary**, **06-integrations** — tra cứu khi cần: metrics/API/security, thuật ngữ, tích hợp nguồn ngoài.

## Quy ước

- `status: draft` trong frontmatter ở hầu hết file; riêng `01-observability/01-06-sdks.md` đã ở `status: done`.
- `!Note` — cảnh báo lỗi im lặng/hành vi dễ nhầm, xuất hiện phổ biến, gần như thay cho block cảnh báo chuẩn.
- `(suy luận)` — đánh dấu phần vượt ngoài source, chỉ xuất hiện một lần (`02-03-01-dynamic-authoring.md`); một số chỗ khác tự nhận nội dung là suy luận/dựng cấu trúc trong văn xuôi nhưng chưa gắn nhãn `(dựng lại)` theo đúng quy ước repo — nợ kỹ thuật cần dọn.

## Nguồn

Ánh xạ URL docs gốc ở [`SOURCES.md`](SOURCES.md).
