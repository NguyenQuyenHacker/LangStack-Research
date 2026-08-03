---
title: Prompt Management — Features — Runtime Reliability
doc_source:
  - https://langfuse.com/docs/prompt-management/features/caching
  - https://langfuse.com/docs/prompt-management/features/guaranteed-availability
accessed:
version: v4
status: draft
related:
  - ./02-03-00-index.md
---

# Runtime Reliability

## Tổng quan

Ứng dụng production gọi `get_prompt()` trên đường nóng — mỗi request tới người dùng có thể phải lấy prompt trước khi gọi model. Hai feature ở đây cùng giải quyết một rủi ro: server Langfuse chậm hoặc down thì không được kéo theo ứng dụng chậm hoặc lỗi.

Caching là lớp chặn đầu — sau lần fetch đầu tiên, các lần gọi sau lấy từ bộ nhớ cục bộ (client-side), không round-trip mạng. Guaranteed Availability là lớp xử lý khi mọi con đường lấy dữ liệu mới đều thất bại: pre-fetch lúc khởi động hoặc giá trị fallback do người dùng khai báo. Hai cơ chế không thay thế nhau — cache làm giảm số lần phải gọi mạng, fallback trả lời câu hỏi "nếu gọi mạng thất bại thì lấy gì".

---

## Caching

**Khái niệm.** SDK Langfuse giữ một cache phía client (client-side) cho prompt đã fetch, theo thời gian sống (TTL — time to live) cấu hình được qua tham số `cacheTtlSeconds` (JS/TS) hoặc `cache_ttl_seconds` (Python). Mặc định TTL là 60 giây. Trong thời gian còn hạn, `get_prompt()` trả thẳng bản trong cache, không gọi mạng. Khi TTL hết hạn, SDK vẫn trả ngay bản cũ (stale) cho lần gọi đó, đồng thời âm thầm làm mới (revalidate) ở nền — tài liệu gọi đây là stale-while-revalidate.

Tài liệu còn mô tả cache phía server: API của Langfuse có một tầng cache bằng Redis, phía sau là PostgreSQL làm nguồn dữ liệu cuối cùng. Cache phía client là tầng ta chạm tới đầu tiên và cũng là tầng quyết định độ trễ ta cảm nhận được.

**Vai trò.** Nhờ cache client-side, độ trễ chỉ xuất hiện ở lần gọi đầu tiên cho mỗi prompt; các lần sau gần như tức thời vì không đợi mạng. Tài liệu dẫn số đo: fetch lần đầu trung bình khoảng 39ms qua 1000 lần gọi tuần tự, median 37ms — con số minh hoạ chi phí của một lần round-trip thật, để thấy giá trị của việc không phải lặp lại nó mỗi request.

Muốn tắt cache — ví dụ ở môi trường dev cần luôn thấy bản mới nhất — đặt `cacheTtlSeconds` (hoặc tham số Python tương ứng) bằng `0`.

**Ví dụ.**

```python
prompt = langfuse.get_prompt("movie-critic", cache_ttl_seconds=300)
```

```ts
const prompt = await langfuse.prompt.get("movie-critic", {
  cacheTtlSeconds: 300,
});
```

Chi tiết cấu hình: `https://langfuse.com/docs/prompt-management/features/caching`

---

## Guaranteed Availability

**Khái niệm.** `get_prompt()` chỉ báo lỗi khi hai điều kiện cùng xảy ra: chưa có bản nào của prompt đó trong cache (ví dụ lần gọi đầu tiên lúc ứng dụng vừa khởi động) **và** yêu cầu mạng tới Langfuse API thất bại. Tài liệu nêu hai cách để loại bỏ rủi ro này, không phải một cơ chế tự động — ta phải chủ động áp dụng một trong hai (hoặc cả hai):

1. **Pre-fetch lúc khởi động (startup):** gọi `get_prompt()` ngay khi ứng dụng khởi động, để nạp sẵn prompt vào cache trước khi có traffic thật. Nếu lệnh fetch này thất bại, tài liệu khuyến nghị cho ứng dụng dừng khởi động (fail fast) thay vì chạy tiếp với prompt rỗng.
2. **Giá trị fallback:** truyền tham số `fallback` vào `get_prompt()` — một chuỗi (text prompt) hoặc mảng message có `role`/`content` (chat prompt). Khi mạng thất bại và cache trống, SDK trả về giá trị fallback này thay vì ném lỗi. Object prompt trả về có cờ `is_fallback` (Python) / `isFallback` (JS/TS) để ứng dụng biết đang chạy bằng bản dự phòng, không phải bản thật từ Langfuse.

**Vai trò.** Fallback là lớp phòng thủ cuối khi cả cache lẫn mạng đều không cho ra prompt: ứng dụng vẫn có một giá trị để gọi model, thay vì crash hoặc trả lỗi cho người dùng cuối. Cờ `is_fallback`/`isFallback` cho phép log hoặc cảnh báo riêng khi hệ thống đang chạy ở chế độ suy giảm (degraded), để đội vận hành biết cần kiểm tra kết nối tới Langfuse.

**Ví dụ.**

```python
prompt = langfuse.get_prompt(
  "movie-critic",
  fallback="Do you like {{movie}}?"
)
prompt.is_fallback  # True nếu đang dùng bản fallback
```

```ts
const prompt = await langfuse.prompt.get("movie-critic", {
  fallback: "Do you like {{movie}}?"
});
prompt.isFallback;
```

Chi tiết cấu hình: `https://langfuse.com/docs/prompt-management/features/guaranteed-availability`

---

## Tham chiếu chéo

Với một prompt bất kỳ, Caching là lớp phòng thủ đầu tiên — hầu hết request chưa bao giờ chạm tới mạng vì bản trong cache còn hạn (hoặc đang trong cửa sổ stale-while-revalidate). Guaranteed Availability chỉ vào việc khi Caching cũng miss: chưa từng fetch được prompt đó, và lần gọi mạng để lấy nó thất bại. Pre-fetch lúc khởi động thực chất là cách chủ động nạp cache trước để tình huống miss đó khó xảy ra hơn; fallback là phương án cuối khi pre-fetch không có hoặc chính pre-fetch cũng thất bại.

- [Chỉ mục Prompt Management Features](./02-03-00-index.md) — vị trí của hai feature này trong nhóm *(chưa viết — xem SOURCES.md)*
