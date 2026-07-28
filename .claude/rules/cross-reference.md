# Cross-link

## Đường dẫn tương đối, đã verify

Cross-link dùng đường dẫn tương đối tính từ file đang viết. Note nằm sâu một cấp trong nhánh, nên link sang chương khác có dạng `../03-harness/03-02-tools.md`, sang gốc repo là `../../GLOSSARY.md`.

**Trước khi viết một link, phải xác nhận đích tồn tại.** Hai bước:

1. Tra `<nhánh>/SOURCES.md` — file đó đã được khai báo chưa, tên chính xác là gì.
2. Đọc thư mục đích để xác nhận file có trên đĩa.

Chỉ có trong `SOURCES.md` mà chưa có trên đĩa: vẫn link được (site bật `ignoreDeadLinks`), nhưng phải ghi vào mục 6 của note rằng đích chưa viết.

Không có ở cả hai chỗ: không được bịa tên file. Diễn đạt bằng văn xuôi hoặc ghi vào mục 6.

## Anchor

Link tới một mục cụ thể phải dùng anchor có thật — mở file đích, lấy đúng tiêu đề, chuyển thành slug. Không đoán anchor từ tên mục mình tưởng tượng.

## Hai chiều khi đáng

Khi A stub và trỏ sang B là nguồn chính, cân nhắc thêm link ngược từ B sang A ở mục 5 (Ranh giới và đánh đổi) của B. Không bắt buộc — chỉ làm khi người đọc B thật sự cần biết A tồn tại.

## Link ra ngoài

Link tới docs gốc đặt ở mục 7 (Tham chiếu), kèm ngày truy cập. Không rải URL docs giữa thân bài trừ khi câu văn cần chỉ đúng một trang cụ thể.
