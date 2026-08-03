---
title: Evaluation — Scores
doc_source:
  - https://langfuse.com/docs/evaluation/scores/overview
  - https://langfuse.com/docs/evaluation/scores/score-analytics
  - https://langfuse.com/docs/evaluation/scores/data-model
accessed: 2026-07-31
version: v4
status: draft
related:
  - ./evaluation-concepts.md
  - ./evaluation-overview.md
---

# Evaluation — Scores

Score là data object dùng chung của Langfuse để lưu mọi kết quả đánh giá: dù chấm bằng người, LLM judge, code, hay phản hồi người dùng cuối, kết quả đều quy về một dạng score. Mục này gồm bản chất score, bốn kiểu dữ liệu, schema ràng buộc (ScoreConfig), và công cụ phân tích có sẵn (Score Analytics).

## Tổng quan

Mọi phần ở đây xoay quanh một đối tượng và vòng đời của nó: score được tạo ra sao, gắn vào đâu, kiểu gì, ràng theo schema nào, rồi phân tích thế nào. Score object là điểm hội tụ của mọi phương pháp chấm; score type quyết định giá trị có gộp/so được không; ScoreConfig ép score theo một schema thống nhất; Score vs Tag phân định khi nào dùng score, khi nào dùng tag; cách tạo score trỏ sang các note evaluation-methods; Score Analytics đọc chính các score đó để kiểm độ tin và theo dõi xu hướng.

## 1. Score (data object)

**Khái niệm.** Score là đối tượng lưu kết quả đánh giá. Mỗi score gồm `name` (ví dụ `correctness`, `helpfulness`), một `value`, một `dataType`, và tùy chọn `comment`. Mỗi score trỏ tới **đúng một** trong bốn cấp: `trace`, `observation`, `session`, hoặc `dataset run` — phổ biến nhất là gắn lên trace để chấm trọn một lượt tương tác đầu-cuối; session để chấm xuyên nhiều lượt; observation để chấm một bước dưới trace; dataset run để chấm hiệu năng một lần chạy. Trường `source` được đặt tự động theo nguồn tạo: `API`, `EVAL`, hoặc `ANNOTATION`. Score thêm được vào bất cứ lúc nào, kể cả rất lâu sau khi trace đã tạo.

Thuộc tính đầy đủ của Score object:

| Thuộc tính | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `id` | string | Có | Định danh score. SDK tự sinh. Dùng được như idempotency key để update score. |
| `name` | string | Có | Tên score, ví dụ `user_feedback`, `hallucination_eval`. |
| `value` | number | Không | Giá trị số. Luôn có với numeric và boolean; tùy chọn với categorical; không dùng cho text. |
| `stringValue` | string | Không | Giá trị chuỗi. Dùng cho categorical, boolean (dạng chuỗi), text. Tự đặt cho categorical theo config nếu có `configId`. |
| `dataType` | string | Không | Tự đặt theo config khi có `configId`. Không thì khai tay: `NUMERIC`, `CATEGORICAL`, `BOOLEAN`, `TEXT`. |
| `source` | string | Có | Tự đặt theo nguồn: `API`, `EVAL`, hoặc `ANNOTATION`. |
| `comment` | string | Không | Ghi chú đánh giá — user feedback, lý giải của eval, hoặc ghi chú nội bộ. |
| `traceId` | string | Không | Id trace mà score gắn vào. |
| `observationId` | string | Không | Id observation (ví dụ một lần gọi LLM) mà score gắn vào. |
| `sessionId` | string | Không | Id session mà score gắn vào. |
| `datasetRunId` | string | Không | Id dataset run mà score gắn vào. |
| `configId` | string | Không | Id ScoreConfig để score tuân một schema. Đặt trong UI hoặc qua API. |

**Vai trò.** Là điểm chuẩn hóa: mọi phương pháp chấm đổ về cùng một cấu trúc, nên trộn được nhiều nguồn chấm trên cùng một object và đưa thẳng vào analytics, dashboard, hoặc API.

**Ví dụ.** Một trace trả lời khách nhận score `hallucination_eval`, source `EVAL` (LLM-as-a-Judge), value 0; cùng trace đó nhận score `user_feedback`, source `API` (thumbs up), value 1 — hai nguồn chấm khác nhau nằm chung một trace, đọc cùng lúc.

Chi tiết: https://langfuse.com/docs/evaluation/scores/overview · data model https://langfuse.com/docs/evaluation/scores/data-model

## 2. Bốn kiểu score (score types)

**Khái niệm.** Mỗi score mang một `dataType`, quyết định value biểu diễn thế nào và có gộp/so được không:

| Kiểu | Value | Dùng khi |
|---|---|---|
| `NUMERIC` | Số thực (ví dụ `0.9`) | Phán xét liên tục: accuracy, relevance, độ tương đồng |
| `CATEGORICAL` | Chuỗi từ tập nhãn định sẵn (ví dụ `"correct"`, `"partially correct"`) | Phân loại rời rạc, biết trước tập giá trị |
| `BOOLEAN` | `0` hoặc `1` | Kiểm pass/fail: phát hiện hallucination, validate format |
| `TEXT` | Chuỗi tự do (1–500 ký tự) | Ghi chú mở: nhận xét reviewer, phản hồi định tính |

**Vai trò.** Chọn kiểu theo bản chất phán xét: liên tục thì NUMERIC, phân loại biết trước thì CATEGORICAL, pass/fail thì BOOLEAN, ghi chú mở thì TEXT.

**Ví dụ.** Chấm accuracy trên thang 0.0–1.0 → NUMERIC; gán `"correct"`/`"partially correct"`/`"incorrect"` → CATEGORICAL; có hallucination hay không → BOOLEAN; reviewer ghi lý do → TEXT.

**!Note:** TEXT score không dùng được trong experiments, LLM-as-a-Judge, và Score Analytics, vì text tự do không gộp hay so sánh được. Tạo TEXT score với ý định phân tích định lượng thì nó vẫn ghi bình thường nhưng lặng lẽ vắng mặt ở các nơi đó — không báo lỗi.

## 3. Score config (ScoreConfig)

**Khái niệm.** ScoreConfig là schema ràng buộc cho score, để cả nhóm chấm theo một chuẩn. Gồm score name, data type, và ràng buộc miền giá trị: min/max cho numeric, danh sách categories cho categorical, 1–500 ký tự cho text. Định nghĩa trong UI hoặc qua API. Config **bất biến** — sửa không được, chỉ archive rồi tạo bản mới; đã archive thì khôi phục lại được bất cứ lúc nào. Khi score trỏ tới `configId`, `dataType` và `stringValue` (với categorical) được đặt tự động theo config.

Thuộc tính ScoreConfig object:

| Thuộc tính | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `id` | string | Có | Định danh score config. |
| `name` | string | Có | Tên config, ví dụ `user_feedback`, `hallucination_eval`. |
| `dataType` | string | Có | `NUMERIC`, `CATEGORICAL`, `BOOLEAN`, hoặc `TEXT`. |
| `isArchived` | boolean | Không | Config đã archive hay chưa. Mặc định false. |
| `minValue` | number | Không | Giá trị nhỏ nhất cho numeric. Không đặt thì mặc định −∞. |
| `maxValue` | number | Không | Giá trị lớn nhất cho numeric. Không đặt thì mặc định +∞. |
| `categories` | list | Không | Tập nhãn cho categorical. Danh sách cặp label–value. |
| `description` | string | Không | Mô tả thêm về config. |

**Vai trò.** Chuẩn hóa schema chấm across team để score nhất quán, so sánh được về sau. Bắt buộc phải dựng trước khi chấm tay qua UI (mục 6, Scores via UI).

**Ví dụ.** Config `response_quality`, kiểu CATEGORICAL, categories = {"good", "acceptable", "poor"}; mọi reviewer chấm qua UI buộc chọn trong ba nhãn này, không ai tự gõ nhãn lệch chuẩn.

Chi tiết: https://langfuse.com/docs/evaluation/scores/data-model#score-config

## 4. Comment

**Khái niệm.** Mỗi score có trường `comment` tùy chọn, ghi lý do (vì sao LLM judge cho điểm đó), ghi chú reviewer, hoặc ngữ cảnh; comment hiện cạnh score trong UI. Ranh giới dùng: comment là lý giải bổ sung *trên một score đã có*; còn phản hồi định tính đứng độc lập thì dùng TEXT score (mục 2), không nhét vào comment.

## 5. Score vs Tag

**Khái niệm.** Score đo *tốt tới đâu*; tag mô tả *là cái gì*. Hai thứ khác nhau về thời điểm và mục đích:

| | Scores | Tags |
|---|---|---|
| Mục đích | Đo chất lượng | Mô tả loại |
| Dữ liệu | Numeric, categorical, boolean, hoặc text | Nhãn chuỗi đơn giản |
| Thời điểm thêm | Bất cứ lúc nào, kể cả lâu sau khi tạo trace | Đặt lúc tracing, sau đó không đổi được |
| Dùng cho | Đo chất lượng, analytics, experiments | Lọc, phân đoạn, sắp xếp |

Quy tắc: biết category ngay lúc tracing (ví dụ feature hay API endpoint nào kích hoạt trace) thì dùng tag; cần phân loại hoặc đánh giá trace *về sau* thì dùng score. Tag thuộc mảng observability, có note riêng.

## 6. Cách tạo score

Năm đường thêm score, mỗi đường có note riêng dưới `evaluation-methods/` — ở đây chỉ nêu tên và điều kiện, không giảng lại:

- **LLM-as-a-Judge** — evaluator tự động chấm theo tiêu chí tùy biến, chạy trên trace production hoặc kết quả experiment.
- **Code evaluators** — logic Python/TypeScript cho kiểm tra tất định (exact match, validate JSON, quy tắc nghiệp vụ).
- **Scores via UI** — chấm tay trực tiếp trên UI; cần dựng ScoreConfig (mục 3) trước.
- **Annotation Queues** — quy trình review theo lô.
- **Scores via API/SDK** — đẩy score từ code; đây là đường cho user feedback (thumbs/star), kết quả guardrail, pipeline chấm tùy biến.

Chi tiết mỗi đường: các note dưới `evaluation-methods/`.

## 7. Score Analytics

**Khái niệm.** Score Analytics là công cụ phân tích score có sẵn ngay khi có dữ liệu, không cần cấu hình. Hai chế độ: phân tích **một score** (tổng số, mean/mode, độ lệch chuẩn, biểu đồ phân phối, xu hướng theo thời gian) và **so hai score** cùng data type (chỉ số tương quan/đồng thuận + heatmap). Visualization và metric tự đổi theo data type. Hai tab dữ liệu: **Matched** (chỉ object có gắn cả hai score — để so đúng) và **All** (phân phối từng score độc lập — để thấy độ phủ). Metric: numeric dùng Pearson, Spearman, MAE, RMSE; categorical/boolean dùng Cohen's Kappa, F1, Overall Agreement.

**Vai trò.** Kiểm độ tin của evaluator (hai judge có đồng thuận không), theo dõi xu hướng chất lượng, phát hiện regression sau deploy, và lộ khoảng trống phủ — khi matched count thấp hơn nhiều so với tổng từng score thì nhiều object đang thiếu một trong hai score.

**Ví dụ** (từ nguồn). Dùng cả GPT-4 và Gemini chấm `helpfulness` (NUMERIC); chọn hai score so nhau, Statistics card báo Pearson = 0.984 kèm nhãn "Very Strong", heatmap hiện đường chéo rõ → hai judge đồng thuận mạnh, eval đáng tin.

**!Note:** Query kỳ vọng >100k score (ở một trong hai score) tự động lấy mẫu ngẫu nhiên vì lý do hiệu năng — thống kê khi đó tính trên mẫu, không phải toàn bộ dữ liệu. Có chỉ báo hiện khi sampling bật; nếu cần đủ dữ liệu, thu hẹp bằng time range hoặc lọc object type.

Giới hạn khác (beta): tối đa hai score một lần (nhiều hơn thì so từng cặp); chỉ so cùng data type; TEXT không hỗ trợ (mục 2).

Chi tiết: https://langfuse.com/docs/evaluation/scores/score-analytics

## Tham chiếu chéo

- Mọi phương pháp chấm (mục 6) đổ kết quả về Score object (mục 1); data type (mục 2) quyết định score có vào được Analytics (mục 7) và experiments hay không — TEXT bị loại ở cả hai.
- Cách tạo score chi tiết nằm ở các note dưới `evaluation-methods/`; note này chỉ trỏ tên.
- Score gắn ở cấp trace/observation/session/dataset run; mô hình các đối tượng đó thuộc observability data model và experiments data model — xem note tương ứng, không lặp ở đây.
- User feedback (thumbs/star) là score `source=API`, chi tiết ở note user-feedback (observability).
- Tag (mục 5) thuộc observability, không phải score.
- Nhất quán với note Concepts: ở đó Score là một trong bốn khối nền; note này là bản khai triển của khối đó.