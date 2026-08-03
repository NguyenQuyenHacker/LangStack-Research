---
title: Evaluation — Experiments
doc_source:
- https://langfuse.com/docs/evaluation/experiments/data-model
- https://langfuse.com/docs/evaluation/experiments/datasets
- https://langfuse.com/docs/evaluation/experiments/experiments-via-sdk
- https://langfuse.com/docs/evaluation/experiments/experiments-via-ui
- https://langfuse.com/docs/evaluation/experiments/experiments-ci-cd
accessed: 2026-07-31
version: v4
status: draft
---

# Evaluation — Experiments

## Tổng quan

**Định nghĩa.** Experiment là một lần chạy tập dữ liệu kiểm thử (Dataset) qua ứng dụng LLM, kèm tùy chọn chấm điểm kết quả. Mỗi lần chạy tạo ra một **Dataset run** (đồng nghĩa Experiment run).

**Mục tiêu.** Kiểm thử có cấu trúc trên cùng một bộ dữ liệu chuẩn; so sánh các phiên bản prompt/model; phát hiện hồi quy chất lượng trước khi release.

**Ba cách khởi chạy.** Qua SDK (lập trình), qua UI (kiểm thử prompt), trong CI/CD (tự động hóa trong pipeline) — tương ứng ba mục 3, 4, 5.

## 1. Mô hình dữ liệu

**Định nghĩa.** Tập các đối tượng cấu thành một Experiment và quan hệ giữa chúng.

**Đối tượng dữ liệu.**

| Đối tượng | Nội dung |
|---|---|
| Dataset | Tập các đầu vào (input) và, tùy chọn, đầu ra kỳ vọng (expected output). |
| DatasetItem | Một phần tử của Dataset: input, expected output, metadata; liên kết được về trace/observation gốc. |
| DatasetRun | Một lần chạy Dataset qua ứng dụng; đại diện một phiên bản/cấu hình đem so sánh. |
| DatasetRunItem | Bản ghi nối một DatasetItem với Trace sinh ra trong lần chạy đó. |

**Logic người dùng cung cấp (khi chạy qua SDK).**

| Loại | Nhiệm vụ |
|---|---|
| Task | Nhận một item, trả về output. |
| Evaluator | Chấm output của một item → tạo một Score. |
| Run Evaluator | Đánh giá toàn bộ kết quả lần chạy, tính chỉ số tổng hợp → gắn vào Dataset run. |

**Quan hệ end-to-end.** Mỗi DatasetItem đưa vào ứng dụng như input → sinh một Trace + một DatasetRunItem; Score gắn thêm vào Trace để đánh giá output.

> !Note: Dataset cục bộ (không lưu trên Langfuse) khi chạy qua SDK chỉ sinh Trace, không tạo Dataset run — chưa có màn so sánh/tổng hợp.

Nếu muốn tìm hiểu thêm hãy tham khảo thông qua https://langfuse.com/docs/evaluation/experiments/data-model

## 2. Dataset

**Định nghĩa.** Bộ dữ liệu kiểm thử gồm input và expected output — nền tảng của mọi Experiment, dùng chung cho cả UI lẫn SDK.

**Mục tiêu.** Tạo test case từ trace production thật; cùng nhóm xây dựng item; có một nguồn dữ liệu kiểm thử thống nhất.

**Khả năng chính.**

| Khả năng | Nội dung |
|---|---|
| Tạo item từ production | Chọn trace ứng dụng chạy sai → chuyên gia bổ sung expected output → kiểm thử phiên bản mới trên chính dữ liệu đó. |
| Đa phương thức (multi-modal) | Item đính kèm ảnh, audio, video, tài liệu ở input/expected output/metadata. Hỗ trợ qua SDK; UI chưa hỗ trợ item có media. |
| Thư mục (folder) | Gom nhóm dataset bằng cách thêm dấu `/` vào tên. |
| Versioning | Mỗi lần thêm/sửa/xóa/lưu trữ item tạo một phiên bản theo mốc thời gian; lấy được dataset đúng trạng thái tại một mốc để tái lập thí nghiệm. Chỉ áp dụng cho item, không cho schema. |
| Schema enforcement | Gắn JSON Schema cho input/expected output; item được kiểm tra tự động, item sai bị từ chối kèm lỗi cụ thể. |

Nếu muốn tìm hiểu thêm hãy tham khảo thông qua https://langfuse.com/docs/evaluation/experiments/datasets

## 3. Experiments via SDK

**Định nghĩa.** Cách chạy Experiment bằng lập trình: đưa ứng dụng hoặc prompt qua từng item của một dataset (cục bộ hoặc trên Langfuse), tùy chọn chấm điểm.

**Mục tiêu.** Chạy đúng logic ứng dụng của mình (không chỉ prompt); dùng hàm chấm điểm tùy biến; chạy nhiều thí nghiệm song song trên cùng dataset; tích hợp vào hạ tầng đánh giá sẵn có.

**Experiment runner tự xử lý.** Chạy song song có giới hạn; tự tạo trace cho mọi lần thực thi; chấm điểm hai mức; cô lập lỗi để một item hỏng không dừng cả thí nghiệm. Dataset trên Langfuse → tự tạo Dataset run để so sánh trong UI; dataset cục bộ → chỉ ghi trace và score.

**Hai mức chấm điểm.**

| Mức | Phạm vi |
|---|---|
| Evaluator | Nhận input, output, expected output, metadata của một item → trả chỉ số → thành Score trên trace. |
| Run evaluator | Đánh giá toàn bộ kết quả → tính chỉ số tổng hợp (ví dụ độ chính xác trung bình) → gắn vào Dataset run. |

**Bổ trợ.**

- *autoevals*: thư viện các hàm chấm điểm dựng sẵn (ví dụ Factuality) để dùng lại.
- *Kích hoạt từ UI*: cấu hình webhook để bấm nút chạy thí nghiệm SDK ngay trong UI — Langfuse gửi metadata dataset tới endpoint bên ngoài; endpoint chạy ứng dụng, chấm điểm, đẩy score ngược lại thành một Experiment run.

Nếu muốn tìm hiểu thêm hãy tham khảo thông qua https://langfuse.com/docs/evaluation/experiments/experiments-via-sdk

## 4. Experiments via UI (Prompt Experiments)

**Định nghĩa.** Chạy thí nghiệm ngay trong giao diện để thử các phiên bản prompt hoặc model và so sánh kết quả cạnh nhau.

**Mục tiêu.** Kiểm thử prompt (không phải toàn bộ logic ứng dụng); lặp nhanh giữa các phiên bản prompt/model; chặn hồi quy khi thay đổi prompt.

**Điều kiện cần.**

| Yêu cầu | Nội dung |
|---|---|
| Prompt dùng được | Biến của prompt trùng key trong input của item (ví dụ `{{question}}` khớp key `"question"`). Prompt chat ánh xạ được placeholder tới key chứa lịch sử hội thoại. |
| Dataset dùng được | Input của item là JSON, key JSON khớp biến của prompt. |
| Kết nối LLM | Phải cấu hình kết nối tới nhà cung cấp model trong cài đặt dự án (prompt chạy thật cho từng item). |
| Evaluator (tùy chọn) | LLM-as-a-Judge (chấm tiêu chí ngữ nghĩa) hoặc code evaluator (kiểm tra tất định), chấm dựa trên expected output. |

**Luồng thao tác.** Mở dataset → Start Experiment → chọn prompt, kết nối LLM, dataset, (tùy chọn) structured output theo JSON schema và evaluator → chạy → xem điểm tổng hợp trong bảng Experiments và so sánh các lần chạy cạnh nhau.

Nếu muốn tìm hiểu thêm hãy tham khảo thông qua https://langfuse.com/docs/evaluation/experiments/experiments-via-ui

## 5. Experiments in CI/CD

**Định nghĩa.** Chạy Experiment trong pipeline CI/CD để chặn hồi quy chất lượng trước khi thay đổi được release.

**Mục tiêu.** Tự động kiểm thử mỗi pull request/release; chặn merge khi chất lượng rớt dưới ngưỡng.

**Luồng.** Tạo dataset test case → viết script Experiment bằng SDK → gắn evaluator chấm output → raise `RegressionError` khi điểm vi phạm ngưỡng → dùng GitHub Action `langfuse/experiment-action` chạy script trong workflow.

**Cơ chế chặn (gate).** Script tính một chỉ số tổng hợp (ví dụ độ chính xác trung bình), so với ngưỡng; dưới ngưỡng → raise RegressionError → job CI thất bại → chặn merge/release. Action trả kết quả JSON và (khi đủ quyền) tự đăng bình luận lên pull request: trạng thái từng script, điểm mức run, link tới lần chạy và tới màn so sánh Experiment trên Langfuse.

**Ngoài GitHub Action.** Tích hợp trực tiếp với framework test (Pytest, Vitest): dùng kết quả evaluator tạo assertion, test fail khi điểm rớt dưới ngưỡng.

Nếu muốn tìm hiểu thêm hãy tham khảo thông qua https://langfuse.com/docs/evaluation/experiments/experiments-ci-cd