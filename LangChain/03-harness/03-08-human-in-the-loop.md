---
title: Human-in-the-loop
doc_source: https://docs.langchain.com/oss/python/langchain/human-in-the-loop
accessed: 2026-07-25
version: "unknown"
status: draft
lab:
related:
  - ./guardrails.md
  - ./middleware.md
  - ./streaming.md
---

# Human-in-the-loop — chặn agent chờ người duyệt (`HumanInTheLoopMiddleware`)

> HITL middleware chèn một chốt duyệt của con người vào lời gọi tool của agent: khi model định làm một việc rủi ro, middleware dừng agent lại và chờ quyết định.
> Đây là bản chi tiết của guardrail đã nêu tóm tắt ở [guardrails.md](./guardrails.md#4-human-in-the-loop).

---

## 1. Tổng quan

`HumanInTheLoopMiddleware` (viết tắt HITL — Human-in-the-Loop) là middleware kiểm từng lời gọi tool của model trước khi tool chạy. Nếu lời gọi khớp một quy tắc mình đặt, middleware phát ra một **interrupt** (tín hiệu dừng) làm agent ngừng lại, lưu trạng thái, và chờ người quyết.

Khác với việc để agent tự chạy hết: HITL biến những thao tác không hoàn tác được — xóa dữ liệu, gửi thư ra ngoài, chạy SQL — thành thao tác có người gác cổng.

Vòng chạy gồm ba nhịp: agent chạy tới chỗ cần duyệt thì **dừng**, người đưa **quyết định**, agent **chạy tiếp** theo quyết định đó. Trạng thái được lưu bằng lớp lưu trữ (persistence) của LangGraph nên dừng bao lâu cũng nối lại được. Cơ chế lưu trữ và bản thân interrupt nằm ở trang khác — trang này chỉ dùng, không giải thích cơ chế.

Người quyết có bốn lựa chọn: duyệt nguyên (`approve`), sửa rồi mới chạy (`edit`), từ chối kèm lý do (`reject`), hoặc trả lời thẳng (`respond`) cho loại tool kiểu "hỏi người dùng".

---

## 2. Bốn loại quyết định

### Khái niệm

Bốn cách một người phản hồi lại một interrupt. Đây là trục chính của cả trang — chọn đúng loại quyết định mới xử lý đúng tình huống.

| Loại | Làm gì | Ví dụ |
|---|---|---|
| `approve` | Duyệt nguyên, chạy tool không đổi gì | Gửi email đúng như bản nháp |
| `edit` | Sửa lời gọi tool rồi mới chạy | Đổi người nhận trước khi gửi email |
| `reject` | Từ chối, thêm lời giải thích vào hội thoại | Bác bản nháp email, chỉ cách viết lại |
| `respond` | Bỏ qua việc chạy tool, câu người trả lời trở thành kết quả tool | Trả lời một tool kiểu `ask_user` |

### Vai trò

Bốn loại phủ bốn tình huống khác nhau khi soát một hành động. `approve` cho việc đúng rồi. `edit` cho việc gần đúng, chỉ sai tham số. `reject` cho việc sai hẳn, cần model làm lại. `respond` cho loại tool mà lời người trả *chính là* kết quả — không có việc gì để chạy.

Loại quyết định nào được phép cho mỗi tool phụ thuộc quy tắc khai trong `interrupt_on` (mục 3). Khi nhiều lời gọi tool bị dừng cùng lúc, mỗi hành động cần một quyết định riêng, và các quyết định phải xếp **đúng thứ tự** như trong yêu cầu duyệt.

**!Note:** Khi dùng `edit`, sửa dè dặt. Sửa mạnh tham số gốc có thể khiến model xét lại toàn bộ cách tiếp cận, chạy tool nhiều lần hoặc làm việc ngoài dự tính — lỗi im lặng, không báo gì nhưng hành vi lệch.

---

## 3. Cấu hình interrupt — khai tool nào cần duyệt (`interrupt_on`)

### Khái niệm

`interrupt_on` là một dict ánh xạ tên tool sang loại quyết định được phép cho tool đó. Middleware dừng agent khi một lời gọi tool khớp một mục trong ánh xạ này.

### Vai trò

Đây là nơi phân loại tool theo mức rủi ro: cái nào phải duyệt, cái nào duyệt kiểu gì, cái nào cho chạy thẳng. Không khai đúng ở đây thì hoặc agent dừng cả ở việc vô hại, hoặc bỏ lọt việc nguy hiểm.

### Áp dụng thực tế

Agent nghiệp vụ có ba tool: `write_file` (ghi hồ sơ), `execute_sql` (chạy truy vấn lên cơ sở dữ liệu giao dịch), `read_data` (đọc số liệu). Đọc số liệu thì cho chạy thẳng. Ghi hồ sơ thì cho duyệt đủ kiểu. Chạy SQL thì chỉ cho duyệt hoặc từ chối — cấm sửa tay câu lệnh để tránh chỉnh nhầm thành lệnh xóa.

### Triển khai

```python
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver

agent = create_agent(
    model="gpt-5.4",
    tools=[write_file, execute_sql, read_data],
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "write_file": True,                                        # True = dừng, cho phép cả 4 loại quyết định
                "execute_sql": {"allowed_decisions": ["approve", "reject"]},  # chỉ cho duyệt hoặc từ chối, cấm sửa tay
                "read_data": False,                                        # False = việc an toàn, cho chạy thẳng không duyệt
            },
            description_prefix="Tool execution pending approval",          # tiền tố ghép vào mô tả yêu cầu duyệt
        ),
    ],
    checkpointer=InMemorySaver(),                                          # bắt buộc: nơi lưu trạng thái giữa các lần dừng
)
```

### Các tùy chọn cấu hình

| Tham số | Kiểu | Nghĩa | Mặc định |
|---|---|---|---|
| `interrupt_on` | dict | Ánh xạ tên tool sang cấu hình duyệt. Giá trị là `True` (dừng, cấu hình mặc định), `False` (cho chạy thẳng), hoặc một `InterruptOnConfig` | Bắt buộc |
| `description_prefix` | string | Tiền tố cho phần mô tả yêu cầu duyệt | `"Tool execution requires approval"` |

Bên trong một `InterruptOnConfig`:

| Tham số | Kiểu | Nghĩa |
|---|---|---|
| `allowed_decisions` | list[string] | Danh sách loại quyết định cho phép: `'approve'`, `'edit'`, `'reject'`, `'respond'` |
| `description` | string \| callable | Chuỗi cố định, hoặc một hàm sinh mô tả riêng |

Dùng `True` cho nhanh khi cho phép mọi loại quyết định. Dùng `InterruptOnConfig` khi cần siết loại quyết định cho từng tool, như cấm `edit` ở `execute_sql`.

**!Note:** Thiếu `checkpointer` thì HITL không hoạt động — không có nơi lưu trạng thái thì không dừng-rồi-chạy-tiếp được. `InMemorySaver` chỉ hợp cho thử nghiệm vì trạng thái mất khi tắt tiến trình; chạy thật phải dùng loại lưu bền như `AsyncPostgresSaver`. Cơ chế checkpointer nằm ở trang persistence, không thuộc trang này.

---

## 4. Nhận và trả lời interrupt

### Khái niệm

Khi gọi agent, nó chạy tới lúc xong hoặc tới lúc một lời gọi tool khớp quy tắc thì phát interrupt. Với `version="v2"`, kết quả trả về là một `GraphOutput` có thuộc tính `.interrupts` chứa các hành động cần soát. Lấy danh sách đó đưa cho người duyệt, rồi gọi lại agent với quyết định để chạy tiếp.

### Vai trò

Đây là chỗ code của mình lấy được "agent đang xin duyệt việc gì" để dựng màn hình cho người xem, và là chỗ gửi quyết định ngược vào để nối lại phiên.

### Triển khai

```python
from langgraph.types import Command

config = {"configurable": {"thread_id": "some_id"}}   # thread_id gắn phiên chạy với một luồng hội thoại để dừng/nối lại

result = agent.invoke(                                 # lần gọi 1: chạy tới interrupt thì dừng
    {"messages": [{"role": "user", "content": "Delete old records from the database"}]},
    config=config,
    version="v2",                                      # v2 mới cho ra GraphOutput có .interrupts
)

print(result.interrupts)                              # đọc danh sách hành động đang chờ duyệt
```

**Kết quả in ra** (chép từ tài liệu, đã rút gọn phần args):

```
(
   Interrupt(
      value={
         'action_requests': [                                    ← danh sách hành động chờ duyệt
            {
               'name': 'execute_sql',                            ← tên tool bị chặn
               'arguments': {'query': 'DELETE FROM records ...'}, ← tham số model định chạy
               'description': 'Tool execution pending approval...'← mô tả ghép từ description_prefix + tên tool + args
            }
         ],
         'review_configs': [                                      ← loại quyết định cho phép với hành động này
            {
               'action_name': 'execute_sql',
               'allowed_decisions': ['approve', 'reject']         ← khớp đúng cấu hình interrupt_on ở mục 3
            }
         ]
      }
   ),
)
```

Gửi quyết định để chạy tiếp:

```python
agent.invoke(
    Command(resume={"decisions": [{"type": "approve"}]}),   # gói quyết định trong Command(resume=...)
    config=config,                                          # cùng thread_id mới nối lại đúng phiên đang dừng
    version="v2",
)
```

**!Note:** Không truyền `version="v2"` thì kết quả không có hình dạng `GraphOutput.interrupts` như trên — trang tài liệu chỉ mô tả hành vi cho v2, các bản khác để ngỏ. Và `thread_id` ở lần gọi 2 phải trùng lần 1; sai thì không tìm ra phiên để nối.

### 4.1 `approve` — duyệt nguyên

Duyệt lời gọi tool y nguyên và chạy không đổi gì.

```python
agent.invoke(
    Command(
        resume={
            "decisions": [                    # mỗi hành động chờ duyệt một quyết định, xếp đúng thứ tự
                {"type": "approve"}
            ]
        }
    ),
    config=config,
    version="v2",
)
```

**Điều xảy ra:** tool được chạy đúng như model đề xuất.

### 4.2 `edit` — sửa rồi mới chạy

Sửa lời gọi tool trước khi chạy. Đưa hành động đã sửa kèm tên tool mới và tham số mới.

```python
agent.invoke(
    Command(
        resume={
            "decisions": [
                {
                    "type": "edit",
                    "edited_action": {                    # hành động thay thế cho hành động gốc
                        "name": "new_tool_name",          # tên tool để gọi, thường giữ nguyên như gốc
                        "args": {"key1": "new_value",     # tham số mới
                                 "key2": "original_value"},
                    }
                }
            ]
        }
    ),
    config=config,
    version="v2",
)
```

**Điều xảy ra:** tool chạy với tham số đã sửa thay vì tham số gốc.

**!Note:** Nhắc lại cảnh báo ở mục 2 vì đây là chỗ dễ vấp: sửa mạnh có thể khiến model chạy tool nhiều lần hoặc đổi hướng ngoài dự tính. Sửa tối thiểu, chỉ đúng phần cần đổi.

### 4.3 `reject` — từ chối kèm lý do

Từ chối lời gọi tool và đưa phản hồi thay vì chạy.

```python
agent.invoke(
    Command(
        resume={
            "decisions": [
                {
                    "type": "reject",
                    "message": "No, this is wrong because ..., instead do this ...",  # lý do từ chối, gửi lại cho model
                }
            ]
        }
    ),
    config=config,
    version="v2",
)
```

**Điều xảy ra:** tool không chạy. Câu trong `message` được thêm vào hội thoại làm phản hồi, giúp model hiểu vì sao bị bác và cần làm gì thay thế.

### 4.4 `respond` — lời người trả thành kết quả tool

Dùng cho tool kiểu "hỏi người dùng", nơi phần thực thi thật của tool chính là câu người trả. Tool không chạy; nội dung `message` được trả thẳng làm kết quả tool.

```python
agent.invoke(
    Command(
        resume={
            "decisions": [
                {
                    "type": "respond",
                    "message": "Blue.",          # câu người trả, trả thẳng làm kết quả tool
                }
            ]
        }
    ),
    config=config,
    version="v2",
)
```

**Điều xảy ra:** `message` được trả về cho agent như một `ToolMessage` thành công. Dùng `respond` khi tool cố tình chỉ là chỗ giữ chỗ cho đầu vào của người — ví dụ tool `ask_user` hỏi để làm rõ yêu cầu.

### 4.5 Nhiều quyết định cùng lúc

Khi nhiều hành động bị dừng cùng lúc, đưa mỗi hành động một quyết định, xếp đúng thứ tự như trong interrupt:

```python
{
    "decisions": [
        {"type": "approve"},                                   # hành động 1: duyệt
        {
            "type": "edit",                                    # hành động 2: sửa rồi chạy
            "edited_action": {
                "name": "tool_name",
                "args": {"param": "new_value"}
            }
        },
        {
            "type": "reject",                                  # hành động 3: từ chối
            "message": "This action is not allowed"
        }
    ]
}
```

**!Note:** Sai thứ tự quyết định so với thứ tự hành động thì quyết định gắn nhầm hành động — code chạy trơn nhưng duyệt nhầm việc. Đây là lỗi im lặng nguy hiểm nhất của phần này.

---

## 5. Stream cùng HITL — cập nhật thời gian thực

Dùng `stream()` thay `invoke()` để nhận cập nhật lúc agent đang chạy và đang xử lý interrupt. Đặt `stream_mode=['updates', 'messages']` với `version="v2"` để vừa nhận tiến độ agent vừa nhận mẩu chữ chảy dần của model trong cùng định dạng v2.

```python
from langgraph.types import Command

config = {"configurable": {"thread_id": "some_id"}}

for chunk in agent.stream(                              # chảy dần tiến độ và mẩu chữ tới khi gặp interrupt
    {"messages": [{"role": "user", "content": "Delete old records from the database"}]},
    config=config,
    stream_mode=["updates", "messages"],
    version="v2",
):
    if chunk["type"] == "messages":                     # nhánh mẩu chữ của model
        token, metadata = chunk["data"]
        if token.content:
            print(token.content, end="", flush=True)    # end="" để chữ nối liền, không xuống dòng
    elif chunk["type"] == "updates":                    # nhánh tiến độ agent
        if "__interrupt__" in chunk["data"]:            # phát hiện tín hiệu dừng
            print(f"\n\nInterrupt: {chunk['data']['__interrupt__']}")

for chunk in agent.stream(                              # sau khi có quyết định, chảy tiếp cũng bằng stream
    Command(resume={"decisions": [{"type": "approve"}]}),
    config=config,
    stream_mode=["updates", "messages"],
    version="v2",
):
    if chunk["type"] == "messages":
        token, metadata = chunk["data"]
        if token.content:
            print(token.content, end="", flush=True)
```

Chi tiết các chế độ stream nằm ở [streaming.md](./streaming.md), không thuộc trang này.

> Nếu ứng dụng chỉ cần dừng rồi chạy tiếp bằng `invoke`, **bỏ qua mục này hoàn toàn**. Đây là phần cho trường hợp cần hiển thị tiến trình thời gian thực, không phải kiến thức bắt buộc.

---

## 6. Vòng đời thực thi — HITL chèn vào chỗ nào

Middleware định nghĩa một hook `after_model` — chạy **sau** khi model sinh câu trả lời nhưng **trước** khi bất kỳ tool nào chạy. Đây là chỗ HITL cài chốt duyệt. Năm nhịp:

1. Agent gọi model để sinh câu trả lời.
2. Middleware soi câu trả lời tìm các lời gọi tool.
3. Nếu lời gọi nào cần người duyệt, middleware dựng một `HITLRequest` gồm `action_requests` và `review_configs` rồi gọi interrupt.
4. Agent chờ quyết định của người.
5. Dựa trên các quyết định trong `HITLResponse`, middleware: chạy các lời gọi được duyệt hoặc đã sửa, tổng hợp `ToolMessage` cho lời gọi bị từ chối, trả câu người viết thẳng thành `ToolMessage` cho quyết định `respond`, rồi chạy tiếp.

Đây là lý do bốn loại quyết định ở mục 2 dẫn tới bốn nhánh khác nhau ở nhịp 5. Cơ chế của hook `after_model` nói chung thuộc trang middleware, trang này chỉ nêu HITL dùng hook đó.

---

## Tham chiếu chéo

- [guardrails.md](./guardrails.md#4-human-in-the-loop) — bản tóm tắt HITL trong nhóm guardrails; nội dung khớp với file này, file này là bản chi tiết
- [middleware.md](./middleware.md) — cơ chế hook `after_model`, interrupt, và cách middleware chèn vào luồng
- [streaming.md](./streaming.md) — các chế độ `stream_mode` dùng ở mục 5
- LangGraph interrupts: `https://docs.langchain.com/oss/python/langgraph/interrupts`
- LangGraph persistence: `https://docs.langchain.com/oss/python/langgraph/persistence`
- Middleware API reference: `https://reference.langchain.com/python/langchain/middleware/`