---
description: Fetch một trang docs rồi viết note tiếng Việt theo template CONVENTIONS.md
argument-hint: <url-docs> [file-đích]
allowed-tools: WebFetch, Read, Write, Edit, Glob, Grep
---

Viết một note nghiên cứu từ trang docs này.

- URL docs: `$0`
- File đích (có thể trống): `$1`

## Bước 1 — Xác định file đích

`$1` có giá trị thì đó là file đích. Trống thì suy ra: đoán nhánh từ hostname/path của URL, đọc `<nhánh>/SOURCES.md`, tìm dòng có URL này. Có dòng khớp thì lấy cột File. Không có dòng nào khớp thì **dừng lại và hỏi tôi** file đích nên là gì — không tự đặt tên.

File đích đã tồn tại và có nội dung: hỏi tôi muốn viết mới hay bổ sung.

## Bước 2 — Fetch

`WebFetch` đúng URL `$0`. Đọc kỹ, ghi lại version LangChain/LangGraph/Langfuse nếu trang có nêu.

Trang redirect hoặc 404: báo tôi URL mới, không tự viết theo trang khác.

## Bước 3 — Viết

Theo template 7 mục ở `CONVENTIONS.md` mục 5. Frontmatter điền `doc_source` = `$0`, `accessed` = ngày hôm nay, `lc_version` = giá trị đọc được (`unknown` nếu không có), `status: draft`.

Mục 3 và mục 5 là phần tạo giá trị — không diễn đạt lại mục 2. Nội dung dựng lại phải gắn nhãn `(dựng lại)`.

Cross-link sang note khác: verify đích tồn tại trước, theo `.claude/rules/cross-reference.md`.

## Bước 4 — Đồng bộ SOURCES.md

Cập nhật cột "Ngày truy cập" của dòng tương ứng trong `<nhánh>/SOURCES.md`. Dòng chưa có thì thêm mới, đủ 4 cột.

## Bước 5 — Báo cáo

Liệt kê: file đã ghi, `lc_version` đọc được, những chỗ đã gắn `(dựng lại)`, những mục đã đưa vào "Câu hỏi còn mở", cross-link nào trỏ tới file chưa tồn tại.
