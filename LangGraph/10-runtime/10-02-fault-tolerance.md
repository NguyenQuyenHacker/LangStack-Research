---
title: Fault tolerance
doc_source: https://docs.langchain.com/oss/python/langgraph/fault-tolerance
accessed: 2026-07-30
lc_version: unknown
status: draft
lab:
related:
  - ../02-persistence/02-02-checkpointers.md
  - ../08-graph-api/08-03-use-graph-api.md
---

# Fault tolerance — chịu lỗi ở cấp node

> Ba cơ chế ghép được để xử lý khi một node thất bại: **retry**, **timeout**, **error handler**.
> Cùng với [`set_node_defaults`](#5-graph-defaults--cấu-hình-một-lần-cho-mọi-node) để cấu hình một lần cho cả graph, và *graceful shutdown* để dừng sạch giữa chừng.

---

## 1. Tổng quan

Khi một node thất bại — API ngoài chậm, lỗi mạng tạm thời, exception không bắt — LangGraph cho ba cơ chế xử lý, ghép được với nhau: **retry** (tự chạy lại theo loại lỗi và backoff), **timeout** (chặn thời gian một lần chạy), **error handler** (chạy hàm phục hồi sau khi hết retry).

Điểm phải nắm trước hết: **thứ tự ghép là cố định.** Một attempt của node ném exception bất kỳ (kể cả `NodeTimeoutError` từ timeout) → retry policy quyết định có chạy lại không → *chỉ khi* hết retry, error handler mới chạy.

```
attempt lỗi ──> retry_policy khớp? ──yes, còn lượt──> chạy lại
                      │
                      └─ hết lượt / không có ──> error_handler? ──yes──> chạy handler (update + goto)
                                                                  └─no──> exception nổi lên trên
```

Một ngoại lệ quan trọng đứng ngoài toàn bộ sơ đồ: `interrupt()` (dừng chờ người) **không** đi vào retry hay error handler — nó dùng cơ chế riêng để tạm dừng graph.

> [!note]
> Timeout per-node và error handler cấp node cần `langgraph>=1.2`. Retry có sẵn từ trước.

---

## 2. Retries — tự chạy lại attempt thất bại

Retry policy tự chạy lại một attempt thất bại dựa trên loại exception và cấu hình backoff. Nỗi đau: node gọi API ngoài, lỗi 5xx hay rớt mạng là chuyện tạm thời — chạy lại là qua, không đáng để cả graph chết.

Gắn qua `retry_policy=` khi `add_node`:

```python
builder.add_node(
    "call_api",
    call_api,
    retry_policy=RetryPolicy(max_attempts=3),   # tính cả lần đầu, tức tối đa 2 lần retry
)
```

**Hành vi mặc định — điều dễ hiểu sai nhất.** `retry_on` mặc định là `default_retry_on`: retry trên **mọi** exception *trừ* các loại sau (và lớp con của chúng): `ValueError`, `TypeError`, `ArithmeticError`, `ImportError`, `LookupError`, `NameError`, `SyntaxError`, `RuntimeError`, `ReferenceError`, `StopIteration`, `StopAsyncIteration`, `OSError`.

Nghĩa là các lỗi lập trình (sai kiểu, sai tên) *không* retry — đúng, vì chạy lại cũng lỗi y hệt. Với exception từ `requests`/`httpx`, chỉ retry khi status 5xx. `NodeTimeoutError` retry được mặc định.

### Bảng tham số `RetryPolicy`

| Tham số | Mặc định | Ý nghĩa |
|---|---|---|
| `max_attempts` | `3` | Số lần thử tối đa, tính cả lần đầu |
| `initial_interval` | `0.5` | Giây trước lần retry đầu |
| `backoff_factor` | `2.0` | Hệ số nhân khoảng chờ sau mỗi retry |
| `max_interval` | `128.0` | Trần khoảng chờ giữa các retry |
| `jitter` | `True` | Thêm nhiễu ngẫu nhiên vào khoảng chờ |
| `retry_on` | `default_retry_on` | Loại exception cần retry, hoặc callable trả `True` nếu nên retry |

### Tùy biến điều kiện retry

Truyền một callable hoặc loại exception vào `retry_on`. Import `default_retry_on` để *mở rộng* hành vi mặc định thay vì viết lại từ đầu:

```python
def custom_retry_on(exc):
    if isinstance(exc, MyCustomError):  # lỗi nghiệp vụ của mình: không retry
        return False
    return default_retry_on(exc)        # còn lại giữ nguyên logic mặc định
```

### Xem trạng thái retry để chuyển sang fallback

Bên trong node, đọc `runtime.execution_info` để biết đang ở lần thử thứ mấy — hữu ích khi API chính lỗi mãi thì đổi sang API dự phòng:

```python
def my_node(state: State, runtime: Runtime) -> State:
    if runtime.execution_info.node_attempt > 1:   # từ lần retry đầu tiên trở đi
        return {"result": call_fallback_api()}    # đổi sang API dự phòng
    return {"result": call_primary_api()}         # lần đầu vẫn gọi API chính
```

Các trường của `execution_info`: `node_attempt` (số lần thử, đánh số từ 1), `node_first_attempt_time`, `thread_id`, `run_id`, `checkpoint_id`, `task_id`. `execution_info` có sẵn cả khi không đặt retry policy — khi đó `node_attempt` luôn là `1`.

---

## 3. Timeouts — chặn thời gian một attempt

`timeout=` chặn thời gian tối đa cho *một attempt* của node. Nỗi đau: một API treo vô hạn kéo cả graph đứng theo — cần một mốc để cắt.

> [!note]
> Timeout **chỉ áp cho node async**. Node sync gắn `timeout` bị từ chối ngay lúc compile. Cần bọc I/O chặn (blocking) thì đưa vào `asyncio.to_thread` bên trong một node async.

Truyền số giây, một `timedelta`, hoặc một `TimeoutPolicy` để tách hai loại giới hạn:

```python
builder.add_node("call_model", call_model, timeout=60)                  # 60 giây
builder.add_node("call_model", call_model, timeout=timedelta(minutes=2))
builder.add_node("call_model", call_model,
                 timeout=TimeoutPolicy(run_timeout=120, idle_timeout=30))
```

### Hai loại giới hạn — khác nhau ở chỗ có reset hay không

`run_timeout` và `idle_timeout` giải quyết hai kiểu treo khác nhau. Đặt cùng lúc được — cái nào chạm trước sẽ hủy attempt.

| | `run_timeout` | `idle_timeout` |
|---|---|---|
| Bản chất | Trần cứng theo đồng hồ tường cho một attempt | Trần theo *tiến độ*: chỉ chạm khi node ngừng tiến triển đủ lâu |
| Có reset? | Không bao giờ, dù node vẫn hoạt động | Reset mỗi khi node phát một tín hiệu tiến triển |
| Hợp với | Chặn tổng thời gian một lần chạy | Node dài nhưng vẫn đang chạy đều, chỉ cắt khi *treo thật* |

**Tín hiệu tiến triển** (dưới `refresh_on="auto"` mặc định) reset đồng hồ idle: ghi state, xuất stream chunk, lên lịch child-task, gọi stream-writer, và bất kỳ callback event nào của LangChain từ node hoặc con cháu nó (token LLM, tool call, chain start/end...).

**Heartbeat mode.** Đặt `refresh_on="heartbeat"` để thu hẹp nguồn reset về *chỉ* các lời gọi `runtime.heartbeat()`. Hữu ích khi muốn định nghĩa "idle" nghiêm ngặt, không bị đám con cháu ồn ào reset hộ:

```python
async def long_running_node(state: State, runtime: Runtime) -> State:
    for batch in fetch_batches():       # công việc dài, không tự phát tín hiệu tiến triển
        process(batch)
        runtime.heartbeat()             # tự tay reset đồng hồ idle sau mỗi batch
    return {"result": "done"}
```

`runtime.heartbeat()` là no-op khi ở ngoài một attempt có tính idle, nên gọi vô điều kiện cũng an toàn.

### `NodeTimeoutError`

Khi timeout chạm, LangGraph ném `NodeTimeoutError`, **xóa mọi write của attempt lỗi**, rồi để retry policy quyết định. Các trường: `node`, `elapsed` (giây đã trôi), `kind` (`"idle"` hoặc `"run"`), `idle_timeout`, `run_timeout`.

`NodeTimeoutError` retry được mặc định, nên ghép `timeout` với retry policy chạy ngay không cần chỉnh: đồng hồ timeout reset mỗi attempt mới, write của attempt timeout bị xóa trước retry kế.

```python
builder.add_node("call_model", call_model,
                 timeout=TimeoutPolicy(idle_timeout=30),
                 retry_policy=RetryPolicy(max_attempts=3))
```

### Timeout động qua `Send`

Trong map-reduce (dùng `Send` để phát node động), truyền timeout thẳng trên `Send` để đè timeout tĩnh của node đích cho riêng lần push đó:

```python
def fan_out(state: OverallState):
    return [
        Send("process_item", {"item": item},
             timeout=TimeoutPolicy(idle_timeout=15))   # đè timeout tĩnh cho từng item
        for item in state["items"]
    ]
```

Bỏ timeout trên `Send` thì timeout đặt lúc `add_node` áp. Cách này cho phép đặt mặc định rộng ở node rồi siết chặt cho từng lời gọi.

---

## 4. Error handling — phục hồi sau khi hết retry

Error handler chạy sau khi node lỗi *và* đã hết retry. Nó nhận state hiện tại, có thể cập nhật state hoặc định tuyến sang node khác qua `Command`. Nỗi đau: hết retry rồi thì mặc định cả graph chết — nhưng nhiều luồng cần *bù trừ* (Saga) rồi đi tiếp, không phải abort.

Handler chỉ chạy sau khi retry policy cạn, hoặc chạy ngay nếu không cấu hình retry. Retry và handler tách rời: cấu hình "khi nào retry" và "khi nào bù trừ" độc lập.

```python
def payment_error_handler(state: State, error: NodeError) -> Command:
    return Command(
        update={"status": f"compensated: {error.error}"},  # ghi lại đã bù trừ
        goto="finalize",                                    # đi tiếp sang node finalize
    )

graph = (
    StateGraph(State)
    .add_node("charge_payment", charge_payment,
              retry_policy=RetryPolicy(max_attempts=3, retry_on=ConnectionError),
              error_handler=payment_error_handler)          # hết retry mới gọi handler
    .add_node("finalize", finalize)
    .add_edge(START, "charge_payment")
    .compile()
)
```

**`NodeError` — ngữ cảnh lỗi truyền vào handler.** Handler nhận `error: NodeError` bằng cách chú thích kiểu (cùng cơ chế như `runtime: Runtime`). Đây là dataclass đóng băng, hai trường: `node` (tên node lỗi) và `error` (exception đã ném). Tham số này *tùy chọn* — handler không cần ngữ cảnh có thể dùng chữ ký gọn hơn như `(state)` hoặc `(state, runtime)`.

**Định tuyến bằng `Command`** cho phép cả Saga: `update` state rồi `goto` sang node bù trừ thay vì abort. Ví dụ đặt trước kho → charge tiền lỗi → handler ghi trạng thái bù trừ rồi nhảy tới `finalize`.

Ba hành vi cần nhớ:

- **Resume-safe.** Provenance của lỗi được checkpoint. Nếu graph bị ngắt hoặc process chết *sau khi* node lỗi nhưng *trước khi* handler xong, lúc resume từ checkpoint handler vẫn thấy đúng `NodeError` cũ.
- **`interrupt()` không vào handler.** Interrupt dùng cơ chế `GraphBubbleUp` để tạm dừng cho luồng human-in-the-loop, bỏ qua cả retry lẫn handler. Graph tạm dừng như thường.
- **Lỗi subgraph nổi lên parent.** Node bọc một subgraph, subgraph ném exception không bắt thì exception đó nổi lên node cha; nếu node cha có handler, handler chạy với exception của subgraph nằm trong `error.error`.

---

## 5. Graph defaults — cấu hình một lần cho mọi node

Thay vì lặp `retry_policy=`, `error_handler=`, `timeout=`, `cache_policy=` trên từng `add_node`, dùng `set_node_defaults` để đặt mặc định toàn graph ở một chỗ.

```python
graph = (
    StateGraph(State)
    .set_node_defaults(
        retry_policy=RetryPolicy(max_attempts=3),
        error_handler=default_error_handler,
        timeout=TimeoutPolicy(run_timeout=30),
    )
    .add_node("step_a", step_a)         # cả hai node dưới cùng dùng bộ mặc định trên
    .add_node("step_b", step_b)
    .add_edge(START, "step_a")
    .compile()
)
```

**Precedence.** Giá trị đặt thẳng trên `add_node()` luôn đè mặc định. Mặc định được giải quyết lúc `compile()`, nên gọi `set_node_defaults()` trước hay sau `add_node()` đều được.

```python
.add_node("step_a", step_a)                                     # dùng default_error_handler
.add_node("step_b", step_b, error_handler=custom_error_handler) # per-node đè default
```

**Ma trận áp dụng.** Không phải mặc định nào cũng áp cho mọi loại node. Node-error-handler (đăng ký qua `add_node(error_handler=...)`) bị loại khỏi một số mặc định để tránh hành vi nguy hiểm:

| Mặc định | Node thường | Node error-handler | Lý do |
|---|---|---|---|
| `retry_policy` | ✅ | ✅ | Handler nên được retry khi lỗi tạm thời |
| `timeout` | ✅ | ✅ | Handler treo cũng cần bị hủy như node treo |
| `error_handler` | ✅ | ❌ | Handler không được tự bắt chính mình |
| `cache_policy` | ✅ | ❌ | Cache kết quả handler là không an toàn |

**Scope.** Mặc định đặt ở graph cha **không** truyền xuống subgraph — mỗi graph tự quản mặc định của mình.

Handler mặc định nhận cùng chữ ký `(state, error: NodeError)`; nó cũng nhận thêm `RunnableConfig` làm tham số thứ ba tùy chọn nếu cần đọc `thread_id` hay giá trị config khác.

---

## 6. Cùng cơ chế trong Functional API

`timeout=` và `retry_policy=` áp y hệt cho `@task` và `@entrypoint`:

```python
@task(timeout=TimeoutPolicy(idle_timeout=30), retry_policy=RetryPolicy(max_attempts=3))
async def call_api(url: str) -> str:
    response = await fetch(url)
    return response.text

@entrypoint(timeout=60)
async def my_workflow(inputs: dict) -> str:
    return await call_api("https://api.example.com/data")
```

Hành vi giống `add_node`: timeout ném `NodeTimeoutError`, write bị xóa, retry policy quyết định.

---

## 7. Graceful shutdown — dừng sạch giữa chừng, resume được

Cho phép dừng một graph đang chạy *sau khi step hiện tại xong*, lưu một checkpoint resume được. Nỗi đau: nhận SIGTERM hay bị supervisor thu hồi tài nguyên mà không muốn mất công việc dở.

> [!note]
> Cần `langgraph>=1.2`.

Tạo một `RunControl`, truyền qua `control=` cho `invoke`/`stream`. Gọi `request_drain()` từ luồng bất kỳ để báo run nên dừng:

```python
control = RunControl()
# trong signal handler: control.request_drain("sigterm")

try:
    result = graph.invoke(inputs, config, control=control)
except GraphDrained as e:
    print(f"Drained: {e.reason}")       # graph dừng sớm, checkpoint đã lưu, resume sau
```

**Drain là hợp tác, chỉ tác động giữa các step**, không cắt ngang việc đang chạy:

| Tình huống | Hành vi |
|---|---|
| Node đang chạy dở | Chạy tới hết. Drain có hiệu lực ở step kế |
| Node đang retry | Vòng retry chạy tới cạn hoặc thành công, drain có hiệu lực sau |
| Graph kết thúc tự nhiên đúng lúc drain | Trả về bình thường. Soi `control.drain_requested` để phân biệt |
| Còn step phía sau | Ném `GraphDrained(reason)`, checkpoint đã lưu và resume được |
| Subgraph xin drain | `GraphDrained` nổi lên parent, dừng nó ở step boundary của chính nó |

**Resume** một run đã drain bằng `invoke(None, config)` với cùng `thread_id`. Bên trong node, đọc `runtime.drain_requested` / `runtime.drain_reason` để bỏ qua việc nặng trước khi tới step boundary.

Mẫu xử lý SIGTERM:

```python
control = RunControl()
signal.signal(signal.SIGTERM, lambda *_: control.request_drain("sigterm"))
try:
    result = graph.invoke(inputs, config, control=control)
except GraphDrained as e:
    log.info("graph drained: %s", e.reason)   # resume ở lần khởi động sau với cùng config
```

> [!note]
> `request_drain()` **không** hủy asyncio task hay giết thread đang chạy. Cần trần cứng thì ghép drain với một timeout và cơ chế hủy task.

---

## Giới hạn cần nhớ

- Timeout **chỉ async**: node sync gắn timeout bị từ chối lúc compile.
- Mỗi node tối đa **một** `error_handler`.
- Handler tự lỗi thì exception nổi lên như thể node không có handler.
- `set_node_defaults` **không** truyền xuống subgraph — mỗi graph tự quản.

---

## Tham chiếu chéo

- [02-02 Checkpointers](../02-persistence/02-02-checkpointers.md) — resume-safe của error handler và graceful shutdown dựa trên checkpoint
- [08-03 Dùng Graph API](../08-graph-api/08-03-use-graph-api.md) — `add_node`, `Send`, `Command` mà các cơ chế ở đây gắn vào
- [10-01 Runtime Pregel](./10-01-runtime-pregel.md) — retry/timeout/handler áp ở cấp node của runtime Pregel
- Trang tài liệu Fault tolerance: `https://docs.langchain.com/oss/python/langgraph/fault-tolerance`