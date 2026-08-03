---
title: Observability — Features — Phản hồi & chú thích
doc_source:
  - https://langfuse.com/docs/observability/features/user-feedback
  - https://langfuse.com/docs/observability/features/corrections
  - https://langfuse.com/docs/observability/features/comments
accessed: 2026-08-03
version: v4
status: draft
related:
  - ./01-05-00-index.md
---

# Phản hồi & chú thích

Nhóm ba tính năng để con người — người dùng cuối, chuyên gia lĩnh vực, hoặc thành viên nhóm — gắn thông tin đánh giá và ghi chú lên trace **sau khi** trace đã được ghi lại.

## Tổng quan

Khác các nhóm feature lo việc thu và tổ chức dữ liệu tự động (sampling, batching, gắn nhãn), nhóm này là lớp tín hiệu do con người tạo ra và bổ sung lên dữ liệu đã có. Hai trong ba tính năng hạ cánh dưới dạng *score* gắn vào trace, một tính năng là ghi chú tự do.

`User Feedback` thu tín hiệu đánh giá từ người dùng cuối (hoặc suy ra từ hành vi họ) về việc output có giúp được gì không. `Corrections` ghi lại bản output đúng do chuyên gia cung cấp, đặt cạnh output gốc. `Comments` là ghi chú tự do cho cộng tác nội bộ, không sinh ra score.

## 1. User Feedback

### Khái niệm

Cơ chế thu tín hiệu đánh giá của người dùng cuối về chất lượng một output, lưu dưới dạng score gắn vào trace tương ứng. Có hai loại. **Explicit** là tín hiệu người dùng chủ động đưa ra: thumbs up/down, chấm sao, hoặc comment — tín hiệu rõ nhưng tỷ lệ phản hồi thấp và lệch về phía người không hài lòng. **Implicit** là tín hiệu suy ra từ hành vi: thời gian đọc, thao tác copy output, chấp nhận gợi ý, hay thử lại truy vấn — khối lượng lớn trên mọi lượt tương tác nhưng tín hiệu nhập nhằng, cần diễn giải.

Về cách vận hành: frontend hoặc backend gọi hàm tạo score (`score` / `create_score`) với `traceId` để móc tín hiệu vào đúng trace. Ở frontend, Browser SDK chỉ dùng public key (không được để lộ secret key). Với implicit feedback, ta có thể tự động hóa bằng LLM-as-a-Judge để chấm mọi response mà không cần người dùng tác động.

### Vai trò

Tìm ra các response bị đánh giá thấp, xây dataset đánh giá, và ưu tiên hạng mục cải thiện dựa trên trải nghiệm thật thay vì phỏng đoán.

### Ví dụ

Chatbot hỗ trợ khách hàng gắn nút thumbs up/down dưới mỗi câu trả lời; lọc trace có `user-feedback < 1` để khoanh vùng các response người dùng chấm kém. Ở phía backend, hệ thống ghi score `ticket-resolution = 1` khi ticket đóng thành công, `= 0` khi phải chuyển lên nhân viên — dùng chính trạng thái ticket làm tín hiệu implicit.

**!Note:** Feedback từ frontend chỉ móc được vào trace nếu `traceId` khớp một trace có thật. Trong ví dụ docs, message ID lấy từ `getActiveTraceId() || ""`; nếu không có active trace, giá trị rơi về chuỗi rỗng. Khi đó score vẫn tạo thành công nhưng không gắn vào trace nào — tín hiệu mất, không có lỗi báo ra.

Chi tiết cấu hình: https://langfuse.com/docs/observability/features/user-feedback

## 2. Corrections

### Khái niệm

Cơ chế ghi lại bản output "lẽ ra phải như thế này" do chuyên gia lĩnh vực cung cấp, hiển thị cạnh output gốc kèm diff view chỉ ra phần thay đổi. Bản chất lưu trữ là một score với `dataType: "CORRECTION"` và `name: "output"`. Mỗi trace hoặc observation chỉ giữ được một corrected output.

Thêm correction qua hai đường. Qua UI: mở trang chi tiết trace/observation, dùng trường **Corrected Output** dưới output gốc, chuyển giữa chế độ JSON validation và plain text, trình soạn tự lưu khi gõ và có diff so sánh. Qua API/SDK: gọi `create_score` với ba tham số định danh trên. Việc **đọc lại** correction hiện chỉ có endpoint HTTP (`GET /api/public/scores?dataType=CORRECTION`); fetch qua SDK Python/TypeScript được docs ghi là "coming soon".

### Vai trò

Dựng dataset fine-tuning chất lượng cao từ trace production (ghép input gốc với output đã sửa), benchmark output thực tế so với kỳ vọng để phát hiện lỗi hệ thống, và làm bước human-in-the-loop trong quy trình review.

### Ví dụ

Agent tư vấn sinh ra một output sai một điều khoản. Chuyên gia mở trace, nhập bản đúng vào trường Corrected Output; hệ thống lưu nó thành score dạng CORRECTION. Sau đó export toàn bộ cặp (input gốc, corrected output) từ các trace tương tự làm dữ liệu huấn luyện cho vòng cải thiện tiếp theo.

Chi tiết cấu hình: https://langfuse.com/docs/observability/features/corrections

## 3. Comments

### Khái niệm

Lớp ghi chú tự do gắn vào trace, observation, session, hoặc prompt để nhóm cộng tác — không phải score, không dùng cho chấm điểm. Thao tác chủ yếu qua UI: nút comment mở side drawer chứa thread theo thứ tự thời gian và ô soạn (nếu có quyền write), hỗ trợ markdown cơ bản, `@mentions` để tag thành viên (kèm gửi email thông báo), và reactions emoji. Comment còn neo được vào một đoạn text cụ thể trong input/output/metadata qua chế độ JSON Beta view. Cũng có API tương ứng (`GET`/`POST /api/public/comments`).

Về quyền: tác giả chỉ xóa được comment của chính mình; admin dự án không xóa được comment người khác qua UI. Về tính toàn vẹn tham chiếu: nếu dữ liệu trace/observation bị cập nhật *sau khi* comment đã tạo, comment chuyển sang trạng thái "detached" với chỉ báo trực quan cho biết phần được tham chiếu có thể đã đổi.

### Vai trò

Đánh dấu bất thường trong một trace, ghi chú debug và edge case, phối hợp cải thiện prompt trong các chu kỳ review — trao đổi nội bộ ngay tại chỗ dữ liệu thay vì tách sang kênh khác.

### Ví dụ

Reviewer phát hiện một trace agent trả lời lệch yêu cầu. Họ để comment `@mention` người phụ trách prompt và neo comment vào đúng đoạn output trong JSON Beta view để chỉ chính xác chỗ sai, thay vì mô tả vòng vo cả trace.

Chi tiết cấu hình: https://langfuse.com/docs/observability/features/comments

## Tham chiếu chéo

`User Feedback` và `Corrections` cùng hạ cánh dưới dạng **score** gắn vào trace — mọi cơ chế lọc, export, và phân tích áp cho score đều dùng lại được cho hai tính năng này; xem file về scores/evaluation khi có. `Comments` đứng riêng: là ghi chú tự do, không sinh score, nên không xuất hiện trong luồng dữ liệu đánh giá.

Ràng buộc cần nhớ khi triển khai: đọc lại corrections hiện chỉ có đường HTTP (SDK Python/TypeScript chưa hỗ trợ) — nếu pipeline dựng dataset dựa vào SDK fetch thì phải chờ hoặc gọi thẳng REST.

Trỏ về: [./01-05-00-index.md](./01-05-00-index.md)