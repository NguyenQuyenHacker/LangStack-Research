---
title: Platform — API & Data Platform
doc_source:
- https://langfuse.com/docs/api-and-data-platform/overview
- https://langfuse.com/docs/api-and-data-platform/features/agent-skill
- https://langfuse.com/docs/api-and-data-platform/features/cli
- https://langfuse.com/docs/api-and-data-platform/features/mcp-server
- https://langfuse.com/docs/api-and-data-platform/features/export-from-ui
- https://langfuse.com/docs/api-and-data-platform/features/export-to-blob-storage
- https://langfuse.com/docs/api-and-data-platform/features/observations-api
- https://langfuse.com/docs/api-and-data-platform/features/public-api
- https://langfuse.com/docs/api-and-data-platform/features/query-via-sdk
- https://langfuse.com/docs/api-and-data-platform/features/scores-api
accessed: 2026-07-31
version: v4
status: draft
---

# Platform — API & Data Platform

## Tổng quan

**Định nghĩa.** API & Data Platform là nhóm công cụ cho phép đưa dữ liệu trong Langfuse ra ngoài và thao tác với Langfuse bằng chương trình, thay vì chỉ dùng giao diện. Toàn bộ dữ liệu (trace, observation, score, prompt, dataset...) và tính năng đều truy cập được qua đây.

*Giải thích nhanh vài từ dùng xuyên suốt:*
- *API*: cổng để phần mềm khác gọi vào Langfuse lấy/ghi dữ liệu bằng code.
- *SDK*: thư viện viết sẵn (Python, JS/TS) bọc API, để gọi cho tiện thay vì tự viết yêu cầu HTTP.
- *trace / observation / score*: bản ghi một lượt xử lý / một bước con trong lượt đó / điểm chất lượng gắn vào.

**Mục đích thường gặp.** Tính phí theo chi phí LLM đã ghi nhận; đưa kết quả đánh giá lên dashboard bên ngoài; xuất dữ liệu thô để tinh chỉnh (fine-tune) model; ghép dữ liệu Langfuse với hành vi người dùng trong kho dữ liệu (data warehouse).

**Ba lối truy cập chính.** Cho AI/agent thao tác (Agent Skill, CLI, MCP — mục 1–3); xuất dữ liệu ra ngoài (từ giao diện hoặc tự động lên blob storage — mục 4–5); lấy dữ liệu bằng code (Public API và các API con Observations/Scores, hoặc qua SDK — mục 6–9).

Nếu muốn tìm hiểu thêm hãy tham khảo thông qua https://langfuse.com/docs/api-and-data-platform/overview

## 1. Agent Skill

**Định nghĩa.** Agent Skill là một "gói kỹ năng" cài vào công cụ lập trình AI (Claude Code, Cursor, Windsurf...) để agent biết cách dùng Langfuse đúng chuẩn — gồm một file hướng dẫn chính (`SKILL.md`) và các tài liệu tham chiếu cho từng luồng công việc.

**Mục tiêu.** Giúp agent cho kết quả tốt hơn vì được "nạp" sẵn thực hành chuẩn của Langfuse, thay vì tự đoán.

**Cách hoạt động.** Dùng cơ chế *progressive disclosure*: chỉ nạp phần mô tả ngắn vào ngữ cảnh của agent để nó biết khi nào cần dùng; hướng dẫn đầy đủ chỉ nạp khi thực sự cần — giữ ngữ cảnh gọn. Cài bằng cách nhờ chính agent cài từ kho GitHub, qua plugin Cursor, hoặc cài tay.

> !Note: Nếu môi trường cho phép cài công cụ dòng lệnh và chạy lệnh bash, Langfuse khuyến nghị dùng Agent Skill thay cho MCP Server (mục 3).

Nếu muốn tìm hiểu thêm hãy tham khảo thông qua https://langfuse.com/docs/api-and-data-platform/features/agent-skill

## 2. CLI

**Định nghĩa.** CLI (giao diện dòng lệnh) là công cụ bọc toàn bộ Langfuse API để thao tác trực tiếp từ cửa sổ dòng lệnh (terminal).

**Mục tiêu.** Dành cho agent lập trình và người dùng thạo dòng lệnh: để agent tự quản lý Langfuse ngay trong trình soạn thảo; viết script tự động hóa việc lặp lại (xuất trace, chấm điểm hàng loạt, đồng bộ prompt); và tra cứu nhanh hơn mở giao diện.

**Điểm chính.** Bọc động toàn bộ đặc tả API nên mọi endpoint (trace, prompt, dataset, score, session, metric...) đều thành lệnh dùng được. Xác thực bằng cùng cặp khóa API của dự án (public key + secret key) qua biến môi trường, không cần bước đăng nhập riêng; mỗi cặp khóa gắn với một dự án.

Nếu muốn tìm hiểu thêm hãy tham khảo thông qua https://langfuse.com/docs/api-and-data-platform/features/cli

## 3. MCP Server

**Định nghĩa.** MCP Server là máy chủ theo chuẩn Model Context Protocol, cho phép trợ lý/agent AI thao tác với dữ liệu Langfuse bằng chương trình. Đây là máy chủ MCP có xác thực, gắn với dữ liệu dự án (khác với máy chủ MCP công khai chỉ phục vụ tài liệu).

**Mục tiêu.** Kết nối các client AI (Claude Code, Cursor...) tới Langfuse để chúng liệt kê prompt, kéo trace, tạo dataset... qua các "tool" chuẩn hóa.

**Điểm chính.** Kiến trúc phi trạng thái (stateless): mỗi khóa API gắn một dự án; xác thực bằng Basic Auth mã hóa base64. Mặc định có sẵn cả tool đọc lẫn ghi; nếu chỉ muốn đọc, cấu hình danh sách cho phép (allowlist) để chặn thao tác ghi.

Nếu muốn tìm hiểu thêm hãy tham khảo thông qua https://langfuse.com/docs/api-and-data-platform/features/mcp-server

## 4. Export from UI

**Định nghĩa.** Xuất dữ liệu quan sát trực tiếp từ giao diện Langfuse thành file để phân tích, tinh chỉnh model, huấn luyện, hoặc ghép với công cụ ngoài.

**Điểm chính.** Hầu hết các bảng đều xuất theo lô được; mọi bộ lọc đang áp trên bảng cũng áp vào bản xuất. Cấu hình ẩn/hiện cột trên giao diện không ảnh hưởng — file luôn xuất đủ mọi cột. Định dạng: CSV hoặc JSON.

Ngoài cách này, còn xuất được qua blob storage (mục 5), qua SDK/API (mục 6–9), hoặc Metrics API cho số liệu tổng hợp.

Nếu muốn tìm hiểu thêm hãy tham khảo thông qua https://langfuse.com/docs/api-and-data-platform/features/export-from-ui

## 5. Export to Blob Storage

**Định nghĩa.** Thiết lập lịch tự động xuất dữ liệu (trace, observation, observation làm giàu, score) lên kho lưu trữ đám mây dạng blob — S3, Google Cloud Storage, hoặc Azure Blob Storage.

> !Note: Tính năng này không có ở gói Hobby/Core; gói Pro cần add-on Teams, còn Enterprise và bản tự vận hành thì có.

**Mục tiêu.** Đồng bộ dữ liệu đều đặn sang kho ngoài để phân tích, sao lưu, hoặc nạp vào data warehouse mà không phải kéo tay qua API.

**Cấu hình chính.**

| Hạng mục | Nội dung |
|---|---|
| Lịch chạy | Mỗi 20 phút, hoặc theo giờ/ngày/tuần. |
| Định dạng file | Parquet (mặc định, dạng nén cột cho data warehouse), hoặc CSV/JSON/JSONL (có thể nén gzip). |
| Nguồn xuất | Nên dùng `Enriched observations` (gắn sẵn thuộc tính trace vào observation, nhanh hơn); các nguồn `legacy` đang bị loại dần. |
| Chọn nhóm cột | Bật/tắt từng nhóm cột trong bản xuất observation; nhóm `core` bắt buộc, luôn có. |
| Chế độ xuất (Export mode) | Toàn bộ lịch sử / từ lúc bật / từ một ngày tự chọn. |

**Vận hành.** Mỗi lần chạy xuất một khoảng thời gian rồi tiến tới khoảng kế tiếp; có độ trễ ngắn để tránh xuất bản ghi còn đang ghi dở. Sau mỗi lần chạy thành công, hệ thống ghi một file *manifest* liệt kê mọi file đã tạo — manifest xuất hiện nghĩa là mọi file trong đó đã sẵn sàng.

> !Note: File rỗng là bình thường (một khoảng thời gian có thể có dữ liệu bảng này nhưng không có bảng kia), không phải lỗi. Pipeline hạ nguồn nên đọc theo thư mục và chấp nhận file rỗng, đừng dựa vào việc file luôn tồn tại.

Nếu muốn tìm hiểu thêm hãy tham khảo thông qua https://langfuse.com/docs/api-and-data-platform/features/export-to-blob-storage

## 6. Observations API

**Định nghĩa.** API lấy dữ liệu observation ở mức từng dòng (span, generation, event) để phục vụ luồng tùy chỉnh, pipeline đánh giá, và phân tích. Muốn số liệu tổng hợp thì dùng Metrics API thay vì tự kéo dữ liệu thô về gộp.

> !Note: Bản v2 chỉ có trên Langfuse Cloud; bản tự vận hành đang chờ lộ trình chuyển đổi.

**Cải tiến chính của v2 (nhanh và nhẹ hơn v1).**

| Cải tiến | Nội dung |
|---|---|
| Chọn nhóm trường (field groups) | Chỉ lấy nhóm cột cần (`core,basic,usage`...) thay vì kéo cả dòng; trường không xin sẽ vắng khỏi kết quả. |
| Phân trang bằng con trỏ (cursor) | Thay vì số trang, mỗi lần trả về một *cursor* để lần sau đọc tiếp từ đúng chỗ — ổn định hơn khi dữ liệu lớn. |
| Xử lý input/output nhẹ | Mặc định trả input/output dạng chuỗi; chỉ phân tích thành JSON khi cần. |
| Giới hạn chặt hơn | Mặc định 50 dòng/lần, tối đa 1.000. |

**Lưu ý dữ liệu.** API trả về dòng observation, không phải object trace đầy đủ; muốn dựng lại một trace thì gom các dòng theo `traceId`. Mỗi yêu cầu nên kèm mốc thời gian đầu–cuối (`fromStartTime`, `toStartTime`) để giới hạn phạm vi.

Nếu muốn tìm hiểu thêm hãy tham khảo thông qua https://langfuse.com/docs/api-and-data-platform/features/observations-api

## 7. Public API

**Định nghĩa.** API công khai ở mức dự án — nơi truy cập mọi dữ liệu và tính năng Langfuse bằng code (đọc/ghi trace, eval, prompt, cấu hình...).

**Điểm chính.**

| Hạng mục | Nội dung |
|---|---|
| Xác thực | Basic Auth: username là public key, password là secret key (lấy trong cài đặt dự án). |
| Ba nhóm API | Mức dự án (trang này); mức tổ chức (cấp phát dự án, người dùng, quyền); và quản trị hạ tầng cho bản tự vận hành. |
| Truy cập qua SDK | SDK Python/JS/TS bọc sẵn API với kiểu dữ liệu chặt chẽ, gọi qua thuộc tính `api` trên client. |
| Nạp trace vào Langfuse | Đường chính thức là endpoint OpenTelemetry; Ingestion API cũ đã ngừng khuyến nghị. |
| Lấy dữ liệu | Nhu cầu mới dùng các API hiệu năng cao: Observations API v2, Scores API v3, Metrics API v2. |

Nếu muốn tìm hiểu thêm hãy tham khảo thông qua https://langfuse.com/docs/api-and-data-platform/features/public-api

## 8. Query via SDKs

**Định nghĩa.** Dùng SDK Python/JS/TS để truy vấn chính các API công khai mà không phải tự viết yêu cầu HTTP thô.

**Mục tiêu.** Lấy observation mức dòng cho pipeline đánh giá / few-shot / dữ liệu tinh chỉnh; lấy số liệu tổng hợp (chi phí, mức dùng, độ trễ, điểm) cho dashboard hoặc tính phí; tạo dataset bằng chương trình.

**Điểm chính.** Vùng `api` được sinh tự động từ đặc tả API, tên phương thức phản chiếu tài nguyên REST, hỗ trợ lọc và phân trang. Từ Python SDK v4 / JS SDK v5, các API hiệu năng cao là mặc định (`api.observations`, `api.metrics`, `api.scores_v3`/`scoresV3`); các bản cũ chuyển sang nhánh `api.legacy.*`. Mọi endpoint đều có bản bất đồng bộ (async).

> !Note: Dữ liệu mới thường sẵn sàng để truy vấn trong 15–30 giây sau khi nạp. Với nhu cầu xuất toàn bộ định kỳ, nên dùng blob storage (mục 5) thay vì phân trang qua API.

Nếu muốn tìm hiểu thêm hãy tham khảo thông qua https://langfuse.com/docs/api-and-data-platform/features/query-via-sdk

## 9. Scores API

**Định nghĩa.** API lấy dữ liệu score (điểm từ đánh giá tự động, chú thích tay, hoặc điểm nạp qua API) ở mức từng dòng. Muốn điểm trung bình theo nhóm thì dùng Metrics API. Trang này chỉ lo *đọc* score; tạo score dùng helper riêng.

**Điểm chính.**

| Hạng mục | Nội dung |
|---|---|
| Trường `value` có kiểu | Mỗi score có đúng một `value`, kiểu tùy `dataType`: số / đúng-sai / chuỗi (hạng mục, văn bản, sửa lỗi). Pipeline xử lý nhiều loại thì rẽ nhánh theo `dataType`. |
| Nhóm trường (field groups) | Luôn có phần lõi; xin thêm `details`, `subject`, `annotation` khi cần. |
| `subject` — score gắn vào đâu | Mỗi score gắn đúng một đối tượng, phân biệt bằng `kind`: trace / observation / session / experiment (dataset run). |
| Phân trang bằng cursor | Mặc định 50 dòng/lần, tối đa 100; lần sau truyền lại cursor và lặp đúng bộ lọc cũ. |
| Lọc | Đa số bộ lọc nhận danh sách ngăn cách bằng dấu phẩy; lọc theo khoảng giá trị số (`valueMin`/`valueMax`); một số bộ lọc loại trừ nhau (`traceId`, `sessionId`, `experimentId`). |

Nếu muốn tìm hiểu thêm hãy tham khảo thông qua https://langfuse.com/docs/api-and-data-platform/features/scores-api