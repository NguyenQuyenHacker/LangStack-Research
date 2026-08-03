---
title: Prompt Management — Overview & Get Started
doc_source:
  - https://langfuse.com/docs/prompt-management/overview
  - https://langfuse.com/docs/prompt-management/get-started
accessed: 2026-07-31
version: v4
status: draft
related:
  - ./01-05-xx-prompt-data-model.md
---

# Prompt Management — Overview & Get Started

Cách Langfuse lưu, gắn phiên bản và cấp phát prompt tập trung, tách prompt ra khỏi code ứng dụng.

## Tổng quan

Prompt management là cách quản lý prompt có hệ thống — lưu, gắn phiên bản, lấy ra dùng lúc chạy — thay vì hardcode trong code. Prompt nằm ở Langfuse, code chỉ tham chiếu tới.

Hai điểm cốt lõi:

- **Tách cập nhật prompt khỏi deploy code.** Người chỉnh prompt (PM, chuyên gia nghiệp vụ) và người deploy (kỹ sư) thường là hai nhóm. Prompt nằm trong code thì sửa một dòng chữ cũng phải qua kỹ sư, review, deploy. Prompt nằm ở Langfuse thì sửa thẳng trên UI, ứng dụng tự lấy bản mới — có hiệu lực ngay, không cần deploy.
- **Không thêm độ trễ.** SDK cache prompt phía client, lấy prompt nhanh như đọc từ bộ nhớ; Langfuse gặp sự cố cũng không kéo theo rủi ro sẵn sàng của ứng dụng.

## Bắt đầu

Ba bước đưa một prompt vào dùng.

### 1. Lấy API key

Tạo tài khoản Langfuse Cloud hoặc tự host, rồi tạo cặp key (public + secret) trong settings của project.

Chi tiết: https://langfuse.com/docs/prompt-management/get-started#manual-installation

### 2. Tạo prompt

Tạo qua UI, SDK (Python, JS/TS), API, hoặc migrate từ code có sẵn. Prompt thuộc loại text hoặc chat, chọn xong không đổi được. Trùng `name` với prompt cũ thì ghi thành version mới chứ không đè. Gắn label (ví dụ `production`) để đánh dấu bản dùng thật.

Chi tiết: https://langfuse.com/docs/prompt-management/get-started#create-update-prompt-diy

### 3. Dùng prompt trong code

Lúc chạy, code fetch prompt theo label `production` (khuyến nghị) để lấy đúng bản đã duyệt. Có tích hợp sẵn cho nhiều stack (SDK trực tiếp, OpenAI SDK, Langchain, Vercel AI SDK). Prompt về ở dạng template, gọi `compile()` chèn biến: text trả một chuỗi, chat trả một mảng message.

Chi tiết: https://langfuse.com/docs/prompt-management/get-started#use-prompt-diy

**!Note:** Sửa prompt xong nhưng ứng dụng vẫn chạy bản cũ thường do cache phía client của SDK, không phải lỗi ghi. Bản mới chỉ xuất hiện sau khi cache hết hạn.

## Tham chiếu chéo

- Loại prompt (text vs chat), cơ chế version/label, và caching có note riêng — bước 2 và bước 3 chỉ nêu tên, chi tiết nằm ở file data-model và các note feature.