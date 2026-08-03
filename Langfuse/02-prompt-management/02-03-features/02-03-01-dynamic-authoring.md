---
title: Prompt Management — Features — Dynamic Authoring
doc_source:
  - https://langfuse.com/docs/prompt-management/features/variables
  - https://langfuse.com/docs/prompt-management/features/message-placeholders
  - https://langfuse.com/docs/prompt-management/features/composability
  - https://langfuse.com/docs/prompt-management/features/config
accessed: 2026-08-03
version: v4
status: draft
related:
  - ./02-03-00-index.md
---

# Dynamic Authoring

Nhóm bốn tính năng cho phép nội dung, cấu trúc message, hay tham số đi kèm của một prompt object thay đổi tại thời điểm gọi, thay vì cố định lúc tạo.

## Tổng quan

Điểm chung khiến bốn tính năng này được gom lại: mỗi cái tham số hóa một phần khác nhau của prompt object — Variables thay chuỗi bên trong một message, Message Placeholders thay nguyên một mảng message, Composability cho một prompt tham chiếu prompt khác, Config đính kèm tham số nằm ngoài nội dung prompt. Cơ chế giải quyết không đồng nhất: Variables và Message Placeholders resolve qua `.compile()`; Composability resolve ở tầng tag theo version hoặc label; Config đọc trực tiếp từ prompt đã fetch, không qua compile.

## 1. Variables

**Khái niệm.** Variables là chỗ giữ chỗ cho chuỗi động trong prompt. Khai báo bằng cú pháp `{{variable_name}}`, dùng được cả trong text prompt lẫn trong nội dung bất kỳ message nào của chat prompt. Lúc gọi, truyền giá trị thay thế qua `.compile()` — keyword argument ở Python, một object ở JavaScript/TypeScript — phương thức này thay toàn bộ `{{...}}` bằng giá trị thực tế và trả về prompt đã dựng sẵn để gửi cho model.

**Vai trò.** Viết một prompt template dùng lại được cho nhiều lời gọi khác nhau, đổi input không phải sửa định nghĩa prompt gốc mỗi lần.

**Ví dụ.** Prompt `movie-critic` chứa `{{criticLevel}}` và `{{movie}}`; gọi `prompt.compile(criticLevel="expert", movie="Dune 2")` dựng ra `"As an expert movie critic, do you like Dune 2?"`.

Chi tiết cấu hình: https://langfuse.com/docs/prompt-management/features/variables

## 2. Message Placeholders

**Khái niệm.** Message Placeholders là chỗ chèn nguyên một danh sách message định dạng `[{role, content}]` vào một vị trí xác định trong chat prompt — khác Variables ở chỗ chèn cả một mảng message thay vì một chuỗi. Prompt khai báo placeholder bằng phần tử `{"type": "placeholder", "name": "..."}` xen giữa các message thường. Lúc runtime, `.compile(variables, placeholders)` trên `ChatPromptClient` nhận hai phần tách biệt: biến văn bản như Variables, và một dict/object ánh xạ tên placeholder sang mảng message cần chèn. Một prompt khai được nhiều placeholder. Yêu cầu SDK tối thiểu: Python `langfuse >= 3.1.0`, JS/TS `langfuse >= 3.38.0`. Hoạt động cả trong Playground và Prompt Experiments.

**Vai trò.** Dựng chat prompt có phần nội dung là cả một đoạn hội thoại thay đổi theo lượt gọi, điển hình nhất là lịch sử chat.

**Ví dụ.** Prompt `movie-critic-chat` có message `system` chứa `{{criticlevel}}`, tiếp theo là placeholder tên `chat_history`, rồi một message `user` cố định; gọi `prompt.compile(criticlevel="expert", chat_history=[...])` chèn các lượt hội thoại trước đó vào đúng vị trí placeholder.

Chi tiết cấu hình: https://langfuse.com/docs/prompt-management/features/message-placeholders

## 3. Prompt Composability

**Khái niệm.** Prompt Composability cho một prompt tham chiếu tới prompt khác bằng một tag đặc biệt, thay vì chép lặp nội dung. Có hai dạng tham chiếu: cố định theo version — `@@@langfusePrompt:name=PromptName|version=1@@@` — hoặc theo label để giải quyết động — `@@@langfusePrompt:name=PromptName|label=production@@@`. Tag chèn được qua nút `Add prompt reference` trên UI, hoặc gõ tay khi tạo prompt qua SDK/API. Tính năng chỉ áp dụng cho **text prompt**. Docs không nêu giới hạn độ sâu lồng (một prompt tham chiếu prompt khác lại tham chiếu tiếp), cũng không mô tả thời điểm và cách resolve khi trong cùng prompt có cả tham chiếu lẫn variable — cần kiểm chứng bằng lab hoặc đọc source.

**Vai trò.** Giữ các đoạn nội dung dùng chung (hướng dẫn, ví dụ, ngữ cảnh) ở một nơi; sửa prompt gốc thì mọi prompt tham chiếu tới nó cập nhật theo, không phải sửa từng cái.

**Ví dụ.** Tách một hướng dẫn an toàn chung thành prompt `safety-guidelines`; các prompt tác vụ khác nhau chèn `@@@langfusePrompt:name=safety-guidelines|label=production@@@` vào đầu nội dung để cùng dùng chung, sửa một chỗ áp dụng cho tất cả.

Chi tiết cấu hình: https://langfuse.com/docs/prompt-management/features/composability

## 4. Config

**Khái niệm.** Config là một JSON object tùy chọn, tùy ý, đính kèm mỗi prompt object — không phải nội dung text/message mà là chỗ lưu dữ liệu có cấu trúc cho lời gọi LLM. Thường chứa tham số model (`model`, `temperature`, `max_tokens`), schema đầu ra (`response_format`), hoặc định nghĩa tool (`tools`, `tool_choice`), nhưng cấu trúc bên trong hoàn toàn tự do. Config được version cùng với prompt — mỗi version của prompt mang một config riêng. Đọc lại qua thuộc tính `config` trên prompt đã fetch, ví dụ Python: `cfg = prompt.config; model = cfg.get("model")`. Đặt config được qua UI hoặc qua SDK Python/JS-TS lúc tạo prompt. Config không đi qua `.compile()`.

**Vai trò.** Gom tham số vận hành của một lời gọi LLM vào cùng chỗ với nội dung prompt, để đổi model hay tham số không cần sửa code ứng dụng, chỉ cần tạo version prompt mới.

**Ví dụ.** Prompt `invoice-extractor` mang config `{"model": "gpt-4o", "temperature": 0}`; ứng dụng đọc `prompt.config.get("model")` để biết dùng model nào cho lần gọi này, không hardcode trong code.

Chi tiết cấu hình: https://langfuse.com/docs/prompt-management/features/config

## Tham chiếu chéo

- Variables và Message Placeholders cùng qua `.compile()` nhưng thay hai thứ khác nhau: Variables thay chuỗi trong một message, Placeholders thay nguyên một mảng message. Một chat prompt dùng cả hai cùng lúc — `.compile(variables, placeholders)` nhận cả hai tham số tách biệt.
- Composability không đi qua `.compile()`: tham chiếu giải quyết theo version/label ngay ở tag, docs không mô tả bước compile cho nó. Nếu prompt được tham chiếu vào có chứa `{{variable}}` riêng thì variable đó resolve ra sao khi kết hợp — docs không nói rõ, cần kiểm chứng (suy luận).
- Config độc lập với ba tính năng còn lại — đọc trực tiếp từ prompt object, không phụ thuộc việc prompt có dùng Variables, Placeholders, hay Composability hay không.
- Index nhóm feature: [./02-03-00-index.md](./02-03-00-index.md)