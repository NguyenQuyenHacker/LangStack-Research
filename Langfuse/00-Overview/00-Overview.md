---
title: Langfuse — Overview
doc_source: https://langfuse.com/docs
accessed: 2026-07-31
version: "v4"
status: draft
lab:
related:
  - ./langfuse-observability.md
  - ./langfuse-prompt-management.md
  - ./langfuse-evaluation.md
---

# Langfuse — nền tảng vận hành ứng dụng LLM

> Langfuse là platform mã nguồn mở gom ba việc lại một chỗ: 
> - Quan sát (observability), 
> - Quản lý prompt,  
> - Đánh giá chất lượng ứng dụng LLM.

> Ba mảng này tích hợp sẵn với nhau, và cả nền tảng có thể tự host trên hạ tầng của mình.

---

## 1. Tổng quan

-Langfuse khác một công cụ giám sát phần mềm truyền thống (Datadog, Sentry) là nó sinh ra cho hệ thống AI/LLM. 

-Ứng dụng LLM cùng một câu hỏi có thể ra hai câu trả lời khác nhau, và một request thường không phải một lệnh gọi mà là cả một chuỗi: truy xuất dữ liệu (retrieval), tạo vector (embedding), gọi model, gọi API bên ngoài. 

➤ Langfuse theo dõi toàn bộ chuỗi xử lý này, trong khi các công cụ giám sát truyền thống chủ yếu chỉ theo dõi từng request hoặc lỗi riêng lẻ.


Ba trụ cột, mỗi cái lo một giai đoạn khác nhau trong vòng đời một ứng dụng LLM:

| Trụ cột | Tác Dụng |
|---|---|
| Observability | Nhìn thấy chuyện gì đang xảy ra bên trong mỗi request |
| Prompt Management | Quản lý, đánh phiên bản, triển khai prompt tách khỏi code |
| Evaluation | Đo chất lượng output, cả khi phát triển lẫn khi đã chạy thật |

---

## 2. Observability — vì sao ứng dụng LLM cần một loại giám sát riêng

**Vấn đề.** Khi output sai, câu hỏi đầu tiên là *sai ở bước nào*. Một request của ứng dụng LLM hiếm khi là một lệnh gọi — nó là cả chuỗi: truy xuất tài liệu → tạo vector → gọi model → gọi API bên ngoài. Retrieval lấy nhầm, model hiểu sai, hay API trả rác đều cho ra cùng một triệu chứng: kết quả cuối sai. Nhìn mỗi kết quả cuối thì không tách được nguyên nhân.

**➤** **`Observability`** 
  
**Định nghĩa.**: Là lớp giúp truy ngược nguyên nhân lỗi bằng cách ghi lại toàn bộ quá trình xử lý của một request, thay vì chỉ kết quả cuối cùng. Đơn vị ghi nhận là trace — bản ghi đầy đủ một request đi qua mọi bước, từ retrieval, embedding đến gọi model và API bên ngoài.

**Vai trò.** Trace cho phép mở từng bước ra soi, tìm chính xác chỗ hỏng. Trên nền đó, Langfuse dựng thêm mấy lớp để nhìn dữ liệu theo các góc khác nhau:

| Lớp | Nhìn cái gì |
|---|---|
| **Sessions** | Gom nhiều lượt hỏi–đáp của một hội thoại nhiều bước, hoặc một luồng agent, vào một chỗ |
| **Users** | Gắn `userId` để tách chi phí và mức dùng theo từng người |
| **Agent graphs** | Vẽ luồng một agent phức tạp thành đồ thị, thay cho log phẳng |
| **Timeline** | Soi độ trễ, tìm bước nào ăn thời gian |
| **Dashboard** | Nhìn chất lượng, chi phí, độ trễ ở mức tổng |

**Áp dụng thực tế.** Chatbot tra cứu quy định phát hành trái phiếu nhận một câu hỏi, truy 30 điều luật liên quan, đưa vào model, rồi trả lời sai ngưỡng phát hành. Trace cho thấy retrieval đã lấy đúng điều luật, model mới là chỗ bỏ sót — lỗi ở khâu model, không phải khâu tra cứu. Không có trace thì tất cả những gì ta biết chỉ là "bot trả lời sai".

**!Note:** `userId` là trường tự gắn, không tự có. Quên gắn thì trace vẫn chạy, dashboard vẫn lên số tổng, nhưng không tách được chi phí theo từng người — một khoảng mù im lặng, không báo lỗi.

---

## 3. Prompt Management — tách prompt ra khỏi code

**Vấn đề.** Prompt viết cứng trong code thì mỗi lần chỉnh một chữ đều phải sửa code và deploy lại. Không lưu lịch sử ai sửa gì, không đối chiếu được phiên bản mới với cũ, không quay lui nhanh khi bản mới kém hơn.

**➤** **`Prompt Management`**

**Định nghĩa.** Langfuse lưu prompt thành một thực thể độc lập, có phiên bản, tách khỏi code ứng dụng — sửa, đối chiếu, triển khai và quay lui prompt mà không chạm vào code (giống cách quản lý phiên bản một văn bản: sửa, lưu mốc, quay lại bản cũ).

**Vai trò.** Đưa toàn bộ vòng đời một prompt vào một chỗ, thao tác qua UI hoặc code:

| Chức năng | Nội dung |
|---|---|
| **Create** | Tạo prompt qua UI, SDK hoặc API |
| **Version control** | Sửa và đánh phiên bản, nhiều người làm chung |
| **Deploy bằng label** | Triển khai ra môi trường qua *nhãn*, không đụng code; đổi prompt chỉ cần chuyển nhãn sang phiên bản khác |
| **Metrics** | So độ trễ, chi phí, điểm đánh giá giữa các phiên bản |
| **Test in Playground** | Thử prompt trong LLM Playground trước khi dùng thật |
| **Link with traces** | Nối prompt với trace để xem nó chạy ra sao trong bối cảnh thật |
| **Track changes** | Theo dõi prompt thay đổi theo thời gian |

**Áp dụng thực tế.** Prompt tóm tắt bản cáo bạch đang chạy bản v4. Ta soạn v5 chặt hơn về số liệu, thử trong Playground, chạy Experiment đối chiếu (mục 4), rồi chuyển nhãn "production" từ v4 sang v5. Nếu v5 kém, chuyển nhãn về v4 — không deploy, không đụng code.

**!Note:** Cơ chế label chỉ phát huy khi code trỏ vào *nhãn*. Nếu code trỏ thẳng vào một phiên bản cụ thể, mất luôn khả năng đổi prompt không cần deploy — mà điều này không có cảnh báo nào, phải tự đặt quy ước từ đầu.

---

## 4. Evaluation — đo chất lượng khi không có một đáp án đúng duy nhất

**Vấn đề.** Test phần mềm thường có đáp án đúng để so. Output của LLM thì thường không có một câu trả lời đúng duy nhất — đo "tốt" thế nào ở quy mô hàng nghìn request?

**➤** **`Evaluation`**

**Định nghĩa.** Lớp đo chất lượng output, chạy được cả lúc phát triển lẫn trên trace production. Langfuse không ép một cách đo mà cho phối nhiều phương pháp; kết quả mỗi lần chấm gọi là *score*.

**Vai trò.** Cung cấp nhiều phương pháp chấm để phối theo nhu cầu:

| Phương pháp | Cách đo |
|---|---|
| **LLM-as-a-judge** | Dùng một model khác chấm điểm output; chấm được ở từng bước riêng trong ứng dụng |
| **Code evaluators** | Chấm bằng code — kiểm định dạng, kiểm có chứa số liệu bắt buộc |
| **User feedback** | Thu phản hồi người dùng qua Browser SDK (frontend) hoặc SDK/API (server) |
| **Manual labeling / Annotation Queues** | Người chấm tay, làm mốc chuẩn cho các cách chấm tự động |
| **Custom pipelines** | Tự dựng quy trình chấm riêng |

Kèm hai công cụ để chấm có hệ thống khi phát triển: **Datasets** (tập kiểm thử cố định, chạy lại nhiều lần để bảo đảm ổn định) và **Experiments** (chạy prompt hoặc model trên một dataset để so kết quả, làm ngay trên UI, không cần viết code).

Điểm chấm đẩy vào qua SDK hoặc API, nhận ba kiểu giá trị: số (numeric), đúng/sai (boolean), phân loại (categorical):

```python
langfuse.score(
    trace_id="123",              # gắn điểm này vào đúng trace nào
    name="my_custom_evaluator",  # tên bộ chấm, để lọc/nhóm về sau
    value=0.5,                   # giá trị điểm — ở đây là numeric
)
```

Hoặc qua API: `POST /api/public/scores`. Trang overview không in giá trị trả về của hàm, cần đối chiếu trang Evaluation khi triển khai.

**Áp dụng thực tế.** Đánh giá chatbot tra cứu quy định: dựng Dataset 50 câu hỏi có đáp án chuẩn, chạy Experiment giữa prompt v4 và v5, để LLM-as-a-judge chấm độ chính xác pháp lý, chọn bản điểm cao hơn đưa vào production.

**!Note:** `trace_id` là dây nối giữa điểm chấm và request thật. Truyền sai id thì điểm vẫn ghi nhận, không báo lỗi, nhưng gắn nhầm sang trace khác — số liệu đánh giá lệch mà không có dấu hiệu nào cảnh báo.

---

## 5. Điểm mạnh nền tảng và khi nào chọn

Langfuse có các điểm mạnh nền tảng:

- **Mã nguồn mở, tự host được.** Có public API để tự tích hợp; chạy trên hạ tầng của mình, không bắt buộc gửi dữ liệu ra ngoài — điểm đáng cân nhắc với dữ liệu nhạy cảm.
- **Tối ưu cho production.** Thiết kế để chi phí hiệu năng thêm vào là tối thiểu.
- **SDK gốc Python và JS**, cộng tích hợp sẵn với các framework phổ biến: OpenAI SDK, LangChain, LlamaIndex.
- **Đa phương thức (multi-modal)** — trace được cả text lẫn ảnh.
- **Trọn bộ vòng đời** — không phải lắp ba công cụ rời cho ba việc.

Trang tự đặt một lộ trình thực dụng: dựng đủ cả online tracing → quản lý prompt → đánh giá production → đánh giá offline trên dataset là việc tốn thời gian, nên làm dần theo nhu cầu, không phải bật hết một lượt.

---

## Tham chiếu chéo

Các trang con để đào tiếp từng trụ cột (từ chính trang overview):

- Observability: `/docs/observability/overview`, get-started `/docs/observability/get-started`
- Prompt Management: `/docs/prompt-management/overview`, get-started `/docs/prompt-management/get-started`, Playground `/docs/prompt-management/features/playground`
- Evaluation: `/docs/evaluation/overview`, Datasets `/docs/evaluation/features/datasets`, Prompt Experiments `/docs/evaluation/features/prompt-experiments`
- Demo tương tác: `/docs/demo`