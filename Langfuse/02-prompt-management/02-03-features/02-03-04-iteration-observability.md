---
title: Prompt Management — Features — Iteration & Observability
doc_source:
  - https://langfuse.com/docs/prompt-management/features/playground
  - https://langfuse.com/docs/prompt-management/features/link-to-traces
accessed: 2026-08-03
version: v4
status: draft
related:
  - ./02-03-00-index.md
  - ./02-03-02-versioning-deployment.md
---

# Iteration & Observability

Hai tính năng khép vòng lặp cải tiến prompt: thử trước khi prompt chạy thật, và quan sát sau khi nó đã chạy.

## Tổng quan

Cả hai nối việc sửa prompt với dữ liệu thật, nhưng ở hai đầu khác nhau của vòng lặp. Playground cho thử nhanh một prompt ngay trong UI — chỉnh model config, biến số rồi xem model phản hồi thế nào, trước khi prompt đó vào ứng dụng. Link to Traces đi ngược lại: sau khi prompt đã chạy thật, nó gắn trace/generation về đúng phiên bản prompt đã tạo ra chúng, để biết phiên bản nào đang hoạt động tốt ngoài production.

## 1. Playground

**Khái niệm.** Playground là công cụ trong Langfuse để sửa prompt và tham số model rồi xem phản hồi của model ngay trong giao diện, không cần rời sang tool khác hay viết code. Nó có chế độ side-by-side comparison — chạy nhiều biến thể prompt cạnh nhau, hoặc chạy tất cả cùng lúc; mỗi biến thể giữ riêng model config, biến số (prompt variables), tool definition, và placeholder, nên đổi một thứ là thấy tác động ngay. Playground hỗ trợ tool calling — định nghĩa tool bằng JSON schema tùy chỉnh và mock tool response — cùng structured output ép định dạng theo JSON schema; cả hai loại schema này lưu được vào project. Model dùng trong Playground cần khóa API được thêm ở project settings.

**Vai trò.** Thử nhanh một thay đổi prompt hoặc so sánh nhiều biến thể trước khi quyết định phiên bản nào đưa vào dùng.

**Ví dụ.** Từ trang chi tiết một generation trong Observability, bấm `Open in Playground` để mở lại đúng input đã chạy, sửa prompt rồi chạy lại xem model phản hồi khác đi thế nào — không cần sửa code và deploy lại ứng dụng.

Chi tiết cấu hình: https://langfuse.com/docs/prompt-management/features/playground

## 2. Link to Traces

**Khái niệm.** Link to Traces là cơ chế gắn một trace/generation với đúng phiên bản prompt Langfuse đã tạo ra nó. Sau khi gắn, trang chi tiết generation làm nổi bật prompt đã dùng, và Langfuse tự gộp metric theo từng phiên bản prompt ở tab Metrics: độ trễ generation trung vị, số token input trung vị, số token output trung vị, chi phí trung vị, số lần generation, giá trị score trung vị, và timestamp lần generation đầu–cuối. Cách gắn khác nhau theo SDK: Python truyền qua tham số `prompt` của generation; JS/TS dùng `updateActiveObservation({ prompt })` (hoặc `generation.update({ prompt })`); OpenAI SDK dùng `langfuse_prompt` (Python) / `langfusePrompt` (JS/TS); Langchain thêm `metadata={"langfuse_prompt": prompt}` vào `PromptTemplate`; Vercel AI SDK đặt `langfusePrompt` trong field `metadata`. Khi nhiều generation trong cùng ngữ cảnh dùng chung một phiên bản prompt, hoặc khi thư viện instrumentation không expose tham số `prompt` (ví dụ LiteLLM qua OpenTelemetry), dùng `propagate_attributes(prompt=prompt)` để gắn cho tất cả — có từ Python SDK 4.14.0.

**Vai trò.** Theo dõi hiệu suất và đánh giá theo từng phiên bản prompt, dựng lịch sử cải tiến, so sánh phiên bản này với phiên bản khác dựa trên số liệu thật thay vì đoán.

**Ví dụ.** Một ứng dụng đổi từ prompt version 3 sang version 4; nhờ Link to Traces, hai version tách riêng ở tab Metrics — so được ngay chi phí và độ trễ trung vị của version 4 có cải thiện so với version 3 hay không.

> **!Note:** Khi generation dùng fallback prompt (xem Runtime Reliability), Langfuse không tạo link tới phiên bản nào. Trong lúc API sự cố, các lượt chạy bằng fallback biến mất khỏi metrics theo version — số liệu so sánh bị lệch mà không có cảnh báo.

Chi tiết cấu hình: https://langfuse.com/docs/prompt-management/features/link-to-traces

## Tham chiếu chéo

- Playground dùng để thử một phiên bản prompt trước khi deploy; xem [./02-03-02-versioning-deployment.md](./02-03-02-versioning-deployment.md) (Version Control) cho việc phiên bản đó được lưu và quản lý ra sao sau khi chốt.
- Link to Traces đóng vòng lặp ở đầu quan sát: sau khi phiên bản đã deploy và chạy thật, nó là cách duy nhất trong nhóm feature này để biết phiên bản đó đang hoạt động tốt hay xấu ngoài production. Ràng buộc cắt ngang: generation chạy bằng fallback prompt không được gắn link (xem Runtime Reliability), nên metrics theo version không phản ánh giai đoạn dùng fallback.
- Prompt Experiments chạy một prompt qua cả một dataset để đánh giá hàng loạt, khác Playground là thử từng lần một. Nội dung thuộc nhánh Evaluation — xem [../../03-evaluation/03-05-experiments.md](../../03-evaluation/03-05-experiments.md).
- Index nhóm feature: [./02-03-00-index.md](./02-03-00-index.md) — *(chưa có trên đĩa tại thời điểm viết note này)*.