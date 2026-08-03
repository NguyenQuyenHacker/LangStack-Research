---
title: Prompt Management — Features — Versioning & Deployment
doc_source:
  - https://langfuse.com/docs/prompt-management/features/prompt-version-control
  - https://langfuse.com/docs/prompt-management/features/a-b-testing
  - https://langfuse.com/docs/prompt-management/features/folders
accessed: 2026-08-03
version: v4
status: draft
related:
  - ./02-03-00-index.md
---

# Versioning & Deployment

Nhóm ba tính năng quản lý prompt sau khi đã soạn: đưa version nào ra môi trường nào, so sánh hai version trên lưu lượng thật, và tổ chức thư viện prompt khi số lượng lớn.

## Tổng quan

Ba tính năng này thao tác trên ba định danh của prompt object chứ không đụng vào nội dung: Version Control cấp hai primitive `version` (ID tự sinh) và `label` (do người dùng gán); A/B Testing là một cách dùng label — gán hai nhãn cho hai version rồi chia lưu lượng; Folders dùng trục `name` — dấu `/` trong tên tách prompt thành thư mục ảo. A/B Testing không thêm cơ chế mới, nó đứng trên label của Version Control; Folders độc lập, chỉ là quy ước đặt tên.

## 1. Version Control

**Khái niệm.** Version Control là cơ chế quản lý triển khai prompt qua hai định danh song song. Mỗi lần tạo version mới, Langfuse tự gán một `version ID` tăng dần; song song đó người dùng gán `label` tùy ý để theo sơ đồ version riêng — nhãn dùng để trỏ tới môi trường (`staging`, `production`), tenant, hay biến thể thử nghiệm. Trong SDK, fetch prompt theo `version=n` hoặc theo `label="..."`; cập nhật nhãn cho version đã có qua `update_prompt(..., new_labels=[...])` (Python) hoặc `prompt.update({ newLabels: [...] })` (JS/TS). Hai nhãn có ý nghĩa đặc biệt: `latest` luôn trỏ version tạo gần nhất và do Langfuse tự duy trì; `production` là version được phục vụ mặc định khi fetch không kèm nhãn. "Deploy" một version tức là gán nhãn `production` (hoặc nhãn môi trường tự tạo) cho version đó; rollback là gán lại nhãn `production` sang version cũ ngay trên UI. UI còn có view diff giữa các version để lần lại thay đổi. Nhãn có thể được đánh dấu **protected** (tính năng Enterprise / self-hosted EE) — khi đó `viewer`/`member` không sửa/xóa được nhãn, chỉ `admin`/`owner` mới đổi, đồng thời chặn xóa cả prompt.

**Vai trò.** Tách việc sửa nội dung prompt khỏi việc quyết định version nào chạy thật, để đổi hoặc rollback prompt trong ứng dụng chỉ bằng thao tác gán nhãn, không phải deploy lại code.

**Ví dụ.** Một agent hỗ trợ khách hàng đang chạy version có nhãn `production`. Ta tạo version 8 sửa lại lời chỉ dẫn, gán nhãn `staging`, kiểm thử; đạt yêu cầu thì gán `production` sang version 8. Version cũ vẫn còn — nếu version 8 gây lỗi ngoài thật, gán `production` trả về version 7 là xong, không đụng tới code đang deploy.

> **!Note:** Fetch prompt không kèm nhãn không trả về version mới nhất mà trả về version mang nhãn `production`. Sau khi tạo version mới, ứng dụng vẫn phục vụ bản cũ cho tới khi nhãn `production` được chuyển sang — dễ nhầm là "đã cập nhật nhưng không thấy đổi". Muốn lấy bản mới nhất phải fetch theo `label="latest"` một cách tường minh.

Chi tiết cấu hình: https://langfuse.com/docs/prompt-management/features/prompt-version-control

## 2. A/B Testing

**Khái niệm.** A/B Testing là mẫu dùng label của Version Control để chạy nhiều biến thể prompt song song trên lưu lượng thật. Gán mỗi version một nhãn phân biệt (ví dụ `prod-a`, `prod-b`); ứng dụng fetch cả hai rồi tự chọn ngẫu nhiên cho mỗi request (`random.choice` ở Python, so `Math.random()` ở JS/TS); Langfuse gom số liệu theo từng version để so sánh: latency, cost mỗi request, token usage, điểm đánh giá chất lượng, và metric tùy biến. Để số liệu quy được về đúng version, lời gọi LLM phải gắn tham chiếu prompt qua `langfuse_prompt` (Python) / `langfusePrompt` (JS/TS). Docs khuyến nghị dùng khi ứng dụng có cách đo thành công rõ, chịu được dao động hiệu năng, và đã kiểm thử trên dataset trước — điển hình là canary: thả biến thể mới cho một nhóm nhỏ trước khi mở rộng.

**Vai trò.** Đo hiệu năng thực tế của các biến thể prompt trên người dùng thật, bổ sung cho kết quả kiểm thử trên dataset vốn không phản ánh hết đầu vào đa dạng.

**Ví dụ.** Một prompt tóm tắt hội thoại có hai biến thể gán `prod-a` và `prod-b`; ứng dụng chia đôi lưu lượng ngẫu nhiên. Sau một tuần, UI cho thấy `prod-b` giảm token usage nhưng điểm chất lượng thấp hơn — đủ dữ kiện để quyết định gán `production` cho nhánh nào.

> **!Note:** Thiếu `langfuse_prompt` / `langfusePrompt` trên lời gọi thì test vẫn chạy bình thường, nhưng số liệu không quy được về version — bảng so sánh theo version rỗng, mất toàn bộ mục đích của A/B test.

Chi tiết cấu hình: https://langfuse.com/docs/prompt-management/features/a-b-testing

## 3. Folders

**Khái niệm.** Folders là thư mục ảo để gom prompt cùng nhóm, tạo bằng cách thêm dấu `/` vào tên prompt — mỗi đoạn tên kết thúc bằng `/` được UI hiển thị thành một cấp thư mục; không có thực thể folder riêng, chỉ là quy ước trên trường `name`. Truy cập prompt nằm trong folder qua Python SDK yêu cầu `langfuse >= 3.0.2`.

Chi tiết cấu hình: https://langfuse.com/docs/prompt-management/features/folders

## Tham chiếu chéo

- A/B Testing không có primitive riêng — `prod-a`/`prod-b` chỉ là label của Version Control. Khi chạy A/B bằng nhãn tường minh, ứng dụng không đi qua đường fetch mặc định (`production`); phải fetch từng nhãn một.
- Folders nằm trên trục `name`, độc lập với `version`/`label`: đường dẫn thư mục của một prompt không liên quan tới các version hay nhãn của nó.
- Việc gắn `langfuse_prompt` trong A/B Testing là cùng cơ chế liên kết prompt với trace của Prompt Management nói chung — chi tiết ở note Link to Traces, không giảng lại ở đây.
- Index nhóm feature: [./02-03-00-index.md](./02-03-00-index.md)