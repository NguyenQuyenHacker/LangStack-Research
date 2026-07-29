---
title: Store
doc_source: https://docs.langchain.com/oss/python/langgraph/stores
accessed: 2026-07-28
lc_version: unknown
status: draft
lab:
related:
  - ./02-02-checkpointers.md
  - ./02-04-add-memory.md
---

# Store (`BaseStore`)

> Bộ nhớ dài hạn chạy **xuyên qua nhiều thread** của LangGraph — nơi cất những thứ phải sống sót sau khi cuộc hội thoại kết thúc.
> Đi cặp với checkpointer nhưng lo một việc khác hẳn: xem [02-02 Checkpointers](./02-02-checkpointers.md).

---

## 1. Tổng quan

**Khái niệm** : Store là kho key-value cho agent lưu thông tin **truy được từ bất kỳ thread nào** — sở thích người dùng, kiến thức tích lũy, những dữ kiện không nên chết theo một cuộc hội thoại.

Đặt cạnh checkpointer [02-02 Checkpointers](./02-02-checkpointers.md): checkpointer lưu **toàn bộ state của graph, đóng khung trong một thread**; store giữ dữ liệu tùy ý, tra được từ mọi thread. Mở một thread mới với cùng người dùng thì checkpointer cho ta một tờ giấy trắng, còn store vẫn nhớ.

---

## 2. Namespace, key, value

Store lưu từng item. Mỗi item có ba phần: **namespace** (nhóm nó thuộc về), **key** (định danh riêng trong nhóm), **value** (nội dung, là một dict).

```python
namespace = ("1", "memories")  # nhóm item thuộc về
key = str(uuid.uuid4())          # định danh riêng trong nhóm
value = {"food_preference": "I like pizza"} # nội dung
```

---

## 3. Ba thao tác cơ bản — `put`, `search`, và cấu trúc `Item`

**Ghi.** `store.put` nhận namespace, key, value:

```python
memory_id = str(uuid.uuid4())                       # key: định danh duy nhất
memory = {"food_preference": "I like pizza"}        # value: dict nội dung
store.put(namespace_for_memory, memory_id, memory)  # ghi vào đúng namespace
```

**Đọc.** `store.search`.

```python
memories = store.search(namespace_for_memory)   # lấy toàn bộ ký ức trong namespace
memories[-1].dict()                             # [-1] lấy mẩu mới nhất; .dict() đổi Item -> dict
```

**Kết quả in ra:**

```
{'value': {'food_preference': 'I like pizza'},                  ← nội dung ta đã ghi
 'key': '07e0caf4-1631-47b7-b15f-65515d4c1843',                 ← uuid đã sinh ở trên
 'namespace': ['1', 'memories'],                                ← tuple bị serialize thành list
 'created_at': '2024-10-02T17:22:31.590602+00:00',              ← dấu thời gian lúc tạo
 'updated_at': '2024-10-02T17:22:31.590605+00:00'}              ← lúc cập nhật gần nhất
```

---
## 4. Các phần tìm hiểu thêm
 
Ba mục trên đủ để dùng store cho phần lớn trường hợp. Bốn chủ đề còn lại chỉ cần khi gặp đúng nhu cầu — tôi nêu ở đây để biết chúng tồn tại, chi tiết xem tài liệu gốc.
 
**Liệt kê item / namespace.** `store.search` không kèm `query` sẽ trả về mọi item dưới một namespace; `store.list_namespaces` liệt kê các namespace đang tồn tại. Cần khi duyệt sạch một nhóm. Ba chỗ dễ sai lặng lẽ: namespace khớp theo **tiền tố** (không chính xác), vượt `limit` bị **cắt không báo**, và **thứ tự tùy backend** (Postgres theo `updated_at`, InMemory theo thứ tự chèn).
 
**Tìm theo nghĩa (semantic search).** Tìm item theo ý nghĩa thay vì khớp chữ, phải cấu hình một model embedding cho store. Cần khi câu hỏi và nội dung lưu cùng ý nhưng không trùng từ. Xem [mục Semantic search của doc](https://docs.langchain.com/oss/python/langgraph/stores#semantic-search).
 
**Dùng trong LangGraph.** Gắn store vào graph lúc `compile`, rồi lấy ra trong node qua đối tượng `Runtime` để đọc/ghi item theo `user_id`. Cần khi ráp store vào agent thật. Cách dựng bộ nhớ hoàn chỉnh ở [Add memory](https://docs.langchain.com/oss/python/langgraph/add-memory).
 
**Tự viết store riêng (`BaseStore`).** Kế thừa `BaseStore` khi cần backend ngoài các bản dựng sẵn (`Postgres`/`Mongo`/`Redis`). Dùng được bản dựng sẵn thì bỏ qua hoàn toàn. Xem [mục Build a custom store](https://docs.langchain.com/oss/python/langgraph/stores#build-a-custom-store).
 
---

## Tham chiếu chéo

- [02-02 Checkpointers](./02-02-checkpointers.md) — persistence theo thread; store bù phần xuyên-thread cho nó
- [02-04 Add memory](./02-04-add-memory.md) — dùng store để dựng bộ nhớ dài hạn cho agent
- Trang tài liệu gốc: https://docs.langchain.com/oss/python/langgraph/stores