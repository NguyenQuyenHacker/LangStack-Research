# Glossary — thuật ngữ Anh–Việt

Dùng chung cả ba stack. Mỗi mục: thuật ngữ tiếng Anh, cách hiểu ngắn, và quy ước dịch (giữ nguyên EN hay dùng bản Việt). Bảng còn mỏng ở giai đoạn scaffold, bổ sung dần khi viết nội dung.

| Thuật ngữ (EN) | Cách hiểu ngắn | Quy ước |
|---|---|---|
| agent | Vòng lặp model gọi tool rồi nhận kết quả để quyết định bước tiếp | giữ EN |
| middleware | Lớp chèn vào vòng đời agent để can thiệp trước/sau từng bước | giữ EN |
| hook | Điểm móc trong vòng đời để chạy code tùy biến | giữ EN |
| harness | Khung chạy bao quanh model, điều phối tool và trạng thái | giữ EN |
| checkpointer | Thành phần lưu/khôi phục trạng thái đồ thị (thuộc LangGraph) | giữ EN |
| content block | Đơn vị nội dung trong một message (text, tool_use, image...) | giữ EN |
| tool | Hàm mà agent gọi được để tác động ra ngoài | giữ EN / "công cụ" |
| structured output | Buộc model trả về theo schema xác định | giữ EN |
| retrieval | Truy hồi tài liệu liên quan để nạp vào ngữ cảnh | giữ EN / "truy hồi" |
| guardrails | Ràng buộc chặn hành vi ngoài ý muốn | giữ EN |
| human-in-the-loop | Chèn người duyệt vào vòng chạy tự động | giữ EN |
| streaming | Trả kết quả theo dòng, từng phần | giữ EN |
| observability | Khả năng quan sát: trace, log, metric | giữ EN |
| durable execution | Chạy bền, khôi phục được sau gián đoạn (thuộc LangGraph) | giữ EN |

> Bổ sung thuật ngữ mới ngay khi gặp lần đầu trong lúc viết note, kèm quy ước dịch để cả ba stack dùng nhất quán.
