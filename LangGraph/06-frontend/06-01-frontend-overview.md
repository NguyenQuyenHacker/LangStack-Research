---
title: Frontend — tổng quan
doc_source: https://docs.langchain.com/oss/python/langgraph/frontend/overview
accessed: 2026-07-30
lc_version: unknown
status: draft
lab:
related:
  - ./06-02-graph-execution.md
  - ./06-03-custom-stream-channels.md
---

# Frontend LangGraph — tổng quan

> Bộ pattern để render một LangGraph agent ra giao diện web, cập nhật theo thời gian thực. Dùng frontend SDK bản v1.
> Hai pattern cụ thể tách sang [graph-execution](./06-02-graph-execution.md) và [custom-stream-channels](./06-03-custom-stream-channels.md); trang này chỉ dựng khung chung.

---

## 1. Tổng quan

Phần này giải quyết câu hỏi:

- làm sao dựng một giao diện web hiện được một LangGraph pipeline đang chạy tới đâu
- khác gì so với cách stream một cuộc chat thông thường

Khác biệt cốt lõi nằm ở chính cái graph. Một chat stream đổ toàn bộ kết quả vào **một** message của assistant — chữ chảy ra, xong thì có một cục trả lời, còn bên trong hệ thống làm những bước gì thì người dùng không thấy. 

Ngược lại, LangGraph thì cấu trúc thực thi được phơi ra ngoài. Node, state key, checkpoint, interrupt, subgraph, message đang stream — tất cả đều là khái niệm runtime **nhìn thấy được**. Vì nhìn thấy được nên UI có thể bám theo đúng cấu trúc graph, dựng ra giao diện giải thích hệ thống đang làm gì thay vì giấu mọi thứ sau một câu trả lời.

LangGraph viết ở backend bằng Python (`StateGraph`); frontend SDK là JS/TS, có bản cho React, Vue, Svelte, Angular. Hai nửa nối nhau qua cùng một stream API.

---

## 2. Kiến trúc — graph một đầu, stream handle một đầu

Muốn UI hiện từng bước thì UI phải biết được graph có những bước nào và mỗi bước đẻ ra dữ liệu gì. Kiến trúc ở đây tồn tại để nối đúng hai chuyện đó lại.

<div align="center">
  <img src="../assets/images/image copy 7.png" width="600">
</div>


**Đầu backend — graph.** Một graph gồm các node có tên, nối với nhau bằng edge. Mỗi node chạy một bước và ghi kết quả vào một state key riêng của nó. Ví dụ trong tài liệu là một pipeline bốn bước: `classify` → `do_research` → `analyze` → `synthesize`, và state có bốn key tương ứng `classification`, `research`, `analysis`, `synthesis`. Điểm cần nắm không phải mấy cái tên, mà là quy tắc: **một bước, một state key**. Chính quy tắc này khiến từng mảnh output có địa chỉ rõ ràng để frontend gắn vào một chỗ trên màn hình.

**Đầu frontend — stream handle.** Frontend nối vào graph qua một "handle" cho phép truy cập theo kiểu reactive (dữ liệu đổi thì UI tự vẽ lại). React lấy handle này qua `useStream`; Angular qua `injectStream` — cùng một shape API. Trên handle có ba thứ đáng nhớ:


---

## 3. Sự khác nhau với chat stream thông thường

Custom graph thường không phải để chat, mà để chạy workflow sản phẩm: pipeline nghiên cứu, luồng phê duyệt, pipeline dữ liệu, làm giàu dữ liệu, review code, lập kế hoạch, phân tích nhiều bước. Với mấy thứ này, một cục message trả về là quá nghèo — người dùng cần thấy tiến trình. Frontend SDK cho render bằng chính các tín hiệu gốc của graph, mỗi khái niệm runtime ánh xạ sang một kiểu trải nghiệm:

| Khái niệm runtime | Thể hiện trên UI |
|---|---|
| **Node có tên** | Mỗi node thành một card, một bước trên timeline, hoặc một badge trạng thái |
| **State key** | Mỗi key có vùng UI riêng cho output có kiểu — phân loại, nguồn, phân tích, tổng hợp cuối |
| **Metadata khi stream** | Điều các mẩu message dở dang về đúng node đã sinh ra chúng |
| **Checkpoint** | Soi lại hoặc chạy tiếp từ một state trước đó — phục vụ debug và truy vết |
| **Interrupt** | Dừng một node để người nhập liệu / duyệt / sửa, rồi chạy tiếp |
| **Subgraph** | Chỉ mở execution lồng nhau ra khi người dùng cần xem sâu hơn |

Cái được của việc SDK phơi mấy khái niệm này ra trực tiếp: ta mở rộng từ một panel chat đơn giản lên tới một trình debug workflow đầy đủ mà **không phải đổi backend protocol**. Backend giữ nguyên, chỉ frontend đọc thêm tín hiệu — đây là lý do một graph viết một lần dùng được cho nhiều mức độ giao diện.
---

## 4. Hai pattern cụ thể

Trang tổng quan dừng ở mức khung. Cơ chế chi tiết nằm ở hai file riêng, ở đây chỉ nêu để biết khi nào cần đọc cái nào:

- **Graph execution** — dựng một pipeline nhiều bước, mỗi node hiện trạng thái riêng và nội dung đang stream. Đây là pattern nền, cần trước. Chi tiết: [06-02-graph-execution](./06-02-graph-execution.md).
- **Custom stream channels** — khi cần đẩy dữ liệu tùy biến từ phía server xuống frontend (ngoài node output và message thông thường), đọc ở client bằng `useExtension` và `useChannel`. Chi tiết: [06-03-custom-stream-channels](./06-03-custom-stream-channels.md).

---

## 5. Quan hệ với frontend patterns của LangChain

Các pattern frontend của LangChain — hiện message dạng markdown, tool calling, human-in-the-loop, resumable stream, time travel — chạy được với **bất kỳ** graph LangGraph nào. Stream API cho cùng một data model lõi dù backend dùng `createAgent`, `createDeepAgent`, hay một `StateGraph` tự viết.

Ý thực dụng rút ra: mấy pattern frontend đó học một lần là dùng lại được trên cả agent dựng sẵn lẫn graph tự viết — không phải học lại theo từng kiểu backend.

---

## Tham chiếu chéo

- [06-02-graph-execution](./06-02-graph-execution.md) — pattern nền: render pipeline nhiều bước, trạng thái theo từng node
- [06-03-custom-stream-channels](./06-03-custom-stream-channels.md) — đẩy dữ liệu server tùy biến xuống frontend qua `useExtension` / `useChannel`
- LangChain frontend patterns (overview): `https://docs.langchain.com/oss/python/langchain/frontend/overview`
- API reference `useStream` (React): `https://reference.langchain.com/javascript/langchain-react/index/useStream`
- API reference `injectStream` (Angular): `https://reference.langchain.com/javascript/langchain-angular/injectStream`