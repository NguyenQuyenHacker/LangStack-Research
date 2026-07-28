---
title: Frontend patterns
doc_source: https://docs.langchain.com/oss/python/langchain/frontend/
accessed: 2026-07-25
lc_version: unknown
status: draft
lab:
related:
  - ./frontend-overview.md
  - ./frontend-integrations.md
---
Chi tiết cách triển khai, code base đơn giản tham khảo tại [**Frontend**](https://docs.langchain.com/oss/python/langchain/frontend/)
# Frontend patterns

> 11 mẫu dựng sẵn cho giao diện agent. Mỗi mẫu là một cách lấy một trạng thái từ `useStream` rồi vẽ theo một nhu cầu cụ thể. File này chỉ trình bày định nghĩa và đặc điểm từng mẫu ở mức lý thuyết; cơ chế và code chi tiết nằm ở trang riêng của từng mẫu.

Kiến trúc chung (agent `create_agent` ở backend + hook `useStream` ở frontend) đã mô tả ở [frontend-overview.md](./frontend-overview.md), không nhắc lại ở đây.

Tài liệu gom 11 mẫu thành bốn nhóm theo mục đích.

> **Về các khối "Kết quả" trong file này.** Trang tài liệu gốc không in output tĩnh cho mẫu nào — nó nhúng một playground tương tác để người đọc tự bấm thử. Các khối hình dưới đây tôi tự dựng lại từ mô tả, để hình dung màn hình hiển thị ra sao. Cần đối chiếu khi chạy thử.

---

## 1. Nhóm — Hiển thị tin nhắn và kết quả

Bốn mẫu xử lý câu hỏi: khi agent trả về một khối nội dung, vẽ nó ra sao cho đúng và đẹp.

### 1.1 Markdown messages

**Khái niệm.** Model thường xuất ra chữ có định dạng markdown (tiêu đề, danh sách, khối code, bảng). Mẫu này chuyển chữ đó thành HTML có định dạng và tô màu code, cập nhật ngay khi chữ đang chảy về.

**Vai trò.** Nếu vẽ nguyên chữ thô, mọi cấu trúc mà model đã tạo ra bị mất, người dùng nhìn thấy một khối chữ phẳng. Mẫu này giữ lại cấu trúc đó.

**Đặc điểm.** Quy trình ba bước: nhận chữ từ `useStream` (dồn dần vào `msg.text`), chuyển thành HTML, rồi vẽ. Mỗi framework có một thư viện chuyển markdown quen thuộc riêng. Một điểm bắt buộc: khi vẽ HTML thô (Vue/Svelte/Angular) phải **che mã độc** bằng bộ lọc trước khi vẽ, vì chữ từ model có thể chứa mã kịch bản gây tấn công XSS; riêng React (`react-markdown`) sinh ra phần tử React trực tiếp nên không cần bước này.

**Kết quả :** cùng một chuỗi markdown thô, sau khi vẽ:

```
Chữ thô model gửi:            Sau khi vẽ ra màn hình:
## Hướng dẫn cài đặt          ┌ Tin nhắn AI ───────────────────────────┐
- Bước 1: tải gói             │ Hướng dẫn cài đặt      ← tiêu đề lớn, đậm │
- Bước 2: chạy lệnh           │                                          │
`pip install langchain`       │  • Bước 1: tải gói     ← danh sách chấm   │
**Xong.**                     │  • Bước 2: chạy lệnh                      │
                              │  ┌──────────────────────┐                │
                              │  │ pip install langchain│ ← khối code,    │
                              │  └──────────────────────┘   nền xám       │
                              │  Xong.                 ← chữ in đậm        │
                              └──────────────────────────────────────────┘
```

---

### 1.2 Structured output

**Khái niệm.** Thay vì trả về chữ, agent trả về một đối tượng có kiểu (typed) đã định trước; giao diện vẽ đối tượng đó thành component riêng thay vì chữ.

**Vai trò.** Có những câu trả lời không nên là văn xuôi — một hồ sơ, một bảng số liệu, một thẻ sản phẩm — mà nên là một khối giao diện có cấu trúc. Mẫu này cho phép agent phát ra đúng cấu trúc đó và giao diện vẽ thành UI tương ứng.

**Đặc điểm.** Điểm cần phân biệt với "Generative UI" (mục 4.3): ở đây kiểu dữ liệu do **lập trình viên định trước** rồi ánh xạ sang một component cố định; agent chỉ điền giá trị. Cơ chế chi tiết nằm ở trang riêng của mẫu này — chưa nằm trong phạm vi file này.

**Kết quả :** thay vì một dòng chữ, agent điền vào một thẻ cố định:

```
Không phải:  "Tên: Công ty ABC, MST: 0101234567, Vốn: 500 tỷ"

Mà là:       ┌ Hồ sơ doanh nghiệp ──────────┐
             │ Tên    : Công ty ABC          │
             │ MST     : 0101234567          │  ← thẻ do lập trình viên
             │ Vốn ĐL  : 500 tỷ              │    vẽ sẵn, agent chỉ điền số
             └───────────────────────────────┘
```

---

### 1.3 Reasoning tokens

**Khái niệm.** Với model có bước "suy nghĩ", mẫu này hiển thị phần suy nghĩ đó trong một khối gập/mở được, tách khỏi câu trả lời chính.

**Vai trò.** Người dùng nâng cao muốn thấy model lập luận thế nào, nhưng phần lập luận không nên chiếm chỗ của câu trả lời. Khối gập lại cho phép hiện khi cần, ẩn khi không.

**Đặc điểm.** Chỉ dùng được khi model có phát ra phần suy nghĩ; model thường không có phần này thì mẫu vô nghĩa. Đây là tính năng cho trường hợp đặc biệt.

**Kết quả :** một khối gập nằm trên câu trả lời chính:

```
Khi gập:   ▸ Đã suy nghĩ trong 4 giây        ← bấm để mở

Khi mở:    ▾ Đã suy nghĩ trong 4 giây
              │ Người dùng hỏi thời tiết Hà Nội.
              │ Cần gọi tool get_weather với city=Hanoi...
              └────────────────────────────────────────

Câu trả lời chính:   Hà Nội hôm nay 31°C, nhiều mây.   ← luôn hiện, nằm ngoài khối gập
```

---

### 1.4 Generative UI

Xem mục 4.3 — tài liệu xếp mẫu này trong nhóm hiển thị nhưng vì nó là mẫu nặng nhất, gộp mô tả ở cuối cho gọn.

---

## 2. Nhóm — Hiển thị hành động của agent

Hai mẫu về việc cho người dùng thấy agent đang làm gì, và chen vào khi cần.

### 2.1 Tool calling

**Khái niệm.** Khi agent gọi tool ngoài (tra thời tiết, tính toán, tìm web, truy vấn cơ sở dữ liệu), kết quả trả về là JSON thô. Mẫu này vẽ mỗi lần gọi tool thành một thẻ giao diện có kiểu, kèm trạng thái đang chạy và xử lý lỗi.

**Vai trò.** Đổ JSON thô ra màn hình thì người dùng không đọc được. Thẻ riêng cho từng tool (thẻ thời tiết khác thẻ tìm kiếm) biến kết quả kỹ thuật thành thứ nhìn hiểu ngay.

**Đặc điểm.** `useStream` gộp mọi lần gọi tool vào một mảng `toolCalls`; mỗi phần tử mang: `name` (tên tool), `input`/`args` (tham số agent truyền vào), `output` (kết quả, hoặc rỗng khi chưa xong), và `status` — một trong ba giá trị `running` / `finished` / `error`. Ba trạng thái này là xương sống: giao diện luôn phải xử lý cả ba, nếu không người dùng sẽ thấy thẻ trống. Agent có thể gọi nhiều tool cùng lúc, nên mảng có thể chứa nhiều phần tử `running` song song, mỗi cái xong độc lập.

**Kết quả :** cùng một thẻ, chuyển qua ba trạng thái theo `status`:

```
status = running          status = finished         status = error
┌────────────────────┐    ┌────────────────────┐    ┌────────────────────────┐
│ ⟳ Running          │ →  │ ☁ Hà Nội           │    │ ✕ Error in get_weather │
│   get_weather...   │    │ 31°C               │    │ Tool execution failed  │
└────────────────────┘    │ Nhiều mây          │    └────────────────────────┘
  (thẻ xám, có spinner)   └────────────────────┘      (thẻ viền đỏ)
                            (thẻ thời tiết riêng)
```

---

### 2.2 Human-in-the-Loop (dừng chờ người duyệt)

**Khái niệm.** Có hành động không nên chạy tự động (gửi email, xóa bản ghi, thực hiện giao dịch). Mẫu này cho agent **dừng lại**, trình hành động đang chờ cho người xem, và chỉ chạy tiếp sau khi người đó quyết.

**Vai trò.** Đặt một chốt kiểm soát của con người trước các thao tác không thể hoàn tác. Không có chốt này thì agent có thể tự làm những việc gây hậu quả thật.

**Đặc điểm.** Dựng trên hai thứ của LangGraph: **interrupt** (tín hiệu dừng — điểm agent trả quyền điều khiển về cho giao diện) và **checkpoint** (nơi lưu trạng thái). Vì trạng thái được lưu, chỗ dừng là **bền**: người dùng có thể tải lại trang, người duyệt có thể trả lời từ một component khác, agent vẫn chạy tiếp từ đúng điểm đã dừng chứ không chạy lại từ đầu.

Khi dừng, `useStream` phơi phần chờ ra ở `stream.interrupt`, chứa danh sách hành động đang chờ (`actionRequests`) và cấu hình cho phép quyết gì (`reviewConfigs`). Người dùng chọn một trong **bốn kiểu quyết định**:

| Kiểu | Ý nghĩa |
|---|---|
| approve | Đồng ý, hành động chạy nguyên trạng |
| reject | Từ chối kèm lý do; tool không chạy, agent nhận lý do rồi tự quyết bước tiếp |
| edit | Sửa tham số của hành động rồi mới đồng ý |
| respond | Người trả lời trực tiếp thay cho tool (dùng với tool kiểu "hỏi người dùng"); câu trả lời trở thành kết quả tool, tool không chạy |

Sau khi quyết, giao diện gọi `stream.submit(...)` với lệnh chạy tiếp; agent nhận quyết định và chạy tiếp. Có thể xâu nhiều chốt dừng trong cùng một lần chạy (ví dụ duyệt việc tìm kiếm, rồi duyệt tiếp việc gửi email), mỗi chốt xử lý độc lập.

Chi tiết hơn về cơ chế interrupt/checkpoint thuộc về trang Human-in-the-loop ở mục "Advanced usage", không phải trang frontend này.

**Kết quả :** một thẻ duyệt hiện ra, agent đứng im tới khi bấm nút:

```
┌ Cần bạn duyệt ────────────────────────────────┐
│ Agent muốn chạy:  send_email                   │
│   Tới     : khachhang@congty.vn                │  ← nội dung actionRequests
│   Tiêu đề : Báo giá đợt phát hành              │
│   ...                                          │
│                                                │
│  [ Đồng ý ]   [ Sửa ]   [ Từ chối ]            │  ← nút nào hiện do reviewConfigs quyết
└────────────────────────────────────────────────┘
        ⏸ agent dừng tại đây tới khi có một quyết định
```

---

## 3. Nhóm — Quản lý hội thoại

Hai mẫu về cách người dùng điều khiển dòng hội thoại.

### 3.1 Branching chat

**Khái niệm.** Cho người dùng sửa một tin nhắn đã gửi, tạo lại phản hồi, và đi lại giữa các **nhánh** hội thoại khác nhau.

**Vai trò.** Người dùng thường muốn thử lại một câu hỏi theo cách khác mà không mất hội thoại cũ. Mỗi lần sửa mở ra một nhánh mới; người dùng chuyển qua lại giữa các nhánh để so sánh.

**Đặc điểm.** Dựa trên lịch sử checkpoint mà `useStream` giữ. Sửa một tin nhắn tạo ra một nhánh rẽ từ điểm đó; các nhánh cùng tồn tại. Cơ chế điều hướng nhánh nằm ở trang riêng của mẫu.

**Kết quả :** một bộ đếm nhánh cạnh tin nhắn cho phép đi qua lại:

```
Bạn:   Phân tích tài chính công ty X        ‹ 2 / 3 ›   ← đang xem nhánh 2 trong 3
       [ Sửa ]  [ Tạo lại ]

  nhánh 1 → trả lời với câu hỏi gốc
  nhánh 2 → trả lời sau khi sửa câu hỏi   ← đang hiển thị
  nhánh 3 → trả lời khi bấm "Tạo lại" lần nữa
```

---

### 3.2 Message queues

**Khái niệm.** Cho phép người dùng xếp nhiều tin nhắn vào hàng đợi trong khi agent đang xử lý; agent giải quyết lần lượt từng cái.

**Vai trò.** Người dùng không phải chờ agent trả lời xong mới gõ tiếp. Họ gửi liên tiếp; hệ thống xếp hàng và agent xử lý tuần tự thay vì bỏ sót hoặc chồng chéo.

**Đặc điểm.** Trọng tâm là thứ tự: các tin trong hàng được xử lý lần lượt, không song song. Cơ chế quản lý hàng đợi thuộc trang riêng của mẫu.

**Kết quả :** các tin gửi thêm xếp hàng chờ trong khi tin đầu đang chạy:

```
Bạn: Tính lãi trái phiếu A          ▶ đang xử lý
Bạn: Rồi so với trái phiếu B        ⏳ đang chờ
Bạn: Xuất ra bảng                   ⏳ đang chờ
          └ agent làm xong cái trên mới sang cái dưới, theo đúng thứ tự
```

---

## 4. Nhóm — Streaming nâng cao

Hai mẫu về việc quản lý bản thân luồng dữ liệu, cộng với Generative UI.

### 4.1 Join & rejoin streams

**Khái niệm.** Cho phép ngắt kết nối khỏi một luồng agent đang chạy rồi nối lại mà không mất phần đã chạy.

**Vai trò.** Kết nối mạng có thể rớt, người dùng có thể chuyển tab hoặc thiết bị. Mẫu này bảo đảm nối lại được vào đúng luồng đang chạy, tiếp tục nhận phần còn lại, thay vì phải chạy lại từ đầu.

**Đặc điểm.** Đây là tính năng cho trường hợp đặc biệt — ứng dụng chat ngắn, chạy nhanh thì thường không cần. Cần khi agent chạy lâu và phiên có thể bị gián đoạn.

**Kết quả :** luồng chảy tiếp từ đúng chỗ dừng sau khi nối lại:

```
...agent đang trả lời: "Cơ cấu giao dịch gồm ba lớp: lớp một là..."
   ✕ mất mạng / đóng tab
   ⟳ Đang nối lại luồng...
   ✓ nối lại xong → "...tài sản bảo đảm, lớp hai là..."   ← tiếp tục, không chạy lại từ đầu
```

---

### 4.2 Time travel

**Khái niệm.** Cho phép xem lại, đi tới, và chạy tiếp từ bất kỳ **checkpoint** nào trong lịch sử hội thoại.

**Vai trò.** Khi cần gỡ lỗi hoặc thử một hướng khác, mẫu này cho quay về một điểm trong quá khứ của hội thoại và chạy lại từ đó, thay vì chỉ đọc lịch sử một cách bị động.

**Đặc điểm.** Dựa trực tiếp trên lịch sử checkpoint của `useStream`. Khác Branching chat ở góc nhìn: Branching nhắm vào người dùng cuối rẽ nhánh hội thoại; Time travel nhắm vào việc soi và chạy lại từ một điểm lịch sử bất kỳ. Cơ chế điều hướng checkpoint thuộc trang riêng.

**Kết quả :** một dòng thời gian các checkpoint, chọn một điểm để chạy lại từ đó:

```
Lịch sử checkpoint:
  ● 09:00  Câu hỏi ban đầu
  ● 09:01  Agent gọi tool
  ● 09:02  Agent trả lời            ← chọn điểm này
              [ Chạy tiếp từ đây ]  → mở một lần chạy mới bắt đầu từ 09:02
```

---

### 4.3 Generative UI

**Khái niệm.** Agent sinh ra **cả một giao diện** từ yêu cầu bằng ngôn ngữ tự nhiên. Đầu ra của model chính *là* UI: biểu mẫu, thẻ, bảng điều khiển — không phải chữ trong bong bóng chat.

**Vai trò.** Có những tác vụ mà giao diện cần thay đổi theo ngữ cảnh chứ không cố định. Mẫu này để agent tự dựng khối giao diện phù hợp thay vì lập trình viên vẽ trước mọi trường hợp.

**Đặc điểm.** Dùng thư viện `json-render`. Bốn thành phần của quy trình:
- **Catalog (danh mục)**: lập trình viên khai báo những component mà AI được phép dùng, kèm kiểu tham số. Đây là hàng rào — AI chỉ được dùng component đã khai báo với tham số đúng schema, nên đầu ra luôn nằm trong khuôn an toàn.
- **Prompt**: mô tả giao diện muốn có bằng ngôn ngữ tự nhiên.
- **Spec**: AI sinh ra một tài liệu JSON mô tả cây component (một khóa `root` và bản đồ `elements`, mỗi phần tử trỏ tới con của nó bằng ID).
- **Render an toàn**: bộ `Renderer` của `json-render` vẽ spec bằng chính component của bạn, và vẽ **dần** khi spec đang chảy về (bỏ qua lặng lẽ các phần tử chưa tới).

Điểm phân biệt cốt lõi với Structured output (mục 1.2): ở đó lập trình viên cố định một component cho một kiểu dữ liệu; ở đây AI **tự soạn** cây component từ một danh mục nhiều component. Đổi lại tự do lớn hơn là cần hàng rào catalog để giữ an toàn.

**Kết quả :** từ một câu yêu cầu, AI dựng ra cả biểu mẫu:

```
Yêu cầu (ngôn ngữ tự nhiên):  "Tạo form đăng nhập"
        │
        ▼  AI sinh spec JSON (Card › Stack › các ô nhập › nút)
        ▼  Renderer vẽ ra:
┌ Login ─────────────────────┐
│  Email                      │
│  [_______________________]  │
│  Password                   │  ← AI tự soạn cây component từ catalog
│  [_______________________]  │
│  [        Sign In        ]  │  ← nút full-width, kiểu primary
└─────────────────────────────┘
     (khung dựng dần từng component khi spec đang chảy về)
```

---

## 5. Bảng tổng hợp — 11 mẫu và trạng thái nó dùng

| Nhóm | Mẫu | Lấy trạng thái nào | Dùng khi |
|---|---|---|---|
| Hiển thị nội dung | Markdown messages | messages (`msg.text`) | Model trả chữ có định dạng |
| Hiển thị nội dung | Structured output | phản hồi có kiểu | Câu trả lời nên là UI cố định, không phải chữ |
| Hiển thị nội dung | Reasoning tokens | phần suy nghĩ | Model có bước suy nghĩ cần khoe |
| Hành động agent | Tool calling | `toolCalls` | Vẽ tool đang gọi thành thẻ |
| Hành động agent | Human-in-the-Loop | `stream.interrupt` | Chốt duyệt trước thao tác nguy hiểm |
| Quản lý hội thoại | Branching chat | history/checkpoint | Người dùng sửa và rẽ nhánh |
| Quản lý hội thoại | Message queues | hàng đợi tin nhắn | Gửi liên tiếp, xử lý tuần tự |
| Streaming nâng cao | Join & rejoin | luồng đang chạy | Phiên dài, có thể bị ngắt |
| Streaming nâng cao | Time travel | history/checkpoint | Soi và chạy lại từ điểm quá khứ |
| Streaming nâng cao | Generative UI | spec do AI sinh | AI tự dựng cả giao diện |

Ba mẫu nên xem là trường hợp đặc biệt, bỏ qua được nếu ứng dụng không cần: Reasoning tokens, Join & rejoin, Time travel.

---

## Tham chiếu chéo

- [frontend-overview.md](./frontend-overview.md) — kiến trúc chung và danh sách trạng thái của `useStream`
- [frontend-integrations.md](./frontend-integrations.md) — cắm các mẫu này vào thư viện giao diện bên thứ ba
- Các trang chi tiết của từng mẫu: `https://docs.langchain.com/oss/python/langchain/frontend/<tên-mẫu>` (ví dụ `.../tool-calling`, `.../human-in-the-loop`, `.../generative-ui`)