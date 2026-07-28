# Ranh giới file

## Một file, một câu hỏi

Mỗi file note trả lời đúng một câu hỏi. Câu hỏi đó chính là cột "Nội dung trình bày" của file trong `<nhánh>/SOURCES.md`. Viết lan sang câu hỏi của file khác là dấu hiệu ranh giới sai.

## Trùng thì stub, không nhân bản

Khái niệm đã được trình bày đầy đủ ở file khác: viết một đoạn ngắn nêu đủ để đọc tiếp được, rồi cross-link sang file nguồn chính. Không chép lại định nghĩa, không chép lại code mẫu.

Ví dụ: `03-06-guardrails.md` cần nhắc middleware là gì — nêu một câu, link sang `03-03-middleware/03-03-middleware-overview.md`, không diễn giải lại cơ chế hook.

Mỗi khái niệm chỉ có một file là nguồn chính. Nếu không rõ file nào là nguồn chính, tra `SOURCES.md` — file có URL docs gốc của khái niệm đó là nguồn chính.

## Kiểm tra trước khi tạo file mới

Trước khi tạo bất kỳ file `.md` mới trong một nhánh:

1. Đọc `<nhánh>/SOURCES.md` — chủ đề đã có dòng chưa?
2. Có rồi thì viết vào file đã khai báo, không tạo file thứ hai.
3. Chưa có thì thêm dòng vào `SOURCES.md` (file, URL docs, nội dung trình bày, ngày truy cập) cùng lúc với việc tạo file.

Tên file theo `<số-chương>-<số-mục>-<slug>.md`, đúng như `CONVENTIONS.md` mục 6. Số chương phải khớp thư mục chứa nó.
