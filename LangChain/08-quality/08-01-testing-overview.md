---
title: Testing — tổng quan
doc_source: https://docs.langchain.com/oss/python/langchain/test/index
accessed: 2026-07-25
lc_version: unknown
status: draft
lab:
related:
  - ./test-02-unit-testing.md
  - ./test-03-integration-testing.md
  - ./test-04-evals.md
---

# Testing agent — tổng quan

> Giới thiệu ba cách kiểm thử một agent LangChain và trỏ sang trang chi tiết của từng cách.

---

## 1. Tổng quan

Agent để LLM tự quyết bước tiếp theo. Sự linh hoạt đó mạnh, nhưng model là hộp đen: sửa một chỗ khó đoán được ảnh hưởng tới toàn bộ luồng. Vì vậy muốn đưa agent lên production thì phải kiểm thử kỹ.

Tài liệu chia làm ba cách kiểm thử, khác nhau ở chỗ **có gọi mạng thật hay không** và **kiểm cái gì**:

| Cách | Gọi API model thật | Kiểm cái gì | Trang chi tiết |
|---|---|---|---|
| Unit test | Không — thay model bằng bản giả trong RAM | Từng mảnh nhỏ, tất định, khẳng định hành vi chính xác | [test-02](./test-02-unit-testing.md) |
| Integration test | Có — gọi API model thật | Các thành phần ráp với nhau, key và schema khớp, độ trễ chấp nhận được | [test-03](./test-03-integration-testing.md) |
| Evals | Có (agent chạy thật) rồi chấm điểm | Chất lượng cả quỹ đạo thực thi, bằng đối chiếu tất định hoặc LLM chấm | [test-04](./test-04-evals.md) |

Ba cách này không loại trừ nhau — thường dùng cả ba ở các tầng khác nhau: unit test chạy mỗi lần sửa code, integration test chạy trong CI, evals để bắt hồi quy khi đổi prompt/tool/model.

---

## 2. Vì sao agent nghiêng nhiều về integration test

**Khái niệm.** Phần mềm truyền thống chuộng unit test vì đầu vào — đầu ra tất định. Agent thì ngược lại.

**Vai trò.** Biết đặc thù này để phân bổ công sức đúng chỗ: không cố ép mọi thứ vào unit test tất định, mà chấp nhận integration test là xương sống.

Lý do tài liệu nêu: agent xâu chuỗi nhiều thành phần lại với nhau, và bản thân LLM không tất định nên kết quả chập chờn (mỗi lần chạy ra khác nhau một chút). Hai đặc điểm đó khiến việc "ráp thật rồi chạy thật" quan trọng hơn so với phần mềm thường.

---

## 3. Chạy evals ở quy mô lớn — LangSmith

Tài liệu đặt một liên kết sang LangSmith để chạy evaluation ở quy mô lớn, theo dõi kết quả theo thời gian và so sánh các lần thí nghiệm. Cơ chế LangSmith **không nằm trong phạm vi trang này** — nó thuộc cây tài liệu LangSmith riêng. Xem [test-04 mục 7](./test-04-evals.md) để biết phần LangSmith mà trang evals có đề cập.

---

## Tham chiếu chéo

- [test-02-unit-testing.md](./test-02-unit-testing.md) — thay model bằng bản giả, lưu trạng thái trong RAM
- [test-03-integration-testing.md](./test-03-integration-testing.md) — chạy với API model thật, quản key, xử lý chập chờn, kiểm soát chi phí
- [test-04-evals.md](./test-04-evals.md) — chấm điểm quỹ đạo bằng đối chiếu tất định hoặc LLM chấm
- Tài liệu gốc: `https://docs.langchain.com/oss/python/langchain/test/index`