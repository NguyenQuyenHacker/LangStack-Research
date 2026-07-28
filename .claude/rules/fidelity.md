# Trung thực nguồn

## Fetch trước khi viết

Luôn `WebFetch` trang docs hiện hành trước khi viết bất kỳ mục nào. Không viết từ trí nhớ — LangChain v1 đã bỏ trọng tâm khỏi LCEL/Chains, kiến thức v0 trong trí nhớ là sai. Không tin cache: nếu đã fetch trang đó ở phiên trước, vẫn fetch lại.

`accessed` và `lc_version` trong frontmatter phải là giá trị thật của lần fetch này. Không đọc được version từ trang thì để `unknown`, không đoán.

## Không suy diễn ngoài phạm vi trang nguồn

Mọi khẳng định về API, tham số, hành vi phải lấy từ trang docs đã fetch hoặc từ source code đã đọc. Docs không nói rõ thì ghi thẳng, đúng dạng ở `CONVENTIONS.md` mục 2:

```
> ⚠️ Docs không nêu rõ điểm này. Cần kiểm chứng bằng lab / đọc source.
```

Code mẫu chưa đối chiếu với docs thì không viết. Suy đoán thì không trình bày như sự thật.

## Nhãn `(dựng lại)`

Nội dung không lấy trực tiếp từ docs — sơ đồ tự vẽ, bảng so sánh tự lập, thứ tự thực thi tự suy ra từ nhiều trang — phải gắn nhãn `(dựng lại)` ngay tiêu đề mục hoặc caption, kèm căn cứ suy ra.

Mục 3 (Cơ chế bên dưới) và mục 5 (Ranh giới và đánh đổi) của template thường là phần dựng lại. Gắn nhãn ở đó là bình thường, không phải khuyết điểm — che giấu mới là khuyết điểm.

## Gắn cờ chỗ thiếu

Gặp placeholder, ví dụ dở dang, hoặc trang docs mâu thuẫn với trang khác: ghi vào mục 6 (Câu hỏi còn mở) của note, kèm URL cả hai trang. Không tự chọn một bên rồi im lặng.
