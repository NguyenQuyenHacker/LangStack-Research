---
title: Long-term memory
doc_source: https://docs.langchain.com/oss/python/langchain/long-term-memory
accessed: 2026-07-25
lc_version: unknown
status: draft
lab:
related:
  - ./memory.md
  - ./short-term-memory.md
---

# Long-term memory (`store`)

> Trí nhớ sống qua nhiều cuộc hội thoại và nhiều phiên: gọi lại được từ thread bất kỳ, khác short-term ở chỗ short-term chỉ trong một thread.
> Vì sao có hai loại và ba kiểu trí nhớ (semantic / episodic / procedural) — xem [memory](./memory.md). Nhớ trong một thread — xem [short-term-memory](./short-term-memory.md).

---

## 1. Tổng quan

Long-term memory cho agent lưu và gọi lại thông tin xuyên nhiều cuộc hội thoại và phiên. Khác short-term (bó trong một thread), long-term tồn tại qua các thread và gọi lại được bất cứ lúc nào.

Nền của nó là *LangGraph store* — nơi lưu dữ liệu dưới dạng tài liệu JSON, sắp theo `namespace` và `key`.

```python
from langchain.agents import create_agent
from langchain_core.runnables import Runnable
from langgraph.store.memory import InMemoryStore              # store lưu trong RAM, dùng để thử

# InMemoryStore lưu vào dict trong bộ nhớ. Production dùng store gắn DB.
store = InMemoryStore()

agent: Runnable = create_agent(
    "claude-sonnet-4-6",
    tools=[],
    store=store,                                              # bật long-term memory bằng cách gắn store
)
```

Bản production đổi `InMemoryStore` thành `PostgresStore`, gói `langgraph-checkpoint-postgres`, và bọc trong `with PostgresStore.from_conn_string(DB_URI) as store:` kèm `store.setup()`.

Sau khi gắn store, tool đọc và ghi store qua tham số `runtime.store` — xem [mục 4](#4-đọc-store-trong-tool) và [mục 5](#5-ghi-store-từ-tool).

**Quan hệ với short-term.** Đối chiếu trực tiếp: short-term gắn `checkpointer=`, dữ liệu vào **state** của thread, chết theo thread. Long-term gắn `store=`, dữ liệu vào **store**, sống qua mọi thread. Một agent gắn được cả hai cùng lúc.

---

## 2. Ba kiểu trí nhớ và cách ghi — trỏ sang trang khái niệm

Trang này chỉ nói *cách làm* (dựng store, đọc, ghi). Câu hỏi "nên lưu kiểu semantic / episodic / procedural nào", "ghi hot path hay background" thuộc trang khái niệm.

→ [memory §Ba kiểu trí nhớ](./memory.md#4-ba-kiểu-trí-nhớ) và [memory §Hai thời điểm ghi](./memory.md#6-hai-thời-điểm-ghi-trí-nhớ).

---

## 3. Lưu trữ long-term — namespace và key

**Khái niệm.** Mỗi trí nhớ là một tài liệu JSON, nằm dưới một `namespace` tự đặt (giống thư mục) và một `key` riêng (giống tên file). `namespace` là một tuple, hay gắn ID người dùng hoặc tổ chức để dễ tổ chức theo tầng. Tìm chéo giữa các namespace làm được qua bộ lọc nội dung.

**Vai trò.** Cho phép sắp xếp trí nhớ theo tầng (ví dụ mỗi người dùng một nhánh) và tìm lại theo cả nội dung lẫn độ tương đồng nghĩa.

**Triển khai.** Ba thao tác gốc: `put` (ghi), `get` (lấy theo key), `search` (tìm trong namespace):

```python
from collections.abc import Sequence
from langgraph.store.base import IndexConfig
from langgraph.store.memory import InMemoryStore

def embed(texts: Sequence[str]) -> list[list[float]]:
    # Thay bằng hàm embedding thật hoặc đối tượng embeddings của LangChain
    return [[1.0, 2.0] for _ in texts]

store = InMemoryStore(index=IndexConfig(embed=embed, dims=2))  # index bật tìm theo nghĩa; dims = số chiều vector
user_id = "my-user"
application_context = "chitchat"
namespace = (user_id, application_context)                    # namespace là tuple, ở đây gồm 2 tầng

store.put(
    namespace,
    "a-memory",                                               # key trong namespace
    {
        "rules": [
            "User likes short, direct language",
            "User only speaks English & python",
        ],
        "my-key": "my-value",
    },
)

item = store.get(namespace, "a-memory")                       # lấy đúng trí nhớ theo key

items = store.search(                                         # tìm trong namespace
    namespace,
    filter={"my-key": "my-value"},                            # lọc theo nội dung khớp cứng
    query="language preferences",                             # xếp thứ tự theo độ tương đồng nghĩa với câu này
)
```

---

## 4. Đọc store trong tool

**Khái niệm.** Trong tool, đọc store qua `runtime.store`. Đây là chính cái store đã truyền cho `create_agent`.

**Vai trò.** Tool lấy dữ liệu đã lưu từ những phiên trước (ví dụ tên người dùng đã ghi từ lần trước) để dùng cho lượt hiện tại.

**Triển khai.** Ghi sẵn dữ liệu mẫu vào store trước, rồi tool đọc ra theo `user_id`:

```python
from dataclasses import dataclass
from langchain.agents import create_agent
from langchain.tools import ToolRuntime, tool
from langchain_core.runnables import Runnable
from langgraph.store.memory import InMemoryStore

@dataclass
class Context:
    user_id: str

store = InMemoryStore()
store.put(                                                    # nạp sẵn một người dùng vào store
    ("users",),                                              # namespace "users" gom dữ liệu người dùng
    "user_123",                                              # key là chính user ID
    {"name": "John Smith", "language": "English"},
)

@tool
def get_user_info(runtime: ToolRuntime[Context]) -> str:
    """Look up user info."""
    assert runtime.store is not None
    user_id = runtime.context.user_id                        # user_id lấy từ context
    user_info = runtime.store.get(("users",), user_id)       # get trả về đối tượng có .value và metadata
    return str(user_info.value) if user_info else "Unknown user"  # .value là phần dữ liệu đã lưu

agent: Runnable = create_agent(
    model="claude-sonnet-4-6",
    tools=[get_user_info],
    store=store,                                             # truyền store để tool chạm được qua runtime.store
    context_schema=Context,
)

agent.invoke(
    {"messages": [{"role": "user", "content": "look up user information"}]},
    context=Context(user_id="user_123"),
)
```

---

## 5. Ghi store từ tool

**Khái niệm.** Tool ghi vào store bằng `runtime.store.put(namespace, key, data)`. Khác với ghi state trong short-term (trả `Command`), ghi store là gọi thẳng `put`.

**Vai trò.** Lưu thông tin để dùng lại ở phiên sau — ví dụ chat app cho phép agent cập nhật hồ sơ người dùng khi họ khai thêm.

**Triển khai.** `UserInfo` là `TypedDict` mô tả cấu trúc dữ liệu cho model điền; tool nhận rồi `put` vào store:

```python
from dataclasses import dataclass
from langchain.agents import create_agent
from langchain.tools import ToolRuntime, tool
from langchain_core.runnables import Runnable
from langgraph.store.memory import InMemoryStore
from typing_extensions import TypedDict

store = InMemoryStore()

@dataclass
class Context:
    user_id: str

class UserInfo(TypedDict):                                    # khai cấu trúc để model biết cần điền field nào
    name: str

@tool
def save_user_info(user_info: UserInfo, runtime: ToolRuntime[Context]) -> str:
    """Save user info."""
    assert runtime.store is not None
    store = runtime.store
    user_id = runtime.context.user_id
    store.put(("users",), user_id, dict(user_info))          # ghi vào store: (namespace, key, data)
    return "Successfully saved user info."

agent: Runnable = create_agent(
    model="claude-sonnet-4-6",
    tools=[save_user_info],
    store=store,
    context_schema=Context,
)

agent.invoke(
    {"messages": [{"role": "user", "content": "My name is John Smith"}]},
    context=Context(user_id="user_123"),                     # user_id xác định đang cập nhật hồ sơ của ai
)

item = store.get(("users",), "user_123")                     # đọc thẳng từ store để kiểm chứng đã ghi
```

---

## 6. Đối chiếu short-term và long-term

| | Short-term | Long-term |
|---|---|---|
| Gắn vào agent bằng | `checkpointer=` | `store=` |
| Dữ liệu nằm ở | State của thread | Store, theo namespace/key |
| Phạm vi nhớ lại | Một thread | Mọi thread, mọi phiên |
| Đọc trong tool | `runtime.state[...]` | `runtime.store.get(...)` |
| Ghi từ tool | Trả `Command(update=...)` | Gọi `runtime.store.put(...)` |
| Bản thử / production | `InMemorySaver` / `PostgresSaver` | `InMemoryStore` / `PostgresStore` |

### Chọn cái nào

Chọn **short-term** khi: chỉ cần nhớ trong mạch của cuộc hội thoại đang diễn ra (lịch sử tin nhắn, kết quả trung gian trong lượt). Hết thread là quên cũng không sao.

Chọn **long-term** khi: cần nhớ xuyên cuộc — hồ sơ người dùng, sở thích, những gì agent đã học qua nhiều phiên.

Hai cái không loại trừ nhau: một agent gắn cả `checkpointer=` lẫn `store=` để vừa giữ mạch cuộc hiện tại vừa nhớ dài hạn.

---

## 7. Tham chiếu chéo

- [memory](./memory.md) — ba kiểu trí nhớ dài hạn và hai thời điểm ghi; phần "tại sao" mà trang này không bàn.
- [short-term-memory](./short-term-memory.md) — đối chiếu trực tiếp: bên đó dữ liệu vào **state**, ở đây vào **store**.
- Trang tài liệu khác được nêu tên trong nguồn (chưa nghiên cứu ở đây): LangGraph stores (`/oss/python/langgraph/stores`), Persistence.