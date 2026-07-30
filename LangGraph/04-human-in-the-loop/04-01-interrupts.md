---
title: Interrupt
doc_source: [https://docs.langchain.com/oss/python/langgraph/interrupts] 
accessed: 2026-07-29
lc_version: unknown
status: draft
lab:
related:
  - ./04-02-time-travel.md
  - ../02-persistence/02-02-checkpointers.md
---

# Interrupt (`interrupt()`)

> `interrupt()` là cơ chế tạm dừng việc thực thi luồng graph để chờ sự can thiệp từ bên ngoài (Human-in-the-loop), dành cho lập trình viên muốn xây dựng các ứng dụng AI có phê duyệt, chỉnh sửa hoặc thu thập thêm thông tin từ người dùng.
> Phương thức này phụ thuộc hoàn toàn vào hệ thống quản lý trạng thái, có liên kết chặt chẽ với [Checkpointers](https://www.google.com/search?q=../02-persistence/02-02-checkpointers.md).

---

## 1. Tổng quan

`interrupt()` cho phép dừng graph tại một nút bất kỳ mà không làm mất trạng thái (state). Khác với việc dừng graph bằng `break_before` hay `break_after` ở cấp độ node, `interrupt()` được gọi **trực tiếp bên trong logic xử lý của node**, giúp kiểm soát việc tạm dừng linh hoạt dựa trên điều kiện thực thi thực tế.

```python
from langgraph.types import interrupt

def step_approval(state):
    # Tạm dừng và gửi thông tin yêu cầu xác nhận ra bên ngoài
    user_response = interrupt({"question": "Bạn có đồng ý thực hiện giao dịch này không?"})
    return {"status": user_response["action"]}

```

**Kết quả in ra**:

```
Graph interrupted at node 'step_approval'
Value sent to surface: {'question': 'Bạn có đồng ý thực hiện giao dịch này không?'}
State saved to Checkpointer with thread_id: 'session-123'

```

Output cho thấy graph không bị ngắt đột ngột (crash) mà chuyển sang trạng thái tạm dừng, lưu thông tin truyền ra ngoài và đợi Resume từ client.

**Quan hệ với Checkpointers.** `interrupt()` bắt buộc phải đi kèm với một Checkpointer. Nếu không có Checkpointer lưu lại snapshot trạng thái tại thời điểm dừng, graph sẽ không thể khôi phục lại đúng vị trí node đang chạy để nhận dữ liệu truyền vào.

---

## 2. Ngắt luồng linh hoạt (Interrupt Mechanism)

### Khái niệm

`interrupt()` là một hàm đặc biệt trong LangGraph dừng việc thực thi logic nội bộ của node, đẩy một giá trị payload ra ngoài cho client và đóng vai trò như một "điểm đợi" dữ liệu phản hồi.

### Vai trò

Giải quyết bài toán tương tác hai chiều giữa AI và con người trong các quy trình nghiệp vụ quan trọng. Thiếu cơ chế này, bạn sẽ phải tự cắt nhỏ graph thành nhiều subgraph riêng biệt hoặc tự quản lý trạng thái phức tạp bên ngoài ứng dụng.

### Áp dụng thực tế

* **Phê duyệt giao dịch:** Trong ứng dụng ngân hàng/tài chính, chuyển khoản vượt hạn mức cần người dùng xác nhận OTP hoặc Approve trên UI trước khi gọi API chuyển tiền.
* **Sửa đổi nội dung AI:** Trong công cụ viết bài, AI tạo bản nháp -> tạm dừng -> cho phép người dùng chỉnh sửa văn bản -> AI tiếp tục quy trình xuất bản.
* **Thu thập thông tin thiếu:** AI thiếu thông tin để tiếp tục (ví dụ: ngày bay) -> dừng lại hỏi người dùng -> nhận câu trả lời và chạy tiếp.

###  Ba thứ bắt buộc phải có  để `interrupt()` hoạt động:
 
1. **Checkpointer** — để ghi trạng thái graph xuống. Chạy thật thì dùng checkpointer bền (có database sau lưng), không dùng bộ nhớ tạm.
2. **`thread_id`** trong config — để runtime biết nạp lại trạng thái nào khi resume. Đặt qua `config={"configurable": {"thread_id": ...}}`. Đây chính là con trỏ bền: tái dùng cùng một `thread_id` là nối lại đúng checkpoint cũ; đổi giá trị mới là mở một thread trắng.
3. **Payload JSON-serializable** — giá trị truyền vào `interrupt()` phải chuyển được thành JSON (chuỗi, số, dict, list...). Đây là thứ hiện ra cho phía gọi để render lên UI.

### Luồng hoạt đông khi interrupt() kích hoạt 
 
1. Graph bị **treo ngay tại điểm** gọi `interrupt()`.
2. Trạng thái được **lưu** qua checkpointer để về sau resume được.
3. Payload được **đẩy ra** phía gọi: hiện trên `stream.interrupts` nếu dùng event streaming (`graph.stream_events(..., version="v3")`), hoặc dưới khóa `__interrupt__` nếu dùng API `invoke()` mặc định.
4. Graph **chờ vô thời hạn** cho tới khi ta resume.
5. Khi resume, câu trả lời được **truyền ngược** vào node, trở thành giá trị trả về của `interrupt()`.






### Bảng đối chiếu ngắt luồng

| Tiêu chí | Ngắt cấp Node (`break_before` / `break_after`) | Ngắt nội bộ Node (`interrupt()`) |
| --- | --- | --- |
| **Vị trí tác động** | Ranh giới giữa các node | Bất kỳ dòng code nào bên trong node |
| **Dữ liệu truyền ra** | Toàn bộ `State` hiện tại | Payload tùy chỉnh do lập trình viên định nghĩa |
| **Khôi phục (Resume)** | Chạy lại toàn bộ node (hoặc node tiếp theo) | Chạy tiếp ngay từ dòng code bên dưới `interrupt()` |




---

## 3. `Command(resume=...)` — nối lại luồng đã dừng
 
Sau khi interrupt dừng graph, ta chạy tiếp bằng cách **gọi lại graph với một `Command` chứa giá trị resume**. Giá trị đó được đưa ngược về đúng chỗ `interrupt()` đã dừng.
 
```python
config = {"configurable": {"thread_id": "thread-1"}}      # cùng thread_id với lúc dừng, nếu không sẽ nạp nhầm trạng thái
 
stream = graph.stream_events(Command(resume=True), config=config, version="v3")   # True là câu trả lời gửi vào interrupt()
final = stream.output                                     # gom stream tới khi có trạng thái cuối
```
 
**Lưu ý:** 
Phải dùng truyền đúng `thread_id` đã dùng lúc interrupt xảy ra — sai thread là nối vào một trạng thái khác. 

Giá trị đặt trong `Command(resume=...)` **chính là** giá trị trả về của `interrupt()` và có thể truyền được bất kỳ giá trị JSON-serializable nào. 
 
**!Note:** 

- Chỉ `Command(resume=...)` mới là mẫu `Command` được thiết kế để làm **đầu vào** cho `invoke()`/`stream()`/`stream_events()`. Các tham số `Command` khác — `update`, `goto`, `graph` — là để **trả về từ trong node**, không phải để truyền vào. Muốn tiếp tục hội thoại nhiều lượt thì truyền một dict input thường, đừng truyền `Command(update=...)` vào.
 
- Đây là mô hình tư duy phải nắm trước khi làm bất cứ thứ gì với interrupt: **khi resume, runtime chạy lại toàn bộ node từ dòng đầu tiên, không phải từ dòng `interrupt()`.**

---
 
## 4. Các quy tắc khi sử dụng `interrupt()`

### 4.1 Không bọc `interrupt()` trong `try/except` trần
 
`interrupt()` dừng graph bằng cách ném một exception đặc biệt. Nếu ta bọc nó trong `try/except Exception` trần, chính khối except đó **nuốt mất** exception này — graph không dừng, interrupt coi như không tồn tại. Đây là lỗi im lặng điển hình: code chạy trơn, không báo gì, chỉ là chẳng bao giờ dừng để hỏi người.
 
Cách đúng: tách lời gọi `interrupt()` ra khỏi đoạn code dễ lỗi, hoặc nếu buộc phải dùng `try/except` thì bắt **loại exception cụ thể** (ví dụ `NetworkException`) chứ đừng bắt `Exception` chung — bắt cụ thể thì không đụng tới exception của interrupt.
 
```python
# 🔴 Sai: except trần nuốt luôn exception của interrupt → không bao giờ dừng
try:
    interrupt("What's your name?")
except Exception as e:
    print(e)
 
# ✅ Đúng: interrupt đứng ngoài, code dễ lỗi xử lý riêng
name = interrupt("What's your name?")
try:
    fetch_data()                       # thứ này mới có thể văng lỗi mạng
except NetworkException as e:          # bắt cụ thể, không chạm interrupt
    print(e)
```
 
### 4.2 Không đổi thứ tự, không bỏ qua interrupt trong cùng một node
 
Khi một node có nhiều `interrupt()`, LangGraph giữ một danh sách giá trị resume riêng cho node đó. Mỗi lần resume, node chạy lại từ đầu; gặp `interrupt()` nào thì lấy giá trị tương ứng trong danh sách. **Việc ghép cặp này thuần theo chỉ số (index)** — interrupt thứ nhất lấy giá trị thứ nhất, thứ hai lấy thứ hai, cứ thế.
 
Cho nên thứ tự các lời gọi `interrupt()` phải **giống hệt nhau qua mọi lần chạy lại**. Nếu ta bỏ qua một interrupt tùy điều kiện, hoặc lặp interrupt theo một danh sách có thể đổi độ dài giữa các lần, thì số lượng và thứ tự interrupt lệch đi — giá trị resume bị ghép nhầm chỗ. Lại là lỗi im lặng: không văng exception, chỉ là câu trả lời cho câu A lại rơi vào câu B.
 
```python
# ✅ Đúng: ba interrupt, thứ tự cố định mọi lần chạy
name = interrupt("What's your name?")
age  = interrupt("What's your age?")
city = interrupt("What's your city?")
```
 
Hai thứ phải tránh: **bỏ qua interrupt theo điều kiện** (`if ...: age = interrupt(...)`) và **lặp interrupt theo dữ liệu không cố định** (`for item in state["dynamic_list"]: interrupt(...)`) — cả hai đều làm số interrupt đổi giữa các lần resume.
 
### 4.3 Chỉ truyền giá trị JSON-serializable vào `interrupt()`
 
Tùy checkpointer, giá trị phức tạp có thể không tuần tự hóa (serialize) được — ví dụ một hàm thì không serialize nổi. Vì payload phải được lưu xuống checkpointer, nên chỉ nên truyền các kiểu đơn giản: chuỗi, số, boolean, hoặc dict/list chứa các giá trị đơn giản.
 
Không truyền hàm, không truyền instance của class, không truyền object phức tạp. Truyền dict mô tả câu hỏi kèm dữ liệu thô thì được; nhét một validator function hay một `DataProcessor` vào dict đó thì hỏng lúc serialize.
 
### 4.4 Side effect đặt trước `interrupt()` phải idempotent
 
Vì node chạy lại từ đầu mỗi lần resume (mục 4), mọi side effect nằm **trước** `interrupt()` sẽ chạy lại. Idempotent nghĩa là chạy nhiều lần vẫn cho cùng một kết quả như chạy một lần.
 
Đặt một lệnh `create_audit_log(...)` hay `append_to_history(...)` trước `interrupt()` là công thức tạo bản ghi trùng: mỗi lần resume lại tạo thêm một bản. Ba cách chữa: dùng thao tác idempotent như `upsert` thay cho `create`; đặt side effect **sau** `interrupt()` để nó chỉ chạy khi đã có câu trả lời; hoặc tách side effect sang một node riêng.
 
```python
# 🔴 Sai: tạo bản ghi trước interrupt → mỗi lần resume thêm một bản trùng
audit_id = db.create_audit_log({...})
approved = interrupt("Approve this change?")
 
# ✅ Đúng: side effect nằm sau interrupt, chỉ chạy sau khi đã duyệt
approved = interrupt("Approve this change?")
if approved:
    db.create_audit_log(user_id=state["user_id"], action="approved")
```
 
---
 
## 5. Năm mẫu dùng thường gặp
 
Cả năm chỉ là biến thể của cùng một cơ chế dừng-chờ-nhận. Nêu để nhận diện tình huống, không cần đào lại cơ chế.
 
**Phê duyệt / từ chối.** Dừng trước một hành động hệ trọng (gọi API, đổi database, giao dịch tài chính), đẩy chi tiết ra cho người xem, resume bằng `True`/`False`. Trong node có thể dựa vào câu trả lời để định tuyến tiếp (`Command(goto="proceed")` hoặc `goto="cancel"`).
 
**Xem lại và sửa trạng thái.** Đưa nội dung do model sinh ra cho người soát, resume bằng bản đã sửa; giá trị đó ghi đè lại trạng thái. Hữu ích khi cần chỉnh output của LLM trước khi đi tiếp.
 
**Interrupt trong tool.** Đặt `interrupt()` thẳng trong hàm tool. Tool tự dừng chờ duyệt mỗi khi được gọi, cho phép người duyệt hoặc sửa tham số tool trước khi thực thi. Logic phê duyệt sống chung với tool nên tái dùng được ở nhiều chỗ trong graph.
 
**Kiểm tra input của người.** Gọi `interrupt()` trong vòng lặp: nhận input, kiểm tra, sai thì lặp lại với lời nhắc rõ hơn, đúng thì thoát vòng. Mỗi lần resume input sai, node hỏi lại với thông báo cụ thể hơn.
 
**Nhiều interrupt cùng lúc.** Khi các nhánh song song cùng dừng (fan-out ra nhiều node, mỗi node gọi `interrupt()`), ta cần resume nhiều interrupt trong một lần gọi. Cách làm: ánh xạ **mỗi interrupt ID với giá trị resume của nó** (`{i.id: giá_trị for i in stream.interrupts}`) để mỗi câu trả lời ghép đúng interrupt.
 
```
(Interrupt(value='question_a', id='...'), Interrupt(value='question_b', id='...'))   ← hai nhánh song song cùng dừng, mỗi Interrupt có .id để ghép giá trị resume
```
 
---
 
 
## 6. Dùng với subgraph gọi như một hàm
 
Khi một node gọi subgraph, và `interrupt()` nằm trong subgraph, thì lúc resume **cả hai đều chạy lại từ đầu node của mình**: graph cha chạy lại từ đầu node đã gọi subgraph, và subgraph chạy lại từ đầu node đã gọi `interrupt()`. Đây chỉ là quy tắc "node chạy lại từ đầu" (mục 4) áp cho hai tầng lồng nhau — nên mọi code trước lời gọi subgraph ở graph cha cũng chạy lại, chịu chung ràng buộc idempotent ở mục 5.4.
 
---
 
## Tham chiếu chéo
 
- [checkpointers](../02-persistence/02-02-checkpointers.md) — cơ chế lưu trạng thái khi interrupt dừng graph; interrupt chỉ dùng lại, không tự lo phần lưu.
- [time travel](./04-02-time-travel.md) — cùng dựa trên checkpointer và `thread_id`; interrupt dừng-chờ-tiếp ở hiện tại, time travel quay về checkpoint cũ.
- Trang tài liệu gốc: `https://docs.langchain.com/oss/python/langgraph/interrupts`
 