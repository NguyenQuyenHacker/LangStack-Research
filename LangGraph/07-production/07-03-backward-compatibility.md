---
title: Tương thích ngược
doc_source: https://docs.langchain.com/oss/python/langgraph/backward-compatibility
accessed: 2026-07-30
lc_version: unknown
status: draft
lab:
related:
  - ../02-persistence/02-02-checkpointers.md
  - ../08-graph-api/08-02-graph-api.md
---

# Tương thích ngược — sửa code production không làm sập cuộc chạy đang dở

> Câu hỏi lõi: cập nhật code bot/agent trên server thế nào để không làm hỏng các cuộc trò chuyện người dùng đang bỏ dở giữa chừng?
> Cơ chế lưu state do file [checkpointers](../02-persistence/02-02-checkpointers.md) phụ trách; conditional edge và danh sách thay đổi LangGraph tự xử lý được (Graph migrations) thuộc file [graph-api](../08-graph-api/08-02-graph-api.md). Ở đây chỉ dùng lại và trỏ sang.

---

## 1. Tổng quan — cái bẫy của LangGraph

Nhiều hệ thống chạy quy trình theo kiểu: người dùng mở một cuộc trò chuyện (một *thread*), hệ thống **khóa cuộc đó vào đúng bản code lúc nó bắt đầu**. Sửa code sau này chỉ ảnh hưởng người vào sau.

LangGraph làm ngược lại. Khi ta deploy bản mới, LangGraph **bắt mọi thread — cũ lẫn mới — chạy ngay bản mới nhất**, dựa trên dữ liệu cũ đang lưu trong database. Dữ liệu cũ đó gồm state (những gì thread đang giữ) và checkpoint (ảnh chụp thread đang dừng ở bước nào).

Lợi: vá một lỗi là cả người đang chat dở cũng được vá luôn, khỏi làm gì thêm. Giá phải trả: nếu dữ liệu cũ trong database không khớp đòi hỏi của code mới, cuộc trò chuyện **sập ngay khi người dùng chat tiếp**.


Ba nhóm trục trặc, xếp theo mức hay gặp:

1. **Trục trặc kỹ thuật** — hay gặp nhất: bản mới không đọc nổi dữ liệu cũ.
2. **Trục trặc nghiệp vụ** — ít hơn: bản mới đọc được, nhưng thread cũ lẽ ra phải theo cách xử lý cũ chứ không phải cách mới.
3. **Chạy lại ra kết quả khác** (tính bất định) — chỉ xảy ra với Functional API.

LangGraph vốn tự nuốt được một số thay đổi thông thường; danh sách đó ở mục "Graph migrations" của file [graph-api](../08-graph-api/08-02-graph-api.md). Trang này chỉ bàn những thay đổi *nằm ngoài* danh sách đó — chỗ ta phải tự lo.

---

## 2. Trục trặc kỹ thuật — code mới phải đọc được dữ liệu cũ

Khi người dùng chat tiếp, LangGraph làm ba việc liền nhau: lấy dữ liệu cũ từ database, nạp vào khuôn state, rồi gửi tới đúng *tên bước* (node) tiếp theo, chờ bước đó trả về giá trị khớp khuôn state. Vỡ bất kỳ khâu nào trong ba khâu này là sập.


### 2.1 Ba thay đổi dễ làm sập nhất

**Đổi tên hoặc xóa một node (bước xử lý).** Khách đang dừng ở bước `xac_nhan_don` chờ bấm xác nhận. Ta deploy bản mới, đổi tên bước này thành `review_don`. Khách bấm tiếp → LangGraph tìm bước `xac_nhan_don` cũ không thấy → sập. Lý do: điểm bắt đầu khi chạy tiếp là *đầu node nơi thread đã dừng*, node biến mất thì không còn chỗ để tiếp. Điều này đúng cả khi thread đang treo ở một `interrupt`, hoặc một conditional edge đã lưu vẫn định tuyến tới tên cũ.

**Đổi tên hoặc xóa một biến trong state.** Code cũ lưu tên khách vào biến `ten_khach`. Code mới hứng bằng biến `ho_ten`. Code mới đọc `ho_ten` → không có → lỗi. Cũng vỡ nếu biến bị xóa mà một node phía sau còn đọc.

**Thêm một trường bắt buộc.** Code mới bắt buộc phải có `so_dien_thoai`. Khách chat từ hôm qua chưa từng được hỏi trường này. Dữ liệu cũ không qua nổi khâu kiểm (validate) → sập. Cùng kiểu vỡ: biến `Optional` thành bắt buộc, hoặc thu hẹp kiểu dữ liệu.

**!Note:** Thêm, bớt, đổi hướng **đường nối (edge)** giữa các node *vẫn còn tồn tại* là an toàn — hướng đi giữa các bước không được lưu trong checkpoint. Thay đổi *duy nhất* làm vỡ một thread đang treo là đổi tên hoặc xóa node. Đừng ngại sửa đường nối; hãy dè chừng đúng chuyện node.

### 2.2 Cách sửa code an toàn

**Khai biến mới dạng "không bắt buộc".** Dùng `NotRequired` (hoặc `Optional[...] = None`) để dữ liệu cũ thiếu trường này vẫn nạp bình thường:

```python
from typing import NotRequired
from typing_extensions import TypedDict

class State(TypedDict):
    messages: list
    summary: NotRequired[str]        # trường mới KHÔNG bắt buộc → dữ liệu cũ thiếu 'summary' vẫn nạp được
```

**Xóa thì coi như "ngưng dùng", đừng xóa ngay.** Giữ biến/node cũ được khai thêm một thời gian — ít nhất một chu kỳ *drain* (để các thread cũ chạy cạn) — kể cả khi không còn node nào đọc nó. Có vậy dữ liệu cũ mới nạp tiếp được.

**Đổi tên bằng "thêm trước — xóa sau".** Đừng đổi thẳng. Tạo cái mới chạy song song cái cũ, ghi/định tuyến cả hai trong một giai đoạn chuyển tiếp, rồi mới xóa cái cũ khi đã chắc không thread nào đang treo còn phụ thuộc.

**Giữ node bao dung với biến lạ.** `TypedDict` bỏ qua biến thừa lúc chạy, nên dữ liệu sót từ bản cũ không gây lỗi — *trừ khi* một node đọc thẳng một biến không tồn tại.

**Soi thử trên staging trước khi tung ra.** Dùng time travel và `graph.get_state` để đối chiếu vài thread cũ với code mới trên bản deploy staging trước.


### 2.3 Làm sao biết còn ai đang dùng code cũ

Trước khi xóa node hay biến cũ, ta cần biết *có thread nào đang đậu trên bản sắp bỏ không*. LangGraph không tự giữ chỉ mục tìm kiếm trên state của thread, nên câu trả lời tùy nơi đồ thị chạy. Ba đường tra:

**Nếu deploy lên LangSmith.** Dùng thread search của Agent Server, lọc theo trạng thái. Trường `status` nhận `idle`, `busy`, `interrupted`, `error` — truy hàng loạt các thread `interrupted` (đang chờ) hoặc `busy` (đang chạy), thu hẹp thêm bằng bộ lọc metadata.

**Chạy ở bất kỳ đâu.** Dùng LangSmith tracing để theo dõi mấy ngày qua có lượt nào rơi vào node sắp xóa không. Đây là tín hiệu đáng tin nhất cho biết một node/biến đã không còn đường nào chạm tới.

**Khi đã có sẵn một `thread_id`.** Soi thẳng thread đó:

```python
graph.get_state(config)            # checkpoint mới nhất: đang dừng ở node nào, có interrupt nào chờ
graph.get_state_history(config)    # toàn bộ danh sách checkpoint của thread theo thứ tự thời gian
```

Còn phân vân thì cứ giữ node/biến sắp bỏ tại chỗ, đến khi cả danh sách thread lẫn tracing đều cho thấy không còn hoạt động nào trên nó.

---

## 3. Trục trặc nghiệp vụ

Có thay đổi *không* làm sập nhưng làm *sai logic* cho khách cũ: mọi dữ liệu cũ vẫn nạp được, mọi node vẫn tìm thấy, nhưng ý nghĩa của luồng đã khác. Hành vi mới đúng cho khách mới, ta không muốn áp ngược lên khách đã bắt đầu theo luồng cũ.

Cách xử lý: **đóng dấu phiên bản luồng lên state ngay ở bước đầu tiên**, rồi rẽ nhánh bằng một conditional edge (cơ chế conditional edge xem file [graph-api](../08-graph-api/08-02-graph-api.md)).

```python
from typing import NotRequired
from typing_extensions import TypedDict
from langgraph.graph import END, START, StateGraph

class State(TypedDict):
    request: str
    flow_version: NotRequired[int]        # lưu phiên bản luồng; không bắt buộc → khách cũ thiếu nó vẫn hợp lệ
    response: NotRequired[str]

def intake(state: State) -> dict:
    # Khách MỚI vào đây được đóng dấu flow_version = 2.
    # Khách CŨ chạy tiếp qua intake giữ nguyên giá trị đã lưu (state.get trả cái cũ nếu đã có).
    return {"flow_version": state.get("flow_version", 2)}

def triage(state: State) -> dict: ...
def policy_check(state: State) -> dict: ...
def respond(state: State) -> dict: ...

def after_triage(state: State) -> str:
    if state.get("flow_version", 1) >= 2:     # khách cũ không có flow_version → mặc định 1 → bỏ qua policy_check
        return "policy_check"                 # khách mới → bắt buộc kiểm tra chính sách
    return "respond"                          # khách cũ → đi thẳng

builder = StateGraph(State)
builder.add_node("intake", intake)
builder.add_node("triage", triage)
builder.add_node("policy_check", policy_check)
builder.add_node("respond", respond)
builder.add_edge(START, "intake")
builder.add_edge("intake", "triage")
builder.add_conditional_edges("triage", after_triage, ["policy_check", "respond"])   # rẽ nhánh theo flow_version
builder.add_edge("policy_check", "respond")
builder.add_edge("respond", END)

graph = builder.compile()
```

Hành vi: khách cũ chạy tiếp *sau* `triage` đọc `flow_version` từ state đã lưu (hoặc rơi về mặc định 1) và bỏ qua `policy_check`. Khách mới bắt đầu ở `intake`, được đóng dấu `flow_version=2`, chạy đường mới. Khi mọi thread v1 đã xong, gỡ cờ phiên bản và conditional edge đi.

Hai mặc định khác nhau là cố ý: `intake` đóng dấu **2** cho khách mới, `after_triage` mặc định **1** — vì khách cũ chưa từng qua `intake` bản mới nên không có `flow_version`, và ta muốn họ rơi về nhánh cũ.

**!Note:** Khuôn này chỉ chạy đúng nếu đóng dấu phiên bản *ngay lúc thread bắt đầu*, trước mọi nhánh cần phân phiên bản. Đóng dấu muộn hơn thì khách cũ không có giá trị này đúng lúc cần đọc — và nhánh rẽ sai mà không hề báo lỗi.

---

## 4. Chạy lại ra kết quả khác — cái bẫy riêng của Functional API

Nhóm này *chỉ* áp dụng cho Functional API, và cho lời gọi **task** hoặc `interrupt` nằm *bên trong* một node của Graph API. Node Graph API thuần thì khi chạy tiếp sẽ chạy lại từ đầu hàm node — chỉ cần thiết kế side effect sao cho idempotent (chạy nhiều lần vẫn ra một kết quả), không cần giữ thứ tự lời gọi trừ khi node đó có dùng task/`interrupt`.

Vì sao thành bẫy: một `@entrypoint` của Functional API khi khôi phục (resume) sẽ **chạy lại từ đầu toàn bộ thân hàm**, dùng kết quả `@task` đã lưu trong cache để bỏ qua phần đã làm. Hai kiểu thay đổi phá vỡ mô hình này:

**Thêm, bớt, đổi thứ tự lời gọi `@task` / `interrupt`** nằm *trước* điểm khôi phục. LangGraph khớp kết quả cache với lời gọi *theo vị trí* trong lần chạy lại; chèn một task vào giữa làm kết quả của task A bị gán nhầm cho task B.

**Đưa phép toán ngẫu nhiên/thời gian ra ngoài `@task`**, ví dụ `time.time()`, `random.random()`, hay một lời gọi mạng viết thẳng trong thân entrypoint. Khi chạy lại, chúng cho giá trị khác lần đầu → rẽ sai nhánh.

**!Note:** Cả hai đều là lỗi im lặng: không nổ exception, chỉ âm thầm chạy nhầm nhánh hoặc phát nhầm giá trị cache. `time.time()` cài thẳng trong thân entrypoint là cái dễ mắc nhất.

Khi buộc phải sửa đáng kể một `@entrypoint` đang có thread treo, ba lối an toàn: để thread treo chạy cạn (drain) rồi mới deploy; bọc logic mới vào một `@task` mới để kết quả được lưu riêng; hoặc đăng ký một entrypoint mới dưới *tên đồ thị mới* trong `langgraph.json` rồi định tuyến khách mới sang đó.

Cơ chế chạy lại, task, entrypoint thuộc phạm vi file Functional API (chưa có trong bộ này); ở đây chỉ nêu ảnh hưởng của chúng tới tương thích ngược.

---

## 5. Bảng tra nhanh — đổi gì, nguy cơ gì, xử lý sao

| Muốn đổi gì | Nguy cơ | Cách xử lý an toàn |
|---|---|---|
| Đổi tên / xóa node | Thread cũ đang dừng ở node đó → chạy tiếp là sập | "Thêm trước — xóa sau"; giữ node cũ tới khi hết khách treo |
| Xóa / đổi tên biến state | Code mới không đọc được dữ liệu cũ | Coi biến cũ là ngưng dùng, giữ khai báo thêm một chu kỳ drain |
| Thêm trường bắt buộc | Dữ liệu cũ không qua nổi khâu kiểm | Khai `NotRequired` hoặc `Optional[...] = None` |
| Thêm / bớt / đổi hướng edge | *An toàn* — hướng đi không lưu trong checkpoint | Sửa thoải mái, miễn node liên quan còn tồn tại |
| Chèn bước mới vào quy trình | Khách cũ bị ép chạy theo logic mới | Đóng dấu `flow_version` từ đầu + rẽ nhánh điều kiện |
| Sửa thân `@entrypoint` | Chạy lại phát nhầm cache / sai thứ tự | Drain, bọc logic mới vào `@task` mới, hoặc entrypoint tên mới |

Chốt lại: mọi khuôn ở đây đứng trên một sự thật duy nhất — code mới gặp dữ liệu cũ. Kỹ thuật lo *đọc được*, nghiệp vụ lo *chạy đúng logic của thời điểm thread sinh ra*, bất định lo *chạy lại khớp vị trí*. Nắm trục này thì mỗi lần chuẩn bị ship, câu hỏi luôn là: "thread đang treo trên bản cũ sẽ ra sao?"

---

## Tham chiếu chéo

- [02-02 Checkpointers](../02-persistence/02-02-checkpointers.md) — cơ chế lưu state theo thread mà toàn bộ chuyện tương thích ngược dựa vào; hợp đồng "code ↔ dữ liệu cũ" bắt nguồn từ đây.
- [08-02 Graph API](../08-graph-api/08-02-graph-api.md) — conditional edge (Mục 3), và mục "Graph migrations" liệt kê những thay đổi LangGraph tự xử lý được.
- Trang gốc: `https://docs.langchain.com/oss/python/langgraph/backward-compatibility`
- Chủ đề liên quan chưa mở trong bộ này (trang gốc có link, cần fetch khi tra sâu): Functional API / `@task` / `@entrypoint` / determinism; time travel; observability (LangSmith tracing); thread search của Agent Server.