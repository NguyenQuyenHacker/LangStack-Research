# Từ vựng — dùng thống nhất giữa các file
 
Đây là nơi duy nhất chứa quy tắc dùng từ. `SKILL.md` chỉ trỏ sang, không chép lại.
 
Câu hỏi quyết định: **người đọc có phải gõ chữ này vào code không?**
 
- Có → giữ nguyên tiếng Anh
- Không → dịch sang tiếng Việt
Từ chưa có trong bảng thì áp câu hỏi trên rồi bổ sung vào bảng.
 
---
 
## Giữ nguyên tiếng Anh
 
Không dịch, vì người đọc phải gõ đúng những chữ này khi viết code hoặc tra tài liệu gốc:
 
- Tên hàm, phương thức: `stream()`, `invoke()`, `create_agent()`
- Tên thuộc tính: `.text`, `.output`, `.error`
- Tên tham số: `version=`, `name=`, `stream_mode=`
- Tên class, tên thư viện: `AgentMiddleware`, `LangGraph`
- Từ khóa cấu hình: `True`, `None`, `async`
---
 
## Nhóm 1 — Động từ và từ mô tả hành động: dịch thẳng
 
Loại gây tắc nhiều nhất. Dịch luôn trong câu, đừng để nguyên.
 
| Tiếng Anh | Dùng |
|---|---|
| delta | mẩu chữ, phần mới thêm |
| drain | lấy kết quả cuối |
| parse | chuyển thành dữ liệu dùng được |
| dispatch | gọi ra, kích hoạt |
| redact | che |
| emit | phát ra |
| consume | đọc, tiêu thụ |
| interleave | trộn xen kẽ |
| compile | dựng |
| resume | chạy tiếp |
| stream (động từ) | chảy dần, gửi dần |
 
Bắt buộc nhắc từ gốc thì để trong ngoặc **một lần duy nhất**: "từng mẩu chữ (tài liệu gọi là *delta*)".
 
---
 
## Nhóm 2 — Danh từ định danh của thư viện: giữ nguyên
 
`Middleware`, `Transformer`, `Checkpointer`, `Agent`, `Tool`, `Projection`.
 
Giữ nguyên vì người đọc phải gõ đúng và sẽ gặp lại trong tài liệu gốc. Giải thích ngay tại chỗ xuất hiện lần đầu.
 
---
 
## Nhóm 3 — Khái niệm trừu tượng: dịch, ghi từ gốc lần đầu
 
| Tiếng Anh | Dùng | Không dùng |
|---|---|---|
| projection | nhánh dữ liệu | phép chiếu, projection |
| chunk | mẩu vỡ | khối, đoạn |
| delta | mẩu, phần mới thêm | (giữ "delta" khi nói về khái niệm, dịch khi nói về dữ liệu cụ thể) |
| state | trạng thái | state |
| snapshot | ảnh chụp trạng thái | snapshot |
| node | chặng | nút, node |
| run | lần chạy | run |
| subgraph | quy trình con / agent con | đồ thị con |
| namespace | tầng | không gian tên |
| handle | mục, đầu mối | handle |
| instance | bản, một bản cụ thể | thể hiện, instance |
| factory | cái khuôn, hàm tạo | nhà máy |
| envelope | lớp vỏ, dữ liệu gốc chưa phân loại | phong bì |
| wire output | dữ liệu gửi ra ngoài | đầu ra dây |
| parse | (giữ "parse", giải thích tại chỗ) | phân tích cú pháp |
| PII | thông tin cá nhân | (giữ "PII" ở tiêu đề mục, dịch trong thân bài) |
| compile | lúc dựng | biên dịch |
| unit test | kiểm thử riêng lẻ | unit test |
| human-in-the-loop | dừng chờ người duyệt | vòng lặp có con người |
| interrupt | tín hiệu dừng | ngắt |
| checkpointer | nơi lưu trạng thái | điểm kiểm tra |
| middleware | (giữ "middleware", giải thích tại chỗ) | phần mềm trung gian |
| transformer | (giữ "transformer", giải thích tại chỗ) | bộ biến đổi |
| sync / async | đồng bộ / bất đồng bộ | sync / async |
| deprecated | không còn được khuyến nghị | lỗi thời |
| breaking change | thay đổi làm hỏng code cũ | thay đổi phá vỡ |
| fallback | phương án dự phòng | fallback |
| overhead | chi phí phát sinh | overhead |
 
---
 
## Cụm từ khuôn mẫu
 
Cách diễn đạt khoảng trống và suy luận nằm ở `SKILL.md`, mục "Phân biệt dữ kiện với suy luận". Ở đây chỉ giữ những cụm không có ở đó:
 
| Tình huống | Viết |
|---|---|
| Output tự dựng | "**Kết quả in ra** (dựng lại)" |
| Lỗi không báo | "lỗi im lặng — code chạy nhưng sai" |
| Được phép bỏ qua | "**bỏ qua mục này hoàn toàn**, đây là tính năng cho trường hợp đặc biệt" |
| Năng lực mới hoàn toàn | "thứ mới hoàn toàn, không có tương đương ở..." |
 
---
 
## Cấm dùng
 
Những cách diễn đạt sau không mang thông tin, xóa hoặc viết lại:
 
**Mở đầu rỗng:** "Dưới đây là...", "Đây là một câu hỏi hay", "Tất nhiên rồi"
 
**Kết thúc rỗng:** "Hy vọng thông tin này hữu ích", "Mọi thắc mắc xin liên hệ"
 
**Nối câu rỗng:** "Trong bối cảnh hiện nay", "Nhìn chung", "Về cơ bản", "Như đã đề cập ở trên"
 
**Nhấn mạnh rỗng:** "Điều này cho thấy", "Có thể thấy rằng", "Quan trọng là", "Đáng chú ý là", "Cần lưu ý rằng"
 
**Tính từ rỗng:** "toàn diện", "tổng thể", "đa dạng", "linh hoạt", "tối ưu hóa", "nâng cao hiệu quả" — chỉ dùng khi có nội dung cụ thể đi kèm
 
---
 
## Ví von — quy tắc
 
Được khuyến khích khi khái niệm trừu tượng. Nhưng phải là ví von **từ đời sống**, không phải từ một khái niệm kỹ thuật khác.
 
| Đánh giá | Ví dụ |
|---|---|
| Tốt | "đưa cái khuôn bánh, không đưa cái bánh đã đúc" (factory vs instance) |
| Tốt | "băng chuyền chung tự nhặt" so với "hệ thống van, mở van nào ra thứ đó" |
| Tốt | "đường ống nước thô" so với "hệ thống lọc lắp phía sau" (tầng dưới vs tầng trên) |
| Tệ | "giống singleton pattern" — người chưa biết vẫn không hiểu |
| Tệ | "hoạt động như một message broker" — thay một từ lạ bằng một từ lạ khác |
 
Một ví von chỉ dùng **một lần** trong file. Lặp lại nhiều lần thành sáo.
 