---
title: Streaming
doc_source: https://docs.langchain.com/oss/python/langchain/streaming
accessed: 2026-07-22
lc_version: "langgraph>=1.1 (bắt buộc nếu dùng version='v2')"
status: draft
lab:
related:
  - ./02-05-event-streaming.md
---

# Streaming (`stream` / `astream`)

> API streaming **cấp thấp**, kế thừa trực tiếp từ tầng Pregel của LangGraph.
> Trang doc gốc đã gắn khuyến nghị: ứng dụng mới nên dùng [Event streaming](./02-05-event-streaming.md).

---

## 1. Định nghĩa

`stream()` phát ra **một dòng chunk duy nhất** trong suốt quá trình agent chạy. Mọi loại dữ liệu — token của model, cập nhật trạng thái sau mỗi bước, dữ liệu tự định nghĩa — đều đi chung dòng này.

Hệ quả về mặt lập trình: người viết code phải **tự phân loại** từng chunk trước khi xử lý. Đây là điểm khác biệt bản chất so với event streaming, nơi dữ liệu được tách sẵn thành các nhánh riêng.

Vị trí trong kiến trúc:

```
create_agent  →  LangGraph (Pregel)  →  stream()  →  chunk thô
                                            ↑
                                  stream_events() bọc bên trên
```

`stream()` **không phụ thuộc** vào `stream_events()`. Chiều ngược lại thì có.

---

## 2. `stream_mode` — ba kênh dữ liệu

Truyền một hoặc nhiều mode dưới dạng list.

| Mode | Phát ra cái gì | Dùng khi |
|---|---|---|
| `updates` | Cập nhật state sau **mỗi bước** của agent. Nhiều node chạy trong cùng một bước thì phát riêng từng cập nhật. | Theo dõi tiến trình; lấy message đã hoàn chỉnh (đã parse tool call) |
| `messages` | Tuple `(token, metadata)` từ **mọi node có gọi LLM** | Hiển thị token chảy ra màn hình |
| `custom` | Dữ liệu tùy ý do chính bạn ghi vào từ trong node/tool | Báo tiến độ nghiệp vụ: "đã lấy 10/100 bản ghi" |

Ba mode này là **ba lát cắt khác nhau của cùng một lần chạy**, không loại trừ nhau. `stream_mode=["messages", "updates"]` là cặp hay dùng nhất: `messages` cho token chảy mượt, `updates` cho message đã hoàn chỉnh.

### Kênh `custom` ghi từ đâu

Dùng `get_stream_writer()` bên trong tool. Ràng buộc cần biết trước khi dùng: tool có `get_stream_writer()` sẽ **không gọi được ngoài ngữ cảnh thực thi của LangGraph** — ảnh hưởng trực tiếp tới việc unit test tool đó độc lập.

---

## 3. Định dạng output — v1 và v2

Đây là điểm dễ nhầm nhất của trang doc này.

**v1** (mặc định hiện tại): khi dùng nhiều mode, mỗi chunk là tuple `(mode, data)`, phải unpack thủ công.

**v2** (`version="v2"`, cần LangGraph ≥ 1.1): mọi chunk là dict `StreamPart` với ba khóa `type`, `ns`, `data` — **cùng một hình dạng** bất kể dùng mode nào hay bao nhiêu mode.

```python
for chunk in agent.stream(inputs, stream_mode=["updates", "custom"], version="v2"):
    if chunk["type"] == "updates":
        ...
    elif chunk["type"] == "custom":
        ...
```

v2 còn thay đổi cả `invoke()`: trả về object `GraphOutput` có `.value` (state) và `.interrupts` (tuple các Interrupt, rỗng nếu không có), tách bạch state khỏi metadata của interrupt.

> **Cảnh báo về đánh số phiên bản:** `version="v2"` của `stream()` và `version="v3"` của `stream_events()` là **hai trục độc lập**. v3 không phải bản kế tiếp của v2 trong cùng một API.

---

## 4. Các tình huống thực tế
 
### 4.0 Nền tảng cần nắm trước
 
Bốn tình huống dưới đây đều bắt nguồn từ **một sự thật kỹ thuật duy nhất**: LLM sinh output **từng token một**, không sinh trọn gói.
 
Điều đó kéo theo ba hệ quả chi phối toàn bộ cách thiết kế streaming:
 
**Hệ quả 1 — mọi thứ đều đến ở dạng mảnh vỡ.** Không chỉ văn bản. Tham số của tool call là một chuỗi JSON, mà JSON cũng do model sinh ra token by token, nên nó cũng vỡ. Bạn sẽ nhận được `{"`, rồi `city`, rồi `":"`, rồi `Boston` — từng mảnh rời, chưa parse được thành dict cho tới mảnh cuối cùng.
 
**Hệ quả 2 — mảnh vỡ và kết quả chốt là hai loại dữ liệu khác nhau, phục vụ hai mục đích khác nhau.** Mảnh vỡ dùng để hiển thị (hiệu ứng chữ chạy). Kết quả chốt dùng để xử lý logic (ghi log, kiểm tra, ra quyết định). Không thể lấy loại này thay cho loại kia.
 
**Hệ quả 3 — vì vậy có hai mode chính, và chúng bổ sung nhau chứ không thay thế nhau:**
 
| | `stream_mode="messages"` | `stream_mode="updates"` |
|---|---|---|
| Phát ra khi nào | Mỗi khi LLM sinh một token | Mỗi khi một **bước** của agent kết thúc |
| Nội dung | Mảnh vỡ chưa hoàn chỉnh | Cập nhật state, dữ liệu đã chốt |
| Nguồn phát | Mọi node có gọi LLM | Mọi node có ghi vào state |
| Tần suất | Rất dày, hàng trăm lần | Thưa, vài lần mỗi lượt |
 
Ghi nhớ một câu: **`messages` cho mảnh vụn đang chảy, `updates` cho kết quả đã chốt.** Gần như mọi tình huống phức tạp bên dưới đều là sự phối hợp của hai mode này.
 
---

### 4.1 Token suy luận (reasoning / thinking)
 
**Bài toán.** Một số model có bước suy nghĩ nội bộ trước khi đưa ra câu trả lời cuối. Cần hiển thị phần suy nghĩ đó theo thời gian thực, nhưng **tách bạch** khỏi câu trả lời — thường là in mờ, thu gọn được, hoặc đặt ở khối riêng trên UI.
 
**Cơ chế bên dưới.** Reasoning **không phải một kênh riêng**. Nó vẫn là token của LLM, vẫn chảy qua `stream_mode="messages"` cùng dòng với văn bản thường. Thứ phân biệt hai loại nằm bên trong từng token.
 
Cụ thể: mỗi token (`AIMessageChunk`) có thuộc tính `content_blocks` — một **danh sách các khối nội dung**, mỗi khối có trường `type`. Đây là điểm mấu chốt: một token không phải là "một cục text", nó là một túi chứa các khối được gắn nhãn loại. Lọc theo nhãn là ra được thứ mình cần:
 
- `type == "reasoning"` → nội dung nằm ở `block["reasoning"]`
- `type == "text"` → nội dung nằm ở `block["text"]`
**Vì sao `content_blocks` quan trọng hơn nó có vẻ.** Mỗi nhà cung cấp trả về reasoning theo định dạng riêng — Anthropic dùng `thinking` block, OpenAI dùng `reasoning` summary, các hãng khác lại khác. Nếu đọc thẳng dữ liệu thô của provider, đổi model là phải viết lại toàn bộ tầng xử lý. LangChain quy đổi hết về một loại block chuẩn `"reasoning"` thông qua `content_blocks`. Đoạn code bên dưới **chạy nguyên xi** khi chuyển từ Anthropic sang OpenAI.
 
**Cách làm:**
 
```python
model = ChatAnthropic(
    model_name="claude-sonnet-4-6",
    thinking={"type": "enabled", "budget_tokens": 5000},  # bắt buộc bật
)
agent = create_agent(model=model, tools=[get_weather])
 
for token, metadata in agent.stream(inputs, stream_mode="messages"):
    if not isinstance(token, AIMessageChunk):
        continue
    reasoning = [b for b in token.content_blocks if b["type"] == "reasoning"]
    text = [b for b in token.content_blocks if b["type"] == "text"]
    if reasoning:
        print(f"[thinking] {reasoning[0]['reasoning']}", end="")
    if text:
        print(text[0]["text"], end="")
```
 
Giải thích hai chỗ dễ bỏ qua trong đoạn trên:
 
`isinstance(token, AIMessageChunk)` — mode `messages` phát ra token từ **mọi** node có LLM, và không phải mọi thứ chảy qua đều là mảnh vỡ của AI message. Không lọc kiểu thì code vỡ ở dòng `.content_blocks`.
 
`end=""` trong `print` — mỗi token là một mảnh của cùng một câu, in xuống dòng thì mất hết cảm giác chữ chảy liên tục.
 
**Output:**
 
```
[thinking] The user is asking about the weather in San Francisco. I have a tool
[thinking]  available to get this information. Let me call the get_weather tool
[thinking]  with "San Francisco" as the city parameter.
The weather in San Francisco is: It's always sunny in San Francisco!
```
 
Nhìn output thấy rõ: phần thinking cũng vỡ thành nhiều mảnh, mỗi lần lặp in ra một đoạn.
 
**!Note.** Reasoning phải được bật ở cấu hình model. Nếu quên bật, vòng lặp vẫn chạy trơn tru, không exception, không cảnh báo — danh sách `reasoning` chỉ đơn giản luôn rỗng. Đây là kiểu lỗi im lặng khó lần nhất, vì code trông như đúng.
 
---
 
### 4.2 Tool call — hai lớp dữ liệu tách rời
 
**Bài toán.** Model quyết định gọi tool. Trên UI cần cả hai: hiệu ứng tham số đang được gõ ra dần, **và** thông tin chính xác "đã gọi `get_weather` với `city='Boston'`" để ghi log hoặc hiển thị badge.
 
**Cơ chế bên dưới.** Đây chính là Hệ quả 1 ở mục 4.0 thể hiện rõ nhất. Tham số tool là JSON, JSON do model sinh token by token, nên nó đến ở dạng vỡ:
 
| | Lớp 1 — đang sinh | Lớp 2 — đã chốt |
|---|---|---|
| Là gì | Mảnh chuỗi JSON, chưa parse được | Dict Python hoàn chỉnh |
| Trường chứa | `token.tool_call_chunks` | `message.tool_calls` |
| Mode | `messages` | `updates` |
| Thời điểm | Trong lúc model đang nói | Sau khi node kết thúc |
| Dùng để | Hiệu ứng gõ chữ | Logic, log, kiểm tra |
 
**Đọc `tool_call_chunks` cho đúng.** Mỗi mảnh có bốn trường, và ba trong số đó thường là `None`:
 
- `index` — **quan trọng nhất**. Model có thể gọi nhiều tool trong một lượt; `index` cho biết mảnh này thuộc tool call thứ mấy. Bỏ qua trường này là ghép nhầm tham số của tool A vào tool B.
- `name` và `id` — chỉ có ở **mảnh đầu tiên** của mỗi tool call, các mảnh sau đều `None`. Đây là lý do output nhìn có vẻ "thiếu dữ liệu" ở các dòng sau.
- `args` — mảnh chuỗi JSON. Nối hết lại theo `index` mới ra được JSON hợp lệ.
**Cách làm — bật cả hai mode cùng lúc:**
 
```python
for chunk in agent.stream(inputs, stream_mode=["messages", "updates"], version="v2"):
    if chunk["type"] == "messages":
        token, metadata = chunk["data"]
        if isinstance(token, AIMessageChunk) and token.tool_call_chunks:
            print(token.tool_call_chunks)          # lớp 1
    elif chunk["type"] == "updates":
        for source, update in chunk["data"].items():
            if source in ("model", "tools"):        # source = tên node
                print(update["messages"][-1])       # lớp 2
```
 
`source` là **tên node** phát ra cập nhật, không phải tên tool. Với `create_agent` mặc định có hai node: `model` (nơi LLM chạy) và `tools` (nơi tool thực thi). Lọc theo `source` là cách phân biệt "AI vừa quyết định gọi tool" với "tool vừa trả kết quả".
 
**Output** (rút gọn) — đọc từ trên xuống thấy đúng vòng đời:
 
```
[{'name': 'get_weather', 'args': '',        'id': 'call_D3Or...', 'index': 0}]   ← mảnh đầu, có name+id
[{'name': None,          'args': '{"',      'id': None, 'index': 0}]             ← từ đây name/id rỗng
[{'name': None,          'args': 'city',    'id': None, 'index': 0}]
[{'name': None,          'args': '":"',     'id': None, 'index': 0}]
[{'name': None,          'args': 'Boston',  'id': None, 'index': 0}]
[{'name': None,          'args': '"}',      'id': None, 'index': 0}]             ← mảnh cuối, JSON đủ
Tool calls: [{'name': 'get_weather', 'args': {'city': 'Boston'}, ...}]           ← lớp 2, đã parse
Tool response: [{'type': 'text', 'text': "It's always sunny in Boston!"}]
The| weather| in| Boston| is| **|sun|ny|**|.|                                     ← câu trả lời cuối
```
 
---
 
### 4.3 Human-in-the-loop — dừng chờ người duyệt
 
**Bài toán.** Trước khi agent gọi tool có rủi ro — chuyển tiền, gửi mail, xóa dữ liệu — cần người thật xác nhận, sửa tham số, hoặc chặn lại.
 
**Cơ chế bên dưới.** Interrupt **không phải một exception**, cũng không phải một callback. Nó là cơ chế **dừng và lưu trạng thái**: agent chạy tới điểm cần duyệt thì ghi toàn bộ state xuống checkpointer rồi thoát khỏi vòng lặp. Lần chạy sau đọc lại state từ đúng chỗ đó và đi tiếp.
 
Đây là lý do ba thứ sau đều **bắt buộc**, thiếu một là không resume được:
 
| Thành phần | Vai trò |
|---|---|
| `HumanInTheLoopMiddleware` | Quyết định tool nào cần duyệt |
| Checkpointer | Nơi lưu state lúc dừng |
| `thread_id` trong config | Khóa để lần chạy sau tìm lại đúng state đó |
 
Trên LangSmith deployment, checkpointer được cấp tự động. Chạy local thì phải truyền tay: `create_agent(..., checkpointer=InMemorySaver())`.
 
**Interrupt xuất hiện ở đâu trong stream.** Ở mode `updates`, dưới key nguồn đặc biệt `"__interrupt__"` — đứng **ngang hàng** với `"model"` và `"tools"` trong cùng vòng lặp `for source, update in chunk["data"].items()`. Nghĩa là không cần nhánh xử lý riêng biệt, chỉ thêm một điều kiện.
 
**Bước 1 — chạy và gom interrupt:**
 
```python
agent = create_agent(
    "openai:gpt-5.4",
    tools=[get_weather],
    middleware=[HumanInTheLoopMiddleware(interrupt_on={"get_weather": True})],
    checkpointer=InMemorySaver(),
)
config = {"configurable": {"thread_id": "some_id"}}
 
interrupts = []
for chunk in agent.stream(inputs, config=config,
                          stream_mode=["messages", "updates"], version="v2"):
    if chunk["type"] == "updates":
        for source, update in chunk["data"].items():
            if source == "__interrupt__":
                interrupts.extend(update)      # gom lại, chưa xử lý vội
```
 
Vòng lặp kết thúc sớm hơn bình thường — agent đã dừng. Output:
 
```
Tool execution requires approval
Tool: get_weather
Args: {'city': 'Boston'}
 
Tool execution requires approval
Tool: get_weather
Args: {'city': 'San Francisco'}
```
 
Hai yêu cầu duyệt nằm trong **cùng một** interrupt, ở `interrupt.value["action_requests"]`. Model gọi hai tool trong một lượt thì cả hai cùng bị chặn một lần, không phải hai lần dừng riêng biệt.
 
**Bước 2 — ra quyết định.** Cấu trúc dữ liệu là dict lồng hai tầng, dễ nhầm:
 
- Tầng ngoài: khóa theo `interrupt.id`
- Tầng trong: khóa `"decisions"`, giá trị là **danh sách** — mỗi phần tử ứng với một `action_request`
```python
decisions = {
    interrupt.id: {"decisions": [
        {"type": "edit", "edited_action": {"name": "get_weather",
                                           "args": {"city": "Boston, U.K."}}},
        {"type": "approve"},
    ]}
    for interrupt in interrupts
}
```
 
Ví dụ trên sửa tham số của tool thứ nhất và duyệt thẳng tool thứ hai. Doc gốc có trang riêng liệt kê đầy đủ các loại quyết định; hai loại thấy trong ví dụ là `edit` và `approve`.
 
**Bước 3 — resume bằng chính vòng lặp cũ.** Chỉ thay input, thân vòng lặp giữ nguyên:
 
```python
for chunk in agent.stream(Command(resume=decisions), config=config,
                          stream_mode=["messages", "updates"], version="v2"):
    ...  # không đổi một dòng nào
```
 
`Command(resume=...)` thay chỗ của dict input ban đầu. Vì `config` mang cùng `thread_id`, agent tìm lại state đã lưu và đi tiếp từ đúng điểm dừng — không chạy lại từ đầu, không gọi lại LLM ở bước trước.
 
```
Tool response: [{'type': 'text', 'text': "It's always sunny in Boston, U.K.!"}]
Tool response: [{'type': 'text', 'text': "It's always sunny in San Francisco!"}]
```
 
Tool thứ nhất chạy với tham số đã sửa, tool thứ hai chạy nguyên bản.
  
---
 
### 4.4 Sub-agent — biết token đến từ agent nào
 
**Bài toán.** Supervisor gọi weather_agent thông qua một tool bọc ngoài. Cả hai đều là LLM, cả hai đều phát token qua mode `messages`. Trên một dòng stream duy nhất, token của chúng lẫn vào nhau — UI không biết đoạn chữ đang chảy là của ai.
 
**Cơ chế bên dưới.** Agent con chạy trong một **graph lồng** (subgraph) với namespace riêng. Mặc định, `stream()` chỉ phát event của graph ngoài cùng; event bên trong subgraph bị chặn lại. `subgraphs=True` là công tắc mở kênh cho tầng lồng chảy ra.
 
Còn việc **gán nhãn** ai là ai thì dựa vào `name=` truyền lúc `create_agent`. Tên này được LangChain đính vào `metadata` của mỗi token dưới khóa `lc_agent_name`.
 
**Ba bước, thiếu bước nào cũng hỏng:**
 
| Bước | Thiếu thì sao |
|---|---|
| Đặt `name=` cho **từng** agent | `metadata.get("lc_agent_name")` trả `None` |
| `subgraphs=True` khi stream | Token của agent con không xuất hiện |
| Đọc `metadata["lc_agent_name"]` | Có dữ liệu nhưng không dùng, nhãn sai |
 
```python
weather_agent = create_agent(model=..., tools=[get_weather], name="weather_agent")
supervisor    = create_agent(model=..., tools=[call_weather_agent], name="supervisor")
 
current_agent = None
for chunk in supervisor.stream(inputs, stream_mode=["messages", "updates"],
                               subgraphs=True, version="v2"):
    if chunk["type"] == "messages":
        token, metadata = chunk["data"]
        if (agent_name := metadata.get("lc_agent_name")) != current_agent:
            print(f"\n🤖 {agent_name}: ")     # chỉ in nhãn khi có chuyển agent
            current_agent = agent_name
        print(token.text, end="")
```
 
Biến `current_agent` giữ agent đang hoạt động, để nhãn chỉ in **khi có chuyển giao**. Không có nó, mỗi token in kèm một nhãn — hàng trăm dòng nhãn cho một câu trả lời.
 
**Output** — đọc dọc thấy quyền điều khiển chuyển qua lại:
 
```
🤖 supervisor:
Tool calls: [{'name': 'call_weather_agent', 'args': {'query': "Boston weather..."}}]
🤖 weather_agent:                                    ← chuyển xuống agent con
Tool calls: [{'name': 'get_weather', 'args': {'city': 'Boston'}}]
Tool response: It's always sunny in Boston!
Boston| weather| right| now|:| **|Sunny|**|.
🤖 supervisor:                                       ← trả quyền về supervisor
Boston| weather| right| now|:| **|Sunny|**|.
```
 
Chú ý dòng cuối trùng nội dung dòng trên: agent con trả kết quả cho tool, tool trả cho supervisor, supervisor nhắc lại cho người dùng. Nếu UI không phân biệt được agent, người dùng sẽ thấy cùng một câu hiện ra hai lần mà không hiểu vì sao.
 
**Ghi chú.** `name=` còn được đính vào mọi `AIMessage` do agent đó sinh ra, nên truy vết được cả sau khi chạy xong, không chỉ lúc stream.
 
**Đánh giá.** Ba bước trên là **quy ước thủ công** — không có gì ép buộc, quên là hỏng im lặng. Event streaming thay bằng projection có sẵn `stream.subagents`: mỗi agent con là một handle riêng với `.name` và `.cause`, không cần bật công tắc, không cần đọc metadata — [xem 02-05, mục 4](./02-05-event-streaming.md#4-sub-agent).
 
---
 
## 5. Tắt streaming có chọn lọc
 
Đặt `streaming=False` khi khởi tạo model. Ba tình huống cần:
 
- Hệ multi-agent, chỉ muốn một số agent phát token ra ngoài
- Trộn lẫn model hỗ trợ và không hỗ trợ streaming
- Triển khai lên LangSmith, không muốn output của một model nào đó chảy về client
Không phải integration nào cũng nhận tham số `streaming`. Trường hợp đó dùng `disable_streaming=True` — tham số này có ở **mọi** chat model qua base class.
 
---
 
## 6. Giới hạn — lý do event streaming ra đời
 
| Vấn đề | Biểu hiện ở `stream()` |
|---|---|
| Phân loại thủ công | Phải `if chunk["type"] == ...` cho từng nhánh xử lý |
| Vòng đời tool | Không có kênh riêng cho input → output delta → output cuối → lỗi |
| Sub-agent | Phải bật `subgraphs=True` rồi tự đọc metadata để gán nhãn |
| Dữ liệu tùy biến | `get_stream_writer()` xâm lấn vào thân tool, làm tool khó test độc lập |
| Che PII trên đường truyền | Không có cơ chế sẵn ở tầng output |
 
---
 
## 7. Kết luận cho việc chọn API
 
Dùng `stream()` khi: code sẵn có đang chạy ổn định, hoặc cần thao tác sát tầng Pregel (mode `values`, `debug`, subgraph streaming ở mức thấp).
 
Dùng [`stream_events()`](./02-05-event-streaming.md) khi: xây dựng mới, đặc biệt là UI/frontend cần tiêu thụ nhiều luồng độc lập.
 
---
