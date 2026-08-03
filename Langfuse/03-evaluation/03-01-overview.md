---
title: Evaluation — Overview
doc_source: https://langfuse.com/docs/evaluation/overview
accessed: 2026-07-31
version: v4
status: draft
---

# Evaluation — Overview

Evaluation là lớp trong Langfuse gom mọi cách đánh giá một LLM app về một chỗ: chấm bằng model (LLM-as-a-Judge), chấm tay (human annotation), hoặc quy trình chấm tùy biến qua API/SDK.

## Vấn đề

Không có eval, ta đánh giá hành vi của LLM app bằng cảm tính. Đổi một dòng prompt, đổi model, sửa một đoạn code — ta không có cách nào biết chất lượng đi lên hay đi xuống, ngoài việc đọc vài output rồi tự thấy "có vẻ ổn". Cách này không lặp lại được và không so sánh được giữa các phiên bản. Hậu quả là regression (thay đổi làm app tệ đi) chỉ lộ ra khi đã lên production, khi người dùng thật đã gặp.

Eval thay chỗ cảm tính đó bằng dữ liệu: một bộ tiêu chí cố định, chấm được thành con số, chạy lại được mỗi lần có thay đổi — nên bắt được regression *trước* khi ship.

## Định nghĩa

Eval là một phép kiểm tra **lặp lại được** trên hành vi của ứng dụng. "Lặp lại được" là điểm cốt: cùng một bộ tiêu chí, chạy lại trên nhiều phiên bản khác nhau, cho ra con số đặt cạnh nhau so được. Nhờ đó câu hỏi "bản mới có tốt hơn bản cũ không" trả lời được bằng số, không bằng cảm nhận.

Langfuse cho trộn nhiều loại tiêu chí trong cùng một chỗ — chấm bằng model, chấm tay, workflow tùy biến — nên đo được nhiều chiều trên cùng một ứng dụng: chất lượng, giọng điệu (tonality), độ chính xác dữ kiện, độ đầy đủ, và các chiều khác.

## Hai chế độ: online và offline

Cùng bộ khái niệm, nhưng chấm ở hai thời điểm khác nhau, phân biệt theo *dữ liệu được chấm là gì*:

- **Online** — chấm trên trace của production đang chạy, tức chấm chính những lượt phục vụ người dùng thật. Trả lời "app đang chạy tốt tới đâu ngay lúc này".
- **Offline** — chấm trước khi ship, trên kết quả của một lần chạy thử. Trả lời "thay đổi sắp đưa ra có làm app tốt hơn không".

## Bốn khối khái niệm nền

Toàn bộ mảng Evaluation dựng trên bốn danh từ xuất hiện xuyên suốt docs: **evaluator, score, dataset, experiment**. Nắm bốn khối này trước thì các trang feature sau chỉ là biến thể cách dùng.

Vai trò từng khối, rút từ nguồn:
- **Evaluator** — thành phần thực hiện việc chấm, đưa ra đánh giá. Có thể là người chấm tay, hoặc một quy trình tự động (ví dụ một model khác đóng vai giám khảo).
- **Score** — kết quả một lần chấm, ở dạng con số hoặc nhãn. Đây là dữ liệu để về sau theo dõi xu hướng theo thời gian.
- **Dataset** — một bộ test case cố định, dùng lại được qua nhiều lần chạy.
- **Experiment** — một lần chạy app trên dataset đó để so một thay đổi (prompt/model/code) với phiên bản trước.

*(suy luận: trang Overview chỉ liệt kê bốn danh từ này và nói Core Concepts giải thích cách chúng ghép nhau, chứ chưa tự định nghĩa evaluator sinh ra score. Bốn dòng vai trò trên là cách tôi ghép từ bảng tra + mô tả loop; định nghĩa chuẩn nằm ở Core Concepts, cần đối chiếu khi viết note con.)*

Chi tiết: https://langfuse.com/docs/evaluation/core-concepts

## Vòng AI engineering loop

Bốn khối trên không dùng rời rạc — chúng nối thành một vòng khép kín trong quá trình phát triển app. Lấy một chatbot đang chạy production làm ví dụ, vòng đó đi như sau:

1. **Chấm trace live** — mỗi lượt hội thoại thật được ghi lại thành một trace. Ta gắn score lên các trace này (tự động hoặc tay) để biết lượt nào app trả lời tốt, lượt nào hỏng. Đây là phần **online**.
2. **Thu thập ca đáng lưu thành dataset** — những trace điển hình, nhất là các ca app trả lời sai, được nhặt ra và gom thành một bộ test case cố định. Từ đây trở đi là phần **offline**.
3. **Chạy experiment để so thay đổi** — khi muốn sửa (đổi prompt, đổi model…), ta chạy phiên bản mới trên chính bộ dataset đó, đặt kết quả cạnh phiên bản cũ.
4. **Evaluator đánh giá kết quả** — chấm output của experiment để biết bản mới tốt lên hay tệ đi. Đạt thì ship ra production; ship xong lại sinh ra trace live mới, quay về bước 1.

Trình tự tóm lại: production sinh ra trace → trace tốt/xấu được chọn làm bộ test case (dataset) → mỗi thay đổi phải chạy qua bộ test đó (experiment) → evaluator chấm rồi mới quyết định ship. Eval nằm ở mọi mắt xích, không phải một bước cuối.

*(suy luận: trang Overview chỉ liệt kê bốn hoạt động và nói eval "chạy xuyên suốt" vòng lặp, không mô tả thứ tự khép kín hay việc ship xong quay lại bước 1. Cách nối bốn bước thành vòng và việc gán online↔bước 1, offline↔bước 2–4 là cách tôi đọc; vòng đầy đủ nằm ở trang academy bên dưới, chưa đọc.)*

Bối cảnh vòng lặp đầy đủ: https://langfuse.com/academy/ai-engineering-loop

## Tra cứu feature theo nhu cầu

Bảng ánh xạ nhu cầu sang feature tương ứng, giữ nguyên từ nguồn để tra nhanh khi viết các note con.

| Nhu cầu | Feature |
|---|---|
| Xem và chấm trace thủ công | Annotation Queues, Scores via UI |
| Thu phản hồi từ người dùng cuối | User Feedback |
| Ghi chú tự do trên trace | Text scores, Annotation Queues |
| Theo dõi các nhóm lỗi lặp lại | Score configs, scores |
| Dựng bộ test case dùng lại được | Datasets |
| So prompt/model/code cạnh nhau | Experiments via UI, Experiments via SDK |
| Chặn deploy khi có regression | CI/CD experiments |
| Chạy kiểm tra tất định (deterministic) | Code Evaluators |
| Tự động chấm trace production live | LLM-as-a-Judge, Scores via API/SDK |
| Theo dõi score biến động theo thời gian | Score Analytics, custom dashboards |

## Tham chiếu chéo

- **Core Concepts** là note nền, đọc trước mọi note feature: https://langfuse.com/docs/evaluation/core-concepts
- Mỗi hàng trong bảng tra sẽ là một note riêng dưới `evaluation-methods/`, `scores/`, `experiments/`.