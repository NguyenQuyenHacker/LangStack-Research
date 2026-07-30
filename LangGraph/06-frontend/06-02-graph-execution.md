---
title: Graph execution trên UI
doc_source: https://docs.langchain.com/oss/python/langgraph/frontend/graph-execution
accessed: 2026-07-30
lc_version: unknown
status: draft
lab:
related:
  - ./06-01-frontend-overview.md
  - ./06-03-custom-stream-channels.md
  - ../03-streaming/03-01-streaming.md
---

# Graph execution trên UI

> Pattern render một pipeline nhiều bước thành từng card — mỗi node một card, có trạng thái riêng và nội dung stream theo thời gian thực.
> Đây là pattern nền của bộ frontend, cần nắm trước [custom-stream-channels](./06-03-custom-stream-channels.md). Cơ chế stream ở tầng dưới nằm ở [03-01-streaming](../03-streaming/03-01-streaming.md).

---

## 1. Tổng quan

Một agent chạy bốn năm bước — phân loại, tra cứu, phân tích, tổng hợp — mà chỉ trả về một cục message cuối thì người dùng ngồi nhìn màn hình đứng im, không biết nó đang ở bước nào. Pattern này lấy chính cấu trúc graph ra làm giao diện: mỗi node thành một card, card hiện node đang chạy hay xong, và chữ của node nào chảy vào card của node đó.

Khác một assistant response thông thường ở chỗ: thay vì coi cả lượt chạy là một câu trả lời duy nhất, ta phơi ra ngoài đúng những thứ LangGraph dùng bên trong — tên node, state key, trạng thái, metadata khi stream. Cấu trúc graph trở thành UX của sản phẩm.

---

## 2. Node tự được phát hiện, không hardcode

Cách ngây thơ là viết cứng một danh sách node trên frontend: "graph có classify, research, analyze, synthesize", rồi dựng bốn card theo danh sách đó. Cách này vỡ ngay khi backend thêm một node, đổi tên, hay đổi thứ tự — UI vẫn vẽ theo danh sách cũ, lệch với graph thật mà không báo lỗi.

`useStream` bỏ được cái hardcode đó. Khi graph chạy, nó **phát hiện từng node lúc node đó chạy** và gom vào `stream.subgraphs`. Lấy danh sách node đang có bằng một dòng: `[...stream.subgraphs.values()]`. Mỗi phần tử là một `SubgraphDiscoverySnapshot` — ảnh chụp một node tại thời điểm quan sát, mang hai thứ ta cần:

| Thuộc tính | Chứa gì | Dùng làm gì |
|---|---|---|
| `node.nodeName` | Tên node, ví dụ `classify` | Nhãn cho card header và progress bar |
| `node.status` | Trạng thái hiện tại của node | Quyết định badge, màu, mở/gập card |

Danh sách này chính là điểm nối: backend chủ động thêm/đổi/sắp xếp node, frontend quyết định mỗi output hiện ra thành gì — badge trạng thái, panel markdown, bảng, biểu đồ, trace view, hay card phê duyệt. Hai bên thỏa thuận qua tên node và state key, không dính chặt vào nhau.

---

## 3. Chữ của từng node — `useMessages(stream, node)`

Có danh sách node rồi, câu hỏi tiếp theo: chữ đang stream ra là của node nào? Nếu cứ đọc theo thứ tự message rồi đoán, thì graph chạy song song hai nhánh là loạn ngay — không biết mẩu chữ này thuộc nhánh nào.

`useMessages(stream, node)` giải quyết đúng chỗ đó: truyền vào một snapshot node, nó trả về đúng những message thuộc riêng node ấy, cả lúc đang stream lẫn khi đã xong. Card không phải đoán theo thứ tự, mỗi card tự cập nhật từ đúng luồng sự kiện của node mình. Nhờ vậy giao diện đỡ được các nhánh chạy song song mà không cần suy đoán.

Cơ chế đăng ký: selector đầu tiên được mount sẽ mở một subscription riêng cho namespace của node đó; khi card unmount thì subscription tự được thả ra. Ta không phải dọn tay.

**!Note:** Tên node **không** nhất thiết trùng state key nó ghi vào. Trong graph mẫu của tài liệu, node tên `do_research` ghi kết quả vào key `research`. Vì thế đọc chữ của node phải qua `useMessages(stream, node)` chứ đừng lấy `stream.values[node.nodeName]` — lấy theo tên node sẽ trật key và ra rỗng, mà không có lỗi nào bật lên.

---

## 4. Bốn trạng thái của một node

Mỗi node đã phát hiện đều mang trạng thái hiện tại ở `node.status`, nhận một trong bốn giá trị: `pending` (chưa tới lượt), `running` (đang chạy), `complete` (xong), `error` (lỗi). Đây là toàn bộ đầu vào để tô màu badge, chọn icon, và quyết định card nào tự mở ra.

Cách dùng điển hình theo tài liệu: card đang `running` thì tự bung nội dung, `complete` thì tự gập lại cho gọn; ở progress bar, node lỗi tô đỏ nhưng các node khác vẫn chạy tiếp và hoàn tất bình thường — lỗi một node không kéo sập cả pipeline.

---

## 5. Chữ đang chảy và giá trị cuối — dùng nguồn nào

Có hai nguồn dữ liệu, mỗi nguồn cho một mục đích, đừng lẫn:

| Nguồn | Cho ra gì | Dùng khi |
|---|---|---|
| `useMessages(stream, node)` | Message scoped theo node — cả lúc stream lẫn xong | Nội dung chảy trong từng card |
| `stream.values` | Toàn bộ state của graph, đọc theo state key thật | Cần đúng một field cuối, ví dụ `synthesis` |

Quy tắc thực dụng: trong card, hiện message scoped mới nhất; chỉ đụng tới `stream.values` khi thật sự cần lấy một field trạng thái của cả graph theo đúng key của nó. Giá trị đã hoàn tất vẫn luôn còn ở `stream.values` để lấy sau.

**!Note:** Chữ đang stream có thể là token dở hoặc markdown chưa đóng — ví dụ một dấu `**` mở mà chưa có dấu đóng. Bộ render markdown phải nuốt được cú pháp dang dở, không thì màn hình nhảy loạn định dạng mỗi lần có mẩu chữ mới về.

---

## 6. Pipeline động — node bị bỏ qua thì không hiện

Không phải graph nào cũng chạy đủ mọi node. Có pipeline rẽ nhánh theo input: câu hỏi dữ kiện đơn giản thì bỏ qua bước `Research`. `stream.subgraphs` chỉ chứa những node **đã thực sự chạy** trong thread hiện tại, nên node bị bỏ qua đơn giản là không xuất hiện — UI không đẻ ra card rỗng cho bước không chạy.

Hệ quả cho cách dựng progress bar: hoặc chỉ vẽ những node đã phát hiện, hoặc vẽ mờ các node dự kiến mà chưa có snapshot nào khớp. Đây là lựa chọn thiết kế, tài liệu nêu cả hai hướng, không chốt hướng nào.

Phần dựng cụ thể progress bar, card gập/mở, và danh sách card ghép lại là chi tiết render phía React — tài liệu có code mẫu nhưng đó là cách trình bày một khả năng, không phải khái niệm mới. Nắm được mục 2–6 là đủ để tự dựng theo framework mình dùng (React, Vue, Svelte, Angular đều cùng shape API).

---

## 7. Vài nguyên tắc khi làm thật

- **Vẽ card từ `stream.subgraphs`, đừng hardcode.** Bước rẽ nhánh hoặc bị bỏ qua chỉ hiện ra khi nó chạy — hardcode là sai lệch với graph thật.
- **Coi state key như một cam kết với frontend.** Chốt xem output nào của graph đủ ổn định để frontend render, rồi ghi rõ mấy key đó ngay cạnh định nghĩa graph.
- **Dùng message scoped cho card.** Nó chạy được cả khi node đang stream lẫn sau khi xong, và không buộc card dính vào tên state key.
- **Tự gập node đã xong.** Pipeline dài thì gập bớt card hoàn tất để người dùng nhìn vào bước đang chạy.
- **Xử lý lỗi theo từng node.** Node lỗi hiện lỗi ngay trong card của nó, không gập cả pipeline — node khác vẫn có thể chạy xong.

Hai gợi ý còn lại của tài liệu — hiện thời gian ước tính từ dữ liệu lịch sử, và thêm một thanh tiến độ tổng ("bước 2/4") ở đầu — là tùy chọn trải nghiệm, không bắt buộc.

---

## Tham chiếu chéo

- [06-01-frontend-overview](./06-01-frontend-overview.md) — khung chung: vì sao render graph khác một chat stream; bảng ánh xạ 6 khái niệm runtime sang UX
- [06-03-custom-stream-channels](./06-03-custom-stream-channels.md) — đẩy dữ liệu server tùy biến ngoài node output, đọc bằng `useExtension` / `useChannel`
- [03-01-streaming](../03-streaming/03-01-streaming.md) — cơ chế stream ở tầng dưới mà pattern này đứng trên
- API reference `useStream` (React): `https://reference.langchain.com/javascript/langchain-react/index/useStream`
- API reference `SubgraphDiscoverySnapshot`: `https://reference.langchain.com/javascript/langchain-react/SubgraphDiscoverySnapshot`