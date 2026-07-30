---
title: Graph API
doc_source: https://docs.langchain.com/oss/python/langgraph/graph-api
accessed: 2026-07-30
lc_version: unknown
status: draft
lab:
related:
  - ./08-03-use-graph-api.md
  - ../10-runtime/10-01-pregel-runtime.md
---

# Graph API — State, Nodes, Edges

---

## 1. Tổng quan

Graph API dựng workflow từ ba thành phần: 

-`State` (khối dữ liệu chung, là ảnh chụp trạng thái hiện tại), 

-`Nodes` (hàm làm việc, nhận state trả về phần cập nhật),
                                          
-`Edges` (quyết định chạy node nào tiếp theo). 

**Gói gọn**: **node làm việc, edge chỉ đường**.

Đồ thị chạy theo cơ chế **truyền thông điệp** qua các "super-step": node xong việc thì gửi update dọc theo edge tới node kế; node chạy song song thuộc cùng một super-step, node chạy tuần tự thuộc các super-step khác nhau; đồ thị dừng khi không còn node nào hoạt động.

---

## 2. State — khối dữ liệu chung của đồ thị

**Khái niệm.** `State` gồm hai phần: *schema* (hình dạng dữ liệu) và *reducer* (cách áp update vào state). Schema là đầu vào cho mọi node và edge; node phát ra update, reducer quyết định trộn update đó vào state ra sao.



**Vai trò.** Không có state chung, các node phải tự truyền dữ liệu cho nhau bằng tay. State cho phép nhiều node đọc/ghi cùng một khối, và reducer cho phép quy định "ghi đè" hay "cộng dồn" cho từng khóa riêng.

### 2.1 Schema — TypedDict, dataclass, hay Pydantic

Ba lựa chọn, khác nhau về mục đích:

| Loại | Dùng khi |
|---|---|
| `TypedDict` | Mặc định, nhanh nhất |
| `dataclass` | Cần giá trị mặc định cho khóa state |
| Pydantic `BaseModel` | Cần validate kiểu dữ liệu đệ quy lúc chạy (chậm hơn) |

**!Note:** Với Pydantic, validate chỉ chạy trên **đầu vào của node đầu tiên**, không chạy cho các node sau hay cho output. Ngoài ra factory cấp cao `create_agent` không nhận state schema kiểu Pydantic.

### 2.2 Reducer — cách trộn update vào state

**Khái niệm.** Reducer là một hàm hai đối số: **trái** = giá trị đang có trong state, **phải** = update node vừa trả về. LangGraph gọi `reducer(left=state[key], right=update[key])` và lưu giá trị trả về làm state mới.

**Vai trò.** Mỗi khóa có reducer riêng. Không khai báo reducer thì mặc định là **ghi đè** — bỏ giá trị trái, giữ giá trị phải. Muốn **cộng dồn** (nối list, tích lũy lịch sử) thì gắn reducer tùy biến qua `Annotated`.

```python
from operator import add
from typing import Annotated
from typing_extensions import TypedDict

class State(TypedDict):
    foo: int                              # không reducer → ghi đè
    bar: Annotated[list[str], add]        # reducer add → nối list
```

**Kết quả** khi state là `{"foo": 1, "bar": ["hi"]}`, node 1 trả `{"foo": 2}`, node 2 trả `{"bar": ["bye"]}` (dựng lại):

```
{'foo': 2, 'bar': ['hi', 'bye']}     ← foo bị ghi đè; bar được nối thêm nhờ reducer add
```

Muốn bỏ qua reducer để **ghi đè thẳng** một khóa vốn có reducer cộng dồn, bọc giá trị bằng `Overwrite` (chi tiết ở [08-03 mục Bypass reducer](./08-03-use-graph-api.md)).

### 2.3 Nhiều schema — input, output, private

**Mục đích.** Khi đồ thị trở nên phức tạp, state thường chứa cả dữ liệu đầu vào, kết quả cuối cùng và nhiều dữ liệu trung gian được tạo ra trong quá trình xử lý. Việc tách nhiều schema giúp **kiểm soát dữ liệu mà graph nhận vào, trả ra và dữ liệu chỉ dùng nội bộ**, từ đó giúp API rõ ràng và dễ bảo trì hơn.

- `input_schema`: xác định những dữ liệu bên ngoài được phép truyền vào graph.
- `output_schema`: xác định những dữ liệu graph trả về sau khi thực thi.
- `PrivateState`: chứa các channel chỉ phục vụ trao đổi giữa các node trong quá trình xử lý, không thuộc API đầu vào hoặc đầu ra.

> **Lưu ý:** Các schema này chỉ dùng để **tổ chức và giới hạn giao diện (API)** của graph, **không chia state thành nhiều phần độc lập**.

**Điểm mấu chốt.** Graph vẫn chỉ có **một state duy nhất** (`OverallState`). Mỗi node có thể **ghi vào bất kỳ channel nào đã khai báo trong `OverallState`**, kể cả channel đó không nằm trong `input_schema` của node hoặc không thuộc `output_schema`.

```python
builder = StateGraph(
    OverallState,
    input_schema=InputState,
    output_schema=OutputState,
)

graph.invoke({"user_input": "My"})
# {'graph_output': 'My name is Lance'}
```

**!Note:** `input_schema`, `output_schema` và `PrivateState` **không che giấu dữ liệu khi streaming**. Với `stream_mode="values"`, LangGraph sẽ phát toàn bộ state hiện tại, bao gồm cả các channel trong `PrivateState`. Nếu chỉ muốn stream một số channel, hãy truyền thêm `output_keys=[...]`.

### 2.4 Làm việc với `messages`

**Mục đích.** Trong các ứng dụng chatbot hoặc AI Agent, state thường cần lưu toàn bộ lịch sử hội thoại để cung cấp ngữ cảnh cho LLM. LangGraph cung cấp reducer `add_messages` để quản lý danh sách message một cách an toàn và thuận tiện.

Khác với reducer `add` chỉ nối thêm phần tử vào danh sách, `add_messages` sẽ:
- Thêm (`append`) message mới vào lịch sử.
- Cập nhật (ghi đè) message cũ nếu trùng `id`, thay vì tạo bản sao.
- Tự động deserialize dữ liệu thành các đối tượng `Message` của LangChain.

```python
from langgraph.graph.message import add_messages
from langchain.messages import AnyMessage
from typing import Annotated
from typing_extensions import TypedDict

class GraphState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
```

Vì `messages` luôn được deserialize thành các đối tượng `Message`, có thể truy cập thuộc tính trực tiếp:

```python
state["messages"][-1].content
```

**!Note:** Nếu state của graph chỉ cần lưu lịch sử hội thoại, có thể sử dụng sẵn `MessagesState`. Đây là một `TypedDict` đã định nghĩa trường `messages` với reducer `add_messages`, giúp không cần tự khai báo lại và có thể kế thừa để bổ sung các channel khác.

---

## 3. Nodes — hàm xử lý logic của graph

**Khái niệm.** Node là hàm Python (sync hoặc async) nhận tối đa ba đối số: `state` (trạng thái đồ thị), `config` (`RunnableConfig`, chứa `thread_id`, tag tracing), `runtime` (`Runtime`, chứa `context` và các thứ như `store`, `stream_writer`, `execution_info`, `server_info`, `heartbeat`, `control`). Thêm node bằng `add_node`; không đặt tên thì lấy tên hàm.

```python
def node_with_runtime(state: State, runtime: Runtime[Context]):
    return {"results": f"Hello, {state['input']}!"}

builder.add_node("node_with_runtime", node_with_runtime)
```

**!Note — tính idempotent khi chạy lại.** Checkpoint lưu ở **ranh giới super-step**, không lưu giữa chừng một node. Nếu đồ thị dừng rồi resume (sau interrupt hoặc retry), **cả node chạy lại từ đầu** — code và side-effect trước điểm dừng chạy lại lần nữa. Thiết kế node sao cho chạy hai lần không hỏng state (dùng upsert, idempotency key, hoặc đọc-trước-khi-ghi). Chi tiết retry/tolerance ở file fault-tolerance.

**Đổi cấu trúc đồ thị khi resume.** Thêm/bớt/đổi tên node và edge **không** phá vỡ resume của thread cũ (khác với quy tắc determinism của code trong node/task). Resume dùng state đã lưu và chạy đồ thị hiện tại.

**START và END.** `START` là node ảo đại diện đầu vào của người dùng — dùng `add_edge(START, "node_a")` để chỉ node chạy đầu. `END` là node kết thúc — `add_edge("node_a", END)`.

**Node caching.** Gắn `cache_policy=CachePolicy(ttl=..., key_func=...)` cho node và compile với `cache=InMemoryCache()` (hoặc `SqliteCache`) để bỏ qua tính toán lặp lại cùng input. Lần chạy thứ hai với cùng input trả về ngay, kèm metadata `{'cached': True}`.

---

## 4. Edges — định tuyến luồng

Bốn loại edge:

| Loại | Hàm | Ý nghĩa |
|---|---|---|
| Normal | `add_edge("a", "b")` | Luôn đi A → B |
| Conditional | `add_conditional_edges("a", route_fn)` | Gọi hàm route quyết định node kế |
| Entry point | `add_edge(START, "a")` | Node chạy đầu |
| Conditional entry | `add_conditional_edges(START, route_fn)` | Chọn node đầu theo logic |

Một node có nhiều edge ra thì **tất cả node đích chạy song song** trong super-step kế. Hàm route trả về tên node (hoặc list tên); có thể kèm dict ánh xạ `{True: "node_b", False: "node_c"}`.

**!Note:** Với mỗi node, chọn **một** cơ chế định tuyến — hoặc normal edge (tĩnh), hoặc conditional edge / `Command` (động). Trộn cả hai từ cùng một node khiến cả hai đường cùng chạy, rất khó suy luận hành vi.

---

## 5. Send — map-reduce, số nhánh chưa biết trước

**Khái niệm.** `Send` xử lý tình huống số edge **không biết trước** và mỗi nhánh cần một bản `State` **khác nhau**. Điển hình là map-reduce: node đầu sinh ra một list đối tượng, ta muốn áp một node lên từng đối tượng, nhưng số lượng chỉ biết lúc chạy.

**Áp dụng thực tế.** Node đầu trả về danh sách 500 mã doanh nghiệp cần thẩm định. Ta không thể khai báo sẵn 500 edge. `Send` sinh 500 nhánh, mỗi nhánh nhận đúng một mã làm state riêng, chạy song song rồi gộp kết quả về một khóa cộng dồn.

```python
from langgraph.types import Send

def continue_to_jokes(state: OverallState):
    return [Send("generate_joke", {"subject": s}) for s in state["subjects"]]

graph.add_conditional_edges("node_a", continue_to_jokes)
```

`Send` trả về từ conditional edge, nhận hai đối số: tên node và state truyền vào node đó.

---

## 6. Command — vừa cập nhật state vừa định tuyến

**Khái niệm.** `Command` là primitive điều khiển luồng, nhận bốn tham số: `update` (cập nhật state), `goto` (đi tới node), `graph` (nhắm đồ thị cha khi ở subgraph), `resume` (nối lại sau interrupt).

**Vai trò.** Dùng `Command` khi cần **đồng thời** cập nhật state **và** rẽ nhánh trong cùng một node — thay cho việc phải tách thành node cập nhật + conditional edge riêng. Chỉ rẽ nhánh mà không đổi state thì dùng conditional edge cho gọn hơn.

```python
from typing import Literal

def my_node(state: State) -> Command[Literal["my_other_node"]]:
    return Command(update={"foo": "bar"}, goto="my_other_node")
```

Ba ngữ cảnh dùng `Command`: (1) **trả về từ node** — `update` + `goto` + `graph`; (2) **đầu vào cho `invoke`/`stream`** — chỉ dùng `resume` để nối lại sau interrupt; (3) **trả về từ tool** — cập nhật state từ trong tool.

**!Note — hai lỗi im lặng thường gặp:**

- Khai báo `Command` **phải kèm annotation** `Command[Literal["node_b", ...]]` liệt kê node đích, nếu không đồ thị không vẽ được và LangGraph không biết đường đi.
- `Command` chỉ **thêm** edge động; **edge tĩnh khai báo bằng `add_edge` vẫn chạy**. Nếu `node_a` trả `Command(goto="x")` mà còn có `add_edge("node_a", "node_b")` thì **cả `x` lẫn `node_b` cùng chạy**. Với mỗi node dùng một kiểu định tuyến.

**Đầu vào cho `invoke`.** Chỉ `Command(resume=...)` mới hợp lệ làm đầu vào (có thể kèm `update` để vừa nối lại vừa đổi state). **Đừng** dùng `Command(update=...)` một mình để tiếp tục hội thoại — mọi `Command` truyền vào sẽ resume từ **checkpoint gần nhất** (bước cuối đã chạy), nên nếu đồ thị đã xong nó sẽ như bị treo. Để tiếp tục hội thoại trên thread cũ, truyền **dict thường**.

**Điều hướng lên đồ thị cha.** Từ node trong subgraph, `graph=Command.PARENT` nhảy sang node ở đồ thị cha gần nhất. Khi update một khóa **dùng chung** giữa cha và subgraph, **bắt buộc** khóa đó ở state cha có reducer.

---

## 7. Runtime context — cấu hình truyền lúc chạy

**Khái niệm.** `context_schema` cho phép truyền dữ liệu **không thuộc state** vào node lúc chạy — ví dụ tên model, kết nối database.

```python
graph = StateGraph(State, context_schema=ContextSchema)
graph.invoke(inputs, context={"llm_provider": "anthropic"})

def node_a(state: State, runtime: Runtime[ContextSchema]):
    llm = get_llm(runtime.context.llm_provider)
```

Đọc trong node hoặc conditional edge qua `runtime.context`. Cách khai báo đầy đủ ở [08-03 mục runtime config](./08-03-use-graph-api.md).

---

## 8. Recursion limit — trần số super-step

**Khái niệm.** Recursion limit là số super-step tối đa cho một lần chạy. Vượt trần thì raise `GraphRecursionError`. Mặc định **1000** (từ bản 1.0.6). Đặt qua config: `graph.invoke(inputs, config={"recursion_limit": 5})`.

**!Note:** `recursion_limit` là khóa config **độc lập**, **không** đặt trong `configurable` như các cấu hình do người dùng định nghĩa. Đặt sai chỗ thì trần không có hiệu lực.

**Xử lý chủ động thay vì để nổ lỗi.** `RemainingSteps` là managed value đếm số bước còn lại tới trần. Đọc `state["remaining_steps"]` trong node để rẽ sang nhánh "trả kết quả tạm" trước khi chạm trần — đồ thị hoàn tất bình thường, không ném ngoại lệ, giữ được state trung gian. So với cách bị động (bắt `GraphRecursionError` ngoài đồ thị): chủ động cho phép suy giảm êm và có kết quả một phần; bị động đơn giản hơn nhưng đồ thị bị chấm dứt. Bộ đếm bước hiện tại nằm ở `config["metadata"]["langgraph_step"]`.

---

## 9. Graph migrations — đổi định nghĩa đồ thị khi đã có state

Tóm tắt quy tắc:

- Thread **đã kết thúc** (không bị interrupt): đổi được **toàn bộ** topology (thêm/bớt/đổi tên node và edge).
- Thread **đang interrupt**: đổi được mọi thứ **trừ** đổi tên / xóa node (vì thread có thể sắp vào node không còn tồn tại).
- **State**: thêm/bớt khóa tương thích cả hai chiều. **Đổi tên khóa** làm **mất** state đã lưu của khóa đó ở thread cũ.

---

## Tham chiếu chéo

- [08-03 Dùng Graph API](./08-03-use-graph-api.md) — cách làm từng việc: sequence, branch, loop, retry, timeout, Command trong tool
- [08-01 Chọn giữa hai API](./08-01-choosing-apis.md) — khi nào chọn Graph API thay vì Functional API
- Super-step / message passing: `../10-runtime/10-01-pregel-runtime.md`
- Trang gốc: https://docs.langchain.com/oss/python/langgraph/graph-api