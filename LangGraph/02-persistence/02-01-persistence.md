---
title: Persistence
doc_source: https://docs.langchain.com/oss/python/langgraph/persistence
accessed: 2026-07-28
version: "unknown"
status: draft
lab:
related:
  - ./02-02-checkpointers.md
  - ./02-03-stores.md
---

# Persistence — lớp bộ nhớ của LangGraph

> Lớp persistence cho agent hai loại bộ nhớ: ngắn hạn qua checkpointer, dài hạn qua store.
> Đây là trang tổng quan. Cơ chế từng cái nằm ở [02-02-checkpointers](./02-02-checkpointers.md) và [02-03-stores](./02-03-stores.md).

---

## 1. Tổng quan

Một đồ thị LangGraph chạy xong là hết: không nối tiếp được hội thoại, sập giữa chừng là mất, không giữ gì qua các lần tương tác. Persistence lo đúng những chỗ đó — giữ thông tin sống lâu hơn một lần chạy, để agent nối tiếp hội thoại, resume sau gián đoạn, phục hồi sau lỗi, và nhớ xuyên các lần tương tác.

LangGraph tách thành hai hệ thống bổ trợ nhau:

- **Checkpointer** — lưu state của một thread thành checkpoint. Bộ nhớ ngắn hạn, phạm vi một thread: nối tiếp hội thoại, human-in-the-loop, time travel, chịu lỗi.
- **Store** — lưu dữ liệu do ứng dụng tự định nghĩa, nằm ngoài state đồ thị. Bộ nhớ dài hạn, xuyên thread: sở thích người dùng, dữ kiện, kiến thức dùng chung.

Phần lớn ứng dụng dùng cả hai: checkpointer theo dõi thread hiện tại, store giữ thông tin bền xuyên các thread.

---

## 2. Checkpointer & Store 
| Tiêu chí | Checkpointer | Store |
|---|---|---|
| Lưu gì | Ảnh chụp state đồ thị | Dữ liệu key-value do ứng dụng định nghĩa |
| Phạm vi | Một thread | Xuyên thread |
| Loại bộ nhớ | Ngắn hạn, theo thread | Dài hạn, xuyên thread |
| Dùng cho | Nối tiếp hội thoại, human-in-the-loop, time travel, chịu lỗi | Sở thích người dùng, dữ kiện, kiến thức chung |
| Cách truy cập | Truyền `thread_id` trong config đồ thị | Đọc/ghi item từ node hoặc từ code ứng dụng |
| Hướng dẫn đầy đủ | [02-02-checkpointers](./02-02-checkpointers.md) | [02-03-stores](./02-03-stores.md) |

Cần nhớ trong một cuộc thì dùng checkpointer; cần nhớ xuyên các cuộc thì dùng store; thường là cả hai.

---

## 3. Các vấn đề khi sử dụng Persistence 

### thread_id quá dài với PostgresSaver

`PostgresSaver` (và `AsyncPostgresSaver`) lưu `thread_id` vào một cột có giới hạn độ dài. `thread_id` vượt cỡ cột thì báo lỗi database.

Cách xử lý: giữ `thread_id` dưới 255 ký tự; cần ID xác định thì dùng UUID hoặc hash.


### MemorySaver mất dữ liệu khi khởi động lại

`MemorySaver` và `InMemorySaver` giữ checkpoint trong RAM. Process restart là mất sạch.

Cách xử lý: production dùng checkpointer bền — `PostgresSaver` (Postgres, có async) hoặc `SqliteSaver` (file local, cho phát triển).

### Checkpoint phình không giới hạn

Hội thoại dài, checkpoint tích lũy dần, làm tăng độ trễ và chi phí lưu.

Cách xử lý: dọn checkpoint cũ định kỳ, hoặc đặt chính sách giữ (retention).

### Đồ thị cha không thấy state subgraph vừa cập nhật

Subgraph cập nhật state nhưng đồ thị cha có thể chưa thấy ngay, vì mỗi subgraph quản lý checkpoint namespace riêng.

Cách xử lý: dùng state dùng chung qua Store cho dữ liệu cần vượt ranh giới đồ thị, hoặc cấu hình subgraph ghi vào checkpoint của cha.

---

## Tham chiếu chéo

- [02-02-checkpointers](./02-02-checkpointers.md) — bộ nhớ ngắn hạn theo thread (ảnh chụp state đồ thị)
- [02-03-stores](./02-03-stores.md) — bộ nhớ dài hạn xuyên thread (dữ liệu do ứng dụng định nghĩa)
- Tài liệu gốc liên quan: Agent Server, Subgraphs — `docs.langchain.com/oss/python/langgraph/...`