---
title: Functional API
doc_source: https://docs.langchain.com/oss/python/langgraph/functional-api
accessed: 2026-07-30
lc_version: unknown
status: draft
lab:
related:
  - ./09-02-use-functional-api.md
  - ../08-graph-api/08-01-choosing-apis.md
---

# Functional API (`@entrypoint`, `@task`)

> Cách thêm persistence, bộ nhớ, dừng chờ người và streaming vào code Python sẵn có mà không phải cấu trúc lại thành pipeline.
> File công thức thực hành nằm ở [09-02](./09-02-use-functional-api.md); phần chọn giữa hai API xem [08-01](../08-graph-api/08-01-choosing-apis.md).

---

## 1. Tổng quan

Functional API gắn bốn tính năng lõi của LangGraph — lưu trạng thái (persistence), bộ nhớ, dừng chờ người xử lý (human-in-the-loop), streaming — vào code có sẵn mà gần như không sửa cấu trúc. Điểm khác so với các framework điều phối khác: chúng bắt gói logic thành pipeline hoặc DAG tường minh, còn Functional API để nguyên `if`, `for`, lời gọi hàm Python thường.

Nó dựng trên hai viên gạch. `@entrypoint` đánh dấu hàm khởi đầu của workflow. `@task` bọc một đơn vị công việc rời. Cả hai chạy trên cùng runtime với [Graph API](../08-graph-api/08-01-choosing-apis.md) nên trộn chung được trong một ứng dụng.

```python
@task
def is_even(number: int) -> bool:                  # đơn vị công việc rời, kết quả sẽ được checkpoint
    return number % 2 == 0

@entrypoint(checkpointer=InMemorySaver())          # checkpointer bật persistence cho workflow
def workflow(inputs: dict) -> str:                 # entrypoint nhận đúng một tham số vị trí
    even = is_even(inputs["number"]).result()      # .result() chờ future trả về, chạy đồng bộ
    return "chẵn" if even else "lẻ"

config = {"configurable": {"thread_id": "1"}}      # thread_id định danh một mạch chạy để lưu/khôi phục
print(workflow.invoke({"number": 7}, config))
```

**Kết quả in ra**:

```python
lẻ    # 7 lẻ nên task is_even trả False, entrypoint chọn nhánh "lẻ"
```

Đoạn trên là mọi thứ Functional API cần ở mức tối thiểu: một task, một entrypoint có checkpointer, một `thread_id`. Các tính năng còn lại đều dựng thêm quanh khung này.

---

## 2. `@entrypoint` — cửa vào của workflow

### Khái niệm

`@entrypoint` biến một hàm thường thành điểm khởi đầu workflow. Hàm được trang trí không còn là hàm bình thường nữa: nó trả về một đối tượng `Pregel` — bộ máy điều phối lo streaming, resume, checkpoint.

### Vai trò

Nó lo phần "chạy dài và có thể bị dừng giữa chừng". Một hàm Python thường chạy một mạch từ đầu tới cuối rồi mất sạch trạng thái. Entrypoint có checkpointer thì mỗi lần chạy được ghi lại, dừng ở một điểm chờ người duyệt rồi chạy tiếp sau nhiều giờ vẫn được.

**Ràng buộc một tham số.** Entrypoint chỉ nhận **một** tham số vị trí làm đầu vào. Cần truyền nhiều thứ thì gói vào một `dict`.

**Cần checkpointer.** Không có checkpointer thì mất persistence và mất luôn human-in-the-loop. Muốn dừng chờ người thì checkpointer là bắt buộc.

### Áp dụng thực tế

Một workflow soạn tờ trình rồi dừng cho trưởng nhóm duyệt. Người duyệt đi họp cả buổi chiều — entrypoint có checkpointer giữ nguyên bản nháp đã soạn, đến tối mở lại duyệt vẫn tiếp đúng chỗ, không phải soạn lại từ đầu.

### Tham số được tiêm tự động

Ngoài đầu vào, entrypoint khai báo thêm vài tham số thì runtime tự truyền vào lúc chạy. Khai đúng tên và đúng kiểu mới nhận được.

| Tham số | Kiểu | Dùng để |
|---|---|---|
| `previous` | `Any` | Đọc trạng thái từ checkpoint lần chạy trước — xem mục 4 |
| `store` | `BaseStore` | Bộ nhớ dài hạn, dùng chung qua nhiều thread — xem [02-04](../02-persistence/02-04-add-memory.md) |
| `writer` | `StreamWriter` | Phát dữ liệu tùy biến khi viết async trên Python < 3.11 |
| `config` | `RunnableConfig` | Đọc cấu hình lúc chạy (trong đó có `thread_id`) |

`store` và `writer` chỉ cần khi thật sự dùng bộ nhớ dài hạn hoặc streaming tùy biến; đa số workflow không khai hai cái này.

**!Note:** Đầu vào và giá trị trả về của entrypoint phải JSON-serializable (dict, list, chuỗi, số, bool). Truyền vào một object không serialize được thì lỗi phát sinh **lúc chạy**, không phải lúc khai báo — nên dễ lọt qua khi viết. Lý do ràng buộc: có serialize được thì mới ghi vào checkpoint và khôi phục được.

---

## 3. `@task` — đơn vị công việc rời

### Khái niệm

`@task` bọc một hàm thành một đơn vị công việc: một lời gọi API, một bước xử lý dữ liệu. Gọi task ra thì nó trả về **ngay** một future — chỗ giữ chỗ cho kết quả sẽ có sau. Lấy kết quả bằng `.result()` (đồng bộ) hoặc `await` (async).

### Vai trò

Đây là chỗ then chốt của cả Functional API. Task lo hai việc mà entrypoint trần không lo được:

Thứ nhất, **kết quả task được ghi vào checkpoint**. Khi workflow bị dừng rồi resume, task đã chạy xong sẽ được lấy lại từ checkpoint chứ không tính lại. Một lời gọi LLM tốn 30 giây, chạy xong một lần là thôi.

Thứ hai, **task cô lập cái không ổn định**. Giá trị ngẫu nhiên, giờ hệ thống, lời gọi mạng — mọi thứ có thể cho kết quả khác nhau giữa các lần — phải nằm trong task thì resume mới khớp lại đúng (xem mục 5).

### Áp dụng thực tế

Một workflow tra cứu 500 mã doanh nghiệp qua API, chạy mất 40 giây, rồi dừng chờ người dùng chọn lọc kết quả. Người dùng bỏ đi ăn trưa, một giờ sau quay lại bấm resume. Nếu lời gọi API nằm trong task, 500 kết quả đã lấy được khôi phục từ checkpoint tức thì; nếu để trần trong entrypoint, workflow gọi lại API 500 mã lần nữa.

### Nơi gọi task

Task **chỉ** gọi được từ trong một entrypoint, một task khác, hoặc một node của [Graph API](../08-graph-api/08-01-choosing-apis.md). Gọi thẳng task từ code ứng dụng chính sẽ không chạy đúng.

### Khi nào cần bọc thành task

- Cần lưu kết quả một thao tác chạy dài để khỏi tính lại khi resume.
- Có human-in-the-loop: **bắt buộc** bọc mọi thứ ngẫu nhiên vào task để resume khớp đúng.
- Cần chạy song song nhiều thao tác I/O (gọi nhiều API cùng lúc).
- Cần theo dõi tiến độ từng bước qua LangSmith.
- Cần cơ chế thử lại khi thất bại.

**!Note:** Đầu ra của task cũng phải JSON-serializable, cùng lý do như entrypoint.

---

## 4. Bộ nhớ ngắn hạn — `previous` và `entrypoint.final`

### Khái niệm

Khi entrypoint có checkpointer, nó nhớ dữ liệu giữa các lần gọi **trên cùng một `thread_id`**. Lần chạy sau đọc lại trạng thái lần chạy trước qua tham số `previous`. Mặc định, `previous` chính là **giá trị return của lần chạy trước**.

```python
@entrypoint(checkpointer=checkpointer)
def my_workflow(number: int, *, previous: Any = None) -> int:
    previous = previous or 0                       # lần đầu previous là None, gán về 0
    return number + previous                       # giá trị trả về này sẽ thành previous của lần sau

my_workflow.invoke(1, config)                      # previous None → trả 1
my_workflow.invoke(2, config)                      # previous là 1 (trả về lần trước) → trả 3
```

**Kết quả in ra:**

```
1    ← invoke(1): number=1, previous rỗng → 0, kết quả 1 + 0
3    ← invoke(2): number=2, previous = 1 (trả về lần trước), kết quả 2 + 1
```

### Vai trò của `entrypoint.final` — tách giá trị trả khỏi giá trị lưu

Mặc định, cái trả về cho người gọi cũng là cái lưu vào checkpoint. Có lúc ta muốn hai cái này khác nhau: trả cho người gọi một bản tóm tắt, nhưng lưu lại một trạng thái nội bộ để lần sau dùng tiếp.

`entrypoint.final(value=..., save=...)` tách đôi: `value` trả cho người gọi, `save` ghi vào checkpoint và thành `previous` lần sau.

```python
@entrypoint(checkpointer=checkpointer)
def accumulate(n: int, *, previous: int | None) -> entrypoint.final[int, int]:
    previous = previous or 0
    total = previous + n
    return entrypoint.final(value=previous, save=total)   # trả previous cho caller, lưu total cho lần sau

print(accumulate.invoke(1, config))                # trả previous (0), lưu 1
print(accumulate.invoke(2, config))               # trả previous (1), lưu 3
print(accumulate.invoke(3, config))               # trả previous (3), lưu 6
```

**Kết quả in ra:**

```
0    ← trả previous lần trước (rỗng → 0), trong khi checkpoint đã lưu 1
1    ← trả previous (1), checkpoint lưu 3
3    ← trả previous (3), checkpoint lưu 6
```

Nếu ứng dụng chỉ cần "trả gì lưu nấy" thì **bỏ qua `entrypoint.final`**. Đây là công cụ cho trường hợp giá trị trả và giá trị lưu cần lệch nhau, không phải kiến thức bắt buộc.

Các công thức bộ nhớ ngắn hạn cụ thể — xem trạng thái thread, lịch sử checkpoint, dựng chatbot nhớ hội thoại — nằm ở [09-02 mục 6](./09-02-use-functional-api.md). Khái niệm bộ nhớ dài hạn nằm ở [02-04](../02-persistence/02-04-add-memory.md).

---

## 5. Determinism — vì sao resume phải "phát lại từ đầu"

### Khái niệm

Đây là chỗ dễ hiểu sai nhất, và hiểu sai nó thì workflow có human-in-the-loop chạy ra kết quả lệch mà không báo lỗi.

Khi resume một workflow, code **không** chạy tiếp từ dòng nơi nó dừng. Nó quay về ranh giới checkpoint và **phát lại** từ đầu entrypoint. Trong lúc phát lại, LangGraph khôi phục kết quả các task và subgraph đã hoàn tất từ checkpoint thay vì tính lại — nhờ đó giữ đúng thứ tự các bước, kể cả với task cho kết quả không cố định.

### Vì sao cái ngẫu nhiên phải nằm trong task

Vì entrypoint phát lại từ đầu, một câu lệnh ngẫu nhiên viết trần trong entrypoint sẽ cho **giá trị mới** mỗi lần phát lại. Bọc nó vào task thì giá trị được khôi phục từ checkpoint, giữ nguyên qua các lần resume.

```
Trong task:      lấy số random (5) → dừng → resume → (khôi phục lại 5) → ...
Không trong task: lấy số random (5) → dừng → resume → lấy random mới (7) → ...
```

### Ghép interrupt với resume theo chỉ số

Điểm này quan trọng với workflow có nhiều lần dừng. LangGraph giữ một danh sách giá trị resume cho mỗi task/entrypoint. Mỗi lần gặp `interrupt`, nó ghép với giá trị resume tương ứng **theo chỉ số** (interrupt thứ nhất ↔ resume thứ nhất). Cơ chế `interrupt` chi tiết xem [04-01](../04-human-in-the-loop/04-01-interrupts.md).

**!Note:** Nếu thứ tự thực thi không được giữ nguyên khi resume — ví dụ vì có nhánh `if` phụ thuộc vào giờ hệ thống lấy trần trong entrypoint — một lần `interrupt` có thể bị ghép nhầm với giá trị resume của lần khác. Code vẫn chạy, không lỗi, chỉ ra kết quả sai. Cách tránh: mọi nhánh rẽ phải phụ thuộc vào **đầu vào** hoặc kết quả **task**, không phụ thuộc vào thứ tính trần trong entrypoint.

---

## 6. Idempotency — thiết kế side effect chịu được chạy lại

### Khái niệm

Idempotent nghĩa là chạy cùng một thao tác nhiều lần cho ra cùng kết quả. Với Functional API, điều này áp cho các thao tác có ghi dữ liệu (gọi API tạo bản ghi, gửi email).

### Vai trò

Khi resume, LangGraph phát lại kết quả các task đã hoàn tất từ checkpoint. Nhưng một task đã **bắt đầu mà chưa kết thúc** thì sẽ chạy lại từ đầu ở lần resume đó. Nếu task đó gửi email, người dùng nhận hai email.

Cách xử lý: đặt mọi lời gọi API vào trong task, và thiết kế chúng idempotent — dùng khóa idempotency, hoặc kiểm tra bản ghi đã tồn tại chưa trước khi tạo.

### Side effect phải nằm trong task

Một hệ quả trực tiếp của determinism: side effect (ghi file, gửi email) viết trần trong entrypoint sẽ chạy lại khi resume vì entrypoint phát lại từ đầu. Bọc vào task thì nó chỉ chạy một lần, lần sau khôi phục từ checkpoint.

```python
@task
def write_to_file():                               # side effect được bọc trong task
    with open("output.txt", "w") as f:
        f.write("Side effect executed")

@entrypoint(checkpointer=checkpointer)
def my_workflow(inputs: dict) -> int:
    write_to_file().result()                       # chạy đúng một lần, resume không lặp lại
    value = interrupt("question")                  # dừng chờ người; xem 04-01 cho cơ chế interrupt
    return value
```

**!Note:** Cùng đoạn này nhưng viết `open(...).write(...)` thẳng trong `my_workflow` thay vì trong task thì file bị ghi **lần thứ hai** khi resume qua `interrupt` — thường không phải điều ta muốn.

---

## 7. Functional API so với Graph API

Hai API cùng runtime, khác ở cách ta mô tả workflow.

| Tiêu chí | Functional API | Graph API |
|---|---|---|
| Luồng điều khiển | `if`, `for`, gọi hàm Python thường | Khai báo graph (node, cạnh) tường minh |
| Bộ nhớ ngắn hạn | Trạng thái cục bộ trong hàm, không chia sẻ | Phải khai `State`, có thể phải viết reducer |
| Checkpoint | Kết quả task ghi vào checkpoint đang có | Sinh checkpoint mới sau mỗi superstep |
| Trực quan hóa | Không vẽ được (graph sinh động lúc chạy) | Vẽ được thành sơ đồ để debug, chia sẻ |

### Nên chọn cái nào

Chọn **Functional API** khi: đã có code Python với `if`/`for` sẵn và chỉ muốn thêm persistence/HIL/streaming vào; muốn ít code, không muốn nghĩ theo cấu trúc graph; không cần vẽ sơ đồ workflow.

Chọn **Graph API** khi: cần vẽ workflow thành sơ đồ để debug hoặc trình bày; muốn cách khai báo tường minh với state và reducer.

Phần so sánh đầy đủ hơn và tiêu chí chọn nằm ở [08-01](../08-graph-api/08-01-choosing-apis.md).

---

## Tham chiếu chéo

- [09-02 Dùng Functional API](./09-02-use-functional-api.md) — các công thức thực hành: chạy song song, retry, timeout, cache, resume sau lỗi, quản lý checkpoint, chatbot.
- [08-01 Chọn giữa Graph API và Functional API](../08-graph-api/08-01-choosing-apis.md) — so sánh sâu và tiêu chí chọn.
- [04-01 Interrupts](../04-human-in-the-loop/04-01-interrupts.md) — cơ chế `interrupt` và `Command(resume=...)`.
- [02-04 Bộ nhớ](../02-persistence/02-04-add-memory.md) — bộ nhớ ngắn hạn và dài hạn.