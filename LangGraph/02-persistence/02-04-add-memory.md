---
title: Nối trí nhớ vào graph
doc_source: https://docs.langchain.com/oss/python/langgraph/add-memory
accessed: 2026-07-29
lc_version: unknown
status: draft
lab:
related:
  - ./02-02-checkpointers.md
  - ./02-03-stores.md
---

# Nối trí nhớ vào graph

> Cơ chế bên dưới đã có ở [02-02 Checkpointers](./02-02-checkpointers.md) và [02-03 Stores](./02-03-stores.md); file này lo phần vận hành.

---

## 1. Hai loại trí nhớ

LangGraph chia trí nhớ làm hai, mỗi loại tựa lên một thành phần đã có file riêng:

| | Trí nhớ ngắn hạn | Trí nhớ dài hạn |
|---|---|---|
| Khái niệm | Lịch sử của **một** hội thoại | Dữ liệu sống **xuyên** các hội thoại |
| Chạy bằng | Checkpointer | Store |
| Phạm vi | Một thread | Mọi thread cùng một user |
| Định vị bằng | `thread_id` | `namespace` + `key` |
| Xem chi tiết | [02-02](./02-02-checkpointers.md) | [02-03](./02-03-stores.md) |

Gắn checkpointer thì agent nhớ trong thread; gắn store thì nhớ xuyên thread. Phần đáng đọc riêng của trang này không phải cách gắn (đã ở hai file kia), mà là **cách quản lý trí nhớ ngắn hạn** ở mục 3.

---

## 2. Gắn vào graph — tóm tắt

**Ngắn hạn:** compile graph với `checkpointer`, rồi invoke kèm `thread_id`.

```python
graph = builder.compile(checkpointer=InMemorySaver())
graph.invoke({"messages": [...]}, {"configurable": {"thread_id": "1"}})
```

**Dài hạn:** compile với `store`, đọc/ghi item trong node qua `runtime.store` (chi tiết `Runtime` ở [02-03](./02-03-stores.md)).

**Production:** thay bản `InMemory` bằng backend có cơ sở dữ liệu — `PostgresSaver`/`PostgresStore`, Redis, MongoDB, Oracle. Mỗi backend nạp bằng `from_conn_string(DB_URI)`. Lần đầu phải chạy `setup()` để tạo schema (xem mục 5).

---

## 3. Quản lý trí nhớ ngắn hạn — giữ hội thoại trong context window

### 3.1 Trim — cắt bớt theo số token

**Khái niệm:** đếm token của lịch sử rồi cắt để phần giữ lại nằm trong hạn mức.

**Kết quả:** model vẫn trả lời đúng nếu ngữ cảnh cần thiết còn trong cửa sổ giữ lại. Ví dụ hỏi "what's my name?" vẫn ra "Your name is Bob" khi tin giới thiệu tên chưa bị cắt.

**Đánh đổi:** cắt cứng theo token — thông tin nằm ngoài cửa sổ mất luôn.

### 3.2 Delete — xóa hẳn tin nhắn khỏi state

**Khái niệm:** bỏ hẳn tin nhắn khỏi lịch sử (khác trim: trim chỉ lọc lúc gọi model, tin gốc vẫn còn trong state).

**Kết quả:** chuỗi `messages` co lại vĩnh viễn — xóa hai tin đầu thì các lượt sau chỉ còn lịch sử từ tin thứ ba trở đi.

**!Note:** sau khi xóa, chuỗi còn lại phải **hợp lệ** với provider. Nhiều provider bắt buộc mở đầu bằng tin `user`, và mỗi tin `assistant` có gọi tool phải kèm tin `tool` kết quả theo sau. Xóa ẩu làm gãy ràng buộc này thì API báo lỗi.

### 3.3 Summarize — tóm tắt lịch sử cũ

**Khái niệm:** thay vì vứt tin cũ, nén chúng thành một đoạn tóm tắt rồi giữ đoạn đó lại.

**Kết quả:** giữ được cả thông tin cũ (dưới dạng tóm tắt) lẫn context window gọn. Model vẫn nhớ "Bob" qua đoạn summary dù các tin gốc đã bị xóa.

**Đánh đổi:** tốn thêm một lời gọi model cho việc tóm tắt.

### So sánh ba cách

| Cách | Giữ được | Mất | Chi phí |
|---|---|---|---|
| Trim | Tin trong hạn mức token | Tin ngoài cửa sổ | Rẻ |
| Delete | Tin ta chọn giữ | Tin đã xóa | Rẻ |
| Summarize | Ý chính toàn bộ lịch sử | Chi tiết nguyên văn | Thêm 1 lần gọi model |

---

## 4. Xem và xóa checkpoint

`graph.get_state(config)` cho snapshot mới nhất của thread; `graph.get_state_history(config)` cho cả lịch sử. Cấu trúc `StateSnapshot` chi tiết ở [02-02](./02-02-checkpointers.md).

Xóa toàn bộ checkpoint của một thread: `checkpointer.delete_thread(thread_id)`.

---

## 5. Database management

Backend có cơ sở dữ liệu (Postgres, Redis, Oracle...) phải chạy **migration tạo schema** trước khi dùng. Theo quy ước, gọi `setup()` trên instance checkpointer hoặc store ở lần đầu tiên. Tên method có thể khác tùy bản cài — đối chiếu `BaseCheckpointSaver`/`BaseStore` của backend đang dùng.

Nên chạy migration như một bước deploy riêng, hoặc chèn vào lúc server khởi động.

---

## Tham chiếu chéo

- [02-02 Checkpointers](./02-02-checkpointers.md) — cơ chế checkpointer đứng sau trí nhớ ngắn hạn
- [02-03 Stores](./02-03-stores.md) — store đứng sau trí nhớ dài hạn
- Trang tài liệu gốc: https://docs.langchain.com/oss/python/langgraph/add-memory