---
title: Custom workflow
doc_source: https://docs.langchain.com/oss/python/langchain/multi-agent/custom-workflow
accessed: 2026-07-25
lc_version: unknown
status: draft
lab:
related:
  - ./04-01-multi-agent-overview.md
  - ./04-05-router.md
---

# Custom workflow (`StateGraph` tự dựng)

> Pattern trong đó bạn tự định nghĩa luồng chạy riêng bằng LangGraph, toàn quyền với cấu trúc đồ thị: bước tuần tự, rẽ nhánh có điều kiện, vòng lặp, chạy song song.
> Là pattern "thoát hiểm" khi bốn pattern chuẩn (Subagents, Handoffs, Skills, Router) không vừa — [Router](./04-05-router.md) chính là một ví dụ của custom workflow.

---

## 1. Tổng quan

Mỗi chặng trong luồng có thể là: một hàm thường, một lần gọi LLM, hoặc cả một agent đầy đủ có tool. Nhúng cả kiến trúc khác vào làm một chặng cũng được — ví dụ đặt cả một hệ multi-agent làm một chặng đơn.

Điểm cốt lõi: gọi thẳng một agent LangChain bên trong bất kỳ chặng LangGraph nào, ghép sự linh động của luồng tự dựng với sự tiện của agent dựng sẵn:

```python
agent = create_agent(model="openai:gpt-5.5", tools=[...])   # một agent dựng sẵn

def agent_node(state: State) -> dict:                       # một chặng LangGraph bọc lời gọi agent
    """A LangGraph node that invokes a LangChain agent."""
    result = agent.invoke({"messages": [{"role": "user", "content": state["query"]}]})  # lấy query từ trạng thái, gọi agent
    return {"answer": result["messages"][-1].content}       # ghi kết quả trở lại trạng thái, khóa "answer"

workflow = (
    StateGraph(State)
    .add_node("agent", agent_node)                          # đăng ký chặng
    .add_edge(START, "agent")                               # START → agent
    .add_edge("agent", END)                                 # agent → END
    .compile()                                              # dựng đồ thị thành thứ chạy được
)
```

**Kết quả in ra** (dựng lại):

```
# workflow.invoke({"query": "Ai vô địch WNBA 2024?"})
{"query": "...", "answer": "New York Liberty vô địch WNBA 2024..."}   ← trạng thái cuối, khóa answer do agent_node ghi vào
```

`StateGraph`, `START`, `END`, `add_node`, `add_edge`, `.compile()` thuộc tài liệu LangGraph — ở đây chỉ dùng, cơ chế đồ thị nằm ở trang LangGraph.

---

## 2. Đặc điểm và khi nào dùng

**Khái niệm.** Toàn quyền với cấu trúc đồ thị. Trộn logic tất định với hành vi agentic. Hỗ trợ tuần tự, rẽ nhánh có điều kiện, vòng lặp, song song. Nhúng pattern khác làm chặng.

**Vai trò.** Dùng khi các pattern chuẩn không vừa yêu cầu, khi cần trộn logic tất định với agentic, hoặc khi bài toán cần định tuyến phức tạp / xử lý nhiều giai đoạn.

**Áp dụng thực tế.** Một luồng hỏi đáp có bước cứng và bước mềm xen kẽ: viết lại câu hỏi (gọi model) → truy hồi tài liệu (tất định, không LLM) → agent suy luận trên tài liệu và gọi thêm tool nếu cần. Bước truy hồi là tìm kiếm vector thuần, không nên để LLM quyết; bước cuối cần agent linh động — custom workflow cho ghép đúng loại chặng vào đúng chỗ.

---

## 3. Ví dụ: luồng RAG ba loại chặng

**Khái niệm.** Luồng trợ lý thống kê WNBA gồm ba loại chặng khác nhau về bản chất:

- **Chặng model** (Rewrite): viết lại câu hỏi người dùng cho truy hồi tốt hơn, dùng structured output.
- **Chặng tất định** (Retrieve): tìm kiếm tương đồng vector — không có LLM.
- **Chặng agent** (Agent): suy luận trên tài liệu đã lấy, gọi thêm tool để lấy thông tin bổ sung.

**Vai trò.** Cho thấy ba loại chặng cùng nằm trong một đồ thị và truyền dữ liệu qua nhau bằng trạng thái LangGraph — mỗi chặng đọc và ghi các khóa có cấu trúc trong `State`.

**Triển khai.**

```python
class State(TypedDict):            # trạng thái mang dữ liệu chảy qua các chặng
    question: str
    rewritten_query: str
    documents: list[str]
    answer: str

# ... dựng vector_store, thêm dữ liệu, tạo retriever (thuộc tầng truy hồi, xem file retrieval) ...

@tool
def get_latest_news(query: str) -> str:                 # tool để chặng agent lấy tin mới nếu cần
    """Get the latest WNBA news and updates."""
    return "Latest: ..."

agent = create_agent(model="openai:gpt-5.5", tools=[get_latest_news])   # agent cho chặng cuối
model = ChatOpenAI(model="gpt-5.5")                                     # model trần cho chặng viết lại

class RewrittenQuery(BaseModel):    # lược đồ structured output cho câu hỏi đã viết lại
    query: str

def rewrite_query(state: State) -> dict:                # CHẶNG MODEL
    system_prompt = """Rewrite this query to retrieve relevant WNBA information..."""
    response = model.with_structured_output(RewrittenQuery).invoke([   # ép model trả đúng cấu trúc RewrittenQuery
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": state["question"]}
    ])
    return {"rewritten_query": response.query}          # ghi câu đã viết lại vào trạng thái

def retrieve(state: State) -> dict:                     # CHẶNG TẤT ĐỊNH — không LLM
    docs = retriever.invoke(state["rewritten_query"])   # tìm vector theo câu đã viết lại
    return {"documents": [doc.page_content for doc in docs]}

def call_agent(state: State) -> dict:                   # CHẶNG AGENT
    context = "\n\n".join(state["documents"])           # ghép tài liệu đã lấy thành ngữ cảnh
    prompt = f"Context:\n{context}\n\nQuestion: {state['question']}"
    response = agent.invoke({"messages": [{"role": "user", "content": prompt}]})
    return {"answer": response["messages"][-1].content_blocks}

workflow = (
    StateGraph(State)
    .add_node("rewrite", rewrite_query)                 # nối ba chặng thành chuỗi tuần tự
    .add_node("retrieve", retrieve)
    .add_node("agent", call_agent)
    .add_edge(START, "rewrite")
    .add_edge("rewrite", "retrieve")
    .add_edge("retrieve", "agent")
    .add_edge("agent", END)
    .compile()
)

result = workflow.invoke({"question": "Who won the 2024 WNBA Championship?"})
print(result["answer"])
```

**Kết quả in ra** (dựng lại):

```
rewrite  → rewritten_query = "New York Liberty 2024 WNBA Finals championship"  ← model chuẩn hóa câu hỏi cho dễ truy hồi
retrieve → documents = ["2024 WNBA Finals: New York Liberty defeated ..."]     ← vector tìm ra tài liệu khớp
agent    → answer = "New York Liberty vô địch WNBA 2024, thắng Minnesota Lynx 3-2." ← agent suy luận trên tài liệu
```

**!Note:** Trong `call_agent`, tài liệu ghi kết quả bằng `response["messages"][-1].content_blocks` nhưng hàm gán vào khóa `answer` rồi `print(result["answer"])`. Các chặng khác dùng `.content` (chuỗi text), riêng chặng này dùng `.content_blocks` (danh sách khối). Điểm này chưa nhất quán trong tài liệu — khi chạy thật cần đối chiếu xem `answer` là chuỗi hay danh sách khối, `print` ra hai dạng khác nhau.

**!Note:** Phần dựng `vector_store`, `retriever`, `embeddings` thuộc tầng truy hồi (retrieval), không phải trọng tâm trang này. Cơ chế truy hồi nằm ở file retrieval, ở đây chỉ dùng để minh họa một chặng tất định.

---

## Tham chiếu chéo

- [04-01 Tổng quan](./04-01-multi-agent-overview.md) — custom workflow là pattern nền, nhúng được các pattern khác
- [04-05 Router](./04-05-router.md) — một ví dụ cụ thể của custom workflow
- Retrieval / RAG: file retrieval của kho (mục 05, đang hoàn thiện)
- `StateGraph`, `START`, `END`, `add_node`, `add_edge`, structured output nền đồ thị: tài liệu LangGraph — `docs.langchain.com/oss/python/langgraph/`
- Agent, `create_agent`: [03-agent-harness](../03-agent-harness/)