---
title: Custom stream channel
doc_source: https://docs.langchain.com/oss/python/langgraph/frontend/custom-stream-channels
accessed: 2026-07-30
lc_version: unknown
status: draft
lab:
related:
  - ./06-01-frontend-overview.md
  - ./06-02-graph-execution.md
  - ../03-streaming/03-02-event-streaming.md
---

# Custom stream channel

> Mở một đường ống riêng có tên để server đẩy dữ liệu tùy biến xuống frontend, đọc bằng `useExtension` hoặc `useChannel`.
> Đứng trên cơ chế event streaming ở [03-02-event-streaming](../03-streaming/03-02-event-streaming.md); phần chọn namespace dùng lại từ [06-02-graph-execution](./06-02-graph-execution.md).

---

## 1. Tổng quan

Một agent không chỉ stream message và tool call. Có những dữ liệu server muốn hiện lên UI theo thời gian thực mà không nhét vừa vào ba loại có sẵn (message, tool call, graph state): số lượng PII đã che, phần trăm tiến độ của một tool chạy lâu, số token đã tiêu. Custom channel là một đường ống riêng, có tên, dành đúng cho loại dữ liệu đó.

Khác ba loại quen thuộc ở chỗ: đây là kênh phụ do ta tự định nghĩa, chạy song song bên cạnh luồng chính chứ không làm bẩn nội dung hội thoại. Server đẩy payload có cấu trúc tùy ý lên kênh, frontend đọc kênh đó thành state phản ứng (dữ liệu đổi thì UI vẽ lại).

Ví dụ xuyên suốt của tài liệu: một agent hỗ trợ khách hàng, phía server có một bộ biến đổi che PII (email, số điện thoại, SSN, số thẻ, IP) khỏi mọi event trước khi tới trình duyệt, đồng thời đẩy số đếm che được lên kênh tên `redaction-stats`. Panel bên cạnh hiện các con số đó cập nhật liên tục.

---

## 2. Hai đầu của một channel

Một custom channel có hai đầu, hiểu được hai đầu này là hiểu cả trang.

**Đầu server — bộ biến đổi luồng.** Một `StreamTransformer` mở một `StreamChannel` có tên rồi push payload lên đó. Kênh được đăng ký trong hàm `init()` — hàm này trả về một map từ khóa tới channel. Điểm cốt lõi nằm ở hàm `process`: nó chạy **cho mỗi protocol event** đi qua. Trong `process`, transformer làm hai việc cùng lúc — sửa chính event tại chỗ (ở ví dụ là bôi PII khỏi phần dữ liệu `messages`, `tools`, `values`), và khi có gì đáng báo thì push một payload lên kênh phụ. Giá trị trả về của `process` quyết định event (đã sửa) có được giữ lại trong luồng đi tiếp xuống client hay không; ví dụ trả về `True` để giữ.

Payload đẩy lên là gì thì tùy transformer — không có khuôn cứng. Trong ví dụ, mỗi lần che được thêm PII, nó push một object gồm mốc thời gian, phần tăng thêm (`delta`), tổng số đếm theo từng loại (`counts`), và tổng cộng (`total`). Frontend cứ theo đúng hình dạng đó mà đọc.

**Gắn transformer vào agent.** Khi dựng agent bằng `create_agent`, truyền transformer qua tham số `transformers`. Từ đó mọi event của agent đều đi qua `process` trước khi ra client.

**Đầu client — selector.** Frontend subscribe vào kênh khớp tên dạng `custom:<tên>` và nhận payload thành state phản ứng. Có hai selector, đi kèm bộ SDK v1 (`@langchain/react`, `vue`, `svelte`, `angular`): `useExtension` lấy payload mới nhất, `useChannel` lấy buffer event thô. Hai mục dưới đây bàn từng cái.

---

## 3. Lấy payload mới nhất — `useExtension`

Khi UI chỉ cần **giá trị hiện tại** — một bộ đếm sống, phần trăm tiến độ, một badge trạng thái — thì đây là lựa chọn gọn nhất. `useExtension` subscribe vào kênh và trả về đúng payload gần nhất mà transformer đã push, đã bóc vỏ và gắn kiểu sẵn. Không phải tự parse gì.

Kiểu trả về theo mô hình phản ứng của từng framework: React và Svelte trả giá trị trần, Vue trả một `Ref` (đọc qua `.value`), Angular trả một signal (gọi `latest()`), và Angular dùng `injectExtension` thay cho `useExtension`. Trước khi payload đầu tiên về, giá trị là `undefined` — UI phải chịu được trạng thái rỗng ban đầu.

**!Note:** `useExtension` nhận **tên trần** của kênh (`"redaction-stats"`), **không** kèm tiền tố `custom:`. Đây là chỗ khác với `useChannel` (mục 4) và là lỗi im lặng điển hình: truyền nhầm dạng tên thì selector không khớp kênh nào, trả `undefined` mãi mà không báo lỗi.

Tham số thứ ba `target` (tùy chọn) giới hạn subscription vào một namespace, đúng cơ chế `useMessages(stream, node)` gắn message vào một node đã phát hiện. Chi tiết cách chọn namespace nằm ở [06-02 mục 3](./06-02-graph-execution.md#3-chữ-của-từng-node--usemessagesstream-node).

---

## 4. Lấy buffer event thô — `useChannel`

`useChannel` là cửa lấy dữ liệu thô, dùng khi cần **lịch sử** thay vì chỉ giá trị mới nhất — một event log, một audit trail — hoặc khi cần một kênh mà không selector cao cấp nào phủ. Nó subscribe một hoặc nhiều kênh và trả về một buffer có giới hạn gồm các protocol event nằm dưới, chứ không phải một payload đã bóc vỏ.

Đổi lại sự linh hoạt là phải tự làm nhiều hơn. Mỗi phần tử là một event thô, payload thật nằm ở `event.params.data` — ta phải tự bóc ra. Angular dùng `injectChannel`.

Buffer điều khiển bằng tham số tùy chọn:

| Tùy chọn | Mặc định | Tác dụng |
|---|---|---|
| `bufferSize` | `"default"` | Số event tối đa giữ trong buffer; vượt trần thì event cũ bị đẩy ra |
| `replay` | `true` | Khi selector mount, phát lại các event đã có sẵn trên kênh, thay vì chỉ nhận event mới từ lúc mount |

**!Note:** `useChannel` nhận **id đầy đủ** của kênh, có tiền tố — dạng mảng `["custom:redaction-stats"]`. Ngược hẳn với `useExtension` ở mục 3 (tên trần). Nhớ nhầm chiều là kênh không khớp.

**!Note:** Với các nhu cầu thông thường, tài liệu khuyên ưu tiên selector cao cấp (`useExtension`, `useMessages`, `useToolCalls`, `useValues`) hơn `useChannel`. Chúng trả giá trị đã bóc vỏ, gắn kiểu, và chỉ theo dõi đúng thứ ta render. Chỉ xuống `useChannel` khi thật sự cần luồng event thô.

---

## 5. Chọn `useExtension` hay `useChannel`

Cả hai đọc cùng một kênh, khác nhau ở cái chúng trả về:

| | `useExtension` | `useChannel` |
|---|---|---|
| Trả về | Payload mới nhất (`T \| undefined`) | Buffer có giới hạn của event thô (`Event[]`) |
| Hình dạng | Đã bóc vỏ, gắn kiểu | Event thô; tự bóc `event.params.data` |
| Subscribe bằng | Tên trần (`"redaction-stats"`) | Id đầy đủ (`["custom:redaction-stats"]`) |
| Dùng khi | Cần giá trị hiện tại | Cần lịch sử, log, hoặc nhiều kênh |
| Tùy chọn | — | `bufferSize`, `replay` |

Chọn `useExtension` khi màn chỉ hiển thị con số/trạng thái đang là gì lúc này. Chọn `useChannel` khi cần dựng lại dòng lịch sử, hoặc gộp nhiều kênh vào một chỗ.

Không nhất thiết chọn một. Một cách làm phổ biến là dùng cả hai trên cùng một kênh: `useExtension` nuôi phần tóm tắt sống (tổng số hiện tại), còn `useChannel` đứng sau một event log cuộn được, ghi mọi lần cập nhật trong cả thread.

---

## 6. Dùng vào việc gì

Custom channel hợp với mọi tín hiệu phía server không nhét gọn được vào message, tool call, hay graph state:

- **Số liệu tuân thủ, che dữ liệu** — đếm PII đã bôi, nội dung bị chặn, số lần dính policy, như ví dụ redaction ở trên.
- **Báo tiến độ** — phần trăm hoàn thành hoặc nhãn bước, do một tool chạy lâu phát ra.
- **Chỉ số sống** — token đã dùng, độ trễ, chi phí cộng dồn trong một lượt chạy.
- **Nguồn và trích dẫn** — tài liệu truy hồi được, đẩy sang panel bên khi agent dẫn nguồn cho câu trả lời.
- **Sự kiện nghiệp vụ** — bất kỳ cập nhật có cấu trúc nào backend muốn hiện ra mà không đụng vào bản ghi hội thoại.

---

## Tham chiếu chéo

- [06-01-frontend-overview](./06-01-frontend-overview.md) — khung chung của bộ frontend; custom channel là một trong hai pattern con
- [06-02-graph-execution](./06-02-graph-execution.md) — cơ chế chọn namespace mà tham số `target` ở đây dùng lại
- [03-02-event-streaming](../03-streaming/03-02-event-streaming.md) — protocol event ở tầng dưới mà transformer can thiệp vào
- API reference `useExtension`: `https://reference.langchain.com/javascript/langchain-react/useExtension`
- API reference `useChannel`: `https://reference.langchain.com/javascript/langchain-react/useChannel`
- API reference `StreamTransformer`: `https://reference.langchain.com/python/langgraph/stream/_types/StreamTransformer`