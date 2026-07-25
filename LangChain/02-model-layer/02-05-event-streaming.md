---
title: Event streaming
doc_source: https://docs.langchain.com/oss/python/langchain/event-streaming
accessed: 2026-07-25
lc_version: "langchain>=1.3 (v3); langchain>=1.3.2 (transformer trên middleware)"
status: draft
lab:
related:
  - ./02-04-streaming.md
---

# Event streaming (`stream_events`)

> API streaming được khuyến nghị cho ứng dụng mới, có từ LangChain v1.3.
> Tầng bên dưới vẫn là cơ chế của [Streaming / Pregel](./02-04-streaming.md).

---

## 1. Định nghĩa

`stream_events(..., version="v3")` **không trả về một dòng chunk**. Nó trả về một **object run** chứa nhiều **projection** — mỗi projection là một khung nhìn riêng vào cùng một lần chạy, đọc độc lập với nhau.

```python
stream = agent.stream_events(inputs, version="v3")

for message in stream.messages:      # nhánh message
    for delta in message.text:       # nhánh text bên trong message đó
        print(delta, end="", flush=True)

final_state = stream.output          # nhánh state cuối
```

**Output** **:

```
It's always sunny in San Francisco!
```

Chữ chảy ra mượt, không mảnh vỡ nào lộ ra ngoài, vì `.text` đã gộp sẵn phần văn bản và bỏ qua tool call chunk lẫn metadata.

So sánh trực tiếp với `stream()`: **cùng dữ liệu nguồn, khác cách lấy ra**. Không phải quan hệ kế thừa giữa hai class, mà là **quan hệ tầng** — `stream_events()` bọc bên trên và phụ thuộc vào tầng dưới.

---

## 2. Projection — khái niệm cốt lõi

**Projection** (phép chiếu) là một nhánh dữ liệu đã được phân loại sẵn, đặt tên sẵn, có kiểu rõ ràng.

Nhớ lại [mục 4.0 của 02-04](./02-04-streaming.md#40-nền-tảng-cần-nắm-trước): LLM sinh output từng token, nên mọi thứ đến ở dạng mảnh vỡ, và mảnh vỡ lẫn với kết quả chốt trên cùng một dòng. Sự thật kỹ thuật đó **không thay đổi** ở event streaming — model vẫn sinh từng token như cũ.

Thứ thay đổi là **ai chịu trách nhiệm phân loại**:

| | `stream()` | `stream_events()` |
|---|---|---|
| Dữ liệu đến | Một dòng trộn lẫn mọi loại | Đã tách sẵn thành nhánh |
| Ai phân loại | Người viết code, bằng `if chunk["type"] == ...` | Thư viện |
| Lấy text | Lọc token → lọc `content_blocks` → lọc `type == "text"` | `message.text` |
| Lấy tool call đã chốt | Bật thêm mode `updates`, đào vào `update["messages"][-1]` | `message.tool_calls.get()` |

->: `stream()` là một băng chuyền chung, mọi thứ chảy qua và bạn phải tự nhặt. `stream_events()` là hệ thống chia van lắp sau băng chuyền đó — mở van nào thì ra thứ đó.

**Hệ quả thực tế:** phần lớn đoạn code phân loại thủ công ở 02-04 biến mất, không phải vì vấn đề biến mất, mà vì nó được đẩy vào thư viện.

---

## 3. Bảng projection

### Projection cấp run

| Projection | Nội dung |
|---|---|
| `stream.messages` | Luồng message của model — **một luồng cho mỗi lần gọi LLM** |
| `stream.values` | Snapshot state |
| `stream.output` | State cuối cùng của agent |
| `stream.tool_calls` | Vòng đời **thực thi** tool: input, output delta, output cuối, lỗi |
| `stream.subagents` | Chỉ các `create_agent` **có đặt tên** |
| `stream.subgraphs` | **Mọi** graph lồng nhau |
| `stream.extensions` | Projection do transformer tự viết sinh ra |
| `for event in stream` | Event protocol thô, đầy đủ envelope, truy cập được mọi kênh |

### Projection cấp message

`stream.messages` sinh ra các object `ChatModelStream`. Mỗi cái có bốn nhánh con:

| Thuộc tính | Nội dung |
|---|---|
| `.text` | Delta văn bản, và văn bản cuối |
| `.reasoning` | Delta suy luận (chỉ với model phát ra reasoning block) |
| `.tool_calls` | Chunk tham số tool call **đang sinh**, và tool call đã chốt |
| `.output` | Object message hoàn chỉnh sau khi lần gọi model kết thúc |

Ngoài ra `message.node` cho biết message này đến từ node nào.

### Hai chế độ đọc — điểm dễ bỏ sót nhất

Mỗi projection đồng bộ đọc được theo **hai cách**, tùy nhu cầu:

| Cách đọc | Cú pháp | Cho ra |
|---|---|---|
| Lặp | `for delta in message.text` | Delta thời gian thực |
| Rút cạn | `str(message.text)` | Văn bản hoàn chỉnh |
| Rút cạn | `message.tool_calls.get()` | Tool call đã chốt |

Đây chính là chỗ giải quyết bài toán "hai lớp dữ liệu" ở [02-04 mục 4.2](./02-04-streaming.md#42-tool-call--hai-lớp-dữ-liệu-tách-rời): không cần bật hai mode, không cần cộng dồn chunk thủ công. Cùng một đối tượng, lặp thì ra mảnh vỡ, rút cạn thì ra kết quả chốt.

**Khác biệt Python / TypeScript.** Lấy số token: Python đọc `message.output.usage_metadata`; TypeScript có `message.usage` riêng. Ghi nhớ nếu làm cả hai phía.

---

## 4. Các tình huống thực tế

Bốn mục dưới đây đặt song song với [mục 4 của 02-04](./02-04-streaming.md#4-các-tình-huống-thực-tế) để đối chiếu trực tiếp.

> **Quy ước về output trong file này.** Trang doc event streaming **không in output mẫu** cho bất kỳ ví dụ nào, khác với trang streaming vốn có output cho gần hết. Các khối output dưới đây do tôi **dựng lại** từ cùng ví dụ weather, suy ra từ cấu trúc dữ liệu doc mô tả. Chúng gắn nhãn ** và cần đối chiếu khi chạy lab. Output ở [02-04](./02-04-streaming.md) thì ngược lại, lấy nguyên từ doc.

---

### 4.1 Token suy luận (reasoning / thinking)

**Bài toán.** Giống hệt 02-04: hiển thị phần suy nghĩ nội bộ của model, tách bạch khỏi câu trả lời.

**Cơ chế bên dưới.** Reasoning dùng **cùng hình dạng** với text — cũng là một projection delta, đọc theo cùng cách. Khác biệt duy nhất là nó chỉ có dữ liệu khi model thực sự phát ra reasoning block.

```python
stream = agent.stream_events(inputs, version="v3")

for message in stream.messages:
    for delta in message.reasoning:
        print(f"[thinking] {delta}", end="", flush=True)

    for delta in message.text:
        print(delta, end="", flush=True)
```

**Output** **:

```
[thinking] The user is asking about the weather in San Francisco. [thinking] I have a tool
[thinking]  available to get this information. [thinking] Let me call the get_weather tool.
The weather in San Francisco is: It's always sunny in San Francisco!
```

Nhãn `[thinking]` lặp ở **mỗi delta**, không phải mỗi dòng, vì lệnh in nằm trong vòng lặp delta. Muốn nhãn chỉ hiện một lần thì in trước vòng lặp.

**Đối chiếu với 02-04 mục 4.1** — cùng một việc, biến mất ba thứ:

| Việc phải làm ở `stream()` | Ở `stream_events()` |
|---|---|
| `isinstance(token, AIMessageChunk)` | Không cần — `stream.messages` đã chỉ chứa message của model |
| Lọc `content_blocks` theo `type == "reasoning"` | Không cần — `.reasoning` là nhánh riêng |
| Đào `block["reasoning"]` lấy nội dung | Không cần — `delta` đã là nội dung |

**!Note.** Reasoning vẫn phải được bật ở cấu hình model. Quên bật thì `.reasoning` không có delta nào, code chạy im lặng không báo lỗi — y hệt bẫy ở 02-04.

---

### 4.2 Tool call — hai projection, đừng nhầm

**Bài toán.** Đây là chỗ event streaming khác `stream()` nhiều nhất, và cũng là chỗ dễ nhầm nhất trong chính event streaming.

Có **hai** projection tên gần giống nhau nhưng thuộc hai giai đoạn hoàn toàn khác:

| | `message.tool_calls` | `stream.tool_calls` |
|---|---|---|
| Cấp | Trong một message | Cấp run |
| Giai đoạn | Model **đang sinh** tool call | Tool **đang chạy** sau khi call phát ra |
| Trả lời | Model định gọi gì, tham số hình thành ra sao | Tool chạy thế nào, ra gì, có lỗi không |
| Tương ứng ở `stream()` | `token.tool_call_chunks` | **Không có** |

**`stream.tool_calls` là năng lực mới**, không có tương đương ở `stream()`. Mỗi phần tử là một lần thực thi tool, với năm thuộc tính:

| Thuộc tính | Nội dung |
|---|---|
| `.tool_name` | Tên tool đang chạy |
| `.input` | Tham số đầu vào đã chốt |
| `.output_deltas` | Output chảy ra dần (với tool có stream) |
| `.output` | Output cuối cùng |
| `.error` | Lỗi, nếu có |

```python
stream = agent.stream_events(inputs, version="v3")

# Giai đoạn 1 — model đang sinh tool call
for message in stream.messages:
    for chunk in message.tool_calls:
        print(f"tool call chunk: {chunk}")

    finalized = message.tool_calls.get()      # rút cạn → tool call đã chốt
    if finalized:
        print(f"finalized tool calls: {finalized}")

# Giai đoạn 2 — tool đang thực thi
for call in stream.tool_calls:
    print(f"{call.tool_name}({call.input})")
    for delta in call.output_deltas:
        print(delta, end="", flush=True)
    print(call.output, call.error)
```

**Output giai đoạn 1** ** — mảnh vỡ tham số, rồi kết quả rút cạn:

```
tool call chunk: {'name': 'get_weather', 'args': '',       'id': 'call_D3Or...', 'index': 0}
tool call chunk: {'name': None,          'args': '{"',     'id': None, 'index': 0}
tool call chunk: {'name': None,          'args': 'city',   'id': None, 'index': 0}
tool call chunk: {'name': None,          'args': '":"',    'id': None, 'index': 0}
tool call chunk: {'name': None,          'args': 'Boston', 'id': None, 'index': 0}
tool call chunk: {'name': None,          'args': '"}',     'id': None, 'index': 0}
finalized tool calls: [{'name': 'get_weather', 'args': {'city': 'Boston'}, 'id': 'call_D3Or...'}]
```

Sáu dòng đầu **giống hệt** output ở [02-04 mục 4.2](./02-04-streaming.md#42-tool-call--hai-lớp-dữ-liệu-tách-rời): cùng dữ liệu, chỉ khác đường lấy ra. Dòng cuối mới là chỗ khác. Ở `stream()` phải bật thêm mode `updates` mới có nó; ở đây chỉ cần gọi `.get()` trên chính đối tượng vừa lặp xong.

**Output giai đoạn 2** **:

```
get_weather({'city': 'Boston'})
It's always sunny in Boston!
It's always sunny in Boston! None
```

Dòng 1 là `.tool_name` kèm `.input`. Dòng 2 là `.output_deltas` chảy ra. Dòng 3 là `.output` và `.error` in cạnh nhau, `None` nghĩa là không lỗi.

**Lưu ý về `.output_deltas`.** `get_weather` là hàm thường trả về một chuỗi, không stream, nên nhiều khả năng chỉ có **một** delta duy nhất. Muốn thấy delta chảy thật thì tool phải là generator hoặc có cơ chế stream riêng. Doc không nói rõ điểm này.

**Vì sao `.error` đáng giá.** Ở `stream()`, tool lỗi thì chỉ thấy `ToolMessage` chứa nội dung lỗi lẫn trong dòng `updates` — phải tự phân biệt "kết quả bình thường" với "thông báo lỗi". Ở đây lỗi là một trường riêng, kiểm tra bằng một điều kiện.

---

### 4.3 Sub-agent

**Bài toán.** Giống 02-04: nhiều LLM cùng phát token, cần biết đoạn chữ đang chảy là của agent nào.

**Cơ chế bên dưới.** Khi một `create_agent` gọi một `create_agent` khác — thường qua tool bọc ngoài, [xem lại kiến trúc ba tầng ở 02-04 mục 4.4](./02-04-streaming.md#44-sub-agent--biết-token-đến-từ-agent-nào) — event của agent bên trong chảy ở **namespace lồng**. Tham số `name=` truyền vào `create_agent` là thứ định danh agent đó trong luồng.

Điểm khác biệt lớn: `stream.subagents` **chỉ chứa các `create_agent` có tên**, nên không phải lọc subgraph thường ra. Mỗi handle có:

| Thuộc tính | Nội dung |
|---|---|
| `.messages` / `.values` / `.tool_calls` / `.output` | Bộ projection **riêng** của agent con |
| `.name` | Tên đã đặt lúc `create_agent` |
| `.cause` | Tool call đã dispatch agent con đó |

`.cause` trả lời câu hỏi "vì sao agent này được gọi" — thứ mà `stream()` hoàn toàn không có.

```python
stream = supervisor.stream_events(inputs, version="v3")

for subagent in stream.subagents:
    print(f"{subagent.name}: ", end="")
    for message in subagent.messages:
        for token in message.text:
            print(token, end="", flush=True)
    print()
```

**Output** **:

```
weather_agent: Boston weather right now: Sunny.
```

**Chỉ một dòng, và đây là điểm cần chú ý nhất của mục này.** `stream.subagents` chỉ chứa **agent con**; `supervisor` là agent gốc nên không nằm trong đó. Muốn hiện cả output của supervisor thì phải đọc thêm `stream.messages` ở cấp run.

Đối chiếu với output ở [02-04 mục 4.4](./02-04-streaming.md#44-sub-agent--biết-token-đến-từ-agent-nào): bản đó in cả supervisor lẫn weather_agent vì `stream.messages` gộp mọi LLM. Hai cách cho hai bức tranh khác nhau, không cái nào sai:

| Muốn gì | Dùng |
|---|---|
| Chỉ theo dõi agent con | `stream.subagents` |
| Toàn bộ, kể cả agent gốc | `stream.messages` |
| Cả hai, có nhãn | `stream.messages`, phân biệt bằng `message.node` |

Suy luận "supervisor không nằm trong `subagents`" đến từ định nghĩa của doc: projection này dành cho *agent con được dispatch qua tool*, và mỗi handle có `.cause` là tool call đã gọi nó — agent gốc thì không có tool call nào gọi. **Doc không khẳng định trực tiếp**, cần lab.

**Đối chiếu với 02-04 mục 4.4** — ba bước thủ công còn lại một:

| Bước ở `stream()` | Ở `stream_events()` |
|---|---|
| Đặt `name=` cho từng agent | **Vẫn cần** — không có tên thì không lên `subagents` |
| Bật `subgraphs=True` | Không cần |
| Đọc `metadata["lc_agent_name"]` | Không cần — dùng `subagent.name` |

**Phân biệt `subagents` và `subgraphs`.** `subagents` là khung nhìn hẹp cho `create_agent` có tên; `subgraphs` phủ **mọi** graph lồng. Subgraph `StateGraph` thường gọi từ tool cũng hiện ở `subgraphs` — đặt tên bằng `.compile(name=...)` để có nhãn ở `subagent.graph_name`. Chọn cái nào tùy UI cần gì.

---

### 4.4 Đọc nhiều projection cùng lúc

**Bài toán.** Đây là vấn đề **mới sinh ra** từ chính thiết kế projection. Tách thành nhiều nhánh thì đọc từng nhánh rất gọn, nhưng khi cần đọc đồng thời — vừa hiện text vừa hiện trạng thái tool — phải có cách phối hợp.

Ba cách, chọn theo ngữ cảnh:

| Ngữ cảnh | Cách làm |
|---|---|
| Async, thực sự song song | `astream_events` + `asyncio.gather` |
| Đồng bộ | `stream.interleave(...)` |
| Kênh không có projection sẵn | Lặp event thô |

**Async — chạy song song thật:**

```python
stream = await agent.astream_events(inputs, version="v3")

async def consume_messages():
    async for message in stream.messages:
        print(await message.text)

async def consume_tool_calls():
    async for call in stream.tool_calls:
        print(call.tool_name, call.input)

await asyncio.gather(consume_messages(), consume_tool_calls())
```

**Đồng bộ — trộn về một vòng lặp:**

```python
for name, item in stream.interleave("messages", "tool_calls", "values"):
    if name == "messages":
        print(item.text)
    elif name == "tool_calls":
        print(item.tool_name, item.input)
    elif name == "values":
        print(item)
```

**Output** ** — ba nhánh đan xen theo đúng thứ tự thời gian:

```
messages    (delta text dang chay)
tool_calls  get_weather {'city': 'Boston'}
values      {'messages': [HumanMessage(...), AIMessage(...)]}
messages    (delta text cau tra loi cuoi)
values      {'messages': [..., ToolMessage(...), AIMessage(...)]}
```

`interleave` **không gom nhóm**, nó giữ nguyên thứ tự sự kiện xảy ra. Vì vậy `messages` xuất hiện rải rác nhiều lần, còn `values` chỉ hiện tại các điểm state thay đổi.

`interleave` trả về cặp `(tên projection, phần tử)`. Nhìn hình dạng thì giống hệt cách phân loại thủ công ở `stream()` — nhưng khác ở chỗ **phần tử đã có kiểu rõ ràng**, không phải dict thô phải tự đào.

**Event thô — lối thoát cuối:**

```python
for event in stream:
    print(event["method"], event["params"]["namespace"], event["params"]["data"])
```

**Output** ** — ba trường in cạnh nhau, cột giữa là namespace:

```
on_chat_model_stream  ()                  {...}
on_tool_start         ()                  {...}
on_chat_model_stream  ('weather_agent',)  {...}
```

Namespace rỗng `()` là graph gốc, tuple khác rỗng là subgraph. **Đây chính là dữ liệu thô mà `stream.subagents` dựa vào để phân tách.** Doc không liệt kê danh sách giá trị `method`, nên tên event ở trên là suy đoán, cần lab để lấy danh sách thật.

Dùng khi cần kênh chưa có projection, hoặc cần soi toàn bộ envelope để debug.

---

## 5. Transformer — thay thế `get_stream_writer()`

**Bài toán.** Cần một nhánh dữ liệu không có sẵn: tiến độ truy xuất, artifact sinh ra giữa chừng, event nghiệp vụ riêng. -> transformer dùng để gửi thông tin từ bên trong tool ra màn hình người dùng, trong lúc tool đang chạy.

**Cách làm.** Viết **stream transformer**, kết quả đọc ở `stream.extensions["<tên>"]`:

```python
stream = agent.stream_events(inputs, version="v3", transformers=[ToolActivityTransformer])

for activity in stream.extensions["tool_activity"]:
    print(activity)
```

**Output** ** — nội dung hoàn toàn do transformer quyết định:

```
{'tool': 'get_weather', 'status': 'started'}
{'tool': 'get_weather', 'status': 'finished', 'duration_ms': 12}
```

Khóa `"tool_activity"` là **tên do transformer tự đặt**, không phải tên cố định của thư viện. Viết transformer khác thì khóa khác.

**Vì sao hơn `get_stream_writer()`.** Ở `stream()`, muốn đẩy dữ liệu tùy biến ra ngoài thì phải gọi `get_stream_writer()` **bên trong thân tool** — và tool đó lập tức không gọi được ngoài ngữ cảnh LangGraph, tức là mất khả năng unit test độc lập. Transformer nằm **ngoài** thân tool, nên tool giữ nguyên là một hàm Python bình thường.

### Gắn transformer vào agent một lần
 
Cần `langchain>=1.3.2`.
 
**Vấn đề trước đã.** Nếu khai báo transformer tại chỗ gọi, mọi nơi gọi agent đều phải nhớ khai báo lại:
 
```python
# file chat.py
stream = agent.stream_events(inputs, version="v3",
                             transformers=[ToolActivityTransformer])
 
# file mobile_api.py
stream = agent.stream_events(inputs, version="v3",
                             transformers=[ToolActivityTransformer])
 
# file background_job.py — người viết sau không biết có thứ này
stream = agent.stream_events(inputs, version="v3")   # thiếu, không ai báo lỗi
```
 
Chỗ thứ ba thiếu nhánh dữ liệu. Code chạy bình thường, chỉ là mất dữ liệu. Đổi ví dụ này thành `PIIMiddleware` thì hậu quả rõ hơn nhiều: chỗ nào quên là chỗ đó email khách hàng chảy thẳng ra màn hình.
 
**Cách xử lý — gói transformer vào một middleware, gắn vào agent:**
 
```python
class ToolActivityMiddleware(AgentMiddleware):
    transformers = (ToolActivityTransformer,)
 
agent = create_agent(model="gpt-5-nano", tools=[get_weather],
                     middleware=[ToolActivityMiddleware()])
```
 
Sau đó mọi nơi gọi chỉ cần viết `agent.stream_events(inputs, version="v3")`. Nhánh dữ liệu luôn có, không thể quên vì không còn gì để quên.
 
Middleware ở đây **không xử lý dữ liệu gì cả**, nó chỉ là cái vỏ để đăng ký. Transformer mới là thứ làm việc thật.
 
> `ToolActivityMiddleware` và `ToolActivityTransformer` là **tên ví dụ trong doc**, không có sẵn trong thư viện. Tìm sẽ không thấy. Ví dụ có thật của cùng cơ chế này là `PIIMiddleware` ở mục 6.
 
 
**Vì sao phải mỗi tầng một bản riêng.** Giả sử transformer của bạn đếm số lần gọi tool.
 
Dùng chung một bản:
 
```
agent chính gọi tool  -> bộ đếm = 1
agent con gọi tool    -> bộ đếm = 2      (lẫn rồi, không tách được ai gọi bao nhiêu)
```
 
Mỗi tầng một bản:
 
```
bản của agent chính -> 1
bản của agent con   -> 1
```
 
Thư viện gọi cái khuôn **một lần cho mỗi tầng**, và nói cho biết đang đúc cho tầng nào. Thông tin "tầng nào" chính là thứ đã gặp ở [mục 4.4](#44-đọc-nhiều-nhánh-cùng-lúc): rỗng `()` là agent chính, có nội dung như `('weather_agent',)` là đang ở trong agent con.
 
**Về dòng `Callable[[tuple[str, ...]], StreamTransformer]` trong doc.** Đây chỉ là cách viết tắt của: *một thứ gọi được, đưa vào một danh sách chữ, nhận về một transformer*. Tên class thỏa điều kiện này, nên đưa tên class là xong — không phải viết thêm gì.
 
### Thứ tự chạy
 
Dữ liệu đi qua các transformer **lần lượt như một dây chuyền**. Ai đứng sau xử lý phần đầu ra của người đứng trước:
 
```
dữ liệu thô
   |
   v  1. transformer tool call có sẵn của thư viện
   |
   v  2. transformer gắn trên middleware (theo thứ tự middleware)
   |
   v  3. transformer truyền thẳng vào create_agent
   |
   v  ra ngoài
```
 
Nhóm 3 đứng cuối nên **được sửa sau cùng**, muốn ghi đè gì cũng được. Đó là ý của câu "quyền quyết định sau cùng" trong doc — không phải quyền hạn gì đặc biệt, chỉ là vị trí cuối dây chuyền.
 
---
 
## 6. Che thông tin cá nhân trên đường truyền
 
`PIIMiddleware` với `apply_to_output=True` dùng chính cơ chế transformer ở mục 5.
 
```python
agent = create_agent(
    model="gpt-5-nano",
    tools=[],
    middleware=[PIIMiddleware("email", strategy="redact", apply_to_output=True)],
)
```
 
**Kết quả in ra** (dựng lại) — so sánh có và không bật:
 
```
# khong bat: nguoi dung van thay email that
Lien he: nguyenvana@example.com
 
# co bat: che ngay tren duong truyen
Lien he: [REDACTED]
```
 
Chuỗi thay thế cụ thể tùy theo cấu hình. Doc không in ví dụ nên dạng `[REDACTED]` chỉ là minh họa.
 
**Vì sao cần.** Cách che thông thường chỉ chạy **sau khi** model nói xong. Nhưng trong lúc model đang nói, chữ đã chảy ra màn hình rồi — thông tin cá nhân kịp lọt qua trong khoảng đó. Transformer bịt đúng khoảng này: quét và che **trước khi** dữ liệu rời khỏi hệ thống.
 
Phạm vi quét: từng mẩu chữ, tham số tool, kết quả tool, và ảnh chụp trạng thái.
 
**Đây là thứ chỉ có ở event streaming.** Với hệ thống xử lý dữ liệu khách hàng, riêng điểm này có thể quyết định chọn API, không cần bàn tới cú pháp.
 
---
 
## 7. Bảng so sánh tổng hợp
 
| | `stream()` | `stream_events()` |
|---|---|---|
| Vị trí | Tầng dưới, sát bộ máy | Tầng trên, bọc ngoài |
| Trả về gì | Một dòng dữ liệu trộn lẫn | Một đối tượng nhiều nhánh |
| Ai phân loại | Người viết code | Thư viện |
| Mẩu vỡ / bản hoàn chỉnh | Hai chế độ riêng, phải bật cả hai | Cùng một thứ, đọc hai kiểu |
| Theo dõi tool chạy | Không có | `stream.tool_calls`, có cả ô lỗi |
| Agent con | Bật công tắc rồi tự đọc nhãn | `stream.subagents`, có `.name` và `.cause` |
| Dữ liệu riêng | Ghi từ trong thân tool | Transformer, ngoài thân tool |
| Che thông tin cá nhân | Không có | `PIIMiddleware(apply_to_output=True)` |
| Dừng chờ người duyệt | Có, mục 4.3 của 02-04 | **Doc không đề cập** |
| Phiên bản | `version="v2"`, cần langgraph≥1.1 | `version="v3"`, cần langchain≥1.3 |
 
### Chuyển code từ cách cũ sang cách mới
 
| Chế độ cũ | Nhánh tương ứng |
|---|---|
| `messages` | `stream.messages`, rồi `.text` / `.reasoning` / `.tool_calls` |
| `updates` | `stream.values` (ảnh chụp trạng thái); `message.output` (câu hoàn chỉnh) |
| `custom` | `stream.extensions[...]`, qua transformer |
| Công tắc tầng lồng + đọc nhãn | `stream.subagents` |
| *(không có)* | `stream.tool_calls` — theo dõi tool chạy |
 
---
 
## 8. Nên chọn cái nào
 
Chọn `stream_events()` khi: làm dự án mới; giao diện cần đọc nhiều luồng độc lập; cần theo dõi tool chạy kể cả khi lỗi; có yêu cầu che thông tin cá nhân.
 
Giữ [`stream()`](./02-04-streaming.md) khi: code cũ đang chạy ổn; cần can thiệp sát bộ máy bên dưới; hoặc **cần tính năng dừng chờ người duyệt** — cho tới khi xác minh được event streaming làm việc này thế nào.
 
---
 
## Cần kiểm chứng thêm
 
- [ ] **Dừng chờ người duyệt.** Trang doc event streaming không nhắc gì tới việc này, trong khi trang streaming có hẳn một mục. Đây là khoảng trống thật của tài liệu, không phải đọc sót. Cần chạy thử xem `stream_events` bắt tín hiệu dừng ở đâu.
- [ ] `stream.values` có thay được chế độ `updates` không. Doc gọi nó là "ảnh chụp trạng thái", nghiêng về nghĩa "toàn bộ trạng thái" hơn là "phần vừa thay đổi". Bảng chuyển đổi ở mục 7 chỉ là **giả thiết**.
- [ ] Vấn đề "câu nói của model chạy trong middleware không vào trạng thái" ở [02-04 mục 4.2](./02-04-streaming.md#42-tool-call--hai-lớp-dữ-liệu-tách-rời) có tự hết không. Suy luận: doc nói `stream.messages` cho một luồng riêng **cho mỗi lần gọi model**, nên về lý thuyết gồm cả model trong middleware. **Doc không khẳng định**.
- [ ] Cách viết một transformer hoàn chỉnh — nằm ở trang LangGraph "Build your own projection".
- [ ] `stream()` và `stream_events()` có dùng chung trong một lần chạy được không.
- [ ] **Toàn bộ khối kết quả in ra trong file này** đều do tôi dựng lại, vì doc không in mẫu nào. Ba chỗ rủi ro cao nhất: hình dạng của `message.tool_calls`, danh sách tên sự kiện ở phần dữ liệu gốc, và việc agent chính có nằm trong `stream.subagents` hay không.
---
 
## Tham chiếu chéo
 
- [02-04 Streaming](./02-04-streaming.md) — tầng bên dưới
- Build your own projection: `/oss/python/langgraph/event-streaming#build-your-own-projection`
- PII detection: `/oss/python/langchain/middleware/built-in#pii-detection`
- Frontend streaming patterns: `/oss/python/langchain/frontend/overview`
 
---

## 6. Che PII trên đường truyền

`PIIMiddleware` với `apply_to_output=True` dùng chính cơ chế transformer ở mục 5.

```python
agent = create_agent(
    model="gpt-5-nano",
    tools=[],
    middleware=[PIIMiddleware("email", strategy="redact", apply_to_output=True)],
)
```

**Output** ** — so sánh có và không có `apply_to_output`:

```
# apply_to_output=False (mac dinh): nguoi doc live van thay email tho
Lien he: nguyenvana@example.com

# apply_to_output=True: che ngay tren duong truyen
Lien he: [REDACTED]
```

Chuỗi thay thế cụ thể phụ thuộc `strategy=`. Doc không in ví dụ nên dạng `[REDACTED]` chỉ là minh họa.

**Vì sao tồn tại.** Redact ở tầng state trong hook `after_model` chỉ chạy **sau khi** model xong. Trong khoảng thời gian model đang stream, PII thô đã kịp chảy tới người đọc live. Transformer bịt đúng khoảng đó — quét PII khỏi wire output **trước khi rời khỏi run**.

Phạm vi quét: text delta, tham số tool call, output của tool, snapshot state.

**Đây là năng lực chỉ có ở nhánh event streaming.** Với hệ thống xử lý dữ liệu khách hàng, đây có thể là lý do quyết định chọn API, độc lập với mọi cân nhắc về cú pháp.

---

## 7. Đối chiếu tổng hợp với `stream()`

| | `stream()` | `stream_events()` |
|---|---|---|
| Tầng | Pregel, cấp thấp | Bọc bên trên |
| Hình dạng trả về | Dòng chunk đơn | Object run nhiều projection |
| Phân loại dữ liệu | Thủ công theo `chunk["type"]` | Sẵn theo projection |
| Mảnh vỡ / kết quả chốt | Hai mode riêng, phải bật cả hai | Cùng đối tượng, lặp hoặc rút cạn |
| Vòng đời thực thi tool | Không có | `stream.tool_calls` với `.error` |
| Sub-agent | `subgraphs=True` + đọc metadata | `stream.subagents` với `.name`, `.cause` |
| Dữ liệu tùy biến | `get_stream_writer()` trong thân tool | Transformer, ngoài thân tool |
| Che PII output | Không có | `PIIMiddleware(apply_to_output=True)` |
| Human-in-the-loop | Có, mục 4.3 của 02-04 | **Doc không đề cập** |
| Version | `version="v2"` (langgraph≥1.1) | `version="v3"` (langchain≥1.3) |

### Ánh xạ khái niệm khi chuyển đổi code

| `stream_mode` cũ | Projection tương ứng |
|---|---|
| `messages` | `stream.messages` → `.text` / `.reasoning` / `.tool_calls` |
| `updates` | `stream.values` (snapshot state); `message.output` (message hoàn chỉnh) |
| `custom` | `stream.extensions[...]` qua transformer |
| `subgraphs=True` + `lc_agent_name` | `stream.subagents` |
| *(không có)* | `stream.tool_calls` — vòng đời thực thi tool |

---

## 8. Kết luận cho việc chọn API

Chọn `stream_events()` khi: xây dựng mới; UI cần tiêu thụ nhiều luồng độc lập; cần theo dõi vòng đời thực thi tool kể cả lỗi; có yêu cầu che PII trên đường truyền.

Giữ [`stream()`](./02-04-streaming.md) khi: code cũ đang chạy ổn; cần thao tác sát tầng Pregel; hoặc **cần human-in-the-loop** — cho tới khi xác minh được event streaming xử lý interrupt thế nào.

---
