---
title: Prompt Management — Concepts
doc_source:
  - https://langfuse.com/docs/prompt-management/data-model
accessed: 2026-07-31
version: v4
status: draft
related:
  - ./features/prompt-config.md
  - ./features/variables.md
  - ./features/composability.md
  - ./features/message-placeholders.md
  - ./features/caching.md
  - ./features/prompt-version-control.md
---

# Prompt Management — Concepts

Các khái niệm nền của Prompt Management: cách Langfuse mô hình hóa một prompt và những cơ chế xoay quanh nó để đổi prompt mà không đổi code.

## Tổng quan

Đây không phải các tính năng rời — chúng là thuộc tính và cơ chế của cùng một đối tượng prompt, cùng phục vụ mục tiêu tách phần chỉ dẫn cho mô hình khỏi mã nguồn và nạp về lúc chạy. Prompt object là đơn vị được quản lý (chỉ dẫn + `config`); `type` cố định prompt là text hay chat; chèn nội dung động cho phép một prompt phục vụ nhiều lần gọi với đầu vào khác nhau; cặp version–label điều khiển version nào đang chạy ở đâu; caching quyết định độ trễ khi một thay đổi có hiệu lực.

## 1. Prompt object

**Khái niệm.** Prompt object là đơn vị được quản lý của Prompt Management, gói phần chỉ dẫn cho mô hình cùng phần cấu hình tùy chọn thành một thực thể có phiên bản. Phần chỉ dẫn là một chuỗi đơn hoặc một mảng message; phần `config` tùy chọn mang các tham số tác động lên hành vi. Ngoài nội dung, object còn có các thuộc tính quản lý `version`, variant và deployment — trang Concepts không định nghĩa variant làm gì.

**Vai trò.** Là đối tượng mà mọi cơ chế còn lại (`type`, chèn động, version–label, caching) đều thao tác lên; phải nắm trước khi đọc các mục sau.

**Ví dụ.** Một agent tra cứu số dư giữ prompt `balance-inquiry` trên Langfuse dưới dạng object. Code không chứa chuỗi prompt mà fetch object theo tên lúc khởi tạo, rồi render với dữ liệu của phiên trước khi gọi mô hình.

Chi tiết cấu hình: https://langfuse.com/docs/prompt-management/features/config

## 2. Text prompt và chat prompt

**Khái niệm.** `type` là kiểu định dạng của phần chỉ dẫn, cố định ngay khi tạo object và không đổi được về sau. `text` là một chuỗi đơn — hợp với ca đơn giản hoặc chỉ cần một system message. `chat` là một mảng message, mỗi message có role (`system`, `user`, `assistant`) — hợp khi cần quản lý trọn cấu trúc hội thoại, đưa vào các lượt trao đổi mẫu, hoặc xử lý chat history.

**Vai trò.** Chọn giữa quản lý một khối chỉ dẫn phẳng và quản lý một hội thoại nhiều lượt. Vì `type` không sửa được sau khi tạo, quyết định này chốt ngay ở bước tạo prompt.

**Ví dụ.** Agent khởi đầu bằng `text` cho một system prompt phân loại yêu cầu. Khi thêm few-shot và cần giữ lịch sử hội thoại của phiên, đội phát triển tạo một prompt mới `type: chat` thay vì cố nhồi cấu trúc nhiều lượt vào một chuỗi text.

## 3. Chèn nội dung động lúc runtime

**Khái niệm.** Cơ chế để phần chỉ dẫn tĩnh nhận nội dung thay đổi theo từng lần chạy, thay vì cố định trong prompt. Có ba loại, khác nhau ở đơn vị được chèn:

- **Variables** — chèn văn bản động vào message.
- **Prompt References** — chèn nguyên một prompt khác vào prompt hiện tại, tái dùng chỉ dẫn chung và tránh lặp.
- **Message Placeholders** — chèn cả một mảng message (ví dụ chat history).

**Vai trò.** Tách phần khung cố định khỏi phần dữ liệu theo phiên, để một prompt object phục vụ được nhiều lần gọi với đầu vào khác nhau mà không sửa prompt.

**Ví dụ.** Prompt `balance-inquiry` giữ khung chỉ dẫn cố định, dùng Variables để nhét tên khách và mã tài khoản mỗi lượt, và Message Placeholders để nạp lịch sử hội thoại của phiên vào đúng vị trí trước khi gọi mô hình.

Chi tiết cấu hình:
- Variables → https://langfuse.com/docs/prompt-management/features/variables
- Prompt References → https://langfuse.com/docs/prompt-management/features/composability
- Message Placeholders → https://langfuse.com/docs/prompt-management/features/message-placeholders

## 4. Version và label

**Khái niệm.** Hai cơ chế bổ trợ điều khiển "bản nào đang chạy." Version là lịch sử bất biến: mỗi lần cập nhật prompt sinh một version mới (1, 2, 3…), không ghi đè bản cũ. Label là con trỏ tới một version cụ thể; code trỏ tới label chứ không trỏ số version. Label thường gặp: `production` (mặc định cho app production), `latest` (luôn trỏ version mới nhất), và label tùy biến cho staging, testing, theo tenant, hoặc A/B test.

**Vai trò.** Đổi prompt đang chạy chỉ bằng việc gán lại label — không sửa, không deploy code; rollback là gán label về version cũ.

**Ví dụ.** Sửa `balance-inquiry` tạo ra version 5 (tự nhận label `latest`). Đội phát triển test version 5 trong playground, rồi chuyển label `production` từ version 4 sang 5; agent nạp version 5 ở lần fetch kế tiếp. Nếu version 5 hồi đáp sai, gán `production` về version 4 để rollback. Cả chu trình không đụng tới code vì code chỉ tham chiếu label.

Chi tiết cấu hình: https://langfuse.com/docs/prompt-management/features/prompt-version-control

## 5. Caching prompt

**Khái niệm.** Langfuse cache prompt đã nạp ở phía SDK, vì hai lý do: không thêm latency cho ứng dụng (không chờ mạng mỗi lần gọi) và loại rủi ro về tính sẵn sàng (Langfuse không phản hồi thì vẫn có bản cache để chạy). Cache có TTL; có thể tắt cache hoặc rút ngắn TTL khi cần cập nhật nhanh hơn.

**Vai trò.** Giữ đường nóng của ứng dụng không phụ thuộc vào từng lần gọi mạng tới Langfuse.

**Ví dụ.** Sau khi gán label `production` sang version 5, vài request đầu của agent vẫn dùng version 4 nằm trong cache cho tới khi TTL hết hạn. Đội vận hành cần bản vá có hiệu lực ngay thì rút TTL hoặc tắt cache cho prompt đó.

**!Note:** Lỗi im lặng — sau khi cập nhật prompt hoặc gán lại label, ứng dụng không báo gì và vẫn chạy, nhưng chạy bằng version cũ trong cửa sổ cache chưa hết hạn. "Đã đổi label" không đồng nghĩa "đã có hiệu lực tức thì"; luồng cần cập nhật gấp phải chủ động rút TTL hoặc tắt cache.

Chi tiết cấu hình: https://langfuse.com/docs/prompt-management/features/caching

## Tham chiếu chéo

Ràng buộc cắt ngang giữa mục 4 và mục 5: version–label chỉ đổi prompt "không đụng code" khi code trỏ tới label; nhưng do caching, việc gán lại label không có hiệu lực tức thì — phải tính TTL khi cần cập nhật gấp. Hai mục này đọc cùng nhau mới đủ để suy ra thời điểm một thay đổi thực sự áp vào production.

Mỗi mục trên có file feature riêng khai triển cấu hình chi tiết (xem `related` ở frontmatter); note này chỉ định nghĩa khái niệm và trỏ URL, không chép hướng dẫn cấu hình.