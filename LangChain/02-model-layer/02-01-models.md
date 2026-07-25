---
title: Models
doc_source: https://docs.langchain.com/oss/python/langchain/models
accessed: 2026-07-25
lc_version: "1.x (Model profiles cần langchain>=1.1)"
status: draft
lab:
---

# MODELS

## 1. KHỞI TẠO MODEL

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("model_name")
```

API key đọc từ biến môi trường (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`...), không cần truyền tay.

## 2. Tham số hay dùng

| Tham số | Ý nghĩa | Mặc định | Khi nào chỉnh |
|---|---|---|---|
| `model` | Tên model, hoặc `{provider}:{model}` | — | Bắt buộc |
| `api_key` | Khóa xác thực | Đọc từ biến môi trường | Khi không dùng biến môi trường |
| `temperature` | Độ ngẫu nhiên. Càng cao càng "bay"; `0` = tất định | Tùy provider | `0` khi cần kết quả lặp lại được |
| `max_tokens` | Trần độ dài câu trả lời | Không giới hạn | Chặn chi phí, chặn model nói dài |
| `timeout` | Số giây chờ trước khi hủy request | Không đặt | Mạng chậm, model reasoning lâu |
| `max_retries` | Số lần thử lại khi lỗi | `6` | `10–15` nếu mạng chập chờn hoặc agent chạy dài |

```python
model = init_chat_model(
    "claude-sonnet-4-6",
    temperature=0.7,
    max_tokens=1000,
    timeout=30,
    max_retries=6,
)
```
---

## 3. Ba cách gọi model

### invoke() — đơn giản nhất

Đưa vào một câu, hoặc cả lịch sử hội thoại. Nhận về **một** `AIMessage`.

```python
conversation = [
    {"role": "system", "content": "Bạn là trợ lý dịch Anh - Pháp."},
    {"role": "user", "content": "Translate: I love programming."},
    {"role": "assistant", "content": "J'adore la programmation."},
    {"role": "user", "content": "Translate: I love building applications."},
]
response = model.invoke(conversation)
```

### stream() — nhả từng mẩu

```python
for chunk in model.stream("What color is the sky?"):
    print(chunk.text, end="", flush=True)
```

`stream()` trả về nhiều `AIMessageChunk` chứ không phải một message. Muốn có message hoàn chỉnh thì **cộng dồn** chúng lại — đúng nghĩa dùng dấu `+`:

```python
full = None
for chunk in model.stream("..."):
    full = chunk if full is None else full + chunk
```

Streaming chỉ có ích nếu **mọi khâu** phía sau xử lý được luồng. Nếu có một bước phải gom đủ toàn bộ output mới làm được việc, thì stream cũng như không.

### batch() — hỏi nhiều câu cùng lúc

Tình huống: có 100 review khách hàng, cần model phân loại tốt/xấu từng cái.

Viết vòng `for` gọi `invoke()` 100 lần thì mỗi lần phải chờ model trả lời xong mới gửi lần kế. Mỗi lần 2 giây → mất 200 giây, mà phần lớn thời gian đó máy mình chỉ ngồi chờ mạng.

`batch()` gửi cả 100 câu đi cùng lúc:

```python
reviews = ["Sản phẩm tốt", "Giao hàng chậm", "Đóng gói ẩu", ...]
results = model.batch(reviews)
# results[0] ứng với reviews[0], results[1] ứng với reviews[1]...
```

**Điều kiện dùng được: các câu hỏi phải độc lập** — câu sau không cần biết kết quả câu trước. Phân loại 100 review, dịch 50 đoạn văn: độc lập, dùng `batch()`. Còn hội thoại nhiều lượt thì lượt sau phụ thuộc lượt trước, phải `invoke()` tuần tự.

**`batch()` hay `batch_as_completed()`?**

| | `batch()` | `batch_as_completed()` |
|---|---|---|
| Trả kết quả khi nào | Cả lô xong hết mới trả | Cái nào xong trả cái đó |
| Thứ tự | Đúng thứ tự input | **Lộn xộn**, ai xong trước ra trước |
| Ghép lại thế nào | Theo index, `results[i]` ↔ `inputs[i]` | Mỗi kết quả kèm sẵn index của input |
| Dùng khi | Cần đủ cả lô mới xử lý tiếp | Muốn hiện kết quả dần lên màn hình |

```python
for idx, response in model.batch_as_completed(reviews):
    print(idx, response.text)   # idx cho biết đây là review thứ mấy
```

**Chặn số request song song.** Mặc định `batch()` bắn hết cùng lúc — 100 câu là 100 request đồng thời, rất dễ dính 429. Giới hạn lại:

```python
model.batch(reviews, config={"max_concurrency": 5})
# lúc nào cũng chỉ 5 request đang chạy, xong 1 mới thả tiếp 1
```

## 4. Tool calling

Model tự nó chỉ sinh ra chữ. Nó không tra được thời tiết, không đọc được database, không gọi được API. Tool là cánh cửa duy nhất để nó chạm vào thế giới bên ngoài.

**Một tool gồm hai nửa:**

| Nửa | Là gì |
|---|---|---|
| **Schema** | Tên tool, mô tả công dụng, danh sách tham số |
| **Hàm** | Đoạn code thực sự làm việc |

Trong LangChain, decorator `@tool` sinh schema tự động từ chữ ký hàm: tên hàm thành tên tool, **docstring thành phần mô tả**, type hint thành kiểu tham số.

```python
@tool
def get_weather(location: str) -> str:
    """Get the weather at a location."""
    return f"It's sunny in {location}."
```

Docstring không phải chú thích cho người đọc code — đó là **toàn bộ thông tin model có** để quyết định có dùng tool này hay không. Viết mơ hồ thì model chọn sai tool.


**!!! Quan trọng: model không chạy tool.** Nó trả về một `tool_call` — nghĩa là "Khi model muốn gọi hàm `get_weather` với `location='Boston'`".

Nên một lượt tool calling luôn có ba step:

1. **Model đề nghị** — trả về `tool_calls` gồm tên tool, tham số, và một `id`.
2. **Thực thi Tool** — chạy hàm, gói kết quả vào `ToolMessage`, gắn đúng `tool_call_id` để model biết kết quả này ứng với đề nghị nào.
3. **Model đọc kết quả** — gọi model lần nữa với lịch sử đã có `ToolMessage`, lúc này nó mới trả lời người dùng.

Ba step này lặp đi lặp lại chính là **agent**. `create_agent` không làm gì huyền bí, nó chỉ tự động hóa vòng lặp trên và biết khi nào dừng. Tự viết tay một lần rồi mới dùng agent sẽ hiểu agent đang làm gì bên trong.

---

## 5. Structured output

Bắt model trả về đúng cấu trúc thay vì văn xuôi, để parse được ngay:

```python
from pydantic import BaseModel, Field

class Movie(BaseModel):
    title: str = Field(description="The title of the movie")
    year: int = Field(description="The year the movie was released")

model_with_structure = model.with_structured_output(Movie)
response = model_with_structure.invoke("Provide details about the movie Inception")
# Movie(title='Inception', year=2010)
```

Ba kiểu schema, chọn theo nhu cầu:

| Kiểu | Được gì |
|---|---|
| Pydantic | Tự validate, mô tả field, lồng nhau |
| `TypedDict` | Gọn, thuần Python |
| JSON Schema | Kiểm soát tối đa, liên thông hệ khác |