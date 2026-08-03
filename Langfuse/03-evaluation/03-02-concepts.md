---
title: Evaluation — Concepts
doc_source: https://langfuse.com/docs/evaluation/core-concepts
accessed: 2026-07-31
version: v4
status: draft
related:
  - ./evaluation-overview.md
---

# Evaluation — Concepts

Core Concepts là trang nền của mảng Evaluation: định nghĩa bốn khối gặp khắp docs (score, evaluation method, dataset, experiment) và cách chúng ghép vào vòng đánh giá offline/online.

## Tổng quan

Mọi hình thức chấm trong Langfuse quy về một vòng: chấm thử trên bộ dữ liệu cố định trước khi deploy (offline), rồi chấm trace thật sau khi deploy (online), và ca lỗi từ trace thật lại bổ sung ngược vào bộ dữ liệu. Bốn khối phục vụ vòng này:

- **Score** — vật chứa kết quả chấm; mọi phương pháp chấm đều đổ về đây.
- **Evaluation Method** — hàm thực hiện việc chấm, sinh ra score.
- **Experiment** — khung chạy app trên một dataset để chấm offline.
- **Online Evaluation** — cấu hình cho evaluation method tự chấm trace production.

Vòng offline/online và phân biệt hai chế độ đã trình bày ở note Overview; mục 1 dưới đây bổ sung ví dụ quy trình cụ thể mà trang Overview không có.

## 1. Vòng đánh giá offline/online

**Khái niệm.** LLM app vận hành theo một vòng kiểm thử–giám sát lặp lại. Offline evaluation chấm app trên một dataset cố định *trước khi* deploy: chạy prompt/model mới trên các test case, xem score, chỉnh tới khi đạt rồi mới deploy — trong Langfuse thực hiện bằng Experiment. Online evaluation chấm trace thật *sau khi* deploy để bắt lỗi trong lưu lượng thực; khi phát hiện ca mà dataset chưa phủ, ta thêm ca đó ngược vào dataset để lần experiment sau bắt được.

**Vai trò.** Hai chế độ khép thành vòng: offline chặn regression trước khi ship, online phát hiện ca thực tế chưa lường, và mỗi ca mới làm dataset lớn dần thành bộ test đại diện.

**Ví dụ** (theo quy trình nguồn, chatbot chăm sóc khách hàng):

1. Sửa prompt cho giọng bớt trang trọng.
2. Trước khi deploy, chạy experiment: test prompt mới trên dataset câu hỏi khách hàng (offline).
3. Xem score và output — giọng cải thiện, nhưng câu trả lời dài ra và vài câu thiếu link quan trọng.
4. Chỉnh prompt, chạy lại experiment.
5. Kết quả đạt, deploy prompt mới lên production.
6. Giám sát bằng online evaluation để bắt ca mới.
7. Phát hiện một khách hỏi tiếng Pháp nhưng bot trả lời tiếng Anh.
8. Thêm câu hỏi tiếng Pháp đó vào dataset để experiment sau bắt được.
9. Sửa prompt cho hỗ trợ tiếng Pháp rồi chạy experiment tiếp.

Qua thời gian, dataset lớn dần từ vài ví dụ thành bộ test case thực tế đa dạng.

## 2. Score

**Khái niệm.** Score là data object dùng chung của Langfuse để lưu kết quả đánh giá. Bất kể việc chấm đến từ đâu — human annotation, LLM judge, kiểm tra bằng code, hay phản hồi người dùng cuối — kết quả đều lưu dưới dạng score. Mỗi score gắn được lên trace, observation, session, hoặc dataset run. Mỗi score có ba thành phần: **name**, **value**, và **data type**; data type nhận một trong `NUMERIC`, `CATEGORICAL`, `BOOLEAN`, `TEXT`.

**Vai trò.** Là điểm hội tụ của mọi phương pháp chấm: nhờ mọi kết quả cùng một định dạng, ta trộn được nhiều nguồn chấm và theo dõi xu hướng trên cùng một trục.

**Ví dụ.** Một trace trả lời khách được LLM-as-a-Judge chấm `helpfulness` = 0.8 (NUMERIC), đồng thời reviewer gắn `tone` = "formal" (CATEGORICAL); cả hai cùng nằm trên trace đó, đọc chung được.

Chi tiết (kiểu score, cách tạo, analytics): https://langfuse.com/docs/evaluation/scores/overview

## 3. Evaluation Methods

**Khái niệm.** Evaluation method là hàm thực hiện việc chấm trên trace, observation, session, hoặc dataset run, và sinh ra score. Langfuse có sẵn năm phương pháp, khác nhau ở chỗ ai/cái gì chấm và chấm khi nào:

| Phương pháp | Chấm bằng gì | Dùng khi |
|---|---|---|
| LLM-as-a-Judge | Dùng một LLM chấm output theo tiêu chí tùy biến | Đánh giá chủ quan ở quy mô lớn (giọng, độ chính xác, mức hữu ích) |
| Code evaluators | Chạy logic Python/TypeScript tùy biến để chấm observation hoặc experiment | Kiểm tra tất định, validate output có cấu trúc, quy tắc nghiệp vụ riêng |
| Scores via UI | Thêm score thủ công trực tiếp trên UI Langfuse | Soát nhanh vài trace, xem từng trace lẻ |
| Annotation Queues | Quy trình review có cấu trúc với hàng đợi tùy biến | Dựng ground truth, gán nhãn hệ thống, cộng tác nhóm |
| Scores via API/SDK | Thêm score bằng code qua API/SDK Langfuse | Pipeline chấm tùy biến, kiểm tra tất định, workflow tự động |

**Vai trò.** Cùng đổ về score nhưng chọn phương pháp theo bản chất tiêu chí: cần tất định thì code evaluator, cần phán xét chủ quan diện rộng thì LLM-as-a-Judge, cần chuẩn vàng do người ra thì Annotation Queues.

**Ví dụ.** Validate rằng output JSON của agent luôn đủ trường bắt buộc → code evaluator (tất định); chấm 5.000 lượt hội thoại xem giọng có đúng brand không → LLM-as-a-Judge (chủ quan, quy mô).

Sau khi dựng method mới, dùng Score Analytics để kiểm/định cỡ score sinh ra: https://langfuse.com/docs/evaluation/scores/score-analytics

## 4. Experiment

**Khái niệm.** Experiment là một lần chạy app trên một dataset rồi chấm output — cách test thay đổi trước khi deploy. Khối này ghép từ sáu đối tượng:

| Đối tượng | Định nghĩa |
|---|---|
| **Dataset** | Tập test case (các dataset item). Experiment chạy trên một dataset. |
| **Dataset item** | Một item trong dataset. Gồm input (kịch bản cần test) và tùy chọn expected output. |
| **Task** | Đoạn code ứng dụng cần test. Task chạy trên từng dataset item, output của nó sẽ được chấm. |
| **Evaluation Method** | Hàm chấm kết quả experiment — có thể là code evaluator, score đẩy từ code qua API/SDK, hoặc LLM-as-a-Judge. |
| **Score** | Kết quả của một lần chấm. Kiểu dữ liệu xem mục 2. |
| **Experiment Run** | Một lần chạy task trên toàn bộ item của dataset, sinh ra output (và score). |

**Cách các đối tượng ghép nhau.** Khi chạy experiment trên một dataset, mỗi dataset item được đưa vào task; task (thường là một lần gọi LLM trong app) sinh output cho từng item — trọn quá trình này là một experiment run, và tập output gắn với các item là experiment results. Sau đó dùng evaluation method nhận (dataset item + output) để sinh score theo tiêu chí ta đặt. Có score rồi thì so được các experiment run với nhau: prompt mới có nâng score không, input nào app hay hỏng, từ đó quyết định thay đổi đã sẵn sàng deploy chưa.

Data model chi tiết: https://langfuse.com/docs/evaluation/experiments/data-model

**Hai cách chạy experiment.** Chạy bằng SDK (toàn quyền trên task, logic chấm) hoặc chạy thẳng trên UI (chọn dataset + prompt version, hợp để lặp nhanh trên prompt mà không viết code). Điều kiện hỗ trợ phụ thuộc nơi đặt dataset và nơi chạy:

| Nơi đặt dataset | Chạy trên Langfuse | Chạy Local/CI |
|---|---|---|
| Dataset trên Langfuse | Experiments via UI | Experiments via SDK |
| Dataset local | Không hỗ trợ | Experiments via SDK |

Tổ hợp dataset local + chạy trên UI Langfuse không được hỗ trợ. Nguồn khuyến nghị để dataset trên Langfuse để [1] so bảng các experiment trên cùng dữ liệu ngay trong UI và [2] cải thiện dataset dần từ trace production/staging — đây là khuyến nghị, không phải ràng buộc kỹ thuật cho việc chạy SDK.

**Vai trò.** Experiment là bộ khung offline: biến một thay đổi (prompt/model/code) thành con số so được với phiên bản trước trên cùng bộ test, để chặn regression trước khi ship.

**Ví dụ.** Có dataset 200 câu hỏi khách hàng; đổi từ model A sang B, chạy experiment run trên cả 200 item, LLM-as-a-Judge chấm `helpfulness`; đặt hai run cạnh nhau thấy B nâng điểm ở phần lớn item nhưng tụt ở nhóm câu hỏi pháp lý → giữ A cho nhóm đó hoặc chỉnh tiếp.

Chi tiết chạy: SDK https://langfuse.com/docs/evaluation/experiments/experiments-via-sdk · UI https://langfuse.com/docs/evaluation/experiments/experiments-via-ui

## 5. Online Evaluation

**Khái niệm.** Online evaluation là cấu hình cho evaluation method tự động chấm trace production. Langfuse hỗ trợ LLM-as-a-Judge, code evaluator, và human annotation check cho chế độ này.

**Vai trò.** Bắt lỗi ngay trên lưu lượng thật thay vì đợi lần test offline kế tiếp; các ca lỗi phát hiện ở đây là nguồn bổ sung dataset, nối lại vòng ở mục 1.

**Ví dụ.** Cấu hình LLM-as-a-Judge chấm `groundedness` trên mọi trace production của một RAG agent; trace nào tụt dưới ngưỡng được đánh dấu để review và đưa vào dataset.

Giám sát bằng dashboard: Langfuse có dashboard theo dõi hiệu năng app và score theo thời gian thực — https://langfuse.com/docs/metrics/features/custom-dashboards

## Tham chiếu chéo

- **Note Overview** giữ vòng offline/online ở mức định vị + bảng tra feature theo nhu cầu. Mục 1 ở đây là bản chi tiết có ví dụ quy trình; hai file phải thống nhất thứ tự offline→online.
- Score, Evaluation Methods, Experiment, Online Evaluation mỗi khối sẽ có note riêng dưới `scores/`, `evaluation-methods/`, `experiments/`.
- Ràng buộc cắt ngang: mọi phương pháp chấm (mục 3) đều đổ kết quả về Score (mục 2); Experiment (mục 4) và Online Evaluation (mục 5) chỉ khác ở chỗ chấm dataset cố định hay chấm trace production, còn evaluation method dùng chung.