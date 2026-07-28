---
title: Frontend — tổng quan
doc_source: https://docs.langchain.com/oss/python/langchain/frontend/overview
accessed: 2026-07-25
lc_version: unknown
status: draft
lab:
related:
  - ./07-02-frontend-patterns.md
  - ./07-03-frontend-integrations.md
---

# Frontend — tổng quan

> Mảng "Frontend" trong tài liệu LangChain nói về cách dựng giao diện web cho một agent: agent chạy ở backend, giao diện nhận trạng thái agent theo thời gian thực và vẽ ra màn hình. Đây là trang gốc; hai nhánh con là [Patterns](./07-02-frontend-patterns.md) và [Integrations](./07-03-frontend-integrations.md).

---

## 1. Frontend ở đây là gì

Không phải một thư viện giao diện. Đây là bộ hướng dẫn nối một **agent** (dựng bằng `create_agent` / `createAgent`) với một giao diện web bất kỳ, để giao diện hiển thị được mọi thứ agent đang làm khi nó đang làm: chữ chảy dần, tool đang gọi, chỗ dừng chờ người duyệt, lịch sử hội thoại.

Điểm khác so với một API chat thông thường: không phải "gửi câu hỏi — đợi — nhận cả câu trả lời". Ở đây giao diện đăng ký vào một luồng và trạng thái được **gửi dần** về, cập nhật liên tục, nên người dùng thấy phản hồi hình thành theo thời gian thực thay vì màn hình đứng im chờ.

---

## 2. Kiến trúc — hai mảnh ghép

Mọi pattern trong mảng này đều đứng trên đúng một kiến trúc, gồm hai phần:

**Phần backend — agent dựng bằng `create_agent`.** Khi dựng xong, `create_agent` sinh ra một đồ thị LangGraph đã compile (đã dựng). Đồ thị này tự phơi ra một API dạng streaming (gửi dần). Đây là nơi chứa toàn bộ logic: gọi model, gọi tool, dừng chờ duyệt, lưu checkpoint.

**Phần frontend — hook `useStream`.** Hook (một hàm tiện ích gắn vào vòng đời component của framework giao diện) đứng ở phía trình duyệt, kết nối tới API mà backend phơi ra. Nó biến luồng dữ liệu thô thành **trạng thái phản ứng** (reactive state — dữ liệu tự cập nhật khiến giao diện tự vẽ lại): danh sách tin nhắn, danh sách tool đang gọi, tín hiệu dừng chờ duyệt, lịch sử, và hơn nữa.

Ranh giới quan trọng: backend giữ logic, frontend chỉ nhận trạng thái rồi vẽ. `useStream` không quan tâm bạn vẽ bằng gì.

**`useStream` có bản cho bốn framework:** React, Vue, Svelte, Angular. Cùng một khái niệm, mỗi framework một gói riêng (`@langchain/react`, `@langchain/vue`, `@langchain/svelte`, `@langchain/angular`).

---

## 3. Các trạng thái mà `useStream` cung cấp

Đây là danh sách trạng thái mà tài liệu gốc liệt kê ở phần kiến trúc. Mỗi pattern con thực chất chỉ là "lấy một trong các trạng thái này ra rồi vẽ theo một cách riêng":

| Trạng thái | Chứa gì | Pattern dùng nó |
|---|---|---|
| messages | Danh sách tin nhắn (người dùng + AI), chữ cập nhật khi chảy về | Markdown messages, hầu hết các pattern |
| tool calls | Các lần agent gọi tool, kèm trạng thái đang chạy / xong / lỗi | Tool calling |
| interrupts (tín hiệu dừng) | Điểm agent dừng lại chờ người quyết định | Human-in-the-Loop |
| history (lịch sử) | Các checkpoint (nơi lưu trạng thái) dọc theo hội thoại | Time travel, Branching chat |

---

## 4. Ba nhóm nội dung con

Trang gốc chia mảng Frontend thành hai nhánh lớn. Đây chỉ là bản đồ; nội dung chi tiết ở hai file kia.

**Patterns — các mẫu dựng sẵn cho từng nhu cầu giao diện.** Tài liệu gom 11 pattern thành bốn nhóm: hiển thị tin nhắn và kết quả, hiển thị hành động của agent, quản lý hội thoại, và streaming nâng cao. Xem [07-02 Frontend patterns](./07-02-frontend-patterns.md).

**Integrations — nối `useStream` vào các thư viện giao diện có sẵn.** `useStream` không phụ thuộc thư viện vẽ nào, nên có thể cắm vào các bộ component AI chat hoặc framework generative UI của bên thứ ba. Xem [07-03 Frontend integrations](./07-03-frontend-integrations.md).

---

## Tham chiếu chéo

- [07-02 Frontend patterns](./07-02-frontend-patterns.md) — 11 mẫu dựng giao diện, mỗi mẫu lấy một trạng thái từ `useStream`
- [07-03 Frontend integrations](./07-03-frontend-integrations.md) — bốn thư viện bên thứ ba cắm vào `useStream`
- Trang gốc: `https://docs.langchain.com/oss/python/langchain/frontend/overview`