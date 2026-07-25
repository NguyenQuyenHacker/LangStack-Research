---
title: Structured output
doc_source: https://docs.langchain.com/oss/python/langchain/structured-output
accessed: 2026-07-25
lc_version: "1.x (strict cần >=1.2; đọc profile để tự chọn strategy cần >=1.1)"
status: draft
lab:
---

# Structured output

---

## Phần I — Khái niệm

### Structured output là gì

Bắt model trả về **dữ liệu có cấu trúc** thay vì văn xuôi.

> Không có structured output: `"Anh John Doe, email john@example.com"` → phải regex.

> Có structured output: `{"name": "John Doe", "email": "john@example.com"}` → dùng luôn.

---

## Phần II — Khung vận hành

Tất cả nằm ở một tham số: `response_format`.

```python
agent = create_agent(
    model="gpt-5.5",
    tools=tools,
    response_format=ContactInfo,   # ← khai báo schema ở đây
)

result = agent.invoke({"messages": [...]})
result["structured_response"]      # ← lấy kết quả ở đây
```

`response_format` nhận bốn thứ:

| Truyền vào | Nghĩa là |
|---|---|
| Một schema (như trên) | LangChain **tự chọn** chiến lược phù hợp |
| `ProviderStrategy(schema)` | Ép dùng cách này — Phần IV |
| `ToolStrategy(schema)` | Ép dùng cách này — Phần V |
| `None` | Không yêu cầu structured output |

### LangChain tự chọn thế nào

Cùng một schema, có hai cách gửi lên API. Truyền schema trần thì LangChain quyết hộ:

```
         response_format=ContactInfo
                    │
                    ▼
   Provider có cho đính schema thẳng
        vào request không?
        ┌───────────┴───────────┐
       CÓ                      KHÔNG
   (GPT, Claude,          (model khác, miễn
    Gemini)                là biết gọi tool)
        │                       │
        ▼                       ▼
   ProviderStrategy         ToolStrategy
      (Phần IV)               (Phần V)
```

## Phần III — Schema: khai báo bằng gì

Bốn kiểu, dùng được cho cả hai chiến lược:

| Kiểu | Trả về | Đặc điểm |
|---|---|---|
| **Pydantic** `BaseModel` | Một **instance** đã validate | Tự kiểm ràng buộc (`ge=1, le=5`), mô tả field bằng `Field(description=...)` |
| **Dataclass** | `dict` | Thuần Python, mô tả bằng comment |
| **TypedDict** | `dict` | Gọn nhất, mô tả bằng comment |
| **JSON Schema** | `dict` | Viết dài nhất, kiểm soát chi tiết nhất, dễ liên thông hệ khác |

Điểm khác nhau quan trọng nhất: **chỉ Pydantic trả về object đã validate**, ba kiểu còn lại trả `dict` thô.

```python
class ProductReview(BaseModel):
    """Analysis of a product review."""
    rating: int | None = Field(description="Rating 1-5", ge=1, le=5)
    sentiment: Literal["positive", "negative"] = Field(description="...")
    key_points: list[str] = Field(description="Lowercase, 1-3 words each")
```

---

## Phần IV — ProviderStrategy

### 4.1 Cách nó chạy

Một số provider cho phép **đính schema thẳng vào request**. 
 
```json
{
  "messages": [...],
  "response_format": { "json_schema": {...} }     ← schema nằm ở đây
}
```
 
### 4.2 Tham số

```python
class ProviderStrategy(Generic[SchemaT]):
    schema: type[SchemaT]
    strict: bool | None = None
```

| Tham số | Bắt buộc | Mặc định | Làm gì |
|---|---|---|---|
| `schema` | Có | — | Khuôn dữ liệu muốn nhận. Bốn kiểu ở Phần III |
| `strict` | Không | `None` (tắt) | Bật chế độ ép nghiêm ngặt. Chỉ OpenAI và xAI hỗ trợ. Cần `langchain>=1.2` |
 
`response_format=ProductRating` và `response_format=ProviderStrategy(ProductRating)` là **tương đương** khi provider hỗ trợ. Chỉ cần viết dạng thứ hai khi muốn bật `strict`.

### 4.3 Hai giới hạn
 
**Ép khuôn không đảm bảo nội dung đúng.** Server bảo đảm JSON hợp lệ, đủ field, đúng kiểu — không bảo đảm giá trị là thật:
 
```
Input:  "Liên hệ: John Doe"          (không có email)
Output: {"name": "John Doe", "email": "john.doe@example.com"}
                                      ↑ bịa, vì schema bắt buộc phải có
```
 
Giảm bằng cách để field `Optional` và ghi rõ trong system prompt không được bịa.
 
**Chỉ ép được kiểu, không ép được khoảng giá trị.** `rating: int` thì server chặn được chữ; còn `ge=1, le=5` là luật của Pydantic, server không đọc.
 
---
 
## Phần V — ToolStrategy
 
### 5.1 Cách nó chạy
 
Provider không cho đính schema thì LangChain lách: khai schema **thành một tool giả**, nhét vào trường `tools`.
 
```json
{
  "messages": [...],
  "tools": [{ "name": "ProductRating", "parameters": {...} }]   ← schema nằm ở đây
}
```
 
Model "gọi tool" đó — tham số nó điền vào **chính là kết quả**. Không có tool nào chạy thật. Vì vậy lịch sử hội thoại sẽ có một cặp tool call + `ToolMessage`.
 
Khác biệt lớn nhất: **không ai chặn model**. Nó tự viết, viết xong mới gửi về, LangChain kiểm sau:
 
```
Model tự viết  →  gửi về (1)  →  LangChain kiểm
                                      │
                            ┌─────────┴─────────┐
                          Đúng                 Sai
                            │                   │
                            ▼                   ▼
                  structured_response    Gửi lỗi về, bắt viết lại
                                                │
                                                └──→ quay lại (1)
```
 
Nhánh "Sai" là mục 5.4.
 
### 5.2 Tham số

```python
class ToolStrategy(Generic[SchemaT]):
    schema: type[SchemaT]
    tool_message_content: str | None
    handle_errors: Union[
        bool,
        str,
        type[Exception],
        tuple[type[Exception], ...],
        Callable[[Exception], str],
    ]
```

| Tham số | Bắt buộc | Mặc định | Làm gì |
|---|---|---|---|
| `schema` | Có | — | Khuôn dữ liệu. Ngoài bốn kiểu ở Phần III còn nhận `Union` |
| `tool_message_content` | Không | `None` | Đổi nội dung `ToolMessage` hiện trong lịch sử sau khi trả kết quả |
| `handle_errors` | Không | `True` | Xử lý lỗi thế nào khi model viết sai |


**`handle_errors`** quyết định có retry hay không: 
| Giá trị | Hành vi |
|---|---|
| `True` (mặc định) | Bắt mọi lỗi, dùng thông báo mặc định |
| `"chuỗi tùy ý"` | Bắt mọi lỗi, **luôn** dùng đúng thông báo này |
| `ValueError` | Chỉ retry đúng loại này, còn lại raise |
| `(ValueError, TypeError)` | Chỉ retry các loại trong tuple, còn lại raise |
| Hàm `(Exception) -> str` | Tự sinh thông báo theo từng loại lỗi |
| `False` | Không retry, raise hết |


**`tool_message_content`** — mặc định `ToolMessage` ghi `Returning structured response: {...}`, tức toàn bộ dữ liệu bị lặp lại trong lịch sử. Đổi thành câu ngắn để tiết kiệm context ở lượt sau:
 
```python
ToolStrategy(
    schema=MeetingAction,
    tool_message_content="Action item captured!",
)
```
 
Chỉ ảnh hưởng context model đọc ở lượt sau, không đụng tới `structured_response`.
 
### 5.3 Union type — chỉ ToolStrategy có
 
Đưa nhiều schema, model tự chọn cái hợp với input:
 
```python
ToolStrategy(Union[ProductReview, CustomerComplaint])
```
 
```
"Sản phẩm tốt, 5 sao, giao nhanh"           → ProductReview
"Hàng giao sai, báo 3 lần không ai xử lý"   → CustomerComplaint
```
 
Đổi lại, model dễ mắc lỗi gọi cả hai schema cùng lú.
 
### 5.4 Xử lý lỗi
 
Model viết sai thì agent **không raise ngay**. Nó nhét thông báo lỗi vào một `ToolMessage` rồi gọi model lại — model đọc được mình sai ở đâu và tự sửa:
 
```
AI  → ProductRating(rating=10, comment="Amazing product")
Tool→ Error: Input should be less than or equal to 5. Please fix your mistakes.
AI  → ProductRating(rating=5,  comment="Amazing product")
Tool→ Returning structured response: {'rating': 5, ...}
```
 
Hai loại lỗi được xử lý:
 
| Lỗi | Khi nào |
|---|---|
| `StructuredOutputValidationError` | Dữ liệu không khớp schema — như `rating=10` ở trên |
| `MultipleStructuredOutputsError` | Model gọi nhiều schema cùng lúc trong khi chỉ được một. Hay gặp khi dùng `Union` |

 
```python
def custom_error_handler(error: Exception) -> str:
    if isinstance(error, StructuredOutputValidationError):
        return "Sai định dạng, viết lại."
    if isinstance(error, MultipleStructuredOutputsError):
        return "Chỉ được chọn một schema."
    return f"Error: {error}"
```
 
---
 
## Phần VI — Đối chiếu hai chiến lược
 
Cùng schema `ProductRating` ở Phần III, cùng input `"Amazing product, 10/10!"`.
 
**ProviderStrategy**
 
```
Request:  response_format: {rating: integer, comment: string}
 
Model viết:  {"rating": 10, "comment": "Amazing product"}
                        ↑
              kiểu int → hợp lệ, server cho qua
              ge=1, le=5 là luật Pydantic → server không đọc
 
Kết quả:  rating=10  ⚠️ sai luật nghiệp vụ, nhưng lọt
Gọi model: 1 lần
```
 
**ToolStrategy**
 
```
Request:  tools: [ProductRating]
 
Lượt 1:  AI  → ProductRating(rating=10, comment="Amazing product")
         Tool→ Error: Input should be less than or equal to 5.
 
Lượt 2:  AI  → ProductRating(rating=5, comment="Amazing product")
         Tool→ Returning structured response: {'rating': 5, ...}
 
Kết quả:  rating=5  ✓
Gọi model: 2 lần, tốn gấp đôi token
```
 
| | ProviderStrategy | ToolStrategy |
|---|---|---|
| Schema nhét vào trường | Trường schema riêng của provider | `tools` |
| Ai kiểm | Server, ngay lúc model đang viết | LangChain, sau khi model viết xong |
| Ép được | Khuôn JSON + kiểu dữ liệu | Toàn bộ luật Pydantic |
| Số lần gọi model | 1 | 1, hoặc hơn nếu sai |
| Union type | Không | Có |
| Dùng được với | GPT, Claude, Gemini, Grok | Mọi model biết gọi tool |
 
### Chọn cái nào
 
Mặc định để LangChain tự chọn. Chỉ viết tên chiến lược ra khi:
 
| Viết tường minh | Khi cần |
|---|---|
| `ToolStrategy(...)` | Union type, hoặc schema có ràng buộc nghiệp vụ (`ge`, `le`, custom validator) |
| `ProviderStrategy(...)` | Bật `strict=True` |
 
`ProviderStrategy` nhanh và chắc hơn, nhưng **không tự bật lên được** — provider không hỗ trợ thì ép cũng rơi về `ToolStrategy`.