# LangStack-Research

Vault VitePress **tiếng Việt** tổng hợp docs OSS của LangChain / LangGraph / Langfuse. Nội dung là note nghiên cứu, không phải code — mọi thay đổi đều là markdown.

Ba nhánh: `LangChain/` (đã xong), `LangGraph/`, `Langfuse/` (đang làm). Mỗi nhánh có `README.md` (trang index) và `SOURCES.md` (ánh xạ file ↔ URL docs gốc).

## Quy ước nguồn

Quy ước viết note nằm ở [CONVENTIONS.md](CONVENTIONS.md) — template 7 mục, quy ước đặt tên file, quy ước ảnh. Thuật ngữ Anh–Việt ở [GLOSSARY.md](GLOSSARY.md). Không chép lại hai file này vào chỗ khác; sửa thì sửa ở đó.

Khi skill `/research-note-vi` có mặt, dùng nó để viết note. Chưa có thì `CONVENTIONS.md` là nguồn quy trình.

## Bốn nguyên tắc lõi

- **Trung thực nguồn** — mọi khẳng định phải truy được về trang docs đã fetch → [.claude/rules/fidelity.md](.claude/rules/fidelity.md)
- **Bám phiên bản** — fetch bản docs hiện hành trước khi viết, không viết theo trí nhớ v0 → [.claude/rules/fidelity.md](.claude/rules/fidelity.md)
- **Ranh giới file** — mỗi file một câu hỏi; trùng thì stub + cross-link → [.claude/rules/file-boundary.md](.claude/rules/file-boundary.md)
- **Nhãn `(dựng lại)`** — nội dung không lấy trực tiếp từ docs phải gắn nhãn → [.claude/rules/fidelity.md](.claude/rules/fidelity.md)

Cross-link: [.claude/rules/cross-reference.md](.claude/rules/cross-reference.md). Văn phong: [.claude/rules/writing-style-vi.md](.claude/rules/writing-style-vi.md).

## Quy trình một note

Tôi đưa frontmatter stub + URL docs → bạn fetch trang đó → viết note theo template → lưu vào đúng nhánh, đúng thư mục chương → điền `lc_version` và `accessed` bằng giá trị thật đọc được lúc fetch.

Trước khi tạo file mới, đọc `<nhánh>/SOURCES.md` xem chủ đề đã có chỗ chưa.

## Lệnh

- `/research <url> [file đích]` — fetch rồi viết một note
- `/audit-sources <nhánh>` — đối chiếu `SOURCES.md` với sidebar docs gốc
- `/new-note` — dựng file khung từ frontmatter stub

## Không đọc

`.prompts/` chứa prompt dựng vault, không phải nội dung vault. Đã chặn bằng deny rule trong `.claude/settings.json`.
