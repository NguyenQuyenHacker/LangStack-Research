---
title: Chọn giữa Graph API và Functional API
doc_source: https://docs.langchain.com/oss/python/langgraph/choosing-apis
accessed: 2026-07-30
lc_version: unknown
status: draft
lab:
related:
  - ./08-02-graph-api.md
  - ../09-functional-api/09-01-functional-api.md
---

# Chọn giữa Graph API và Functional API

> LangGraph cho hai cách dựng workflow của agent trên **cùng một runtime**: Graph API (khai báo) và Functional API (mệnh lệnh).

---

## 1. Tổng quan

Hai API khác nhau ở **cách viết**, không khác **năng lực lõi**. Cả hai đều có persistence, streaming, human-in-the-loop, memory, chạy chung một runtime, và dùng lẫn nhau trong cùng một ứng dụng.

Điểm khác nhau:

- **Graph API** — ta khai báo `State`, các `node`, các `edge`, rồi để runtime điều phối. Luồng đi thành một đồ thị vẽ ra được.
- **Functional API** — ta viết như code Python thường (`if/else`, vòng lặp, gọi hàm), gắn `@entrypoint` và `@task` để lấy các tính năng của LangGraph mà gần như không đổi cấu trúc code.

```python
# Graph API
from langgraph.graph import StateGraph, START
from typing import TypedDict

class State(TypedDict):
    x: int

def double(state: State):                     # node đọc state, trả về phần cập nhật
    return {"x": state["x"] * 2}

graph = StateGraph(State).add_node(double).add_edge(START, "double").compile()
graph.invoke({"x": 5})
```

```python
# Functional API
from langgraph.func import entrypoint, task

@task
def double(x: int) -> int:                     # task = đơn vị công việc, kết quả được checkpoint
    return x * 2

@entrypoint()
def workflow(x: int) -> int:                    # entrypoint = điểm vào, viết như hàm thường
    return double(x).result()                   # .result() lấy giá trị của task

workflow.invoke(5)
```

**Kết quả in ra** (dựng lại):


> Khác biệt hình thức ở output: Graph API luôn trả về **cả state**, Functional API trả về **đúng thứ hàm `return`**.

---

## 2. Khi nào Graph API hợp

Bốn tình huống Graph API là lựa chọn đúng:

- **Nhánh rẽ và cây quyết định phức tạp** — nhiều điểm rẽ phụ thuộc nhiều điều kiện. Khai báo bằng conditional edge làm các nhánh hiện rõ, vẽ ra được để soi.
- **State dùng chung nhiều thành phần** — khi nhiều node cùng đọc/ghi một khối dữ liệu (kết quả tìm kiếm, trạng thái kiểm định...), state chung tường minh giúp phối hợp.
- **Chạy song song rồi gộp** — fan-out nhiều node chạy đồng thời, fan-in đợi tất cả xong rồi hợp kết quả. Runtime lo phần đồng bộ.
- **Nhiều người cùng làm, cần tài liệu hóa** — đồ thị vẽ được nên mỗi người nhận một node, đọc luồng bằng hình.

Mẫu chung: workflow **rẽ nhánh nhiều, có song song, cần nhìn thấy cấu trúc**.

---

## 3. Khi nào Functional API hợp

Bốn tình huống Functional API là lựa chọn đúng:

- **Đã có code thủ tục sẵn** — muốn thêm checkpoint/streaming mà sửa tối thiểu. Bọc `@task`/`@entrypoint`, giữ nguyên `if/else` và vòng lặp.
- **Luồng tuyến tính, rẽ nhánh đơn giản** — chạy tuần tự bước 1 → bước 2 → bước 3, đôi chỗ rẽ nhẹ.
- **Dựng thử nhanh** — không phải định nghĩa schema state hay đồ thị, viết là chạy.
- **State cục bộ trong hàm** — dữ liệu gói gọn trong từng hàm, không cần chia sẻ rộng.

Mẫu chung: workflow **thẳng, ít nhánh, ưu tiên viết nhanh và ít thay đổi code cũ**.

---

## 4. Kết hợp và chuyển đổi

Hai API này **không loại trừ nhau** — dùng chung trong một ứng dụng được. 

➤ Cách phổ biến: phần điều phối đa-agent phức tạp dựng bằng Graph API, phần xử lý dữ liệu tuyến tính viết bằng Functional API rồi gọi vào trong một node.

```python
@entrypoint()
def data_processor(raw_data: dict) -> dict:     # khối tuyến tính viết kiểu functional
    cleaned = clean_data(raw_data).result()
    return transform_data(cleaned).result()

def orchestrator_node(state):                   # node trong Graph API gọi entrypoint như hàm
    processed = data_processor.invoke(state["raw_data"])
    return {"processed_data": processed}
```

Chuyển đổi cả hai chiều đều được: workflow functional lớn dần, nhiều nhánh → tách thành node/edge của Graph API; đồ thị dựng quá nặng cho một luồng thẳng → rút về `@entrypoint` gọn hơn.

---

## 5. Bảng so sánh

| Tiêu chí | Graph API | Functional API |
|---|---|---|
| Paradigm | Khai báo (node/edge/state) | Mệnh lệnh (code thủ tục) |
| Điều khiển luồng | Edge + conditional edge + `Command` | `if/else`, vòng lặp Python |
| Quản lý state | State chung tường minh, có reducer | Cục bộ trong hàm, truyền qua tham số |
| Rẽ nhánh phức tạp | Mạnh, vẽ ra được | Làm được nhưng khó nhìn tổng thể |
| Song song + đồng bộ | Runtime lo (fan-out/fan-in) | Phải tự điều phối |
| Trực quan hóa đồ thị | Có | Không |
| Lượng code khung | Nhiều hơn (schema, node, edge) | Ít, sát code có sẵn |
| Tính năng lõi | persistence, streaming, HITL, memory | Y hệt — cùng runtime |

Điểm cần nhớ: dòng cuối bảng cho thấy **không mất tính năng nào khi đổi API**. Lựa chọn thuần về cách trình bày luồng.

---

## Tham chiếu chéo

- [08-02 Graph API](./08-02-graph-api.md) — cú pháp State/Nodes/Edges/Command của Graph API
- Functional API: `../09-functional-api/09-01-functional-api.md` — `@entrypoint`, `@task`, quy tắc determinism
- Trang gốc: https://docs.langchain.com/oss/python/langgraph/choosing-apis