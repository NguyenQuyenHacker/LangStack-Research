---
title: Tổng quan LangGraph
doc_source: https://docs.langchain.com/oss/python/langgraph/overview
accessed: 2026-07-28
lc_version: unknown
status: draft
lab:
related:
  - ./01-02-thinking-in-langgraph.md
  - ./01-03-workflows-vs-agents.md
---

# Tổng quan LangGraph

> LangGraph là một low-level orchestration framework và runtime để dựng, vận hành, triển khai agent long-running, stateful. Nó nằm *bên dưới* các abstraction dựng sẵn của LangChain, lo phần hạ tầng chứ không lo prompt hay kiến trúc agent.
> Mô hình graph (node + edge + state) được giảng kỹ ở [01-02](./01-02-thinking-in-langgraph.md); ranh giới giữa workflow và agent ở [01-03](./01-03-workflows-vs-agents.md).

---

## 1. Tổng quan

LangGraph là một low-level orchestration framework và là runtime — lớp thực thi chạy bên dưới — để dựng và vận hành agent long-running, stateful.

Low-level là chữ cần nắm ngay, vì nó quyết định khi nào ta chạm tới LangGraph. Nó **không** lo prompt, **không** lo kiến trúc agent. Nó lo phần hạ tầng phía dưới: streaming, persistence, human-in-the-loop, và tương tự.

Khác thứ quen thuộc ở chỗ nào: nếu đã dùng `create_agent` của LangChain, đó là tầng cao — một vòng lặp model-gọi-tool đã dựng sẵn, ta chỉ khai báo model với tool rồi chạy. LangGraph nằm bên dưới cái đó. ta xuống LangGraph khi muốn tự vẽ luồng thay vì mượn vòng lặp dựng sẵn. Không bắt buộc phải qua LangChain mới dùng được — LangGraph chạy độc lập.

Ví dụ "hello world" ngắn nhất chạy được:

```python
from langgraph.graph import StateGraph, MessagesState, START, END

def mock_llm(state: MessagesState):                # một node giả, trả về câu cố định thay cho model thật
    return {"messages": [{"role": "ai", "content": "hello world"}]}

graph = StateGraph(MessagesState)                  # dựng graph rỗng, state theo khuôn MessagesState (chỉ có ô messages)
graph.add_node(mock_llm)                           # thêm một node; tên node lấy theo tên hàm → "mock_llm"
graph.add_edge(START, "mock_llm")                  # nối điểm vào START tới node mock_llm
graph.add_edge("mock_llm", END)                    # nối node mock_llm ra điểm kết thúc END
graph = graph.compile()                            # dựng bản vẽ thành thứ chạy được; trước bước này graph mới chỉ là mô tả

graph.invoke({"messages": [{"role": "user", "content": "hi!"}]})  # chạy một lần với tin nhắn người dùng "hi!"
```

**Kết quả in ra** (dựng lại):

```
{'messages': [HumanMessage(content='hi!'),          ← tin nhắn người dùng ban đầu, vẫn nằm lại trong state
              AIMessage(content='hello world')]}    ← câu node mock_llm trả về, được nối thêm vào sau
```

Để đọc được ví dụ, chỉ cần nắm bốn mảnh: **node** — một hàm làm một việc; **edge** — mũi tên nối node này sang node kia, quyết định thứ tự chạy; **state** — dữ liệu chảy xuyên qua các node (ở đây là ô `messages`); và bước `compile()` — biến bản vẽ thành thứ chạy được. Mạch tư duy graph đầy đủ — vì sao lại là graph, state di chuyển ra sao — nằm ở [01-02](./01-02-thinking-in-langgraph.md).

---

## 2. "Low-level orchestration" lo nỗi đau gì

Vòng lặp hỏi-đáp thông thường trơn tuột: gửi prompt, nhận câu trả lời, xong. Nó gãy ngay khi agent phải làm những việc kéo dài và có ký ức: chạy suốt nhiều phút rồi gặp sự cố phải **resume** từ chỗ dừng chứ không làm lại từ đầu; **dừng giữa chừng** cho một người duyệt rồi mới đi tiếp; **nhớ** qua nhiều phiên khác nhau. Những việc này cần một lớp hạ tầng bên dưới giữ state và điều phối các bước — và đó chính là chỗ LangGraph.

Điểm mạnh riêng của LangGraph: trộn **node deterministic** (chạy y hệt mỗi lần) với **node do model tự quyết** trong cùng một graph.

Hình dung một dây chuyền sản xuất. Có node là máy tự động, làm đúng một thao tác giống hệt nhau mọi lần — đoán trước được, soi lại được từng bước. Có node là thợ lành nghề, nhìn tình huống rồi tự quyết — linh hoạt nhưng khó đoán. LangGraph cho ta xếp cả hai loại node trên cùng một dây chuyền. Nhờ vậy, phần logic cần chắc chắn thì tất định (deterministic) và kiểm toán được (auditable), phần cần mềm dẻo thì để model lo — ta cần kiểm soát chính xác chỗ nào AI được xen vào, chỗ nào không.

---

## 3. Vị trí trong Hệ sinh thái Lang

LangGraph không đứng một mình; nó là một tầng trong chồng sản phẩm. Nắm được ai nằm trên ai giúp biết mình đang cầm đúng công cụ chưa.

| Sản phẩm | Vai trò |
|---|---|
| Deep Agents | Agent harness — dựng sẵn planning, subagent, tool thao tác file, context management; đặt *trên* LangGraph |
| LangChain | Agent framework — các abstraction và tích hợp cho model, tool, agent loop |
| **LangGraph** | Orchestration runtime — durable execution, streaming, human-in-the-loop, persistence |
| LangSmith | Nền tảng tách rời — trace, evaluation, quản lý prompt, deployment (chạy được với mọi framework) |

Ranh giới đáng nhớ nhất là **framework so với runtime**. LangChain là framework: nó cho ta các mảnh ghép và agent loop dựng sẵn. LangGraph là runtime: nó chạy các mảnh đó, lo phần durable và orchestration bên dưới. LangChain agents thực chất được dựng *trên* LangGraph — nên khi dùng `create_agent`, ta vẫn đang chạy trên LangGraph mà không cần chạm tay vào nó.

LangSmith còn tách thành vài mảnh con (Engine dò lỗi trong trace và đề xuất sửa; Fleet là công cụ dựng agent không cần code), nhưng đó không thuộc phạm vi trang này.

---

## 4. Năm năng lực lõi

Trang overview không giảng sâu từng năng lực — mỗi cái có trang riêng. Bảng dưới nêu nó lo gì và trỏ tới nơi giảng chi tiết.

| Năng lực | Nó lo gì | Nơi giảng chi tiết |
|---|---|---|
| persistence | Agent sống sót qua sự cố, chạy dài, resume từ chỗ dừng | doc: `/oss/python/langgraph/persistence` |
| human-in-the-loop | Chèn người vào giữa luồng để soi và sửa state tại bất kỳ điểm nào | doc: `/oss/python/langgraph/interrupts` (cơ chế interrupt/resume); | 
| memory | Bộ nhớ ngắn hạn cho một mạch suy luận + bộ nhớ dài hạn xuyên nhiều phiên | doc: `/oss/python/concepts/memory` |
| Debug với LangSmith | Nhìn xuyên hành vi agent: đường thực thi, chuyển state, số liệu runtime | doc: `/langsmith/observability` |
| Deploy cho production | Hạ tầng co giãn cho workflow long-running, stateful | doc: `/langsmith/deployment` |

Ba dòng đầu là năng lực của bản thân LangGraph; hai dòng cuối thực ra thuộc LangSmith, chỉ ghép vào đây vì trang overview liệt kê chung. Khi tra cứu thì tách nguồn cho đúng.

---

## 5. Nên dùng LangGraph trực tiếp hay LangChain agents

Câu hỏi thực dụng cần trả lời trước khi bắt tay: chạm thẳng vào LangGraph, hay dùng `create_agent` của LangChain?

Dùng **LangChain agents** (`create_agent`) khi: mới bắt đầu với agent; muốn một abstraction high-level; luồng của ta khớp với kiến trúc dựng sẵn — vòng lặp model gọi tool tiêu chuẩn là đủ. Trang tài liệu nói thẳng: người mới bắt đầu hoặc muốn abstraction high-level thì nên dùng agents của LangChain.

Xuống thẳng **LangGraph** khi: cần tự vẽ luồng thay vì mượn vòng lặp dựng sẵn; cần trộn node deterministic với node do model quyết định; cần soi và đánh giá từng node; hoặc luồng không khớp bất kỳ kiến trúc dựng sẵn nào.

---

## Tham chiếu chéo

- [01-02 — Tư duy theo graph trong LangGraph](./01-02-thinking-in-langgraph.md) — mô hình node/edge/state mà mục 1 chỉ chạm nhẹ
- [01-03 — Workflow so với Agent](./01-03-workflows-vs-agents.md) — khi nào deterministic, khi nào giao model quyết (mục 2, mục 5)
- [03-08 — Human-in-the-loop](./03-08-human-in-the-loop.md) — cơ chế interrupt/resume của năng lực HITL (mục 4)
- LangChain agents (`create_agent`): `docs.langchain.com/oss/python/langchain/agents`
- Trang persistence: `docs.langchain.com/oss/python/langgraph/persistence`
- Trang interrupts (HITL): `docs.langchain.com/oss/python/langgraph/interrupts`