---
title: Frontend integrations
doc_source: https://docs.langchain.com/oss/python/langchain/frontend/integrations/
accessed: 2026-07-25
lc_version: unknown
status: draft
lab:
related:
  - ./07-01-frontend-overview.md
  - ./07-02-frontend-patterns.md
---

# Frontend integrations

> Bốn thư viện giao diện bên thứ ba cắm được vào agent LangChain. File này trình bày định nghĩa và đặc điểm từng thư viện ở mức lý thuyết; hướng dẫn cắm và code chi tiết nằm ở trang riêng của từng thư viện.

---

## 1. Vì sao có mảng này

`useStream` không phụ thuộc thư viện vẽ nào (UI-agnostic). Nó chỉ trả về **trạng thái phản ứng** thuần: tin nhắn, tool call, cờ đang tải, giá trị, thông tin thread. Bạn nối trạng thái đó vào lớp hiển thị nào tùy ý.

Vì thế thay vì tự vẽ mọi component chat từ đầu, có thể dùng lại các thư viện giao diện AI có sẵn. Bốn thư viện dưới đây mỗi cái theo một triết lý khác nhau, hợp với một kiểu giao diện khác nhau.

Ba trong bốn (AI Elements, assistant-ui, OpenUI) nối **trực tiếp** vào `useStream`. Riêng CopilotKit cần thêm một điểm cuối (endpoint) riêng đặt cạnh phần triển khai LangGraph.

---

## 2. CopilotKit

**Khái niệm.** Một runtime chat AI đầy đủ, có hỗ trợ generative UI theo cấu trúc. Thêm một điểm cuối CopilotKit riêng vào phần triển khai LangGraph, rồi vẽ các cây component động trong React.

**Vai trò.** Hợp khi muốn một lớp runtime dày dặn quản lý luồng chat, cộng với khả năng agent trả về payload có cấu trúc để dựng UI động — không chỉ là một khung chat mỏng.

**Đặc điểm.**
- Kiểu giao diện: khung chat sẵn của CopilotKit + bộ vẽ tin nhắn tùy chỉnh.
- Tùy biến qua: điểm cuối backend riêng, ngữ cảnh agent, và các bộ vẽ.
- Streaming: luồng chat do runtime quản, kèm payload trợ lý có cấu trúc.
- Tool call: đi qua runtime của CopilotKit và bộ vẽ tùy chỉnh.
- Định dạng agent: phản hồi trợ lý có cấu trúc, kèm Markdown tùy chọn.
- Điểm khác biệt: là thư viện duy nhất trong bốn cái cần điểm cuối riêng thay vì nối thẳng `useStream`.

---

## 3. AI Elements

**Khái niệm.** Bộ component AI chat dựng theo shadcn/ui, ghép được. Thả vào các component như `Conversation`, `Message`, `Tool`, `Reasoning` rồi nối thẳng chúng với `stream.messages`.

**Vai trò.** Hợp khi muốn dựng chat có các kiểu tin nhắn phong phú mà vẫn kiểm soát trực tiếp từng mảnh giao diện.

**Đặc điểm.**
- Kiểu giao diện: các component shadcn/ui ghép lại.
- Tùy biến qua: sửa thẳng file mã nguồn của component.
- Streaming: vẽ dần ở cấp component.
- Tool call: có sẵn bộ component `Tool` / `ToolHeader` / `ToolOutput`.
- Định dạng agent: nhận bất kỳ `stream.messages` nào.

---

## 4. assistant-ui

**Khái niệm.** Một framework React kiểu **headless** (không kèm giao diện cứng, chỉ cung cấp phần logic để bạn tự lắp giao diện) có sẵn lớp runtime đầy đủ. Bắc cầu `useStream` sang `AssistantRuntimeProvider` qua bộ chuyển `useExternalStoreRuntime`.

**Vai trò.** Hợp khi muốn một chat đầy đủ tính năng nhưng lắp đặt tối thiểu — quản lý thread, rẽ nhánh, đính kèm tệp đều có sẵn.

**Đặc điểm.**
- Kiểu giao diện: các "slot" headless + giao diện mặc định.
- Tùy biến qua: ghi đè từng slot component.
- Streaming: quản lý thread có sẵn trong runtime.
- Tool call: tùy chỉnh qua các slot tin nhắn.
- Định dạng agent: nhận bất kỳ `stream.messages` nào.
- Có sẵn: quản lý thread, rẽ nhánh, và hỗ trợ tệp đính kèm.

---

## 5. OpenUI

**Khái niệm.** Một thư viện generative UI cho phép agent sinh ra **cả bảng điều khiển tương tác hoàn chỉnh** bằng một ngôn ngữ mô tả component khai báo (DSL tên `openui-lang`). Sinh ra chuyên cho các giao diện nhiều dữ liệu, kiểu báo cáo.

**Vai trò.** Hợp khi cần bảng điều khiển và báo cáo do agent tạo ra — không phải chat, mà là giao diện dữ liệu dày đặc.

**Đặc điểm.**
- Kiểu giao diện: thư viện component dựng sẵn + DSL khai báo.
- Tùy biến qua: đổi giao diện bằng biến CSS.
- Streaming: kiểu "hoisting" — khung hiện ngay lập tức, dữ liệu điền vào sau.
- Tool call: nằm ngay trong giao diện được sinh ra.
- Định dạng agent: agent xuất ra chữ theo `openui-lang`.

---

## 6. Chọn thư viện nào

Bảng dưới lấy trực tiếp từ trang gốc; cột "hợp nhất khi" là tiêu chí quyết định.

| | CopilotKit | AI Elements | assistant-ui | OpenUI |
|---|---|---|---|---|
| Hợp nhất khi | Cần runtime chat đầy đủ + generative UI có cấu trúc | Chat với kiểu tin nhắn phong phú | Chat đầy đủ tính năng, lắp đặt tối thiểu | Bảng điều khiển và báo cáo do agent sinh |
| Nối vào `useStream` | Không thẳng — cần điểm cuối riêng | Thẳng | Thẳng (qua bộ chuyển) | Thẳng |

Cả bốn đều chạy tốt với agent LangChain. Ba cái sau nối thẳng `useStream`; CopilotKit đáng dùng khi muốn lớp runtime dày hơn và một điểm cuối riêng đặt cạnh phần triển khai LangGraph.

---

## Tham chiếu chéo

- [07-01 Frontend — tổng quan](./07-01-frontend-overview.md) — vì sao `useStream` không phụ thuộc thư viện vẽ
- [07-02 Frontend patterns](./07-02-frontend-patterns.md) — các mẫu giao diện dựng bằng chính `useStream`
- Các trang chi tiết: `https://docs.langchain.com/oss/python/langchain/frontend/integrations/<tên>` (`copilotkit`, `ai-elements`, `assistant-ui`, `openui`)