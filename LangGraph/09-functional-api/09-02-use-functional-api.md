---
title: Dùng Functional API
doc_source: https://docs.langchain.com/oss/python/langgraph/use-functional-api
accessed: 2026-07-30
lc_version: unknown
status: draft
lab:
related:
  - ./09-01-functional-api.md
  - ../04-human-in-the-loop/04-01-interrupts.md
  - ../02-persistence/02-04-add-memory.md
---

# Dùng Functional API — công thức thực hành

> Các công thức chạy được: nhiều đầu vào, song song, ghép với graph, retry/timeout/cache, resume sau lỗi, human-in-the-loop, quản lý checkpoint, streaming.
> Bản chất `@entrypoint`, `@task`, `previous`, determinism, idempotency nằm ở [09-01](./09-01-functional-api.md) — file này không giảng lại, chỉ dùng.

---

## 1. Tổng quan

File này là mặt thực hành của Functional API: cho sẵn từng đoạn code cho từng việc thường gặp. Mọi khái niệm nền — vì sao task được checkpoint, vì sao resume phát lại từ đầu — đã giảng ở [09-01](./09-01-functional-api.md).

Điểm vào đầu tiên cần nhớ: entrypoint nhận đúng một tham số vị trí, nên truyền nhiều thứ thì gói vào một `dict`.

```python
@entrypoint(checkpointer=checkpointer)
def my_workflow(inputs: dict) -> int:
    value = inputs["value"]                        # tách từng phần ra từ dict đầu vào
    another_value = inputs["another_value"]
    ...

my_workflow.invoke({"value": 1, "another_value": 2})   # gói nhiều đầu vào vào một dict
```

---

## 2. Chạy song song các task

### Vai trò

Task trả future ngay khi gọi, nên gọi liền một loạt task rồi mới lấy kết quả thì chúng chạy song song. Hữu ích cho việc I/O — gọi nhiều API LLM cùng lúc thay vì chờ lần lượt.

### Triển khai

```python
@task
def add_one(number: int) -> int:
    return number + 1

@entrypoint(checkpointer=checkpointer)
def graph(numbers: list[int]) -> list[str]:
    futures = [add_one(i) for i in numbers]        # gọi hết một lượt, chưa chờ — các task chạy song song
    return [f.result() for f in futures]           # đến đây mới thu kết quả từng future
```

**Kết quả in ra** (dựng lại):

```
[2, 3, 4]    ← mỗi phần tử +1, ba task chạy đồng thời rồi gom lại
```

Mấu chốt là **gọi hết trước, `.result()` sau**. Nếu `.result()` ngay sau mỗi lời gọi thì thành tuần tự, mất song song.

---

## 3. Ghép với graph và với entrypoint khác

### Gọi một graph từ trong entrypoint

Functional API và Graph API cùng runtime nên gọi lẫn nhau được. Trong entrypoint gọi thẳng `graph.invoke(...)`.

```python
@entrypoint(checkpointer=checkpointer)
def workflow(x: int) -> dict:
    result = graph.invoke({"foo": x})              # gọi graph dựng bằng Graph API
    return {"bar": result["foo"]}
```

**Kết quả in ra:**

```
{'bar': 10}    ← graph nhân đôi foo (5 → 10), entrypoint gói lại thành bar
```

### Gọi một entrypoint từ entrypoint khác

Entrypoint con không cần khai lại checkpointer — nó dùng luôn checkpointer của entrypoint cha.

```python
@entrypoint()                                      # không khai checkpointer, thừa hưởng từ cha
def multiply(inputs: dict) -> int:
    return inputs["a"] * inputs["b"]

@entrypoint(checkpointer=checkpointer)
def main(inputs: dict) -> dict:
    result = multiply.invoke({"a": inputs["x"], "b": inputs["y"]})   # gọi entrypoint con
    return {"product": result}
```

**Kết quả in ra:**

```
{'product': 42}    ← 6 * 7, entrypoint con tính rồi cha gói lại
```

---

## 4. Chính sách của task — retry, timeout, cache

Ba tham số của `@task` (và một phần của `@entrypoint`) xử lý ba nhu cầu riêng khi task chạy lỗi hoặc chạy chậm.

### 4.1 Retry — thử lại khi lỗi

`RetryPolicy(retry_on=...)` cho task tự thử lại khi gặp loại lỗi đã khai. Mặc định `RetryPolicy` đã tối ưu cho một số lỗi mạng cụ thể.

```python
retry_policy = RetryPolicy(retry_on=ValueError)    # chỉ thử lại khi gặp ValueError

@task(retry_policy=retry_policy)
def get_info():
    global attempts
    attempts += 1
    if attempts < 2:
        raise ValueError('Failure')                # lần đầu ném lỗi
    return "OK"                                     # lần hai trả về bình thường
```

**Kết quả in ra:**

```
'OK'    ← lần đầu lỗi, retry_policy thử lại lần hai và thành công
```

### 4.2 Timeout — giới hạn thời gian mỗi lần chạy

Tham số `timeout` (giây hoặc `timedelta`) giới hạn thời gian **một lần chạy async**. Quá giờ thì ném `NodeTimeoutError` (là lớp con của `TimeoutError` chuẩn).

```python
@task(
    timeout=1.0,                                   # mỗi lần chạy tối đa 1 giây
    retry_policy=RetryPolicy(retry_on=NodeTimeoutError),   # quá giờ thì thử lại
)
async def call_api(url: str) -> str:
    await asyncio.sleep(2)                          # cố tình chạy 2 giây → vượt timeout
    return f"result from {url}"

@entrypoint(timeout=5.0)                            # entrypoint cũng có timeout riêng
async def workflow(inputs: dict) -> str:
    return await call_api(inputs["url"])
```

**Kết quả in ra:**

```
Task timed out    ← call_api chạy 2s > 1s nên ném NodeTimeoutError
```

Timeout áp cho **từng lần thử độc lập**, nên mỗi lần retry đồng hồ đếm lại từ đầu.

**!Note:** `timeout` chỉ hỗ trợ task và entrypoint **async**. Đặt `timeout` lên hàm đồng bộ thì LangGraph báo lỗi ngay lúc khai báo — không phải lúc chạy.

### 4.3 Cache — dùng lại kết quả trong khoảng thời gian

`CachePolicy(ttl=...)` giữ kết quả task trong `ttl` giây; gọi lại cùng đầu vào trong khoảng đó thì lấy từ cache, không chạy lại. Cache khai ở cấp entrypoint (`cache=InMemoryCache()`).

```python
@task(cache_policy=CachePolicy(ttl=120))           # giữ kết quả 120 giây
def slow_add(x: int) -> int:
    time.sleep(1)
    return x * 2

@entrypoint(cache=InMemoryCache())
def main(inputs: dict) -> dict[str, int]:
    result1 = slow_add(inputs["x"]).result()       # lần này chạy thật, mất ~1 giây
    result2 = slow_add(inputs["x"]).result()       # cùng x, lấy từ cache, không chờ
    return {"result1": result1, "result2": result2}
```

**Kết quả in ra** (dựng lại):

```
{'result1': 10, 'result2': 10}    ← lần hai lấy cache nên tổng chỉ mất ~1 giây, không phải 2
```

---

## 5. Resume sau lỗi

### Vai trò

Khi một task ném lỗi, các task **đã chạy xong trước đó** đã nằm trong checkpoint. Sửa xong nguyên nhân lỗi rồi gọi lại entrypoint với `None` và **cùng `thread_id`** thì workflow chạy tiếp, không tính lại phần đã xong.

```python
@entrypoint(checkpointer=checkpointer)
def main(inputs, writer):
    slow_task_result = slow_task().result()        # chạy chậm ~1 giây, kết quả được lưu
    get_info().result()                            # lần đầu ném lỗi tại đây
    return slow_task_result

try:
    main.invoke({'any_input': 'foobar'}, config)   # lần đầu: dừng vì get_info lỗi
except ValueError:
    pass

main.invoke(None, config)                          # resume: None + cùng thread_id
```

**Kết quả in ra:**

```
'Ran slow task.'    ← slow_task KHÔNG chạy lại (lấy từ checkpoint), chỉ get_info chạy tiếp
```

Đây chính là mặt lợi cụ thể của việc bọc `slow_task` thành task: resume không phải chờ lại một giây đó.

---

## 6. Human-in-the-loop

### Vai trò

Dừng workflow lại cho người xem/sửa kết quả rồi chạy tiếp. Cơ chế `interrupt` và `Command(resume=...)` là chủ đề riêng, xem [04-01](../04-human-in-the-loop/04-01-interrupts.md). Ở đây chỉ nói phần đặc thù của Functional API: **kết quả các task trước lần dừng được giữ lại**, nên resume không chạy lại chúng.

### Triển khai

Ba task nối tiếp, task giữa dừng chờ người nhập.

```python
@task
def step_1(input_query):
    return f"{input_query} bar"

@task
def human_feedback(input_query):
    feedback = interrupt(f"Please provide feedback: {input_query}")   # dừng, chờ người nhập
    return f"{input_query} {feedback}"

@task
def step_3(input_query):
    return f"{input_query} qux"

@entrypoint(checkpointer=checkpointer)
def graph(input_query):
    result_1 = step_1(input_query).result()        # chạy xong, kết quả được lưu trước khi dừng
    result_2 = human_feedback(result_1).result()   # dừng ở đây
    result_3 = step_3(result_2).result()
    return result_3
```

Chạy với đầu vào `"foo"` rồi resume bằng `Command(resume="baz")`:

**Kết quả in ra** (dựng lại):

```
foo bar baz qux    ← step_1 thêm "bar", người nhập "baz", step_3 thêm "qux"
```

Khi resume, `step_1` không chạy lại — kết quả `"foo bar"` đã nằm trong checkpoint từ trước lần `interrupt`. Đây là hệ quả trực tiếp của determinism (xem [09-01 mục 5](./09-01-functional-api.md)).

---

## 7. Quản lý checkpoint và dựng chatbot nhớ hội thoại

Phần khái niệm `previous` và `entrypoint.final` ở [09-01 mục 4](./09-01-functional-api.md). Dưới đây là các thao tác thực tế.

### 7.1 Xem trạng thái và lịch sử thread

`get_state(config)` cho trạng thái checkpoint mới nhất của một thread; `get_state_history(config)` cho toàn bộ lịch sử.

```python
config = {"configurable": {"thread_id": "1"}}      # có thể thêm checkpoint_id để lấy checkpoint cụ thể
graph.get_state(config)                             # ảnh chụp trạng thái mới nhất
list(graph.get_state_history(config))              # danh sách mọi checkpoint, mới nhất trước
```

`get_state` trả về một `StateSnapshot` — trong đó `values` là dữ liệu hiện tại, `next` là (các) bước sắp chạy, `config` chứa `checkpoint_id` của ảnh chụp này. `get_state_history` trả về danh sách các snapshot như vậy, xếp từ mới đến cũ.

### 7.2 Chatbot nhớ hội thoại

Ghép `previous` (lịch sử tin nhắn cũ) với `entrypoint.final` (trả về phản hồi nhưng lưu cả lịch sử đã nối).

```python
@task
def call_model(messages: list[BaseMessage]):
    return model.invoke(messages)

@entrypoint(checkpointer=checkpointer)
def workflow(inputs: list[BaseMessage], *, previous: list[BaseMessage]):
    if previous:
        inputs = add_messages(previous, inputs)    # nối tin nhắn cũ vào tin nhắn mới
    response = call_model(inputs).result()
    return entrypoint.final(                        # trả về response cho người gọi...
        value=response,
        save=add_messages(inputs, response),       # ...nhưng lưu cả lịch sử để lần sau nhớ tiếp
    )
```

**Kết quả in ra** (dựng lại):

```
lần 1 "hi! I'm bob"     → AIMessage: chào hỏi
lần 2 "what's my name?" → AIMessage: "Your name is Bob."   ← nhớ được nhờ previous + save
```

Điểm cốt lõi: `value` trả cho người gọi chỉ là câu trả lời mới nhất, còn `save` giữ **cả** lịch sử để lần gọi sau `previous` có đủ ngữ cảnh. Không tách hai cái này thì hoặc mất lịch sử, hoặc trả về nguyên cục lịch sử cho người gọi.

---

## 8. Streaming

Functional API dùng chung cơ chế streaming với Graph API; phần đầy đủ là một chủ đề riêng. Ở mức dùng: gọi `stream_events(inputs, config, version="v3")` rồi duyệt theo loại dữ liệu cần.

```python
stream = main.stream_events({"x": 5}, config=config, version="v3")   # v3 là bản mới, bắt buộc ghi rõ
for mode, chunk in stream.interleave("values"):    # lấy các giá trị trả về theo dòng
    print(f"{mode}: {chunk}")
```

**Kết quả in ra:**

```
values: 10    ← giá trị workflow trả về, phát ra theo dòng
```

**!Note:** Viết async trên Python < 3.11 thì `get_stream_writer` không dùng được; phải nhận `writer: StreamWriter` như tham số tiêm của entrypoint (xem bảng tham số ở [09-01 mục 2](./09-01-functional-api.md)).

---

## Tham chiếu chéo

- [09-01 Functional API](./09-01-functional-api.md) — bản chất `@entrypoint`, `@task`, `previous`, `entrypoint.final`, determinism, idempotency.
- [04-01 Interrupts](../04-human-in-the-loop/04-01-interrupts.md) — cơ chế `interrupt` và `Command(resume=...)` dùng ở mục 6.
- [02-04 Bộ nhớ](../02-persistence/02-04-add-memory.md) — bộ nhớ dài hạn qua `store`, dùng chung giữa các thread.