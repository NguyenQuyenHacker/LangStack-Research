---
name: research-note-vi
description: Format chuẩn để viết note research kỹ thuật bằng tiếng Việt từ tài liệu chính thức (docs của thư viện, framework, API, chuẩn kỹ thuật). Bắt buộc dùng skill này bất cứ khi nào người dùng nói "làm research về X", "đọc doc này viết note", "tóm tắt trang doc", "so sánh hai API", "viết tài liệu nghiên cứu", "ghi chú kỹ thuật", "hoàn thiện file research", hoặc dán một hoặc nhiều URL tài liệu kỹ thuật kèm yêu cầu tổng hợp. Cũng kích hoạt khi người dùng đang bổ sung, viết lại, hoặc chỉnh sửa một file note research đã có — kể cả khi họ chỉ nói "viết lại phần X" hay "giải thích kỹ hơn". Skill quy định cấu trúc file, khối giải thích khái niệm, quy tắc phân biệt dữ kiện với suy luận, cách gắn nhãn output dựng lại, và bộ từ vựng tiếng Việt dùng thống nhất.
---
 
# Research Note — Format chuẩn
 
Mục tiêu: người đọc chưa có nền tảng đọc xong vẫn hiểu, như vừa được một người đi trước ngồi cà phê giảng lại — **không phải đọc một bản dịch tài liệu**.
 
Điều này định hình cả skill: file research là thứ mình **hiểu rồi kể lại**, không phải thứ mình **dịch lại theo bố cục trang gốc**. Đọc tài liệu để nắm dữ kiện, nhưng sắp xếp và diễn giải theo mạch của người giảng, không theo thứ tự đoạn của nguồn.
 
Bốn nguyên tắc chi phối toàn bộ skill này:
 
1. **Tư duy rồi mới viết.** Đọc hết, hiểu vấn đề, dựng mạch giảng của riêng mình — rồi mới viết. Không dịch máy móc từng câu bám theo nguồn.
2. **Giải thích mục đích trước cú pháp.** Không bao giờ giới thiệu một khái niệm mà chưa nói nó lo nỗi đau gì. Khái niệm khó thì kèm một ví von đời thường trước khi vào code.
3. **Phân biệt rạch ròi dữ kiện với suy luận.** Cái gì tài liệu nêu, cái gì mình suy ra — không được lẫn. Đây chính là thứ cho phép mình tự do diễn giải mà vẫn không bịa.
4. **Không bịa dữ kiện.** Tự do cách trình bày, nhưng dữ kiện — tên hàm, tham số, hành vi — phải có trong nguồn. Tài liệu không có thì ghi là không có, không lấp bằng phỏng đoán trình bày như sự thật.
---
 
## Tự do cách kể, bám chặt dữ kiện
 
Đây là ranh giới quan trọng nhất, và cũng là chỗ dễ hiểu sai nhất.
 
**Tự do phần nào.** Cách sắp xếp, thứ tự trình bày, độ sâu, ví von, chỗ nào giảng kỹ chỗ nào lướt — tất cả theo mạch giảng của mình, không theo bố cục trang gốc. Một khái niệm tài liệu viết hai dòng, nếu người đọc cần ba đoạn mới thông thì viết ba đoạn. Giảng cho hiểu là việc của mình, không phải việc của trang tài liệu.
 
**Chặt phần nào.** Mọi *dữ kiện* — tên hàm, tên tham số, giá trị mặc định, thứ tự thực thi, hành vi khi lỗi — phải truy được về nguồn. Không thêm tham số không được nhắc, không thêm khối code chưa từng xuất hiện, không dựng ra một hành vi rồi kể như thật. Diễn giải thoải mái, nhưng phải đứng trên dữ kiện có thật.
 
Hai thứ này không mâu thuẫn. Cái cho phép vừa tự do vừa không bịa chính là **nhãn dữ kiện/suy luận** (mục dưới): hiểu biết chung và suy luận của mình được đưa vào, nhưng gắn nhãn rõ, không trộn với cái tài liệu khẳng định.
 
**Về tình huống "Áp dụng thực tế".** Tài liệu hiếm khi cho tình huống có thật nên phần này được tự nghĩ — nhưng chỉ minh họa đúng tính năng đang mô tả, không kéo theo tính năng chưa được nói tới.
 
### Ranh giới với các file khác trong bộ
 
Tự do độ sâu không có nghĩa là giẫm lên file khác. Nếu một chủ đề đã có file riêng phụ trách, chỗ này chỉ nêu tên rồi trỏ sang, không giảng lại toàn bộ cơ chế. Đây là kỷ luật bộ file, không phải kỷ luật bám nguồn: viết đầy đủ ở hai nơi thì hai file lệch nhau ngay lần tài liệu đổi đầu tiên. Giảng sâu ở file chủ, để stub + link ở file còn lại.
 
Dấu hiệu đã đi quá xa — theo nghĩa **bịa**, không phải nghĩa **dài**:
 
- Xuất hiện tên hàm hoặc tham số không có trên trang tài liệu
- Một hành vi được kể như chắc chắn nhưng tài liệu không hề khẳng định
- Giảng lại chi tiết một cơ chế mà file khác trong bộ mới là chỗ phụ trách
---
 
## Quy trình
 
### Bước 1 — Đọc nguồn trước khi viết
 
Đọc **toàn bộ** trang tài liệu. Nếu người dùng đưa nhiều URL, đọc hết trước khi viết dòng nào.
 
Vừa đọc vừa ghi lại ba nhóm riêng:
 
| Nhóm | Nội dung |
|---|---|
| Dữ kiện | Tài liệu nêu rõ ràng |
| Khoảng trống | Tài liệu không đề cập, nhưng người đọc sẽ cần |
| Suy luận | Mình suy ra từ dữ kiện, tài liệu không khẳng định |
 
Ba nhóm này quyết định cách viết ở bước sau. Nhóm 2 và 3 **phải** được gắn nhãn trong file cuối.
 
Đọc xong, gấp tài liệu lại và tự hỏi: nếu phải giảng cái này cho một người chưa biết, mình mở đầu từ đâu, dẫn tới đâu, chỗ nào là cái bẫy? Câu trả lời đó là mạch của file — và nó thường không trùng thứ tự đoạn của trang gốc.
 
### Bước 2 — Xác định người đọc
 
Mặc định: **người biết lập trình cơ bản, đã nắm khái niệm agent và tool ở mức căn bản, nhưng chưa rõ phần trung cấp và chuyên sâu.**
 
Nghĩa là được phép dùng thẳng những từ như *agent*, *tool*, *model*, *prompt* mà không cần định nghĩa lại. Nhưng mọi thứ sâu hơn — cơ chế bên trong, khái niệm riêng của thư viện, cách dữ liệu di chuyển — đều phải giải thích ở lần xuất hiện đầu.
 
Ranh giới này quan trọng: giải thích lại thứ họ đã biết thì loãng, bỏ qua thứ họ chưa biết thì họ tắc.
 
### Bước 3 — Viết theo mạch giảng, không theo khuôn
 
`references/template.md` cho một bộ khung mặc định — dùng làm điểm xuất phát, không phải cái khuôn phải đổ đầy. Mục nào không phục vụ mạch giảng thì bỏ, thứ tự nào hợp lý hơn thì đổi. `references/tu-vung.md` cho bộ từ và quy tắc ví von dùng thống nhất.
 
### Bước 4 — Tự soát trước khi giao
 
Chạy hết checklist ở cuối file này.
 
---
 
## Cấu trúc file
 
```
frontmatter
tiêu đề + một câu định vị
1. Tổng quan
2..n. Các khái niệm chính
n+1. Bảng so sánh           (nếu file so sánh hai thứ)
n+2. Nên chọn cái nào       (kết luận thực dụng)
Tham chiếu chéo
```
 
### Frontmatter
 
```yaml
---
title: <tên trang doc>
doc_source: <URL đầy đủ>
accessed: <YYYY-MM-DD>
version: <phiên bản thư viện, hoặc "unknown">
status: draft | reviewed | verified
lab:                              # điền khi đã chạy thử thực tế
related:
  - ./<file-liên-quan>.md
---
```
 
`status` lên `reviewed` khi đã đọc soát lại, lên `verified` khi đã chạy thử thực tế và điền `lab`.
 
### Mục 1 — Tổng quan
 
Trả lời đúng một câu hỏi: **thứ này là gì, và khác thứ quen thuộc ở chỗ nào.**
 
Kèm một đoạn code ngắn nhất có thể chạy được, và kết quả nó in ra.
 
---
 
## Khuôn giải thích một khái niệm
 
Đây là phần cốt lõi. Nhưng "khuôn" ở đây là **thứ tự ý cần đưa**, không phải một bộ nhãn in đậm phải dán vào mọi mục. Đọc lên phải giống một người đang giảng, không giống một biểu mẫu điền sẵn.
 
Thứ tự ý — đi từ nỗi đau tới cách làm:
 
1. **Nó lo nỗi đau gì.** Trước cả định nghĩa. Thiếu chỗ này thì người đọc thuộc cú pháp mà không biết khi nào dùng. Đây là mở đầu tự nhiên của người giảng: "cái này sinh ra để lo chuyện...".
2. **Ví von đời thường** (nếu khái niệm trừu tượng). Một hình ảnh dễ hình dung — luồng nước, cửa hàng, giao dịch ngân hàng — đặt *trước* khi vào cú pháp. Quy tắc ví von ở `tu-vung.md`: phải từ đời sống, không mượn một khái niệm kỹ thuật khác, mỗi ví von chỉ dùng một lần.
3. **Định nghĩa gọn.** Một đến hai câu, sau khi người đọc đã thấy nó để làm gì.
4. **Tình huống thật.** Có số liệu, có người dùng. Không viết "giả sử bạn cần xử lý dữ liệu" — viết "tool tra 500 mã doanh nghiệp, chạy 40 giây, người dùng nhìn màn hình đứng im".
5. **Code tối thiểu**, cắt hết import và phần khung.
6. **Kết quả** in ra (thật hoặc dựng lại — xem quy tắc nhãn bên dưới).
7. **!Note** chỗ dễ sai, ưu tiên lỗi im lặng — code chạy nhưng sai.
**Viết thành văn xuôi mạch lạc, không nhất thiết dán bảy nhãn in đậm.** Một người anh giảng qua cà phê không nói "Vai trò:..." rồi "Triển khai:..." — họ dẫn từ ý này sang ý kia. Chỉ tách nhãn in đậm khi mục dày, nhiều tầng, cần cho người đọc quét mắt tìm nhanh. Mục ngắn thì để văn xuôi chảy liền.
 
Bắt buộc tối thiểu: **ý số 1 (nỗi đau) và ý số 3 (định nghĩa) luôn phải có.** Bỏ ý số 1 là rơi ngược về dịch tài liệu.
 
Nhãn cảnh báo thống nhất là `**!Note:**` — không dùng "Bẫy", "Lưu ý", "Chú ý", "Cảnh báo". Một nhãn duy nhất để người đọc quét mắt tìm được ngay.
 
Nếu file đọc trong Obsidian, có thể dùng dạng khối thay cho nhãn in đậm để nó hiện thành hộp màu:
 
```markdown
> [!note]
> Reasoning phải được bật ở cấu hình model. Quên bật thì code chạy trơn tru,
> không lỗi, không cảnh báo — nhánh này chỉ đơn giản luôn rỗng.
```
 
Chọn một trong hai dạng và dùng nhất quán trong cả file.
 
### Tên mục — đặt theo nội dung, không đặt theo khuôn
 
Sáu nhãn trên dùng cho **nhãn in đậm bên trong mục**, không dùng làm tên mục.
 
Tên mục phải nói được nội dung cụ thể:
 
| Đừng đặt | Đặt |
|---|---|
| "Là gì", "Giới thiệu" | "Tổng quan" |
| "Tình huống 1" | "Hiện phần suy nghĩ của model" |
| "Use cases" | "Cách lấy từng loại dữ liệu" |
| "Khái niệm cơ bản" | "Nhánh dữ liệu — cách thư viện chia luồng" |
 
### Nếu khái niệm chỉ dành cho trường hợp đặc biệt
 
Nói thẳng ở cuối mục:
 
> Nếu ứng dụng chỉ cần X thì **bỏ qua mục này hoàn toàn**. Đây là tính năng cho trường hợp đặc biệt, không phải kiến thức bắt buộc.
 
Người đọc cần biết cái gì được phép bỏ qua. Không nói thì họ tưởng mọi mục đều phải hiểu.
 
---
 
## Giọng văn — người đi trước giảng lại
 
Viết như một đồng nghiệp từng trải đang ngồi cà phê kể lại cho đàn em, không như tài liệu tham khảo đọc đều đều.
 
- **Đối thoại, có nhịp.** Câu dài xen câu ngắn. Một câu chốt gọn sau một đoạn giải thích. Tránh những đoạn văn dài đều một màu — đoạn nào cũng cùng độ dài, cùng nhịp — đọc mệt và không có điểm nhấn.
- **Dẫn dắt, không liệt kê máy móc.** Nối ý bằng mạch suy nghĩ ("chỗ này mới là cái bẫy", "đến đây thì lộ ra vấn đề"), không phải bằng đề mục khô khan nối tiếp nhau.
- **Đối thoại không có nghĩa là rườm.** Giọng thân mật nhưng mỗi câu vẫn phải mang thông tin. Danh sách từ cấm ở `tu-vung.md` — mở đầu rỗng, nhấn mạnh rỗng, tính từ rỗng — vẫn áp nguyên. Thân mật khác với sáo rỗng: "cái này lo chuyện timeout" thì được, "nhìn chung điều này rất quan trọng" thì cắt.
---
 
## Quy tắc về output
 
### Output lấy từ tài liệu
 
Chép nguyên, không sửa. Rút gọn được nhưng không được thêm dòng nào.
 
### Output tự dựng lại
 
Khi tài liệu **không in output**, được phép dựng lại từ cấu trúc dữ liệu — nhưng phải:
 
1. Gắn nhãn `(dựng lại)` ngay cạnh chữ "Kết quả"
2. Đặt một ghi chú quy ước ở đầu mục chứa các output đó
3. Ghi ngay dưới khối output nào rủi ro cao nhất — thường là chỗ mình đoán
   hình dạng dữ liệu chứ không đọc được từ tài liệu
```markdown
> **Về các khối kết quả in ra.** Trang tài liệu gốc không in kết quả mẫu
> cho ví dụ nào. Các khối dưới đây tôi tự dựng lại từ cấu trúc dữ liệu đã
> mô tả. Cần đối chiếu khi chạy thử.
```
 
**Không dùng ký tự in nghiêng hay in đậm cho nhãn này.** Dùng ngoặc đơn chữ thường: `(dựng lại)`. Lý do: dấu sao bị mất khi người dùng sao chép sang công cụ khác, nhãn biến mất mà nội dung vẫn còn — nguy hiểm hơn không có nhãn.
 
---
 
## Chú thích mọi dòng
 
Áp cho cả code lẫn output: **mọi dòng mang thông tin đều có chú thích**, kể cả dòng nhìn qua thấy hiển nhiên.
 
Lý do: cái hiển nhiên với người viết thường là cái người đọc đang tắc. Và khi chỉ một vài dòng có chú thích, người đọc phải tự đoán mấy dòng còn lại có gì đặc biệt mà bị bỏ qua.
 
Chú thích trả lời **"dòng này làm gì và vì sao viết vậy"**, không mô tả lại cú pháp:
 
| Đừng viết | Viết |
|---|---|
| `# vòng lặp for` | `# mỗi lần model nói là một vòng lặp` |
| `# gọi hàm print` | `# end="" để chữ nối liền, không xuống dòng` |
| `# gán biến stream` | `# v3 là bản mới, bắt buộc ghi rõ` |
 
Căn thẳng cột các dấu chú thích trong cùng một khối. Chú thích so le rất khó đọc.
 
### Trong code — dùng `#`
 
Lý do thực dụng: người đọc sẽ sao chép đoạn code đi chạy thử. `#` là chú thích hợp lệ của Python nên code vẫn chạy; `←` làm hỏng code ngay dòng đầu.
 
Bỏ chú thích cho dòng thuần cú pháp (`import`, đóng ngoặc, khai báo biến rỗng). Còn lại thì giải thích.
 
```python
stream = agent.stream_events(inputs, version="v3")   # v3 là bản mới, bắt buộc ghi rõ
 
for message in stream.messages:                      # mỗi lần model nói là một vòng lặp
    for delta in message.text:                       # mỗi mẩu chữ là một vòng lặp con
        print(delta, end="", flush=True)             # end="" để chữ nối liền, không xuống dòng
 
    luu_vao_db(str(message.text))                    # str() lấy cả câu, không phải từng mẩu
```
 
Nếu một dòng cần giải thích dài hơn một câu, đưa xuống đoạn văn ngay dưới khối code thay vì nhồi vào chú thích.
 
### Trong output — dùng `←`
 
```
tool call chunk: {'name': 'get_weather', 'args': '',       'id': 'call_D3Or'}   ← mảnh đầu, có name và id
tool call chunk: {'name': None,          'args': '{"',     'id': None}          ← từ đây name/id rỗng
tool call chunk: {'name': None,          'args': 'city',   'id': None}          ← đang ghép dần tên tham số
tool call chunk: {'name': None,          'args': '":"',    'id': None}          ← dấu ngăn giữa tên và giá trị
tool call chunk: {'name': None,          'args': 'Boston', 'id': None}          ← giá trị tham số
tool call chunk: {'name': None,          'args': '"}',     'id': None}          ← mảnh cuối, JSON đã đủ
finalized tool calls: [{'name': 'get_weather', 'args': {'city': 'Boston'}}]      ← đã ghép xong, dùng được
```
 
Dòng nào thật sự lặp lại y hệt dòng trên thì ghi `← như trên`, đừng bỏ trống.
 
Output quá dài để chú thích hết thì **rút gọn output**, không bỏ chú thích. Giữ 5–7 dòng tiêu biểu, thêm `...` ở giữa.
 
---
 
## Phân biệt dữ kiện với suy luận
 
Quy tắc **không được vi phạm**.
 
### Dữ kiện từ tài liệu: viết thẳng, không dẫn nguồn
 
Đây là mặc định của cả file. Người đọc đã biết file này viết từ tài liệu chính thức — nhắc lại ở mỗi câu chỉ làm loãng.
 
| Đừng viết | Viết |
|---|---|
| "Doc nói rằng `stream()` trả về một dòng chunk" | "`stream()` trả về một dòng chunk" |
| "Theo tài liệu, tham số này bắt buộc" | "Tham số này bắt buộc" |
| "Doc mô tả nó là ảnh chụp trạng thái" | "Nó là ảnh chụp trạng thái" |
 
Chỉ dẫn nguồn khi **cách diễn đạt của tài liệu chính là vấn đề** — ví dụ khi từ ngữ mơ hồ và mình đang phân tích chính chỗ mơ hồ đó.
 
### Ba trường hợp phải gắn nhãn
 
| Trường hợp | Cách viết |
|---|---|
| Tài liệu không đề cập | "Phần này chưa được nêu", "Không có hướng dẫn cho trường hợp X" |
| Tài liệu mơ hồ | "Điểm này chưa rõ", "Cách diễn đạt để ngỏ khả năng..." |
| Mình suy luận | Nêu suy luận, **nêu căn cứ**, rồi ghi "Đây là suy luận, chưa được xác nhận" |
 
**Xoay vòng cách diễn đạt.** Ba cụm sau đừng dùng quá một lần mỗi file: "chưa được nêu", "chưa rõ", "cần chạy thử". Dùng lặp thì cả file nghe như một mẫu câu.
 
Vài cách thay thế:
 
| Ý | Các cách viết |
|---|---|
| Tài liệu không có | "Không có hướng dẫn cho X", "Phần X bỏ ngỏ", "X không nằm trong phạm vi trang này" |
| Chưa chắc chắn | "Điểm này chưa rõ", "Còn để ngỏ", "Chưa đủ căn cứ để khẳng định" |
| Cần xác minh | "Phải chạy thử mới biết", "Chờ kiểm chứng bằng thực nghiệm", "Cần đối chiếu khi triển khai" |
 
Mẫu cho trường hợp suy luận:
 
```markdown
X không nằm trong Y. Căn cứ: Y dành cho những thứ được gọi ra qua tool, và
mỗi mục có ô `.cause` ghi lệnh gọi đó — X thì không có lệnh nào gọi nó.
Đây là suy luận, chưa được xác nhận trực tiếp.
```
 
### Khoảng trống của tài liệu
 
Đặt **ở chỗ người đọc gặp nó**, không dồn xuống cuối file. Nếu một tính năng không được nhắc tới mà nó ảnh hưởng tới quyết định chọn công nghệ, đó là thông tin quan trọng nhất trong file — đưa lên bảng so sánh và phần kết luận.
 
---
 
## Bảng so sánh — chỉ khi có gì để so sánh
 
**Không phải file nào cũng cần mục này.** Chỉ dựng bảng khi:
 
- Tài liệu mô tả hai cách làm cùng một việc (API cũ và mới, hai chế độ, hai thư viện)
- Hoặc người dùng yêu cầu so sánh nhiều nguồn
Tài liệu chỉ mô tả một thứ duy nhất thì **bỏ mục này**, đừng cố tạo bảng đối xứng cho có.
 
Khi có so sánh thật, dựng hai bảng riêng, đừng gộp:
 
**Bảng 1 — đối chiếu năng lực.** Cột trái là tiêu chí, hai cột phải là hai bên.
 
**Bảng 2 — ánh xạ chuyển đổi.** Cho người đang có code cũ muốn chuyển sang cách mới:
 
```markdown
| Cách cũ | Tương ứng ở cách mới |
|---|---|
| `stream_mode="messages"` | `stream.messages` |
| *(không có)* | `stream.tool_calls` — năng lực mới |
```
 
Dòng `*(không có)*` rất quan trọng: nó cho thấy cái gì là mới hoàn toàn.
 
---
 
## Liên kết chéo
 
Khi có nhiều file cùng chủ đề:
 
- Đặt các mục **song song nhau** giữa các file (mục 4.1 file A nói cùng chủ đề với mục 4.1 file B) để so sánh trực tiếp
- Link bằng đường dẫn tương đối: `[02-04 mục 4.2](./02-04-streaming.md#42-tool-call)`
- Mỗi file có mục "Tham chiếu chéo" ở cuối
- Nội dung giữa các file **không được mâu thuẫn nhau**
---
 
## Ngôn ngữ
 
Toàn bộ quy tắc dùng từ nằm ở `references/tu-vung.md`: ba nhóm từ và cách xử lý từng nhóm, danh sách cấm dùng, quy tắc ví von. Đọc file đó, không chép lại vào đây.
 
Hai điều cần nhớ khi viết:
 
**Không dựng bảng từ điển ở đầu file.** Giải thích thuật ngữ ngay tại chỗ nó xuất hiện lần đầu. Bảng ở đầu file buộc người đọc học thuộc trước khi hiểu, còn giải thích tại chỗ thì họ hiểu ngay lúc cần.
 
**Gặp từ chưa có trong bảng thì hỏi:** *người đọc có phải gõ chữ này vào code không?* Có thì giữ nguyên tiếng Anh, không thì dịch. Rồi bổ sung từ đó vào `tu-vung.md`.
 
---
 
## Checklist tự soát
 
Chạy hết trước khi giao file.
 
**Cấu trúc**
- [ ] Có frontmatter đủ trường
- [ ] Không có bảng từ điển ở đầu file — thuật ngữ giải thích tại chỗ
- [ ] Có "Tham chiếu chéo"
- [ ] Không có mục nào bị lặp (kiểm bằng `grep -n "^## "`)
- [ ] Cấu trúc đi theo mạch giảng, không sao lại thứ tự đoạn của trang gốc
- [ ] Không giảng lại chi tiết cơ chế mà file khác trong bộ mới phụ trách (stub + link)
**Giọng văn**
- [ ] Đọc lên như người đi trước giảng lại, không như biểu mẫu dán nhãn
- [ ] Không có đoạn văn dài đều một màu, thiếu điểm nhấn
- [ ] Không dịch máy theo bố cục trang gốc
**Nội dung**
- [ ] Mọi khái niệm mở đầu bằng nỗi đau/mục đích nó lo, rồi mới định nghĩa
- [ ] Khái niệm trừu tượng có ví von đời thường (không mượn khái niệm kỹ thuật khác)
- [ ] Không có dữ kiện (tên hàm, tham số, hành vi) nào không truy được về nguồn
- [ ] Nhãn cảnh báo dùng `!Note:`, không dùng "Bẫy" / "Lưu ý" / "Chú ý"
- [ ] Mọi khối "Áp dụng thực tế" đều có tình huống thật, không nói chung chung
- [ ] Mỗi khối code đều có kết quả in ra đi kèm
- [ ] Mọi dòng code mang thông tin đều có chú thích `#`, căn thẳng cột
- [ ] Mọi dòng output đều có chú thích `←`, không chỉ vài dòng chọn lọc
- [ ] Chú thích nói "làm gì, vì sao", không mô tả lại cú pháp
- [ ] Output tự dựng đều gắn nhãn `(dựng lại)`
- [ ] Mọi suy luận đều nêu căn cứ và ghi rõ là suy luận
- [ ] Không còn câu "Doc nói rằng", "Theo tài liệu" cho dữ kiện thường
- [ ] Cách diễn đạt khoảng trống có xoay vòng, không lặp một mẫu câu
- [ ] Khoảng trống của tài liệu được ghi ngay tại chỗ người đọc gặp nó
**Ngôn ngữ**
- [ ] Thuật ngữ đã giải thích ở lần xuất hiện đầu
- [ ] Không còn từ trong danh sách cấm ở `tu-vung.md`
- [ ] Tên hàm và thuộc tính giữ nguyên tiếng Anh
- [ ] Ví von là từ đời sống, không phải từ khái niệm kỹ thuật khác
**Liên kết**
- [ ] Link tương đối chạy được
- [ ] Nội dung không mâu thuẫn với file liên quan
---
 
## Tài liệu kèm theo
 
| File | Đọc khi nào |
|---|---|
| `references/template.md` | Bắt đầu một file research mới — sao chép khung này |
| `references/tu-vung.md` | Bất cứ lúc nào phân vân dịch một từ chuyên ngành |
 