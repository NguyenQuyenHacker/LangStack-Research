---
title: Observability — Features — Tìm kiếm trên UI & tích hợp
doc_source:
  - https://langfuse.com/docs/observability/features/filter-search-bar
  - https://langfuse.com/docs/observability/features/full-text-search
  - https://langfuse.com/docs/observability/features/events-table-charts
  - https://langfuse.com/docs/observability/features/url
  - https://langfuse.com/docs/observability/features/mcp-tracing
accessed: 2026-08-03
version: v4
status: draft
related:
  - ./01-05-00-index.md
---

# Tìm kiếm trên UI & tích hợp

Nhóm tính năng để tìm, xem và chia sẻ dữ liệu trace đã ghi trên giao diện, cộng một tính năng tích hợp quyết định cách nối trace giữa MCP client và server.

## Tổng quan

Bốn trong năm tính năng thao tác trên dữ liệu đã có: gõ để lọc (Filter Search Bar), tìm chuỗi trong nội dung (Full-Text Search), đổi bảng thành biểu đồ trên cùng truy vấn (Chart any table), lấy link tới một trace (Trace URLs). Ba tính năng đầu là ba view trên cùng một trạng thái truy vấn — filter thu hẹp dòng, full-text khớp theo nội dung, chart nhìn cùng tập dòng dưới dạng đồ thị. Tính năng thứ năm, MCP Tracing, khác nhóm ở chỗ nó chạm vào cách instrument: quyết định trace của client và server tách rời hay nối thành một.

## 1. Filter Search Bar

### Khái niệm

Thanh nhập một dòng để lọc và tìm trên bảng Observations/Traces bằng cách gõ, thay cho việc dựng filter thủ công ở sidebar. Bar và sidebar là hai trình soạn trên **cùng một filter state**: gõ vào bar thì filter hiện lên sidebar và ngược lại. Câu truy vấn được parse thành đúng bộ filter mà sidebar sinh ra.

Cú pháp là chuỗi các filter `field:value` nối bằng AND ngầm. Hỗ trợ: toán tử so sánh `>`, `>=`, `<`, `<=` cho trường số và datetime; wildcard `*` trên text field (`name:*checkout*` contains, `name:checkout*` starts-with, `name:*checkout` ends-with, `name:=checkout` exact); phủ định bằng tiền tố `-`; any-of `level:(ERROR OR WARNING)` và all-of `tags:(billing AND urgent)` cho trường mảng; dot path cho nested field (`metadata.region:eu`, `scores.accuracy:>0.8`); null check `has:endTime` / `-has:endTime`; và full-text bằng bare word. Hầu hết field có alias ngắn (`env`, `user`, `cost`, `tokens`…). Toàn bộ truy vấn được serialize vào URL để chia sẻ đúng view. Nút **Ask AI** dịch mô tả ngôn ngữ tự nhiên thành query và biết schema thật của project.

### Vai trò

Khoanh vùng nhanh tập trace/observation cần xem bằng cách gõ thay vì click từng filter, và tái lập chính xác một view qua link.

### Ví dụ

Điều tra lỗi trên production: gõ `level:ERROR type:TOOL environment:production latency:>2 name:*checkout*` để lấy các tool call lỗi, chậm quá 2 giây, thuộc luồng checkout; gửi URL cho đồng đội để họ mở đúng view đó.

Chi tiết cấu hình: https://langfuse.com/docs/observability/features/filter-search-bar

## 2. Full-Text Search

### Khái niệm

Cơ chế tìm mọi lần xuất hiện của một keyword hoặc cụm từ trong input, output và metadata của trace và observation — cho trường hợp nhớ nội dung nhưng không nhớ nó thuộc trace nào. Dùng qua thanh search phía trên bảng, kết hợp được với filter và time range; trên bảng v4 còn nhúng ngay trong Filter Search Bar cạnh các filter cấu trúc.

Chạy trên ClickHouse full-text search: text index cho phép bỏ qua phần dữ liệu chắc chắn không khớp trước khi đọc full payload, giữ tốc độ ngay cả khi khối lượng trace lớn. Về ngữ nghĩa khớp: word-based, case-insensitive cho input/output; cụm nhiều từ khớp như một chuỗi liền. Ở API Observations v2, toán tử `matches` làm token-based search trên input, output và string metadata (`matches` case-insensitive cho input/output, case-sensitive cho metadata); các toán tử substring như contains/starts-with/ends-with bị từ chối với lỗi 400 trên input/output vì phải quét toàn bộ nội dung.

### Vai trò

Định vị trace theo nội dung nhớ được, thay vì theo id hay khoảng thời gian.

### Ví dụ

Nhớ một câu trả lời của agent có chứa cụm "refund failed" nhưng không nhớ trace nào — gõ `output:"refund failed"` để lấy đúng các run có cụm đó trong output.

**!Note:** Khớp theo từ nguyên vẹn, không phải substring — `error` khớp `error` nhưng không khớp `errors`. Một chuỗi tồn tại dưới dạng substring nằm trong từ dài hơn sẽ không được tìm thấy; search trả về ít kết quả hơn ta tưởng mà không báo gì, dễ dẫn tới kết luận sai là "không có".

Chi tiết cấu hình: https://langfuse.com/docs/observability/features/full-text-search

## 3. Chart any table

### Khái niệm

Nút gạt **Table | Chart** trên bảng Observations biến các dòng đang lọc thành biểu đồ trên **cùng một truy vấn** — đổi qua lại không thay đổi filter, time range hay dữ liệu, chỉ đổi cách hiển thị. Biểu đồ là tổ hợp bốn lựa chọn trong panel Visualize: **chart type** (Line/Area/Bars theo thời gian; Ranked/Pie theo hạng mục; Number một giá trị duy nhất), **metric** (Count/Latency/Cost/Tokens, mặc định Count), **aggregation** (tùy metric — latency có Average/Median p50/p95/p99/Max/Min; cost và tokens có Sum/Average/p95/Max), **breakdown** (Total/Model/Name/Level/Type/Environment). View kèm cấu hình serialize vào URL để chia sẻ. **Add to dashboard** lưu chart thành widget trên custom dashboard (không lưu time range — dashboard đích cấp khoảng thời gian).

Một số filter không dịch được sang chuỗi thời gian tổng hợp: numeric measure dùng làm filter (lọc theo latency/cost/token — dù ba thứ này vẫn dùng được làm *metric* của chart), filter theo scores/metadata/comments, full-text và text theo trường (`input:`, `output:`), presence check (`has:`). Langfuse không âm thầm bỏ chúng: giữ chart hiển thị và vô hiệu filter đó tại chỗ — facet ở sidebar mờ đi, token trên bar bị gạch ngang, hover giải thích filter vẫn áp cho bảng nhưng chart không dùng được.

### Vai trò

Xem xu hướng của đúng lát cắt vừa lọc mà không rời bảng, rồi giữ lại lên dashboard nếu đáng theo dõi tiếp.

### Ví dụ

Lọc còn các generation của một model, gạt sang Chart với chart type Line, metric Latency, aggregation p95, breakdown Model để có "p95 latency by model over time" trên đúng tập dòng đã lọc; Add to dashboard nếu cần theo dõi lâu dài.

Chi tiết cấu hình: https://langfuse.com/docs/observability/features/events-table-charts

## 4. Trace URLs

### Khái niệm

Mỗi trace có một URL riêng để mở trực tiếp hoặc chia sẻ. Lấy URL trong SDK: Python `langfuse.get_trace_url()` (hoặc truyền `trace_id`), JS/TS `langfuse.getTraceUrl(traceId)` — hữu ích để ghi vào log hoặc mở khi chạy experiment trong notebook.

Mặc định chỉ thành viên project xem được trace. Có thể đặt một trace thành `public` để chia sẻ qua link công khai không cần đăng nhập: Python `set_current_trace_as_public()` hoặc `span.set_trace_as_public()`, JS/TS `rootSpan.setTraceAsPublic()`. Đặt public đồng nghĩa bất kỳ ai có link đều xem được toàn bộ nội dung trace — với dữ liệu nhạy cảm, đây là quyết định phải cân nhắc kỹ (xem thêm ràng buộc masking ở [./01-05-00-index.md](./01-05-00-index.md)).

### Vai trò

Deep-link tới một trace cụ thể từ log hay báo cáo, hoặc mở trace cho người ngoài project qua link công khai.

### Ví dụ

Pipeline ghi URL trace của mỗi run thất bại vào log hệ thống để trực ban click thẳng vào Langfuse xem, thay vì tra lại theo id.

Chi tiết cấu hình: https://langfuse.com/docs/observability/features/url

## 5. MCP Tracing

### Khái niệm

Cách nối trace giữa MCP client và server. Mặc định, client và server sinh trace **độc lập** — có ích khi cần ranh giới dịch vụ rõ hoặc khi hai bên do hai đội khác nhau quản. Để có một trace thống nhất chạy từ client qua server tới API bên ngoài, ta propagate trace context qua trường `_meta` của MCP (định dạng W3C Trace Context của OpenTelemetry): trích context hiện tại ở phía client, inject vào `_meta` của tool call, trích và khôi phục ở phía server, sau đó mọi thao tác server kế thừa context của client.

### Vai trò

Dựng một trace liền mạch cho luồng đi qua ranh giới MCP client–server, thay vì phải ghép thủ công hai trace rời.

### Ví dụ

Agent gọi một MCP server để truy vấn dữ liệu ngoài. Không nối context thì được hai trace tách rời (một của client, một của server), khó lần cả luồng; inject context vào `_meta` thì cả chuỗi client → server → API ngoài nằm trong một trace duy nhất.

**!Note:** Mặc định là hai trace rời. Nếu ta kỳ vọng một trace thống nhất nhưng không propagate context qua `_meta`, hệ thống không báo lỗi — chỉ lặng lẽ cho ra hai trace không nối với nhau.

Chi tiết cấu hình: https://langfuse.com/docs/observability/features/mcp-tracing

## Tham chiếu chéo

Filter Search Bar, Full-Text Search và Chart any table cùng chạy trên **data model v4**: trên Langfuse Cloud phải bật **Langfuse v4 preview** mới dùng được; bản self-hosted phải nâng lên v4. Ask AI trong Filter Search Bar là tính năng Cloud-only, đang beta, mặc định tắt (owner/admin bật trong Organization Settings), chạy trên model hosted ở AWS Bedrock với zero data retention.

Ba tính năng đó là ba view trên cùng một truy vấn — nội dung mô tả chúng phải nhất quán với nhau: bar thu hẹp dòng, full-text là khả năng khớp nội dung dùng ngay trong bar, chart là cách nhìn khác của cùng tập dòng đã lọc. Trace URLs và MCP Tracing không phụ thuộc ràng buộc v4/Fast ở trên.

Ràng buộc cắt ngang với masking: link công khai của Trace URLs phơi bày đúng nội dung đã lưu; nếu dữ liệu chưa được mask ở tầng client trước khi gửi, đặt trace public sẽ để lộ nguyên trạng — xem [./01-05-00-index.md](./01-05-00-index.md).

Trỏ về: [./01-05-00-index.md](./01-05-00-index.md)