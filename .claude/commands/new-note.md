---
description: Dựng file note khung từ frontmatter stub — chỉ khung, không viết nội dung
argument-hint: [đường-dẫn-file]
allowed-tools: Read, Write, Glob
---

Tạo một file note khung. **Không fetch docs, không viết nội dung.**

Frontmatter stub tôi đưa nằm trong tin nhắn này (hoặc ở `$ARGUMENTS`). Nếu tôi chưa đưa stub, hỏi tôi trước khi làm gì khác.

## Bước 1 — Kiểm tra

- Trường bắt buộc: `title`, `doc_source`. Thiếu thì hỏi.
- Đường dẫn file đúng quy ước `<nhánh>/<thư-mục-chương>/<chương>-<mục>-<slug>.md`.
- Đọc `<nhánh>/SOURCES.md`: chủ đề này đã có dòng chưa? Có rồi mà file đã tồn tại thì báo tôi, dừng lại.

## Bước 2 — Ghi file

Frontmatter: giữ nguyên các trường tôi đưa, bổ sung trường còn thiếu theo `CONVENTIONS.md` mục 5 với giá trị mặc định — `accessed` để trống, `lc_version: unknown`, `status: draft`, `lab:` để trống.

Thân bài: 7 heading đúng thứ tự và đúng chữ của template, mỗi mục để lại một dòng ghi chú `<!-- ... -->` nhắc mục đó phải chứa gì. Không viết câu nội dung nào.

## Bước 3 — SOURCES.md

Chưa có dòng cho file này thì thêm vào `<nhánh>/SOURCES.md`, đúng chương, đủ 4 cột. Cột "Ngày truy cập" để trống — chưa fetch.

## Bước 4

Báo đường dẫn file đã tạo và dòng đã thêm vào `SOURCES.md`. Nhắc tôi chạy `/research <url>` để điền nội dung.
