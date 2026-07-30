---
title: Subgraph
doc_source: https://docs.langchain.com/oss/python/langgraph/use-subgraphs
accessed: 2026-07-29
lc_version: unknown
status: draft
lab:
related:
  - ../02-persistence/02-02-checkpointers.md
  - ../03-streaming/03-01-streaming.md
---

# Subgraph — graph lồng trong graph

> Subgraph là một graph hoàn chỉnh được cắm vào graph khác như một node. Dùng để dựng hệ multi-agent, tái sử dụng một cụm node, hoặc chia việc cho nhiều nhóm phát triển độc lập.
> Cơ chế checkpointer nói chung nằm ở [02-02 checkpointers](../02-persistence/02-02-checkpointers.md); ở đây ta chỉ xét nó áp vào subgraph ra sao.

---

## 1. Tổng quan

**`Subgraph`**  là một graph được cắm vào graph khác làm node. Node thường là một hàm — nhận state, trả về phần cần cập nhật. Subgraph thay chỗ hàm đó bằng cả một graph có node, edge và state schema riêng: nhìn từ ngoài graph cha vẫn thấy một node, nhìn vào trong là một cỗ máy hoàn chỉnh.
 
**Dùng nó cho ba việc**: 
- dựng hệ multi-agent (mỗi agent một subgraph), 
- tái sử dụng một cụm node ở nhiều graph, và 
- phân chia phát triển (mỗi nhóm làm một subgraph, giữ đúng giao diện vào/ra thì cha ráp lại được mà không cần biết ruột bên trong).
 
---

## 2. Hai cách nối state giữa cha và subgraph
 
Trước hết cần hiểu "key". Hình dung state của một graph là **một tờ khai có sẵn vài ô, mỗi ô có tên**. "Key" chính là tên của một ô. Graph chạy tới đâu thì chuyền tay nhau tờ khai đó; mỗi node đọc ô nó cần và ghi vào ô nó muốn.
 
Điểm mấu chốt: **mỗi graph tự quy định tờ khai của nó có ô nào.** Người viết graph cha quyết định cha có ô gì; người viết subgraph quyết định subgraph có ô gì. Hai bên không nhất thiết giống nhau.
 
Vậy câu hỏi quyết định, hỏi trước khi nối: **cha và subgraph có ô nào trùng tên nhau không?** Trả lời xong là biết chọn cách nào.
 
### 2.1 Trùng ô → cắm thẳng subgraph vào node
 
Khi subgraph đọc và ghi trên đúng những ô mà cha đang dùng, ta truyền thẳng subgraph đã compile vào `add_node`, không cần hàm trung gian. Trường hợp hay gặp là các agent cùng ghi vào một cuộc hội thoại `messages`:
 
```python
# tra_cuu_kh: subgraph đã compile, dùng chung ô messages với cha
builder.add_node("tra_cuu", tra_cuu_kh)   # cắm thẳng, không hàm bọc
```
 
Vì chung một ô nên con ghi vào đâu là cha đọc được ngay, không có bước chuyển đổi nào.
 
### 2.2 Khác ô → gọi subgraph bên trong một node
 
Khi subgraph có tờ khai riêng, không ô nào trùng tên với cha, ta không cắm thẳng được: đưa cho con một tờ khai toàn ô lạ, con nhìn vào không thấy ô nào nó biết nên **không biết lấy dữ liệu ở đâu**. Lúc này phải có người đứng giữa chép dữ liệu từ ô của cha sang đúng ô con đòi, rồi chép kết quả ngược lại. Người đứng giữa đó là **hàm node bọc**.
 
Quy tắc của hàm bọc gói trong một câu: **cái ta đưa vào `.invoke(...)` phải khớp tên ô đầu vào của subgraph.** Dữ liệu lấy từ đâu là chuyện của ta — thường là đọc ra từ ô của cha.
 
Ví dụ: cha giữ mã xe trong ô `car_id`, subgraph tra cứu lại chỉ biết ô vào `ma_o_to` và ô ra `ket_qua`. Hàm bọc đổi tên ô ở cả hai đầu:
 
```python
def call_tra_cuu(state):                                # state là tờ khai của cha
    out = tra_cuu_xe.invoke({"ma_o_to": state["car_id"]})   # vào: đọc car_id của cha, dán vào ô ma_o_to
    return {"thong_tin_xe": out["ket_qua"]}                 # ra:  lấy ket_qua của con, dán vào ô thong_tin_xe
```
 
Đọc cho đúng: `state["car_id"]` chỉ là **đọc giá trị sẵn có** trong ô `car_id` của cha, không tra cứu gì. Việc đi tìm hồ sơ xe là việc subgraph làm **bên trong nó**, sau khi đã nhận `ma_o_to`. Hàm bọc chỉ làm mỗi việc đổi nhãn ô ở hai đầu.
 
Diễn biến với `car_id = "123123"` (dựng lại — tài liệu không in output cho ví dụ này):
 
```
cha có sẵn:   car_id = "123123"                    ← ai đó điền từ trước, hàm bọc chỉ đọc
đưa cho con:  {"ma_o_to": "123123"}                ← đổi nhãn ô, chưa tra cứu gì
con xử lý:    tra cứu xong, trả  {"ket_qua": {...}}  ← "đi tìm" là việc bên trong con
trả về cha:   thong_tin_xe = {...}                 ← đổi nhãn ket_qua -> thong_tin_xe
```
 
Một điểm cần nhớ: cái quyết định chọn cách nào **không phải subgraph làm gì bên trong**, mà chỉ là **tên ô vào/ra của nó có khớp ô của cha không**. Bên trong phức tạp đến đâu cũng chỉ cần nhìn ô vào và ô ra.
 
**!Note:** Khi cắm thẳng subgraph vào node mà hai bên **vô tình trùng tên ô nhưng ý nghĩa khác nhau**, subgraph ghi đè lên state của cha mà không báo lỗi — dữ liệu bị lẫn. Trùng ô là hợp đồng giao tiếp, phải cố ý; trùng nhầm là bug khó truy.

---

## 3. Cơ chế duy trì bộ nhớ của Subgraph

Ví dụ: hình dung một bot chăm sóc khách hàng, mỗi khi gặp câu hỏi hóc thì đẩy sang một subagent chuyên trách. Subagent "chuyên viên thanh toán" **có nên nhớ** những câu khách đã hỏi ở lượt trước, hay mỗi lần được gọi lại bắt đầu từ con số không?

Tham số đó là `checkpointer` khi gọi `.compile()` trên subgraph. Ba giá trị, ba chế độ:

| Chế độ | `checkpointer=` | Hành vi cốt lõi |
|---|---|---|
| Per-invocation (mặc định) | `None` | Mỗi lần gọi bắt đầu mới tinh, nhưng trong phạm vi một lần gọi vẫn thừa hưởng checkpointer của cha để hỗ trợ interrupt và chạy bền |
| Per-thread | `True` | State tích lũy qua các lần gọi trên cùng một thread; lần sau tiếp nối lần trước |
| Stateless | `False` | Không lưu checkpoint gì cả, chạy như một lời gọi hàm thường; không interrupt, không chạy bền |

**!Note:** Muốn các tính năng persistence của subgraph (interrupt, xem state, nhớ qua nhiều lượt) hoạt động, **graph cha bắt buộc phải được compile kèm một checkpointer**. Subgraph để `None` chỉ có nghĩa "kế thừa của cha" — nếu cha không có gì để kế thừa thì cũng bằng không.

### 3.1 Per-invocation — mặc định, mỗi lần gọi một đời sống riêng

Chọn chế độ này khi mỗi lần gọi subgraph là độc lập, subagent không cần nhớ gì từ lần trước. Đây là kiểu phổ biến nhất, đặc biệt trong hệ multi-agent nơi subagent xử lý các yêu cầu rời rạc kiểu "tra đơn hàng của khách này" hay "tóm tắt tài liệu kia".

Để trống `checkpointer` hoặc đặt `None`. Mỗi lần gọi khởi động lại từ đầu — hỏi về táo xong, hỏi tiếp về chuối thì subagent không còn nhớ gì về táo. Nhưng có một điểm tinh tế: **trong lòng một lần gọi**, subgraph vẫn mượn checkpointer của cha, nên nó vẫn `interrupt()` để dừng chờ người duyệt rồi chạy tiếp được. "Mới tinh mỗi lần gọi" không đồng nghĩa với "không dừng được giữa chừng".

Gọi cùng một subgraph nhiều lần trong một lượt cũng không xung đột — mỗi lần gọi được cấp một không gian checkpoint (namespace) riêng, nên hỏi chuyên viên trái cây về táo và về chuối cùng lúc vẫn chạy song song êm.

### 3.2 Per-thread — subagent tích lũy trí nhớ qua các lượt

Chọn chế độ này khi subagent cần nhớ những lần trao đổi trước: một trợ lý nghiên cứu dựng dần bối cảnh qua nhiều lượt, hay một trợ lý code theo dõi những file nó đã sửa. Compile với `checkpointer=True`. Lịch sử và dữ liệu của subagent tích lũy qua các lần gọi trên cùng một thread; mỗi lần tiếp nối chỗ lần trước dừng lại.

Có hai lưu ý quan trọng khi dùng chế độ này:

Thứ nhất — **không gọi song song được.** Khi LLM có một subagent per-thread làm tool, nó có thể tự ý gọi tool đó nhiều lần cùng lúc (hỏi chuyên viên trái cây về táo và chuối đồng thời). Cả hai lần gọi ghi vào **cùng một namespace** nên đụng nhau, sinh xung đột checkpoint. Cách chặn mà tài liệu dùng là `ToolCallLimitMiddleware` giới hạn số lần gọi.\

Thứ hai — **nhiều subagent per-thread khác nhau phải có namespace riêng.** Nếu ta [gọi subgraph bên trong node](#2-hai-cách-nối-state-giữa-cha-và-subgraph), LangGraph cấp namespace theo thứ tự gọi (lần một, lần hai...). Nghĩa là đổi thứ tự gọi là đổi luôn ai nạp state của ai — trí nhớ của chuyên viên trái cây có thể nạp nhầm sang chuyên viên rau củ. Cách chữa: bọc mỗi subagent trong một `StateGraph` riêng với **tên node duy nhất**, để mỗi subgraph có một namespace cố định theo tên chứ không theo thứ tự. Còn subgraph [cắm thẳng làm node](#dùng-chung-key--cắm-thẳng-subgraph-vào-node) thì đã tự có namespace theo tên, không cần bọc thêm.

### 3.3 Stateless — chạy như hàm thường

Chọn khi ta muốn subagent chạy đúng như một lời gọi hàm, không tốn chi phí checkpoint. Compile với `checkpointer=False`. Đổi lại, subgraph **không dừng/tiếp được** và **không chạy bền**.

**!Note:** Không có checkpoint nghĩa là không phục hồi được. Nếu tiến trình chết giữa chừng, subgraph không cứu lại được — phải chạy lại từ đầu. Đây là cái giá của việc bỏ checkpoint, không phải một chi tiết phụ.

---

## 4. Bảng so sánh ba chế độ

Cùng một trục — điều khiển bằng `checkpointer` trên `.compile()` — nhưng năng lực ba chế độ lệch nhau ở năm điểm:

| Năng lực | Per-invocation (`None`) | Per-thread (`True`) | Stateless (`False`) |
|---|---|---|---|
| Interrupt (dừng chờ người duyệt) | ✅ | ✅ | ❌ |
| Nhớ qua nhiều lượt | ❌ | ✅ | ❌ |
| Gọi nhiều subgraph **khác nhau** trong một node | ✅ | ⚠️ dễ đụng namespace, có cách né | ✅ |
| Gọi **cùng một** subgraph nhiều lần trong một node | ✅ | ❌ | ✅ |
| Xem được state của subgraph | ⚠️ chỉ trong lần gọi hiện tại, lúc đang bị interrupt | ✅ | ❌ |

Đọc bảng này để thấy vì sao **per-invocation là mặc định**: nó giữ được interrupt và chạy bền, cho phép gọi song song, mà vẫn cô lập từng lần gọi. Chỉ khi thật sự cần trí nhớ liên lượt mới bước sang per-thread và chấp nhận ràng buộc không-song-song đi kèm.

---

## 5. Xem trạng thái bên trong subgraph

Khi đã bật persistence, ta soi được state của subgraph để gỡ lỗi và theo dõi, qua `get_state(config, subgraphs=True)`. Với per-invocation, nó trả về state của **lần gọi hiện tại** (chỉ có ý nghĩa khi đang bị interrupt, vì mỗi lần gọi khởi động lại). Với per-thread, nó trả về state **tích lũy** qua mọi lần gọi trên thread. Với stateless thì không có gì để xem — không checkpoint nào được lưu.

**!Note:** Chỉ soi được state khi LangGraph **nhận diện tĩnh** được subgraph — tức subgraph phải được cắm làm node hoặc gọi trực tiếp bên trong node. Nếu subgraph được gọi **bên trong một tool** (kiểu subagents), LangGraph không thấy nó qua lớp gián tiếp đó, nên không soi state được. Riêng interrupt thì vẫn nổi lên tới graph gốc bất kể lồng sâu bao nhiêu — hai chuyện này tách biệt, đừng nhầm "không xem được state" thành "không interrupt được".

---

## 6. Xem output chảy ra từ subgraph

Để theo dõi các lần chạy lồng nhau, tài liệu khuyên dùng **event streaming**: projection `stream.subgraphs` tự phát hiện từng lần chạy con và phơi ra `path`, `messages`, `values` của nó — khỏi phải tự tách chuỗi namespace bằng tay. Nếu cần sự kiện thô, ta lặp trực tiếp trên stream rồi lọc theo `event["method"]` và `event["params"]["namespace"]`.

Cơ chế streaming nói chung ở [03-01 streaming](../03-streaming/03-01-streaming.md); ở đây chỉ cần nhớ một điều: với subgraph, `stream.subgraphs` là đường ngắn nhất để nhìn thấy cái gì đang chạy ở tầng nào.

---

## Tham chiếu chéo

- [02-02 checkpointers](../02-persistence/02-02-checkpointers.md) — cơ chế checkpointer và thread nói chung; file này chỉ xét nó áp vào subgraph
- [03-01 streaming](../03-streaming/03-01-streaming.md) — event streaming và các projection; nền cho mục 6
- Trang tài liệu gốc: `https://docs.langchain.com/oss/python/langgraph/use-subgraphs`
- Graph API (khái niệm graph, node, edge, key `messages`): `https://docs.langchain.com/oss/python/langgraph/graph-api`