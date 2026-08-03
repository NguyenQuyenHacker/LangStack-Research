---
title: Observability — Features — Thuộc tính gắn nhãn
doc_source:
  - https://langfuse.com/docs/observability/features/environments
  - https://langfuse.com/docs/observability/features/tags
  - https://langfuse.com/docs/observability/features/metadata
  - https://langfuse.com/docs/observability/features/releases-and-versioning
accessed: 2026-08-01
version: v4
status: draft
related:
  - ./01-05-00-index.md
---

# Thuộc tính gắn nhãn (Environments, Tags, Metadata, Releases & Versions)

> Bốn thuộc tính dùng để gắn thêm chiều thông tin lên trace và observation, phục vụ việc lọc, đối chiếu và phân tích số liệu trong Langfuse.
> Xem tổng quan cụm tính năng tại [01-05-00 index](./01-05-00-index.md).

---

## 1. Tổng quan

Langfuse ghi lại hoạt động của ứng dụng LLM dưới dạng các đối tượng dữ liệu (trace, observation, score). Bản thân các đối tượng này chỉ mang nội dung nghiệp vụ — input, output, thời gian, chi phí. Bốn thuộc tính trong tài liệu này bổ sung chiều phân loại lên các đối tượng đó, để về sau có thể lọc và cắt lát số liệu theo từng chiều.

Bốn thuộc tính khác nhau về vai trò:

| Thuộc tính | Vai trò | Định dạng |
|---|---|---|
| Environment | Cô lập dữ liệu theo môi trường triển khai (production, staging, dev) | Một chuỗi duy nhất |
| Tags | Phân loại tự do bằng danh sách nhãn | Danh sách chuỗi |
| Metadata | Đối chiếu bằng cặp khóa–giá trị | Cặp khóa–giá trị |
| Release / Version | Theo dõi tác động của thay đổi phiên bản mã lên số liệu | Một chuỗi duy nhất |

Việc gộp bốn thuộc tính này thành một cụm là cách tổ chức của bộ tài liệu, không phải một khái niệm hợp nhất mà Langfuse định nghĩa — mỗi trang tài liệu mô tả riêng một thuộc tính. Đây là suy luận về mặt cấu trúc, chưa được nguồn khẳng định.

Điểm kỹ thuật chung: ba trong bốn thuộc tính (tags, metadata, version) — và cả environment ở phạm vi request trong Python SDK — được gán qua cùng một cơ chế `propagate_attributes()`. Cơ chế này áp một giá trị cho **mọi observation nằm trong ngữ cảnh** hiện tại, thay vì phải gán thủ công lên từng observation. Ràng buộc chung của cơ chế được trình bày ở mục 6.

---

## 2. Environment — cô lập dữ liệu theo môi trường triển khai

### Mục đích

Environment cho phép dùng chung một project nhưng vẫn tách dữ liệu của các môi trường khác nhau — production, staging, development. Nhờ đó dữ liệu phát triển không lẫn vào dữ liệu vận hành, mỗi môi trường lọc và phân tích được độc lập, trong khi vẫn dùng lại được dataset và prompt giữa các môi trường.

### Phạm vi áp dụng và lọc

Thuộc tính `environment` hiện diện trên mọi loại sự kiện: trace, observation (span, event, generation), score, và session. Trên giao diện Langfuse, bộ lọc environment nằm ở thanh điều hướng và áp dụng cho toàn bộ các view.

### Quản lý

Environment được tạo tự động ngay lần đầu có dữ liệu đẩy lên với một giá trị `environment` mới, và tồn tại vĩnh viễn. Hiện chưa xóa hoặc đổi tên được qua giao diện.

**!Note:** Vì environment tạo tự động theo giá trị đẩy lên và không sửa được sau đó, một lỗi gõ sai (ví dụ `prod` và `production` dùng lẫn lộn) sẽ sinh ra hai môi trường tách biệt tồn tại vĩnh viễn, làm phân mảnh số liệu mà không dọn được từ UI. Cần thống nhất tên trước khi đưa vào chạy.

---

## 3. Tags — nhãn phân loại dạng danh sách

### Mục đích

Tags phân loại và lọc observation cùng trace theo các tiêu chí tự do: theo use case, theo hàm hoặc API được gọi, theo môi trường, hay bất kỳ tiêu chí nào khác. Khác environment (một giá trị duy nhất, mang tính cô lập), tags là một danh sách nhãn phẳng phục vụ gom nhóm.

Một observation có thể mang nhiều tag. Toàn bộ tag của các observation trong một trace được tự động tổng hợp và gắn lên chính đối tượng trace.

---

## 4. Metadata — cặp khóa–giá trị để đối chiếu

### Mục đích

Metadata làm giàu observation bằng các cặp khóa–giá trị, phục vụ hiểu và đối chiếu observation với nhau. Có thể lọc theo khóa metadata trên cả giao diện lẫn API. Khác tags (danh sách nhãn phẳng), metadata mang cấu trúc khóa–giá trị nên phù hợp lưu các chiều có tên rõ ràng như `region`, `user_tier`, `request_id`.

Tài liệu chia metadata thành hai loại theo phạm vi áp dụng.

### Metadata lan truyền (propagated)

Dùng `propagate_attributes(metadata={...})` để tự động áp metadata cho mọi observation trong một ngữ cảnh:

```python
from langfuse import observe, propagate_attributes

@observe()
def process_data():
    with propagate_attributes(
        metadata={"source": "api", "region": "us-east-1", "user_tier": "premium"}
    ):                                                    # áp cho mọi observation con
        result = perform_processing()
        return result
```

Loại này chịu ràng buộc riêng: giá trị phải là chuỗi tối đa 200 ký tự (giá trị vượt quá bị loại bỏ), và khóa chỉ được chứa ký tự chữ–số (không khoảng trắng, không ký tự đặc biệt).

### Metadata không lan truyền (non-propagated)

Khi chỉ muốn gắn metadata cho **một observation cụ thể**, dùng `update()` trên chính observation đó:

```python
from langfuse import get_client

langfuse = get_client()
with langfuse.start_as_current_observation(as_type="span", name="process-request") as root_span:
    root_span.update(metadata={"stage": "parsing"})       # chỉ observation này nhận metadata
    # hoặc: langfuse.update_current_span(metadata={"stage": "parsing"})
```

---

## 5. Releases & Versions — theo dõi tác động của thay đổi mã

### Mục đích

Hai thuộc tính này gắn thông tin phiên bản mã lên dữ liệu, để trả lời hai câu hỏi vận hành: đo tác động của một thử nghiệm A/B trên production lên chi phí, độ trễ và chất lượng (*"đổi sang model mới thì ảnh hưởng thế nào?"*), và giải thích biến động số liệu theo thời gian (*"vì sao độ trễ của chain này tăng lên?"*).

Điểm phân biệt: `release` gắn với **toàn bộ ứng dụng**, còn `version` gắn với **từng observation có tên cụ thể**.

### Release — phiên bản toàn ứng dụng

`release` đánh dấu phiên bản tổng thể của ứng dụng, thường đặt bằng semantic version hoặc git commit hash. SDK tìm giá trị `release` theo thứ tự: (1) tham số lúc khởi tạo SDK, (2) biến môi trường, (3) biến định danh release tự động trên các nền tảng triển khai phổ biến.

```python
from langfuse import Langfuse

langfuse = Langfuse(release="v2.1.24")   # đặt release ngay khi khởi tạo client (ưu tiên cao nhất)
```

JS/TS SDK đọc biến môi trường `LANGFUSE_RELEASE` — tiện đặt trong pipeline CI/CD. Nếu không đặt gì, SDK tự nhận diện release từ biến môi trường có sẵn trên các nền tảng như Vercel, Heroku, Netlify.

### Version — phiên bản từng observation

`version` thêm được vào mọi loại observation (span, generation, event...). Nhờ đó theo dõi được tác động của một `version` mới lên số liệu của đối tượng có cùng `name`, thông qua phần analytics của Langfuse.

```python
from langfuse import observe, propagate_attributes

@observe()
def process_data():
    with propagate_attributes(version="1.0"):   # áp version cho mọi observation con
        result = perform_processing()
        return result
```

Cũng có thể đặt trực tiếp trên một observation qua tham số `version` khi tạo, thay vì lan truyền cho cả ngữ cảnh.

---

## 6. Ràng buộc chung của Attribute Propagation

Ba thuộc tính tags, metadata, version đều dùng chung cơ chế Attribute Propagation, và tài liệu nêu cùng một khối lưu ý trên cả ba trang. Langfuse dùng các observation có gắn thuộc tính này để dựng số liệu ở cấp tương ứng (tags-level, metadata-level, version-level metrics). Ba ràng buộc:

- Giá trị phải là **chuỗi, tối đa 200 ký tự**.
- Phải gọi **sớm trong trace** để mọi observation đều được phủ. Gọi muộn thì các observation tạo trước đó không mang thuộc tính, làm số liệu sai lệch.
- Giá trị không hợp lệ bị loại bỏ kèm một cảnh báo (warning).

**!Note:** Ràng buộc "gọi sớm" là loại lỗi im lặng nguy hiểm nhất ở đây — mã vẫn chạy, không lỗi, chỉ là các observation sinh ra trước lệnh `propagate_attributes()` thiếu thuộc tính, khiến metric đếm thiếu mà không có dấu hiệu báo động.

---

## 7. Bảng so sánh bốn thuộc tính

| Tiêu chí | Environment | Tags | Metadata | Release / Version |
|---|---|---|---|---|
| Cấu trúc | Một chuỗi | Danh sách chuỗi | Cặp khóa–giá trị | Một chuỗi |
| Mục tiêu | Cô lập môi trường | Phân loại, gom nhóm | Đối chiếu theo chiều có tên | Theo dõi phiên bản mã |
| Gắn ở cấp | Client / process (Python: cả request) | Observation → tổng hợp lên trace | Observation | Release: ứng dụng; Version: observation |
| Cách đặt phổ biến | Biến `LANGFUSE_TRACING_ENVIRONMENT` / tham số init | `propagate_attributes(tags=[...])` | `propagate_attributes(metadata={...})` / `update()` | Release: init / env var; Version: `propagate_attributes(version=...)` |
| Giới hạn độ dài | ≤ 40 ký tự (kèm regex) | ≤ 200 ký tự / tag | ≤ 200 ký tự / giá trị (loại lan truyền) | ≤ 200 ký tự |
| Sửa được sau khi tạo | Không xóa/đổi tên qua UI | Không (mô hình bất biến) | Tài liệu không nêu | Tài liệu không nêu |
| Có mặt trên | Trace, observation, score, session | Observation + trace | Observation | Observation (version); toàn app (release) |

---

## 8. Phân biệt Tags và Metadata

Tài liệu mô tả tags và metadata riêng rẽ, không đặt cạnh nhau để so sánh, nên ranh giới khi nào dùng cái nào không được nêu tường minh. Suy luận từ cấu trúc dữ liệu của hai bên:

- **Tags** là danh sách phẳng, không có khóa — hợp để đánh dấu sự hiện diện của một đặc điểm ("có/không thuộc nhóm này"), ví dụ `experiment-a`, `beta-user`, `flagged`.
- **Metadata** là cặp khóa–giá trị — hợp khi cần lưu một chiều có tên và giá trị đi kèm, ví dụ `region=us-east-1`, `user_tier=premium`.

Căn cứ: tài liệu cho biết tags được tổng hợp lên trace và dùng làm tiêu chí lọc, còn metadata cho phép lọc theo *khóa*. Đây là suy luận về mặt sử dụng, chưa được tài liệu khẳng định trực tiếp — nên đối chiếu lại nếu cách phân loại này ảnh hưởng tới thiết kế log.

---

## Tham chiếu chéo

- [01-05-00 index](./01-05-00-index.md) — tổng quan cụm tính năng Observability Features
- Cơ chế `propagate_attributes` (Python SDK): `https://langfuse.com/docs/observability/sdk/instrumentation#propagate-attributes`
- Data Model (các loại đối tượng dữ liệu): `https://langfuse.com/docs/observability/data-model`
- FAQ tổ chức nhiều environment: `https://langfuse.com/faq/all/managing-different-environments`