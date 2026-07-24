---
title: Messages
doc_source: https://docs.langchain.com/oss/python/langchain/messages
accessed: 2026-07-22
lc_version: "1.x (content_blocks có từ v1)"
status: draft
lab:
---

# Messages



---

## Phần I — Khái niệm

### Message là gì

Message là **đơn vị context** của model. Không phải "định dạng chat" mà là toàn bộ trạng thái hội thoại được vật chất hóa thành dữ liệu.

Model **stateless**: nó không nhớ gì giữa hai lần gọi. Mọi thứ nó biết tại thời điểm suy luận đều nằm trong list message mình gửi lên. Cái gọi là "trí nhớ hội thoại" chỉ là mình gửi lại lịch sử mỗi lần.

> **Một message = Role + Content + Metadata**

| Thành phần | Trả lời câu hỏi | Đào sâu ở |
|---|---|---|
| **Role** | Ai nói? | Phần III |
| **Content** | Nói cái gì? | Phần IV |
| **Metadata** | Kèm thông tin gì? | Phần V |

---

## Phần II — Khung vận hành

Trước khi bóc từng loại message, cần thấy chúng xuất hiện lúc nào. Một lượt hội thoại có tool đi qua bốn nhịp:

```
[SystemMessage, HumanMessage]              ← prompt + systemprompt
        ↓ invoke
AIMessage(tool_calls=[...])                ← model đề nghị gọi tool
        ↓ mình chạy tool
ToolMessage(tool_call_id khớp)             ← trả kết quả về
        ↓ invoke lại (list đã nối dài)
AIMessage(text)                            ← câu trả lời cuối
```


## Phần III — Role: bốn loại message

| Loại | Vai trò |
|---|---|
| `SystemMessage` | Đây là Systemprompt: vai trò, tone, ràng buộc hành vi cho AI|
| `HumanMessage` | Input người dùng, chứa được multimodal |
| `AIMessage` | Output model: text, tool call, reasoning, metadata |
| `ToolMessage` | Kết quả của **một** lần thực thi tool |

### 3.1 SystemMessage
 
Lời hướng dẫn từ "hệ thống" đặt ra (Ví dụ: "Bạn là chuyên gia về Python").
Đây chính là system prompt

### 3.2 HumanMessage

Nội dung gồm 
- `content`: nội dung input từ người dùng
- `name`: phân biệt nhiều người dùng
- `id`: để truy vết

### 3.3 AIMessage

Do model sinh ra. 

```python
messages = [
    SystemMessage("..."),
    HumanMessage("Can you help me?"),
    AIMessage("Chắc chắn rồi, đây là..."), 
    HumanMessage("What's 2+2?"),
]
```

Các trường của `AIMessage`:

| Trường | Nội dung |   
|---|---| 
| `text` | Phần text thuần, đã trích sẵn | 
| `content` | Payload thô theo format provider |
| `content_blocks` | Bản chuẩn hóa của `content` |
| `tool_calls` | Tool model muốn gọi; rỗng nếu không có |
| `usage_metadata` | Token counts + phân rã |
| `response_metadata` | Thông tin provider trả về | 
| `id` | Định danh message | 

**Streaming:** `stream()` trả `AIMessageChunk` chứ không phải `AIMessage`. Chunk cộng dồn bằng `+`, kết quả tương đương một message hoàn chỉnh.

### 3.4 ToolMessage

Mang kết quả của **đúng một** lần chạy tool trở về.

| Trường | Ghi chú |
|---|---|
| `content` | Kết quả đã stringify, là input để model đọc cái này |
| `tool_call_id` | Phải khớp `id` trong `tool_calls` của `AIMessage` |
| `name` | Tên tool |
| `artifact` | Dữ liệu bổ sung không được gửi đến mô hình nhưng có thể được truy cập thông qua lập trình. |

```python
ToolMessage(
    content="It was the best of times...",
    tool_call_id="call_123",                            
    name="search_books",
    artifact={"document_id": "doc_123", "page": 0},     
)
```

---

## Phần IV — Content

### 4.1 Content là gì

Content là **phần dữ liệu** của message — thứ được gửi lên model.

Có hai dạng:

```python
# Dạng 1: một chuỗi
HumanMessage("Hello, how are you?")

# Dạng 2: một list nhiều mảnh, mỗi mảnh gọi là một block
content = [
    {"type": "text",  "text": "Mô tả ảnh này giúp tôi"},
    {"type": "image", "url": "https://.../a.jpg"},
]
```

Mỗi block có `type` cho biết nó là loại gì. Nhớ được "content có thể là một **list block**" là nắm được phần lớn mục này.

### 4.2 `content_blocks`

Mỗi provider đặt tên block một kiểu. Cùng là "suy luận", Anthropic gọi `thinking`, OpenAI gọi `reasoning`. Code đọc thẳng `content` sẽ phải sửa mỗi lần đổi model.

> `content_blocks` là thuộc tính giúp các khối nội dung được **chuyển sang một chuẩn chung**:

```python
message.content         # {"type": "thinking",  "thinking": "..."}    ← Anthropic viết vậy
message.content_blocks  # {"type": "reasoning", "reasoning": "..."}   ← dịch ra chuẩn chung
```

Dữ liệu vẫn nằm nguyên trong `content`. `content_blocks` chỉ đọc lại rồi dịch ra khi mình gọi tới. Chi tiết riêng của provider không mất — dồn vào `extras`.

| | `content` | `content_blocks` |
|---|---|---|
| Là gì | Dữ liệu gốc, lưu thật | Bản dịch của dữ liệu đó |
| Format | Theo từng provider | Chuẩn chung LangChain |
| Dùng khi | Cần đúng cấu trúc gốc | Muốn code chạy với mọi provider |

### 4.3 Danh mục block

| Nhóm | Block | Ghi chú |
|---|---|---|
| Core | `text`, `reasoning` | `text` có `annotations` cho citation |
| Multimodal | `image`, `audio`, `video`, `file`, `text-plain` | Xem 4.4 |
| Tool calling | `tool_call`, `tool_call_chunk`, `invalid_tool_call` | `tool_call_chunk` là mảnh vụn khi stream |
| Server-side tool | `server_tool_call`, `server_tool_call_chunk`, `server_tool_result` | Provider tự chạy, không sinh `ToolMessage` |
| Dự phòng | `non_standard` | Bọc cấu trúc provider chưa được chuẩn hóa |

`invalid_tool_call` tồn tại vì model **có thể sinh JSON hỏng**. Nên kiểm trường này thay vì mặc định `tool_calls` luôn đúng.

### 4.4 Multimodal

Ảnh, audio, video, file đều là một block trong list `content`. Ba cách chỉ nguồn:

```python
{"type": "image", "url": "https://.../a.jpg"}                      # file public
{"type": "image", "base64": "AAAA...", "mime_type": "image/jpeg"}  # file cục bộ
{"type": "image", "file_id": "file-abc123"}                        # đã upload lên provider
```

`base64` bắt buộc kèm `mime_type`, tốn token và vướng giới hạn dung lượng. `file_id` rẻ nhất khi một file dùng lại nhiều lần.