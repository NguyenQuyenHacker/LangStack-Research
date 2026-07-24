# Quy ước viết research

Áp dụng cho cả ba stack. Đọc trước khi viết bất kỳ file note nào.

## 1. Ngôn ngữ

Nội dung viết bằng tiếng Việt. Giữ nguyên tiếng Anh: tên class, tên hàm, tham số, và thuật ngữ kỹ thuật chưa có bản dịch ổn định (`middleware`, `harness`, `checkpointer`, `hook`, `content block`). Lần đầu xuất hiện một thuật ngữ, giải thích ngắn trong ngoặc đơn.

## 2. Không bịa

Mọi khẳng định về API, tham số, hành vi phải lấy từ trang docs tương ứng hoặc từ source code đã đọc. Nếu docs không nói rõ, ghi thẳng:

```
> ⚠️ Docs không nêu rõ điểm này. Cần kiểm chứng bằng lab / đọc source.
```

Không suy đoán rồi trình bày như sự thật. Không viết code mẫu chưa đối chiếu với docs. Nguồn chuẩn cho LangChain: `https://docs.langchain.com/oss/python/langchain/*` (danh mục đầy đủ ở `https://docs.langchain.com/llms.txt`).

## 3. Bám phiên bản

LangChain v1 đã bỏ trọng tâm khỏi LCEL và Chains, chuyển sang `create_agent` + middleware. Trước khi viết mỗi file, `WebFetch` đúng URL docs được chỉ định. Không viết theo tài liệu v0 trong trí nhớ.

## 4. Văn phong

Câu ngắn, mỗi câu một ý. Không mở đầu bằng "Trong bối cảnh hiện nay", "Nhìn chung", "Về cơ bản". Không kết bằng "Hy vọng phần này hữu ích". Viết thành đoạn văn khi nội dung liền mạch; bullet chỉ dùng khi liệt kê từ 3 mục rời rạc trở lên.

## 5. Template mỗi file note

```markdown
---
title: <Tiêu đề tiếng Việt>
doc_source: https://docs.langchain.com/oss/python/langchain/<path>
accessed: <YYYY-MM-DD>
lc_version: <version đọc được từ docs, để "unknown" nếu không xác định>
status: draft
lab: <đường dẫn labs/ nếu có, để trống nếu chưa>
---

# <Tiêu đề>

## 1. Vấn đề phần này giải quyết
Nêu thẳng: thiếu thành phần này thì gặp khó khăn gì. Tối đa 5 câu.

## 2. Khái niệm và API chính
Định nghĩa từng khái niệm. Liệt kê signature chính, giải thích tham số quan trọng.

## 3. Cơ chế bên dưới
Phần cốt lõi. Không chép docs — giải thích thứ tự thực thi, dữ liệu đi qua đâu, cái gì
được gọi lúc nào. Nếu docs không đủ, ghi rõ và đề xuất cách kiểm chứng.

## 4. Ví dụ chạy được
Code tối giản, có chú thích tiếng Việt. Nếu có lab tương ứng, link tới `../labs/...`.
Ghi rõ output kỳ vọng.

## 5. Ranh giới và đánh đổi
Khi nào KHÔNG nên dùng. So sánh với cách làm thay thế. Chi phí đi kèm.

## 6. Câu hỏi còn mở
Gạch đầu dòng những điểm chưa chắc chắn, cần lab hoặc đọc source để trả lời.

## 7. Tham chiếu
- [Tên trang](URL) — truy cập YYYY-MM-DD
```

Mục 3 và 5 là phần tạo ra giá trị. Nếu mục 3 chỉ diễn đạt lại mục 2 thì chưa đạt — phải đào sâu thêm.

## 6. Quy ước đặt tên file

`<số-chương>-<số-mục>-<slug>.md`, ví dụ `02-01-agents.md`. Mỗi khái niệm chỉ có một file là nguồn chính; file khác nhắc tới thì link, không chép lại.

## 7. Quy ước ảnh và sơ đồ

Hai thư mục trong mỗi stack:

```
assets/images/      # Ảnh chụp màn hình, sơ đồ đã render (.png, .jpg, .svg)
assets/diagrams/    # Sơ đồ nguồn Mermaid (.mmd) để sửa lại được
```

Tên ảnh theo file note tham chiếu nó: `<số-chương>-<số-mục>-<slug>-<số thứ tự>.png`, ví dụ `02-01-agent-loop-1.png`.

Chèn bằng đường dẫn tương đối (mọi note nằm sâu một cấp):

```markdown
![Vòng lặp thực thi của agent](../assets/images/02-01-agent-loop-1.png)
*Hình 2.1 — Vòng lặp model → tool → model trong `create_agent`*
```

Mọi hình phải có caption dạng `Hình <chương>.<thứ tự>`. Không chèn ảnh không caption. Ưu tiên viết Mermaid trực tiếp trong file `.md`; chỉ khi sơ đồ quá phức tạp mới xuất `.png` và lưu file `.mmd` nguồn vào `assets/diagrams/` cùng tên.
