---
description: Đối chiếu SOURCES.md của một nhánh với danh mục docs gốc, báo trang mới/đổi tên/gộp/mất
argument-hint: <LangChain|LangGraph|Langfuse>
allowed-tools: WebFetch, Read, Glob
---

Audit `$0/SOURCES.md`. Chỉ báo cáo, không sửa file nào.

## Bước 1 — Đọc phía vault

Đọc `$0/SOURCES.md`, lập danh sách (file, URL docs, ngày truy cập). Với mỗi dòng, kiểm tra file có thật trên đĩa không.

## Bước 2 — Đọc phía docs gốc

Fetch danh mục hiện hành của nhánh đó. LangChain/LangGraph: `https://docs.langchain.com/llms.txt`. Langfuse: `https://langfuse.com/docs` (hoặc `llms.txt` nếu có).

Lọc ra tập URL thuộc phạm vi nhánh đang audit.

## Bước 3 — Diff

Báo cáo 5 nhóm:

1. **Trang mới** — có ở docs, chưa có dòng nào trong `SOURCES.md`
2. **Đổi tên / đổi path** — URL trong `SOURCES.md` giờ redirect sang chỗ khác
3. **Đã gộp hoặc bỏ** — URL trong `SOURCES.md` giờ 404
4. **File thiếu** — có dòng trong `SOURCES.md` nhưng file không có trên đĩa
5. **Note cũ** — `accessed` cách hôm nay quá 30 ngày

Với nhóm 1, đề xuất tên file theo quy ước `<chương>-<mục>-<slug>.md` và chương phù hợp — đề xuất thôi, chờ tôi duyệt.

## Bước 4 — Kết luận

Một bảng tổng kết: tổng số dòng, số khớp, số lệch theo từng nhóm. Không đề xuất hành động nào ngoài danh sách trên.
