---
title: Runtime Pregel
doc_source: https://docs.langchain.com/oss/python/langgraph/pregel
accessed: 2026-07-30
lc_version: unknown
status: draft
lab:
related:
  - ../08-graph-api/08-02-graph-api.md
  - ./10-02-fault-tolerance.md
---

# Runtime Pregel (`Pregel`)

> `Pregel` là lớp thực thi (runtime) của LangGraph — thứ thực sự chạy bên dưới mọi graph.
> Khi ta compile một [StateGraph](../08-graph-api/08-02-graph-api.md) hoặc tạo một `@entrypoint`, cái nhận về chính là một `Pregel` instance.

---

## 1. Tổng quan

Pregel là runtime của LangGraph. Nó ghép hai thành phần — **actors** và **channels** — thành một ứng dụng, rồi chạy chúng theo mô hình *Bulk Synchronous Parallel*. Actors đọc dữ liệu từ channel và ghi ngược lại channel; channel là nơi trung chuyển dữ liệu giữa các actor.

Khác biệt với thứ ta quen: StateGraph và `@entrypoint` là hai API cấp cao để *mô tả* logic. Pregel là thứ *chạy* logic đó. Ta hiếm khi viết Pregel trực tiếp — compile StateGraph ra một Pregel là xong — nhưng hiểu runtime giúp ta đọc được hành vi khi thứ tự thực thi, song song, hay checkpoint không như kỳ vọng.

Tên "Pregel" lấy từ thuật toán Pregel của Google cho tính toán song song quy mô lớn trên đồ thị.

Bản Pregel trần nhất — một node, đọc channel `a`, nhân đôi chuỗi, ghi vào `b`:

```python
node1 = (
    NodeBuilder().subscribe_only("a")   # node chỉ nghe một channel duy nhất: "a"
    .do(lambda x: x + x)                # nhận giá trị của "a", nối chính nó vào nó
    .write_to("b")                      # ghi kết quả sang channel "b"
)

app = Pregel(
    nodes={"node1": node1},
    channels={"a": EphemeralValue(str), "b": EphemeralValue(str)},
    input_channels=["a"],               # "a" nhận input khi invoke
    output_channels=["b"],              # "b" là thứ trả ra
)

app.invoke({"a": "foo"})
```

**Kết quả in ra:**

```
{'b': 'foofoo'}                          ← "foo" + "foo", đúng như node1 định nghĩa
```

**Quan hệ với chịu lỗi.** Retry, timeout, error handler đều gắn ở cấp node của runtime này. Chi tiết ở [10-02 Fault tolerance](./10-02-fault-tolerance.md).

---

## 2. Vòng đời một step — mô hình Bulk Synchronous Parallel

Pregel không chạy các actor tùy tiện theo thứ tự gọi. Nó chia thực thi thành nhiều **step**, mỗi step gồm ba pha cố định. Đây là cái quyết định vì sao kết quả một graph song song vẫn tất định (deterministic).

Nỗi đau nó lo: nhiều actor chạy song song, nếu actor này ghi channel trong khi actor kia đang đọc cùng channel thì kết quả phụ thuộc thứ tự chạy — mỗi lần chạy ra một kiểu. BSP tách rạch ròi pha đọc và pha ghi để chuyện đó không xảy ra.

Hình dung như một ca làm việc theo hiệp: cả đội cùng vào làm, làm xong hiệp mới tổng kết ghi bảng, rồi mới sang hiệp sau. Không ai vừa làm vừa nhìn bảng người khác đang sửa dở.

Ba pha mỗi step:

| Pha | Việc |
|---|---|
| **Plan** | Chọn actor nào chạy trong step này. Step đầu: các actor nghe channel input. Step sau: các actor nghe channel *vừa được cập nhật ở step trước*. |
| **Execution** | Chạy song song toàn bộ actor đã chọn, tới khi tất cả xong / một cái lỗi / chạm timeout. Trong pha này, mọi thay đổi channel **chưa nhìn thấy được** với các actor. |
| **Update** | Ghi vào channel những giá trị các actor vừa tạo ra trong step này. |

Lặp tới khi không còn actor nào được chọn để chạy, hoặc chạm số step tối đa.

Điểm cốt lõi: một giá trị ghi ở step N chỉ hiện ra cho các actor ở step N+1. Đây là lý do một actor ghi lại chính channel nó nghe sẽ tạo ra vòng lặp (cycle) qua các step, thay vì đệ quy trong một step.

---

## 3. Actors — `PregelNode`

Một actor là một `PregelNode`. Nó nghe (subscribe) channel, đọc dữ liệu từ đó, ghi dữ liệu ra đó. `PregelNode` triển khai giao diện Runnable của LangChain, nên nó ghép được vào chuỗi Runnable như mọi thành phần khác.

Ba mảnh dựng nên một node qua `NodeBuilder`:

```python
node2 = (
    NodeBuilder().subscribe_to("b")     # nghe "b"; subscribe_to trả về dict {"b": ...}
    .do(lambda x: x["b"] + x["b"])      # nên phải lấy x["b"], khác subscribe_only lấy thẳng
    .write_to("c")                      # ghi sang "c"
)
```

Phân biệt hai cách nghe: `subscribe_only("a")` đưa thẳng giá trị của `a` vào hàm; `subscribe_to("b")` đưa vào một dict, phải bóc `x["b"]`. Chọn nhầm thì hàm nhận sai kiểu dữ liệu.

---

## 4. Channels — kênh liên lạc giữa các actor

Channel là nơi actor trao dữ liệu cho nhau, hoặc gửi dữ liệu cho chính nó ở step tương lai. Mỗi channel có ba thứ: kiểu giá trị, kiểu update, và một **hàm update** — nhận một chuỗi các update rồi quyết định giá trị lưu lại thay đổi ra sao. Chính hàm update này phân biệt bốn loại channel dưới đây.

### 4.1 `LastValue` — giữ giá trị cuối

Loại mặc định. Ghi cái gì vào thì giữ đúng cái đó, đè lên giá trị cũ. Dùng cho input, output, hoặc chuyển một giá trị từ step này sang step kế.

```python
channel: LastValue[int] = LastValue(int)
```

### 4.2 `Topic` — kênh PubSub, gửi nhiều hoặc tích lũy

Dùng khi một actor cần gửi *nhiều* giá trị, hoặc khi ta muốn gom output qua nhiều step. Cấu hình được: khử trùng lặp giá trị, hoặc tích lũy toàn bộ giá trị ghi trong một lần chạy.

```python
channel: Topic[str] = Topic(str, accumulate=True)   # accumulate=True: giữ lại mọi giá trị qua các step
```

Ví dụ tích lũy — node1 ghi `b` và `c`, node2 đọc `b` ghi tiếp `c`, `c` là Topic accumulate:

```python
app.invoke({"a": "foo"})
```

**Kết quả in ra:**

```
{'c': ['foofoo', 'foofoofoofoo']}        ← cả hai lần ghi vào "c" đều được giữ, không đè
```

### 4.3 `BinaryOperatorAggregate` — cộng dồn qua các step

Lưu một giá trị bền, mỗi update áp một toán tử hai ngôi lên (giá trị hiện tại, update mới). Dùng để tính tổng chạy dần (running total, running concat...).

```python
total = BinaryOperatorAggregate(int, operator.add)   # mỗi lần ghi cộng thêm vào giá trị hiện có
```

Điểm cần nhớ để phân biệt với DeltaChannel: **reducer ở đây chạy lúc write** — giá trị đã gộp mới là thứ được serialize vào checkpoint.

### 4.4 `DeltaChannel` — chỉ lưu phần chênh mỗi step

> [!note]
> `DeltaChannel` cần `langgraph>=1.2`, đang ở giai đoạn **beta**, API có thể đổi.

**Nó lo nỗi đau gì.** Một channel vừa ghi liên tục vừa phình to dần — điển hình là list message của một thread hội thoại dài. Với channel thường, cứ mỗi step toàn bộ list được serialize lại vào checkpoint, nên checkpoint phình tuyến tính theo độ dài thread. `DeltaChannel` chỉ lưu **phần mới ghi ở step đó**, không lưu lại cả khối.

Dấu hiệu nên dùng: kích thước checkpoint của một channel tăng tuyến tính theo độ dài thread. Dùng y như một reducer thường trong `Annotated`:

```python
class State(TypedDict):
    messages: Annotated[list[str], DeltaChannel(my_reducer)]
```

**Bulk reducer — khác reducer thường ở chỗ nào.** Reducer truyền vào `DeltaChannel` là *bulk reducer*: nó nhận (state hiện tại, **cả chuỗi** writes của step này) trong một lần gọi, không gọi từng cặp. Khác hẳn reducer per-key trong StateGraph vốn được gọi một lần cho mỗi update.

```python
def list_reducer(state, writes):        # writes là cả chuỗi các list ghi trong step
    result = list(state)                # sao chép state, không sửa tại chỗ
    for write in writes:                # duyệt từng list đã ghi
        result.extend(write)            # nối theo đúng thứ tự
    return result
```

**Reducer phải associative (bất biến theo cách gom batch).** Điều kiện bắt buộc:

```
reducer(reducer(state, [xs]), [ys]) == reducer(state, [xs, ys])
```

Áp từng batch một phải cho kết quả y hệt áp gộp. Không thỏa thì state dựng lại sẽ khác nhau tùy cách LangGraph gom writes qua các step — hành vi không nhất quán.

> [!note]
> **Reducer chạy lúc dựng lại, không phải lúc ghi.** Khác `BinaryOperatorAggregate` (reducer chạy lúc write, giá trị gộp được lưu vào checkpoint), reducer của `DeltaChannel` chỉ chạy khi giá trị channel được *tái tạo* từ các write đã lưu — ở lần đọc kế, ở actor step sau, hoặc khi phát lại lịch sử. Thứ được serialize là các write thô theo từng step.

Ba hệ quả khi thiết kế reducer:

- **Phải là hàm thuần của `(state, writes)`.** Mọi side effect, random, đọc đồng hồ (`uuid.uuid4()`, `datetime.now()`) sẽ chạy lại mỗi lần tái tạo và ra kết quả khác nhau mỗi lần phát lại — chúng *không* được nướng cứng vào write.
- **Đừng dựa vào việc mutation của write được lưu.** Nếu reducer sửa một write (ví dụ gán ID cho item chưa có ID), sửa đó chỉ sống trong giá trị tái tạo; write lưu vẫn giữ hình dạng gốc.
- **Gắn ID và metadata bền ở phía trên (upstream).** Nếu code phía sau cần tham chiếu item theo ID qua các lượt, gán ID đó *trước khi* ghi vào channel — không phải trong reducer.

**`snapshot_frequency` — chặn độ trễ đọc.** Không có snapshot, đọc giá trị `DeltaChannel` phải phát lại toàn bộ lịch sử write — O(N) với thread N step. Đặt `snapshot_frequency=K` ghi một snapshot đầy đủ mỗi K step, chặn độ sâu đọc còn tối đa K step:

```python
messages: Annotated[list[str], DeltaChannel(my_reducer, snapshot_frequency=5)]
```

K cao: ít tốn lưu trữ, đọc chậm hơn. K thấp: chặn độ trễ chặt hơn, checkpoint lớn hơn. `None` (mặc định) bỏ snapshot hẳn — hợp khi ít đọc hoặc thread ngắn.

> [!note]
> **Không hỗ trợ rollback về bản không có `DeltaChannel`.** `langgraph>=1.2` ghi checkpoint delta theo định dạng mới mà bản cũ không đọc được. Thread đã dùng `DeltaChannel` rồi thì hạ cấp LangGraph sẽ để lại checkpoint không đọc được. Cần rollback thì phải migrate hoặc bỏ các thread đó trước khi hạ cấp.

### Bảng chọn channel

| Channel | Hàm update | Dùng khi |
|---|---|---|
| `LastValue` | Đè giá trị cũ | Mặc định; input/output; chuyển một giá trị qua step |
| `Topic` | Gom nhiều giá trị (khử trùng / tích lũy) | Một actor gửi nhiều giá trị; gom output qua các step |
| `BinaryOperatorAggregate` | Áp toán tử hai ngôi, gộp lúc write | Tính tổng / nối chuỗi chạy dần |
| `DeltaChannel` | Bulk reducer associative, gộp lúc đọc | Channel ghi nhiều **và** phình lớn (list message thread dài) |

Ba loại đầu là kiến thức nền dùng thường xuyên. `DeltaChannel` chỉ đụng tới khi checkpoint phình vì một channel cụ thể — không cần nếu thread ngắn.

---

## 5. Hai API cấp cao đều sinh ra một Pregel

Ta gần như luôn tạo Pregel gián tiếp qua một trong hai API.

**StateGraph (Graph API).** Mô tả graph bằng node và edge, `compile()` trả về một Pregel. Sau compile, in `graph.nodes` và `graph.channels` để soi — LangGraph tự dựng thêm nhiều channel nội bộ (các channel `branch:...`, `start:...`) phục vụ định tuyến, ngoài các channel state ta khai báo.

```python
builder = StateGraph(Essay)
builder.add_node(write_essay)
builder.add_node(score_essay)
builder.add_edge(START, "write_essay")
builder.add_edge("write_essay", "score_essay")
graph = builder.compile()               # graph là một Pregel instance
```

**Functional API.** Dùng `@entrypoint` để định nghĩa một hàm nhận input trả output; nó cũng là một Pregel. Channel nội bộ tối giản hơn — chủ yếu `__start__`, `__end__`, `__previous__`.

```python
@entrypoint(checkpointer=checkpointer)
def write_essay(essay: Essay):
    return {"content": f"Essay about {essay['topic']}"}
```

Chi tiết hai API này thuộc file khác trong bộ; ở đây chỉ cần nắm: cả hai đều biên dịch xuống cùng một runtime Pregel, nên hành vi thực thi (BSP, channel) mô tả ở trên áp cho cả hai.

---

## Tham chiếu chéo

- [08-02 Graph API](../08-graph-api/08-02-graph-api.md) — StateGraph, API cấp cao chính sinh ra Pregel
- [10-02 Fault tolerance](./10-02-fault-tolerance.md) — retry, timeout, error handler gắn ở cấp node của runtime này
- Trang tài liệu Pregel: `https://docs.langchain.com/oss/python/langgraph/pregel`