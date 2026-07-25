---
title: Custom middleware
doc_source: https://docs.langchain.com/oss/python/langchain/middleware/custom
accessed: 2026-07-24
version: "1.x"
status: draft
lab:
related:
  - ./03-03-middleware-overview.md
  - ./03-04-middleware-built-in.md
---

# Custom middleware (`AgentMiddleware`, `@before_model`, `@wrap_model_call`)

> Tự viết middleware bằng cách cài các hook chạy ở những điểm định sẵn trong luồng chạy của agent.
> Điểm móc nằm ở đâu trong vòng lặp agent xem [03-03](./03-03-middleware-overview.md); danh sách các bản đã viết sẵn xem [03-04](./03-04-middleware-built-in.md).

> **Về các khối kết quả in ra.** Trang tài liệu gốc không in kết quả mẫu cho ví dụ nào. Bốn khối output trong file này tôi dựng lại từ các lệnh `print` có trong chính đoạn mã và từ thứ tự chạy được tài liệu mô tả bằng chữ. Tất cả đều gắn nhãn `(dựng lại)`. Cần đối chiếu khi chạy thử.

---

## 1. Tổng quan

Hook là một hàm của mình được agent gọi vào một thời điểm định sẵn — trước khi gọi model, sau khi model trả lời, quanh mỗi lệnh gọi tool. Middleware tự viết là tập hợp các hook đó, đóng gói lại rồi truyền vào `create_agent`.

Có hai trục lựa chọn, độc lập với nhau:

| Trục | Hai lựa chọn | Quyết định điều gì |
|---|---|---|
| Kiểu hook | node-style / wrap-style | Hook chỉ chạy **tại** một điểm, hay chạy **bao quanh** một lệnh gọi |
| Cách khai | decorator / class | Bọc một hàm rời, hay dựng một lớp kế thừa `AgentMiddleware` |

Cùng một logic viết được bằng cả bốn tổ hợp. Chọn sai trục thứ nhất thì không làm được việc (node-style không chặn được lệnh gọi); chọn sai trục thứ hai chỉ là dài dòng hơn.

---

## 2. Hai kiểu hook — node-style và wrap-style

### 2.1 Node-style — chạy tuần tự tại một điểm

**Khái niệm.** Node-style hook chạy tại một điểm cố định trong luồng, làm xong việc của mình rồi trả quyền cho agent. Nó không quyết định được bước kế tiếp có chạy hay không.

**Vai trò.** Dùng cho việc quan sát và ghi nhận: ghi log, kiểm tra điều kiện, cập nhật trạng thái. Đây là loại hook đúng khi mình chỉ cần *biết* chuyện gì đang xảy ra chứ không cần *can thiệp* vào lệnh gọi.

| Hook | Chạy lúc nào |
|---|---|
| `before_agent` | Trước khi agent bắt đầu (một lần mỗi lần gọi) |
| `before_model` | Trước mỗi lệnh gọi model |
| `after_model` | Sau mỗi câu trả lời của model |
| `after_agent` | Sau khi agent xong (một lần mỗi lần gọi) |

**Áp dụng thực tế.** Bàn hỗ trợ nội bộ đặt trần 50 tin nhắn mỗi cuộc. Chạm trần thì trả một câu đóng cuộc thay vì gọi model thêm lần nữa.

**Triển khai.**

```python
from langchain.agents.middleware import before_model, after_model, AgentState
from langchain.messages import AIMessage
from langgraph.runtime import Runtime
from typing import Any

@before_model(can_jump_to=["end"])                                              # khai trước là hook này có thể nhảy tới "end"
def check_message_limit(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    if len(state["messages"]) >= 50:                                            # đếm số tin nhắn đang có trong trạng thái
        return {
            "messages": [AIMessage("Conversation limit reached.")],             # tin nhắn này được cộng vào hội thoại
            "jump_to": "end"                                                    # bỏ luôn lệnh gọi model, đi thẳng ra cuối
        }
    return None                                                                 # trả None nghĩa là không đổi gì, chạy tiếp

@after_model
def log_response(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    print(f"Model returned: {state['messages'][-1].content}")                   # [-1] là tin nhắn model vừa trả về
    return None
```

**Kết quả in ra** (dựng lại) — từ lệnh `print` trong `log_response`:

```
Model returned: Tôi đã kiểm tra, đơn hàng của bạn đang ở kho Hà Nội.   ← in một lần sau mỗi lượt model trả lời
Model returned: Bạn cần tôi tra thêm mã vận đơn không?                  ← lượt sau, in lại
```

**!Note:** `@before_model(can_jump_to=["end"])` phải khai trước thì `jump_to` mới có tác dụng. Trả về `{"jump_to": "end"}` mà quên khai `can_jump_to` là dạng lỗi dễ đi qua mắt nhất ở đây — hành vi cụ thể khi thiếu khai báo không được tài liệu mô tả.

### 2.2 Wrap-style — chạy bao quanh một lệnh gọi

**Khái niệm.** Wrap-style hook nhận vào yêu cầu (`request`) và một hàm `handler`. Nó tự quyết định gọi `handler` bao nhiêu lần: **không lần nào** (cắt mạch, tự trả kết quả), **một lần** (luồng bình thường), hoặc **nhiều lần** (thử lại).

**Vai trò.** Đây là loại hook duy nhất kiểm soát được luồng chạy. Mọi logic thử lại, đệm kết quả, đổi model giữa chừng, biến đổi yêu cầu trước khi gửi đi đều phải viết ở đây.

| Hook | Chạy lúc nào |
|---|---|
| `wrap_model_call` | Bao quanh mỗi lệnh gọi model |
| `wrap_tool_call` | Bao quanh mỗi lệnh gọi tool |

**Áp dụng thực tế.** Agent gọi model qua một cổng nội bộ có lúc trả về lỗi 502. Thử lại hai lần là qua. Node-style hook không làm được việc này vì nó không cầm được lệnh gọi trong tay.

**Triển khai.**

```python
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from typing import Callable

@wrap_model_call
def retry_model(
    request: ModelRequest,                                    # yêu cầu sắp gửi cho model
    handler: Callable[[ModelRequest], ModelResponse],         # gọi hàm này thì model mới thật sự chạy
) -> ModelResponse:
    for attempt in range(3):                                  # tối đa 3 lượt: 1 lần đầu + 2 lần thử lại
        try:
            return handler(request)                           # gọi được là trả về ngay, thoát vòng lặp
        except Exception as e:
            if attempt == 2:                                  # lượt cuối vẫn hỏng thì ném lỗi ra ngoài
                raise
            print(f"Retry {attempt + 1}/3 after error: {e}")  # còn lượt thì báo rồi quay lại vòng lặp
```

**Kết quả in ra** (dựng lại) — từ lệnh `print` trong đoạn trên:

```
Retry 1/3 after error: 502 Bad Gateway   ← lượt đầu hỏng, chuẩn bị gọi lại
Retry 2/3 after error: 502 Bad Gateway   ← lượt hai vẫn hỏng
                                          ← lượt ba thành công nên không in gì thêm
```

**!Note:** Hàm trên không có `return` sau vòng lặp. Vòng `for` kết thúc mà chưa `return` và chưa `raise` thì hàm trả về `None` — không phải một `ModelResponse`. Với `range(3)` và điều kiện `attempt == 2` thì nhánh đó không xảy ra, nhưng ai sửa `range(3)` thành một biến mà quên sửa `attempt == 2` sẽ gặp đúng lỗi im lặng này. Bản dùng lớp ở tài liệu tránh được bằng cách so `attempt == self.max_retries - 1`.

**Bản dùng lớp cho cùng logic:**

```python
from langchain.agents.middleware import AgentMiddleware, ModelRequest, ModelResponse
from typing import Callable

class RetryMiddleware(AgentMiddleware):
    def __init__(self, max_retries: int = 3):
        super().__init__()                                    # bắt buộc, lớp cha cần khởi tạo
        self.max_retries = max_retries                        # số lượt lấy từ tham số khởi tạo

    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        for attempt in range(self.max_retries):
            try:
                return handler(request)
            except Exception as e:
                if attempt == self.max_retries - 1:           # so với chính số lượt đã cấu hình
                    raise
                print(f"Retry {attempt + 1}/{self.max_retries} after error: {e}")
```

---

## 3. Cập nhật trạng thái từ trong hook

**Khái niệm.** Cả hai kiểu hook đều ghi được vào trạng thái của agent, nhưng bằng hai cơ chế khác nhau.

**Vai trò.** Trạng thái là chỗ duy nhất để một hook nhớ được điều gì giữa các lượt. Không ghi được trạng thái thì không đếm được số lần gọi, không đánh dấu được cờ, không truyền được dữ liệu từ `before_model` sang `after_model`.

| Kiểu hook | Cách ghi |
|---|---|
| Node-style (`before_agent`, `before_model`, `after_model`, `after_agent`) | Trả thẳng về một từ điển. Từ điển được nhập vào trạng thái qua các bộ gộp (reducer) của graph |
| `wrap_model_call` | Trả về `ExtendedModelResponse` bọc một `Command` để nhét bản cập nhật đi kèm câu trả lời của model |
| `wrap_tool_call` | Trả thẳng về một `Command` |

Tài liệu nêu ba loại dữ liệu hay ghi theo cách này: điểm kích hoạt việc tóm tắt, dữ liệu về mức tiêu thụ, và các trường tự đặt tính ra từ yêu cầu hoặc từ câu trả lời.

### 3.1 Node-style — trả về một từ điển

```python
from langchain.agents.middleware import after_model, AgentState
from langgraph.runtime import Runtime
from typing import Any
from typing_extensions import NotRequired

class TrackingState(AgentState):
    model_call_count: NotRequired[int]                          # NotRequired: trường có thể vắng mặt lúc đầu

@after_model(state_schema=TrackingState)                        # phải khai schema thì hook mới thấy trường mới
def increment_after_model(state: TrackingState, runtime: Runtime) -> dict[str, Any] | None:
    return {"model_call_count": state.get("model_call_count", 0) + 1}   # .get với mặc định 0 vì lượt đầu trường chưa có
```

Khóa của từ điển trả về ánh xạ thẳng sang tên trường trong trạng thái.

### 3.2 Wrap-style — trả về `ExtendedModelResponse` bọc một `Command`

```python
from langchain.agents.middleware import (
    wrap_model_call, ModelRequest, ModelResponse, AgentState, ExtendedModelResponse
)
from langgraph.types import Command
from typing import Callable
from typing_extensions import NotRequired

class UsageTrackingState(AgentState):
    last_model_call_tokens: NotRequired[int]

@wrap_model_call(state_schema=UsageTrackingState)
def track_usage(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ExtendedModelResponse:
    response = handler(request)                                  # gọi model trước, có kết quả rồi mới ghi trạng thái
    return ExtendedModelResponse(
        model_response=response,                                 # câu trả lời của model vẫn đi tiếp bình thường
        command=Command(update={"last_model_call_tokens": 150}), # bản cập nhật đi kèm, không thay thế câu trả lời
    )
```

`Command` chạy qua các bộ gộp của graph, nên bản cập nhật được nhập đúng cách và phần tin nhắn là **cộng thêm** chứ không đè lên trạng thái cũ.

### 3.3 Nhiều lớp middleware cùng ghi trạng thái

**Khái niệm.** Khi nhiều lớp middleware cùng trả về `ExtendedModelResponse`, các `Command` của chúng được ghép lại theo ba quy tắc.

**Vai trò.** Không nắm ba quy tắc này thì hai middleware cùng ghi vào một trường sẽ cho kết quả không đoán trước được.

| Quy tắc | Nội dung |
|---|---|
| Đi qua bộ gộp | Mỗi `Command` là một bản cập nhật riêng. Với tin nhắn, nghĩa là cộng dồn |
| Lớp ngoài thắng | Với trường không có bộ gộp, cập nhật chạy từ trong ra ngoài; giá trị của lớp ngoài cùng thắng khi trùng khóa |
| An toàn khi thử lại | Lớp ngoài gọi `handler()` nhiều lần (ví dụ logic thử lại) thì các `Command` từ những lượt trước bị bỏ |

```python
def _last_wins(_a: str, b: str) -> str:
    """Reducer: last writer wins (outer overwrites inner)."""
    return b                                                     # bỏ giá trị cũ, lấy giá trị mới ghi vào

class CustomMiddlewareState(AgentState):
    trace_layer: NotRequired[Annotated[str, _last_wins]]          # gắn bộ gộp vào trường bằng Annotated

class OuterMiddleware(AgentMiddleware):
    def wrap_model_call(self, request, handler) -> ExtendedModelResponse:
        response = handler(request)                               # handler ở đây kéo theo cả InnerMiddleware
        return ExtendedModelResponse(
            model_response=response,
            command=Command(update={
                "trace_layer": "outer",                           # ghi sau, nên thắng
                "messages": [SystemMessage(content="[Outer ran]")],
            }),
        )

class InnerMiddleware(AgentMiddleware):
    def wrap_model_call(self, request, handler) -> ExtendedModelResponse:
        response = handler(request)                               # handler ở đây gọi thẳng model
        return ExtendedModelResponse(
            model_response=response,
            command=Command(update={
                "trace_layer": "inner",                           # ghi trước, bị đè
                "messages": [SystemMessage(content="[Inner ran]")],
            }),
        )
```

**Kết quả in ra** (dựng lại) — trạng thái sau một lượt, dựng từ hai quy tắc "đi qua bộ gộp" và "lớp ngoài thắng":

```
trace_layer: "outer"                                  ← inner ghi trước, outer đè lên vì _last_wins
messages:    [..., SystemMessage("[Inner ran]"),      ← tin nhắn cộng dồn, không đè
                   SystemMessage("[Outer ran]")]      ← cả hai cùng còn, theo thứ tự trong ra ngoài
```

Đây là khối rủi ro nhất trong file: thứ tự hai tin nhắn trong danh sách là tôi suy ra từ chiều "trong trước, ngoài sau" của quy tắc thứ hai, tài liệu không khẳng định thứ tự với trường có bộ gộp. Chờ kiểm chứng bằng thực nghiệm.

---

## 4. Hai cách khai — decorator và class

### 4.1 Decorator — bọc một hàm rời

**Khái niệm.** Gắn decorator lên một hàm thường là đủ để hàm đó thành middleware.

**Vai trò.** Cắt bỏ phần khung của lớp khi middleware chỉ có đúng một hook và không cần cấu hình gì.

**Danh sách decorator có sẵn:**

| Nhóm | Decorator |
|---|---|
| Node-style | `@before_agent`, `@before_model`, `@after_model`, `@after_agent` |
| Wrap-style | `@wrap_model_call`, `@wrap_tool_call` |
| Tiện dụng | `@dynamic_prompt` — sinh prompt hệ thống theo tình huống |

```python
@before_model
def log_before_model(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    print(f"About to call model with {len(state['messages'])} messages")   # đếm tin nhắn ngay trước khi gọi
    return None

agent = create_agent(
    model="gpt-5.4",
    middleware=[log_before_model, retry_model],    # hàm đã bọc decorator truyền thẳng, không cần gọi ()
    tools=[...],
)
```

**Kết quả in ra** (dựng lại):

```
About to call model with 3 messages    ← lượt đầu: 1 tin hệ thống + 1 tin người dùng + 1 tin AI trước đó
About to call model with 5 messages    ← sau một vòng gọi tool, thêm 2 tin nhắn
```

Dòng thứ hai là tôi suy ra từ cách vòng lặp agent cộng thêm tin nhắn mỗi vòng; con số cụ thể chưa đủ căn cứ để khẳng định.

Dùng decorator khi: chỉ cần một hook, không có cấu hình phức tạp, hoặc đang dựng thử cho nhanh.

### 4.2 Class — kế thừa `AgentMiddleware`

**Khái niệm.** Dựng một lớp con của `AgentMiddleware` và cài các hook thành phương thức.

**Vai trò.** Ba việc mà decorator không làm được: gộp nhiều hook vào cùng một middleware, khai cả bản đồng bộ lẫn bất đồng bộ cho cùng một hook, và nhận cấu hình qua `__init__` để tái dùng giữa các dự án.

```python
class LoggingMiddleware(AgentMiddleware):
    def before_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        print(f"About to call model with {len(state['messages'])} messages")
        return None

    def after_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        print(f"Model returned: {state['messages'][-1].content}")
        return None

    async def abefore_model(self, state, runtime) -> dict[str, Any] | None:    # bản bất đồng bộ, tiền tố "a"
        return None

    async def aafter_model(self, state, runtime) -> dict[str, Any] | None:     # aafter_model, không phải after_amodel
        print(f"Model returned: {state['messages'][-1].content}")
        return None

agent = create_agent(
    model="gpt-5.4",
    middleware=[LoggingMiddleware()],    # lớp phải được khởi tạo, khác với decorator
    tools=[...],
)
```

**!Note:** Hai điểm dễ nhầm giữa hai cách khai. Decorator truyền vào `middleware=[log_before_model]` — không có ngoặc. Lớp truyền vào `middleware=[LoggingMiddleware()]` — có ngoặc. Và tên bản bất đồng bộ là `abefore_model` / `aafter_model`, chữ `a` đứng đầu tên phương thức.

---

## 5. Mở rộng trạng thái bằng schema riêng

**Khái niệm.** Middleware khai thêm trường vào trạng thái của agent bằng cách kế thừa `AgentState`.

**Vai trò.** Tài liệu nêu bốn việc mở ra từ đây: giữ bộ đếm và cờ sống suốt vòng đời agent; truyền dữ liệu từ `before_model` sang `after_model` hoặc giữa các middleware; cài các mối bận tâm cắt ngang như giới hạn tần suất, theo dõi mức dùng, ngữ cảnh người dùng, nhật ký kiểm toán — mà không phải động vào lõi agent; và ra quyết định dựa trên giá trị đã tích lũy.

**Áp dụng thực tế.** Hệ thống nội bộ tính phí theo phòng ban. Mỗi lần gọi model phải cộng vào bộ đếm gắn với `user_id`, và quá 10 lần trong một cuộc thì dừng.

**Triển khai** (bản decorator):

```python
class CustomState(AgentState):
    model_call_count: NotRequired[int]         # bộ đếm số lần gọi model
    user_id: NotRequired[str]                  # ai đang dùng, để quy phí

@before_model(state_schema=CustomState, can_jump_to=["end"])
def check_call_limit(state: CustomState, runtime: Runtime) -> dict[str, Any] | None:
    count = state.get("model_call_count", 0)
    if count > 10:
        return {"jump_to": "end"}              # chạm trần thì thoát, không kèm tin nhắn nào
    return None

@after_model(state_schema=CustomState)
def increment_counter(state: CustomState, runtime: Runtime) -> dict[str, Any] | None:
    return {"model_call_count": state.get("model_call_count", 0) + 1}

result = agent.invoke({
    "messages": [HumanMessage("Hello")],
    "model_call_count": 0,                     # giá trị khởi đầu truyền vào lúc gọi
    "user_id": "user-123",
})
```

Bản dùng lớp khai schema một lần ở cấp lớp thay vì lặp ở từng hook:

```python
class CallCounterMiddleware(AgentMiddleware[CustomState]):
    state_schema = CustomState                 # khai một chỗ, mọi hook trong lớp đều dùng

    def before_model(self, state: CustomState, runtime) -> dict[str, Any] | None:
        count = state.get("model_call_count", 0)
        if count > 10:
            return {"jump_to": "end"}
        return None

    def after_model(self, state: CustomState, runtime) -> dict[str, Any] | None:
        return {"model_call_count": state.get("model_call_count", 0) + 1}
```

**!Note:** Quên `state_schema=CustomState` ở decorator thì hook làm việc trên `AgentState` gốc. Trường tự đặt không có ở đó — `state.get("model_call_count", 0)` luôn trả về `0`, bộ đếm mãi không tăng, và mã chạy trơn tru không báo gì. Đây là hành vi tôi suy ra từ việc `.get` có giá trị mặc định; tài liệu không mô tả trường hợp thiếu khai schema.

---

## 6. Thứ tự chạy khi có nhiều middleware

**Khái niệm.** Với `middleware=[middleware1, middleware2, middleware3]`, ba loại hook chạy theo ba chiều khác nhau.

**Vai trò.** Thứ tự quyết định ai nhìn thấy dữ liệu trước. Middleware che thông tin cá nhân đặt sau middleware ghi log thì log đã ghi xong bản chưa che.

| Loại hook | Chiều chạy |
|---|---|
| `before_*` | Từ đầu danh sách xuống cuối |
| `after_*` | Từ cuối danh sách ngược lên đầu |
| `wrap_*` | Lồng vào nhau, middleware đầu tiên bọc ngoài cùng |

Luồng đầy đủ tài liệu liệt kê:

```
1.  middleware1.before_agent()                                     ← trước khi vòng lặp bắt đầu
2.  middleware2.before_agent()                                     ← xuôi theo danh sách
3.  middleware3.before_agent()                                     ← như trên
--- vòng lặp agent bắt đầu ---
4.  middleware1.before_model()                                     ← vẫn xuôi
5.  middleware2.before_model()                                     ← như trên
6.  middleware3.before_model()                                     ← như trên
7.  m1.wrap_model_call() → m2.wrap_model_call() → m3... → model    ← lồng nhau, m1 ngoài cùng
8.  middleware3.after_model()                                      ← từ đây đảo chiều
9.  middleware2.after_model()                                      ← ngược lên
10. middleware1.after_model()                                      ← như trên
--- vòng lặp agent kết thúc ---
11. middleware3.after_agent()                                      ← vẫn ngược
12. middleware2.after_agent()                                      ← như trên
13. middleware1.after_agent()                                      ← chạy cuối cùng
```

**!Note:** `wrap_model_call` của middleware **đầu tiên** là lớp ngoài cùng — nó gọi `handler`, mà `handler` ở đó chính là toàn bộ phần còn lại. Nối lại với mục 3.3: lớp ngoài cùng cũng là lớp thắng khi ghi trùng khóa vào trạng thái. Hai điều này cùng nói một chuyện: đặt middleware quan trọng nhất lên đầu danh sách.

---

## 7. Nhảy sớm ra khỏi luồng (`jump_to`)

**Khái niệm.** Trả về một từ điển có khóa `jump_to` để thoát khỏi vị trí hiện tại và nhảy tới một chặng khác.

**Vai trò.** Đây là cách duy nhất để node-style hook cắt luồng. Không có nó thì hook chỉ quan sát được.

| Đích nhảy | Nhảy tới đâu |
|---|---|
| `'end'` | Cuối luồng chạy của agent, hoặc hook `after_agent` đầu tiên |
| `'tools'` | Chặng chạy tool |
| `'model'` | Chặng gọi model, hoặc hook `before_model` đầu tiên |

**Áp dụng thực tế.** Rào chắn nội dung: model trả về câu chứa dấu hiệu đã bị chặn thì thay bằng một câu từ chối và đóng lượt, không để câu đó đi tiếp vào tool nào.

```python
from langchain.agents.middleware import after_model, hook_config, AgentState
from langchain.messages import AIMessage

@after_model
@hook_config(can_jump_to=["end"])                              # khai quyền nhảy; xếp dưới @after_model
def check_for_blocked(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    last_message = state["messages"][-1]                       # câu model vừa trả về
    if "BLOCKED" in last_message.content:
        return {
            "messages": [AIMessage("I cannot respond to that request.")],   # câu thay thế cộng vào hội thoại
            "jump_to": "end"                                                # đóng lượt ngay
        }
    return None
```

Bản dùng lớp gắn `@hook_config` thẳng lên phương thức:

```python
class BlockedContentMiddleware(AgentMiddleware):
    @hook_config(can_jump_to=["end"])
    def after_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        ...
```

**!Note:** Câu bị chặn vẫn nằm trong danh sách tin nhắn — hook cộng thêm câu từ chối chứ không xóa câu cũ. Muốn nó biến mất khỏi lịch sử thì phải làm việc khác; trang này không có hướng dẫn cho việc xóa tin nhắn.

---

## 8. Bảy nguyên tắc tài liệu khuyến nghị

1. Mỗi middleware làm đúng một việc.
2. Xử lý lỗi tử tế — đừng để lỗi trong middleware làm sập agent.
3. Chọn đúng kiểu hook: node-style cho logic tuần tự (ghi log, kiểm tra), wrap-style cho việc điều khiển luồng (thử lại, phương án dự phòng, đệm kết quả).
4. Ghi rõ tài liệu cho mọi trường trạng thái tự đặt.
5. Kiểm thử riêng lẻ từng middleware trước khi ghép vào.
6. Cân nhắc thứ tự chạy — đặt middleware quan trọng lên đầu danh sách.
7. Có bản dựng sẵn thì dùng bản dựng sẵn ([03-04](./03-04-middleware-built-in.md)).

---

## 9. Năm ví dụ tài liệu đưa ra

### 9.1 Sửa prompt hệ thống ngay lúc chạy

**Khái niệm.** Đọc và sửa `request.system_message` trong `wrap_model_call`, rồi truyền bản đã sửa qua `request.override(...)`.

**Vai trò.** Tài liệu gọi đây là một trong những việc hay dùng nhất của middleware: nhét ngữ cảnh, chỉ dẫn riêng cho từng người dùng, hoặc thông tin theo thời điểm vào prompt trước mỗi lệnh gọi model.

```python
@wrap_model_call
def add_context(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:
    new_content = list(request.system_message.content_blocks) + [    # content_blocks luôn là danh sách khối
        {"type": "text", "text": "Additional context."}              # khối mới nối vào cuối, không đè khối cũ
    ]
    new_system_message = SystemMessage(content=new_content)
    return handler(request.override(system_message=new_system_message))   # override tạo bản yêu cầu mới
```

Bốn điểm tài liệu nhấn:

- `ModelRequest.system_message` **luôn** là một đối tượng `SystemMessage`, kể cả khi agent được dựng bằng `system_prompt="chuỗi"`.
- Dùng `SystemMessage.content_blocks` để đọc nội dung dưới dạng danh sách khối, bất kể nội dung gốc là chuỗi hay danh sách.
- Khi sửa, nối thêm khối mới vào `content_blocks` để giữ nguyên cấu trúc đang có.
- Truyền thẳng đối tượng `SystemMessage` vào tham số `system_prompt` của `create_agent` được, dùng cho các trường hợp như điều khiển đệm.

### 9.2 Đổi model theo độ dài hội thoại

**Khái niệm.** Chọn model ngay trong `wrap_model_call` dựa trên nội dung của `request`.

**Vai trò.** Câu ngắn dùng model rẻ, hội thoại dài mới chuyển sang model mạnh.

```python
complex_model = init_chat_model("claude-sonnet-4-6")
simple_model = init_chat_model("claude-haiku-4-5-20251001")

@wrap_model_call
def dynamic_model(request: ModelRequest, handler) -> ModelResponse:
    if len(request.messages) > 10:       # hội thoại đã dài thì đổi sang bản mạnh
        model = complex_model
    else:
        model = simple_model             # còn ngắn thì giữ bản rẻ
    return handler(request.override(model=model))
```

### 9.3 Lọc tool ngay lúc chạy

**Khái niệm.** Cắt danh sách tool trước khi model nhìn thấy, bằng `request.override(tools=...)`.

**Vai trò.** Tài liệu nêu ba lợi ích: prompt ngắn lại; model chọn đúng hơn khi có ít lựa chọn; và lọc được theo quyền của người dùng.

```python
@wrap_model_call
def select_tools(request: ModelRequest, handler) -> ModelResponse:
    relevant_tools = select_relevant_tools(request.state, request.runtime)   # hàm chọn do mình viết
    return handler(request.override(tools=relevant_tools))

agent = create_agent(
    model="gpt-5.4",
    tools=all_tools,          # mọi tool vẫn phải đăng ký từ đầu ở đây
    middleware=[select_tools],
)
```

**!Note:** Cách này chỉ **lọc** trong số tool đã đăng ký sẵn. Đăng ký tool mới phát hiện lúc chạy — ví dụ tool lấy từ máy chủ MCP — là việc khác, nằm ở trang `https://docs.langchain.com/oss/python/langchain/agents#dynamic-tools`.

Sẵn có bản dựng sẵn làm việc tương tự bằng LLM: [`LLMToolSelectorMiddleware`](./03-04-middleware-built-in.md#9-llm-tool-selector--để-một-model-nhỏ-lọc-tool-trước).

### 9.4 Theo dõi từng lệnh gọi tool

**Khái niệm.** `wrap_tool_call` nhận `ToolCallRequest` và trả về `ToolMessage` hoặc `Command`.

**Vai trò.** Ghi lại tên tool, tham số, và kết quả thành công hay hỏng — mà không phải sửa thân hàm của từng tool.

```python
from langchain.tools.tool_node import ToolCallRequest

@wrap_tool_call
def monitor_tool(
    request: ToolCallRequest,
    handler: Callable[[ToolCallRequest], ToolMessage | Command],
) -> ToolMessage | Command:
    print(f"Executing tool: {request.tool_call['name']}")     # tool_call là từ điển, lấy tên bằng khóa
    print(f"Arguments: {request.tool_call['args']}")          # tham số model điền vào
    try:
        result = handler(request)                             # tool thật sự chạy ở dòng này
        print("Tool completed successfully")
        return result
    except Exception as e:
        print(f"Tool failed: {e}")
        raise                                                 # ném lại, không nuốt lỗi
```

**Kết quả in ra** (dựng lại) — từ bốn lệnh `print` trong đoạn trên:

```
Executing tool: search                       ← in trước khi tool chạy
Arguments: {'query': 'lãi suất trái phiếu'}  ← tham số model tự điền
Tool completed successfully                   ← nhánh try chạy trọn
Executing tool: query_database                ← tool tiếp theo trong cùng lượt
Arguments: {'table': 'bonds'}                 ← như trên
Tool failed: connection refused               ← nhánh except, sau dòng này lỗi được ném lại
```

### 9.5 Đệm prompt cho model Anthropic

**Khái niệm.** Với model Anthropic, gắn chỉ thị `cache_control` vào khối nội dung để đệm phần prompt hệ thống dài.

**Vai trò.** Prompt hệ thống chứa cả một tài liệu dài thì mỗi lượt gọi đều trả tiền cho phần đó. Đệm lại thì chỉ trả đủ giá ở lượt đầu.

```python
@wrap_model_call
def add_cached_context(request: ModelRequest, handler) -> ModelResponse:
    new_content = list(request.system_message.content_blocks) + [
        {
            "type": "text",
            "text": "Here is a large document to analyze:\n\n<document>...</document>",
            "cache_control": {"type": "ephemeral"}     # phần nội dung tính đến đây được đệm lại
        }
    ]
    new_system_message = SystemMessage(content=new_content)
    return handler(request.override(system_message=new_system_message))
```

Bốn điểm nhấn về `system_message` ở mục 9.1 áp nguyên cho đoạn này — tài liệu lặp lại đúng danh sách đó.

---

## 10. Bảng so sánh tổng hợp

**Bảng 1 — node-style so với wrap-style**

| | Node-style | Wrap-style |
|---|---|---|
| Hook | `before_agent`, `before_model`, `after_model`, `after_agent` | `wrap_model_call`, `wrap_tool_call` |
| Chặn được lệnh gọi | Không | Có, gọi `handler` 0 lần là cắt mạch |
| Gọi lại được để thử lại | Không | Có, gọi `handler` nhiều lần |
| Sửa được yêu cầu trước khi gửi | Không | Có, qua `request.override(...)` |
| Ghi trạng thái bằng | Trả về từ điển | `ExtendedModelResponse` + `Command`, hoặc `Command` |
| Thoát sớm bằng | `jump_to` (phải khai `can_jump_to`) | Trả thẳng kết quả, không gọi `handler` |
| Chiều chạy | `before_*` xuôi, `after_*` ngược | Lồng nhau, phần tử đầu danh sách bọc ngoài cùng |
| Dùng cho | Ghi log, kiểm tra điều kiện, cập nhật trạng thái | Thử lại, đệm kết quả, biến đổi yêu cầu |

**Bảng 2 — decorator so với class**

| | Decorator | Class |
|---|---|---|
| Truyền vào `create_agent` | `middleware=[ten_ham]` | `middleware=[TenLop()]` |
| Nhiều hook trong một middleware | Không | Có |
| Cả bản đồng bộ và bất đồng bộ cho cùng một hook | Không | Có, thêm phương thức `abefore_model` / `aafter_model` |
| Nhận cấu hình lúc khởi tạo | Không | Có, qua `__init__` |
| Khai schema trạng thái | Từng hook: `@before_model(state_schema=...)` | Một chỗ: `state_schema = CustomState` |

**Chuyển từ decorator sang class**

| Ở decorator | Tương ứng ở class |
|---|---|
| `@before_model` trên hàm | Phương thức `before_model(self, state, runtime)` |
| `@wrap_model_call` trên hàm | Phương thức `wrap_model_call(self, request, handler)` |
| `@before_model(can_jump_to=["end"])` | `@hook_config(can_jump_to=["end"])` trên phương thức |
| `@after_model(state_schema=CustomState)` | `state_schema = CustomState` khai ở cấp lớp |
| *(không có)* | `abefore_model` / `aafter_model` — bản bất đồng bộ, thứ mới hoàn toàn, decorator không có tương đương |
| *(không có)* | `__init__` nhận tham số cấu hình |

---

## 11. Nên chọn cái nào

Chọn **node-style** khi hook chỉ cần đọc trạng thái và ghi lại điều gì đó: ghi log, đếm, gắn cờ, kiểm tra trần rồi thoát bằng `jump_to`.

Chọn **wrap-style** khi cần cầm lệnh gọi trong tay: thử lại, cắt mạch trả kết quả có sẵn, đổi model, sửa prompt hoặc danh sách tool trước khi gửi đi.

Chọn **decorator** khi có đúng một hook và không cần tham số.

Chọn **class** khi cần từ hai hook trở lên, cần bản bất đồng bộ, cần tham số khởi tạo, hoặc định dùng lại middleware ở dự án khác.

Trước cả bốn lựa chọn trên: kiểm tra [danh sách bản dựng sẵn](./03-04-middleware-built-in.md#1-tổng-quan--mười-sáu-bản-dùng-chung-cho-mọi-nhà-cung-cấp) đã. Thử lại, chặn trần, phương án dự phòng, che thông tin cá nhân, tóm tắt đều đã có bản viết sẵn.

---

## Tham chiếu chéo

- [03-03 Middleware tổng quan](./03-03-middleware-overview.md) — vị trí các điểm móc trong vòng lặp agent
- [03-04 Middleware dựng sẵn](./03-04-middleware-built-in.md) — nhiều bản trong đó là hiện thực sẵn của đúng các mẫu ở mục 9
- Đăng ký tool lúc chạy: `https://docs.langchain.com/oss/python/langchain/agents#dynamic-tools`
- Middleware API reference: `https://reference.langchain.com/python/langchain/middleware/`
- Trang gốc: `https://docs.langchain.com/oss/python/langchain/middleware/custom`