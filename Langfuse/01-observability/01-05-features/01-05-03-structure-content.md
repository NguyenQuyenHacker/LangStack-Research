---
title: Observability — Features — Cấu trúc & nội dung observation
doc_source:
  - https://langfuse.com/docs/observability/features/observation-types
  - https://langfuse.com/docs/observability/features/agent-graphs
  - https://langfuse.com/docs/observability/features/multi-modality
  - https://langfuse.com/docs/observability/features/token-and-cost-tracking
accessed: 2026-08-01
version: v4
status: draft
related:
  - ./01-05-00-index.md
  - ./01-05-01-thuoc-tinh-gan-nhan.md
---

# Cấu trúc & nội dung observation (Types, Agent Graphs, Multi-Modality, Token & Cost)

> Bốn khía cạnh mô tả bản thân một observation: nó thuộc loại gì, các observation ghép lại thành đồ thị ra sao, chứa được nội dung đa phương thức nào, và mang số liệu token/chi phí ra sao.
> Khác cụm [thuộc tính gắn nhãn](./01-05-01-thuoc-tinh-gan-nhan.md) — vốn là các nhãn cắt ngang; cụm này nói về nội dung bên trong observation.

---

## 1. Tổng quan

Một trace trong Langfuse là cây các observation. Cụm bốn tính năng này mô tả bản thân từng observation và cách chúng ghép lại, thay vì gắn thêm nhãn từ ngoài vào.

Bốn khía cạnh có quan hệ phụ thuộc, không rời rạc:

- **Observation type** là nền — mỗi observation mang một loại ngữ nghĩa (generation, tool, retriever...).
- **Agent graph** được suy ra *từ* loại observation: chỉ cần trace có một observation không phải span/event/generation là Langfuse dựng đồ thị.
- **Token & cost** chỉ áp cho hai loại observation cụ thể là `generation` và `embedding`.
- **Multi-modality** độc lập hơn — quy định input/output/metadata của observation chứa được media gì.

Vì vậy note này trình bày theo thứ tự: loại observation trước (nền), rồi đồ thị và chi phí (dựng trên loại), cuối là nội dung đa phương thức. Việc gộp bốn tính năng thành một cụm là cách tổ chức của bộ tài liệu, không phải một khái niệm hợp nhất Langfuse định nghĩa — đây là suy luận về cấu trúc, chưa được nguồn khẳng định.

---

## 2. Observation Types — vai trò ngữ nghĩa của mỗi observation

### Mục đích

Observation type gán cho mỗi observation một vai trò ngữ nghĩa, để bổ sung ngữ cảnh và cho phép lọc hiệu quả. Cùng là một "bước" trong trace, nhưng đánh dấu nó là `tool` hay `retriever` hay `generation` quyết định cách Langfuse hiểu và hiển thị bước đó — và như mục 3, mục 5 cho thấy, quyết định cả việc có dựng đồ thị và có tính chi phí hay không.

### Mười loại observation

| Loại | Vai trò |
|---|---|
| `event` | Khối cơ bản nhất — đánh dấu một sự kiện rời rạc trong trace |
| `span` | Khoảng thời gian của một đơn vị công việc |
| `generation` | Lần sinh nội dung của model AI, gồm prompt, token usage và chi phí |
| `agent` | Quyết định luồng ứng dụng, có thể gọi tool dưới sự dẫn dắt của LLM |
| `tool` | Một lệnh gọi công cụ, ví dụ gọi API thời tiết |
| `chain` | Mắt nối giữa các bước, ví dụ chuyển ngữ cảnh từ retriever sang lệnh gọi LLM |
| `retriever` | Bước truy xuất dữ liệu, ví dụ gọi vector store hoặc cơ sở dữ liệu |
| `evaluator` | Hàm đánh giá độ liên quan / đúng đắn / hữu ích của output LLM |
| `embedding` | Lệnh gọi LLM để sinh embedding, gồm model, token usage và chi phí |
| `guardrail` | Thành phần chặn nội dung độc hại hoặc jailbreak |

### Cách đặt

Khi dùng tích hợp với các framework agent, loại observation được đặt tự động — ví dụ đánh dấu một hàm bằng `@tool` trong langchain thì Langfuse tự đặt loại `tool`.

Đặt thủ công qua tham số `as_type` (Python) hoặc `asType` (TypeScript) khi tạo observation:

```python
from langfuse import observe

@observe(as_type="agent")                    # đánh dấu hàm này là observation loại agent
def run_agent_workflow(query):
    return process_with_tools(query)

@observe(as_type="tool")                     # loại tool cho lệnh gọi công cụ ngoài
def call_weather_api(location):
    return weather_service.get_weather(location)
```

**!Note:** Loại observation yêu cầu phiên bản SDK tối thiểu — Python `>=3.3.1`, TypeScript `>=4.0.0`. SDK cũ hơn không đặt được loại, kéo theo agent graph (mục 3) không hiện.

---

## 3. Agent Graphs — dựng đồ thị trực quan từ observation

### Mục đích

Agent graph vẽ luồng agent nhiều bước thành đồ thị trực quan, phục vụ hiểu và gỡ lỗi các chuỗi suy luận và tương tác agent. Tính năng đang ở giai đoạn beta.

### Điều kiện để đồ thị xuất hiện

Có hai đường:

- **Suy ra từ observation.** Chỉ cần trace có một observation thuộc *bất kỳ loại nào ngoài* `span`, `event`, `generation`. Khi đó Langfuse hiểu trace là agentic và tự dựng đồ thị từ thời điểm và mức lồng nhau của các observation.
- **Từ tích hợp LangGraph.** Dùng tích hợp LangGraph thì đồ thị hiện tự động.

**!Note:** Đây là điểm nối trực tiếp với mục 2 — nếu toàn bộ trace chỉ gồm `span`, `event`, `generation`, đồ thị sẽ không xuất hiện dù luồng thực tế có tính agent. Muốn có đồ thị, phải đặt đúng loại observation (`agent`, `tool`, `retriever`...).

### Hai chế độ xem

Cùng một trace vẽ được hai kiểu, chuyển qua lại bằng nút Aggregated / Expanded ở góc trên bên trái; lựa chọn được ghi nhớ qua các trace. Khác biệt cốt lõi: một node ứng với **một tên bước** hay ứng với **một lần gọi**.

| | Aggregated (mặc định) | Expanded ("as it ran") |
|---|---|---|
| Một node là | một tên bước duy nhất | một lần gọi riêng lẻ |
| Lời gọi lặp lại | gộp thành một node kèm bộ đếm | tách thành các node riêng |
| Vòng lặp | vẽ thành chu trình (cạnh quay lại) | trải phẳng thành đồ thị không chu trình (DAG) |
| Đọc ra | hình dạng tổng thể của agent | đúng lần chạy, từng bước một |
| Hợp để | nắm cấu trúc và độ phức tạp trong một cái nhìn | theo dõi hoặc gỡ lỗi một lần chạy cụ thể |

Ở Aggregated, các bước cùng tên gộp lại và kèm bộ đếm — `retrieve_docs (3/3)` nghĩa là bước đó chạy ba lần — còn vòng lặp gọi cùng một tool được vẽ thành chu trình thay vì một chuỗi dài. Ở Expanded, mỗi lần gọi là một node riêng, ba lần gọi `litellm_request` là ba node, vòng lặp trải thành DAG theo thứ tự thực thi. Không chế độ nào "đúng hơn" — chúng trả lời hai câu hỏi khác nhau: Aggregated để hiểu cấu trúc, Expanded để lần theo một lần chạy.

---

## 4. Multi-Modality — nội dung đa phương thức trong observation

### Mục đích

Multi-modality cho phép trace chứa nội dung ngoài văn bản: hình ảnh, âm thanh, và các tệp đính kèm khác. Media nằm ở ba trường của trace/observation: `input`, `output`, `metadata`.

### Bốn cách đưa media vào

Mặc định, SDK tự xử lý dữ liệu mã hóa dạng base64 data URI: trích ra khỏi payload, tải lên object storage của Langfuse, rồi gắn tham chiếu vào trace. Ngoài ra:

- **URL ngoài.** Media tham chiếu qua URL (định dạng Markdown image hoặc OpenAI content part) được render trực tiếp từ nguồn, *không* tải lên object storage của Langfuse.
- **Lớp `LangfuseMedia`.** Khi cần kiểm soát nhiều hơn hoặc media không phải base64, bọc media bằng `LangfuseMedia` trước khi đưa vào input/output/metadata hoặc dataset item.
- **API trực tiếp.** Tự trích base64, khởi tạo upload để lấy `mediaId` và `presignedURL`, rồi PUT tệp lên.

```python
from langfuse import get_client
from langfuse.media import LangfuseMedia

with open("static/bitcoin.pdf", "rb") as f:
    pdf_bytes = f.read()

pdf_media = LangfuseMedia(content_bytes=pdf_bytes, content_type="application/pdf")   # bọc media

langfuse = get_client()
with langfuse.start_as_current_observation(as_type="span", name="analyze-document") as span:
    span.update(input={"document": pdf_media},                # media đặt thẳng vào input
                metadata={"file_size": len(pdf_bytes)})
```

### Định dạng hỗ trợ

Langfuse nhận nhiều nhóm định dạng: hình ảnh (.png, .jpg, .webp, .gif, .svg...), âm thanh (.mp3, .wav, .ogg...), video (.mp4, .webm, .mov...), văn bản và mã (.txt, .md, .html, .csv, .py, .ts...), tài liệu (.pdf, .docx, .xlsx, .pptx), dữ liệu và nén (.json, .xml, .zip, .parquet...). Danh sách MIME type đầy đủ nằm ở trang nguồn.

### Cơ chế: upload, tham chiếu, khôi phục

Với media không tham chiếu qua URL ngoài, Langfuse xử lý theo ba bước.

Về **upload**: SDK tách media khỏi dữ liệu trace ngay ở phía client để tối ưu hiệu năng, tải thẳng lên object storage (S3 hoặc tương thích), rồi thay nội dung gốc bằng một chuỗi tham chiếu. Upload dùng presigned URL có kiểm tra nội dung (độ dài, kiểu, mã băm SHA256). Tệp được khử trùng lặp theo bộ ba project + content type + SHA256 — trùng thì chỉ thay bằng tham chiếu `mediaId` đã có. Python xử lý ở thread nền, JS/TS xử lý bất đồng bộ, đều không chặn luồng chính.

Về **tham chiếu**: media trong trace bị thay bằng token chuẩn hóa:

```
@@@langfuseMedia:type={MIME_TYPE}|id={LANGFUSE_MEDIA_ID}|source={SOURCE_TYPE}@@@
```

Trong đó `source` nhận một trong ba giá trị `base64_data_uri`, `bytes`, `file`. Dựa vào token này, giao diện tự nhận diện `mediaId` và render media inline.

Về **khôi phục**: hàm `resolve_media_references` của client duyệt đối tượng và trả về bản sao sâu, thay mọi chuỗi tham chiếu bằng base64 data URI tương ứng. Hữu ích khi cần đưa nội dung gốc trở lại lúc fine-tuning, chạy dataset, hoặc phát lại một generation.

### Hạ tầng lưu trữ

Trên Langfuse Cloud, tệp đính kèm đa phương thức hiện miễn phí, và Langfuse để ngỏ khả năng áp một chỉ số tính phí mới trong tương lai gần cho phần lưu trữ/tính toán tăng thêm. Khi tự vận hành (self-host), phải tự cấu hình bucket object storage qua các biến `LANGFUSE_S3_MEDIA_UPLOAD_*`; bucket phải có hostname phân giải công khai để SDK upload trực tiếp và trình duyệt tải media về được.

---

## 5. Token & Cost Tracking — số liệu usage và chi phí

### Mục đích và phạm vi

Langfuse theo dõi lượng dùng và chi phí của các lần sinh nội dung LLM, tách theo từng loại usage. Chỉ hai loại observation ghi được usage và cost: `generation` và `embedding`. Mỗi observation mang hai nhóm số liệu — `usage_details` (số đơn vị tiêu thụ theo từng loại usage) và `cost_details` (chi phí USD theo từng loại usage).

Loại usage là chuỗi tự do, khác nhau theo nhà cung cấp: mức đơn giản nhất là `input` và `output`, mô hình phức tạp hơn có thêm `cached_tokens`, `audio_tokens`, `image_tokens`. Trên giao diện, Langfuse cộng mọi loại usage chứa chuỗi `input` thành input tổng, tương tự với `output`; nếu không có loại `total` được đẩy lên, Langfuse cộng tất cả loại thành total.

### Hai nguồn số liệu: ingest và infer

Số liệu usage và cost đến từ một trong hai đường: **đẩy trực tiếp** (ingest, qua API/SDK/tích hợp) hoặc **suy ra** (infer, dựa trên tham số `model` của generation). Số liệu đẩy trực tiếp được ưu tiên hơn số liệu suy ra.

Đẩy trực tiếp usage/cost khi có trong phản hồi của LLM là cách chính xác và ổn định nhất. Nhiều tích hợp tự bắt sẵn hai nhóm số liệu này từ phản hồi.

```python
generation.update(
    usage_details={                                    # số token theo từng bucket
        "input": response.usage.input_tokens,
        "output": response.usage.output_tokens,
        "cache_read_input_tokens": response.usage.cache_read_input_tokens,
    },
    cost_details={                                     # chi phí USD theo từng bucket (tùy chọn)
        "input": 1,
        "cache_read_input_tokens": 0.5,
        "output": 1,
    },
)
```

### Ràng buộc cốt lõi: các bucket loại trừ lẫn nhau

Đây là điểm dễ sai nhất và gây hậu quả thầm lặng. Langfuse coi mỗi khóa trong `usage_details` là một bucket riêng, không chồng lấn — mỗi token phải nằm trong đúng một khóa. Nghĩa là `input` phải *loại trừ* token đã đếm ở các khóa `input_*` khác (như `input_cached_tokens`), và `output` phải loại trừ token đã đếm ở các khóa `output_*` khác (như `output_reasoning_tokens`). Riêng `total` là ngoại lệ — không phải một bucket mà là tổng của mọi bucket.

Langfuse dựa vào hợp đồng này ở ba chỗ: hiển thị (cộng các loại chứa `input`/`output`), suy ra chi phí (khớp từng loại usage với giá theo loại rồi cộng lại), và tính total khi không có total đẩy lên.

**!Note:** Nếu các bucket chồng lấn — ví dụ `input` vẫn còn chứa token đã báo ở `input_cached_tokens` — thì token bị đếm hai lần và chi phí suy ra bị tính trùng, tức con số Langfuse hiển thị *cao hơn* thực tế nhà cung cấp tính. Không có cảnh báo. Riêng `cost_details` đẩy trực tiếp được dùng nguyên văn, không bị ảnh hưởng.

### Chuẩn hóa số đếm inclusive về exclusive: ai làm hộ

Nhiều nhà cung cấp báo số đếm **inclusive** (bao gồm cả phần con). Ví dụ `prompt_tokens` của OpenAI đã gồm cả cached token; ngược lại `input_tokens` của Anthropic đã loại trừ phần cache. Số inclusive phải chuyển thành bucket exclusive trước khi lưu, bằng cách trừ phần chi tiết khỏi số tổng. Việc chuyển đổi này ai làm phụ thuộc đường dữ liệu đi vào:

| Đường vào | Xử lý |
|---|---|
| Tích hợp / SDK wrapper của Langfuse (ví dụ OpenAI wrapper) | Tự bắt và chuyển đổi hộ |
| Thuộc tính usage của OpenTelemetry (`gen_ai.usage.*`, `llm.token_count.*`) | Coi là inclusive, Langfuse tự chuẩn hóa khi nạp |
| Schema usage của OpenAI (có `prompt_tokens_details` / `completion_tokens_details`) | Được nhận diện và chuẩn hóa khi nạp, khớp nghiêm ngặt |
| Khóa phẳng kiểu Langfuse (`usage_details` / `usageDetails`) | Lưu nguyên văn, **không** chuẩn hóa — giá trị phải sẵn là exclusive |

Nếu tự viết instrumentation dùng khóa phẳng, phải tự kiểm tra cách nhà cung cấp báo usage và trừ phần cache/chi tiết khỏi `input`/`output` — đúng một lần — trước khi đưa vào Langfuse.

### Tương thích schema OpenAI

Có thể đẩy usage theo đúng schema OpenAI: `prompt_tokens` ánh xạ thành `input`, `completion_tokens` thành `output`, `total_tokens` thành `total`; các khóa trong `prompt_tokens_details` được làm phẳng với tiền tố `input_`, trong `completion_tokens_details` với tiền tố `output_`. Vì OpenAI báo phần chi tiết theo kiểu inclusive, Langfuse trừ chúng khỏi `input`/`output` để bucket lưu ra là loại trừ lẫn nhau.

**!Note:** Nhận diện schema rất nghiêm ngặt — đối tượng usage phải chứa *chỉ* các trường usage chuẩn của OpenAI. Chỉ cần thừa một khóa (ví dụ một số gateway thêm trường `cost`), Langfuse không nhận ra là schema OpenAI và lưu nguyên văn dưới dạng khóa phẳng — bỏ qua cả ánh xạ lẫn phép trừ. Đây là lỗi thầm lặng; phải loại bỏ khóa thừa trước khi nạp.

### Suy ra usage và cost khi không đẩy trực tiếp

Nếu thiếu usage hoặc cost, Langfuse cố suy ra từ tham số `model` tại thời điểm nạp. Langfuse có sẵn danh sách các model phổ biến và tokenizer của chúng (OpenAI, Anthropic, Google).

Về **usage**: nếu model có tokenizer, Langfuse tự tính số token cho generation đã nạp. Các tokenizer hiện hỗ trợ: `gpt-4o` dùng `o200k_base`, `gpt*` dùng `cl100k_base`, `claude*` dùng tokenizer `claude`. Theo Anthropic, tokenizer của họ không chính xác cho các model Claude 3 — nên gửi token từ phản hồi API nếu có.

Về **cost**: định nghĩa model chứa giá theo từng loại usage, và loại usage phải khớp *chính xác* với khóa trong `usage_details`. Langfuse tự tính chi phí khi (1) usage đã được nạp hoặc suy ra, và (2) có định nghĩa model kèm giá khớp. Chi phí suy ra được tính tại thời điểm nạp, theo thông tin model và giá có ở thời điểm đó.

### Bậc giá (pricing tiers) và định nghĩa model tùy chỉnh

Một số nhà cung cấp tính giá khác nhau tùy số token input — ví dụ Claude Sonnet 4.5 và Gemini 2.5 Pro áp giá cao hơn khi vượt 200K token input. Langfuse hỗ trợ nhiều bậc giá cho một model, mỗi bậc có tên, độ ưu tiên, điều kiện, và giá. Khi tính, Langfuse duyệt các bậc theo thứ tự ưu tiên (bỏ bậc mặc định), lấy bậc đầu tiên thỏa điều kiện; không bậc nào khớp thì dùng bậc mặc định. Điều kiện gồm `usageDetailPattern` (regex khớp khóa usage), `operator` (`gt`, `gte`, `lt`, `lte`, `eq`, `neq`), `value` (ngưỡng), `caseSensitive`. Ví dụ bậc "Large Context" của Claude Sonnet 4.5 có điều kiện `input > 200000`.

Có thể tự thêm định nghĩa model (kèm bậc giá) qua giao diện hoặc Models API. Model khớp với generation theo `model` ↔ `match_pattern` (dùng regex). Model do người dùng định nghĩa được ưu tiên hơn model do Langfuse duy trì.

### Giới hạn với model suy luận (reasoning)

Với các model reasoning như dòng OpenAI o1, Langfuse *không* suy ra được chi phí bằng cách tự tokenize input/output. Model reasoning đi qua nhiều bước, mỗi bước sinh reasoning token được tính như output token; Langfuse không nhìn thấy các reasoning token này nên không suy ra đúng chi phí khi không có token usage. Để có cost tracking cho model reasoning, phải đẩy token usage khi nạp — các wrapper và tích hợp (OpenAI wrapper, Langchain, LlamaIndex, LiteLLM) thu thập và cung cấp sẵn phần này.

**!Note:** Đổi định nghĩa model chỉ áp cho generation *mới* nạp về sau, không tính lại generation cũ.

---

## 6. Bảng tổng hợp bốn khía cạnh

| Khía cạnh | Trả lời câu hỏi | Phạm vi | Phụ thuộc |
|---|---|---|---|
| Observation Types | Observation này đóng vai trò gì | Mọi observation | Nền cho agent graph và token/cost |
| Agent Graphs | Các observation ghép thành luồng ra sao | Trace có loại ngoài span/event/generation | Cần loại observation phù hợp |
| Multi-Modality | Observation chứa nội dung gì | input/output/metadata của mọi observation | Độc lập |
| Token & Cost | Tốn bao nhiêu token, bao nhiêu tiền | Chỉ `generation` và `embedding` | Cần loại observation đúng; cần model definition để suy ra |

---

## Tham chiếu chéo

- [01-05-00 index](./01-05-00-index.md) — tổng quan cụm tính năng Observability Features
- [01-05-01 thuộc tính gắn nhãn](./01-05-01-thuoc-tinh-gan-nhan.md) — environment, tags, metadata, release/version
- Data Model (các loại đối tượng dữ liệu): `https://langfuse.com/docs/observability/data-model`
- Danh sách MIME type đầy đủ và ví dụ đa phương thức: `https://langfuse.com/docs/observability/features/multi-modality`
- Metrics API (truy xuất số liệu usage/cost tổng hợp): `https://langfuse.com/docs/metrics/features/metrics-api`=