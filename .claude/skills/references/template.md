# Template — khung file research
 
Sao chép nguyên phần dưới, thay nội dung trong `<>`.
 
---
 
````markdown
---
title: <tên trang doc>
doc_source: <URL đầy đủ>
accessed: <YYYY-MM-DD>
version: "<phiên bản, hoặc unknown>"
status: draft
lab:
related:
  - ./<file-liên-quan>.md
---
 
# <Tên> (`<hàm chính>`)
 
> <Một câu định vị: nó là gì, dành cho ai, có từ phiên bản nào.>
> <Một câu nói quan hệ với thứ liên quan, kèm link.>
 
---
 
## 1. Tổng quan
 
<Một đoạn: nó là gì, khác thứ quen thuộc ở chỗ nào.>
 
```python
<code ngắn nhất chạy được>
```
 
**Kết quả in ra** (dựng lại nếu tài liệu không có):
 
```
<output>
```
 
<Một câu giải thích vì sao output trông như vậy.>
 
**Quan hệ với <thứ liên quan>.** <Một đoạn.>
 
---
 
## 2. <Tên khái niệm nền tảng — đặt theo nội dung, không đặt "Khái niệm cơ bản">
 
### Khái niệm
 
<Một đến hai câu.>
 
### Vai trò
 
<Nó giải quyết vấn đề gì. Thiếu phần này thì người đọc học thuộc cú pháp
mà không biết khi nào dùng.>
 
### Áp dụng thực tế
 
<Tình huống có thật, có số liệu, có người dùng.>
 
### <Bảng đối chiếu nếu cần>
 
| | <cách cũ> | <cách mới> |
|---|---|---|
| | | |
 
---
 
## 3. Bảng tham số — <tên nhóm tham số>
 
<Đặt tên cụ thể theo cái đang liệt kê: "Bảng tham số của stream_events",
"Các thuộc tính của ChatModelStream", "Danh sách chế độ stream_mode".
Đừng để tên chung chung.>
 
| Tham số | Kiểu / giá trị | Chứa gì | Dùng khi nào |
|---|---|---|---|
| | | | |
 
<Một câu chốt: cái nào dùng thường xuyên, cái nào chỉ cho trường hợp
đặc biệt. Người đọc cần biết cái gì được phép bỏ qua.>
 
---
 
## 4. Cách làm từng việc
 
<Đổi tên mục này theo chủ đề file. Ví dụ tốt: "Cách lấy từng loại dữ liệu",
"Cách xử lý từng loại lỗi", "Cách dùng trong từng kiểu giao diện".
Ví dụ tệ: "Các tình huống", "Use cases", "Ví dụ nâng cao".>
 
> **Về các khối kết quả in ra.** <Ghi chú quy ước nếu output là tự dựng lại.>
 
---
 
### 4.1 <Đặt tên theo việc cần làm>
 
<Ví dụ tốt: "Hiện phần suy nghĩ của model", "Theo dõi tool khi chạy lỗi",
"Biết chữ đang chảy là của agent nào".
Ví dụ tệ: "Tình huống 1", "Trường hợp sử dụng", "Ví dụ nâng cao".>
 
**Khái niệm.** <...>
 
**Vai trò.** <...>
 
**Áp dụng thực tế.** <...>
 
**Triển khai.**
 
```python
<code tối thiểu>
```
 
**Kết quả in ra** (dựng lại):
 
```
<output>
```
 
<Giải thích những dòng đáng chú ý trong output.>
 
**So với <cách khác>:**
 
| Ở <cách cũ> phải làm | Ở <cách mới> |
|---|---|
| | |
 
**!Note:** <Chỗ dễ sai, ưu tiên nêu lỗi im lặng — code chạy nhưng sai.>
 
---
 
## <n>. Bảng so sánh tổng hợp
 
| | <A> | <B> |
|---|---|---|
| | | |
 
### Chuyển code từ cách cũ sang cách mới
 
| Cách cũ | Tương ứng |
|---|---|
| | |
| *(không có)* | <năng lực mới hoàn toàn> |
 
---
 
## <n+1>. Nên chọn cái nào
 
Chọn <A> khi: <liệt kê điều kiện cụ thể>.
 
Chọn <B> khi: <liệt kê điều kiện cụ thể>.
 
---
 
## Tham chiếu chéo
 
- [<file liên quan>](./<file>.md) — <quan hệ>
- <tên trang tài liệu khác>: `<đường dẫn>`
````
 