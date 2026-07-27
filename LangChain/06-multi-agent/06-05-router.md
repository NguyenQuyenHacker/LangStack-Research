---
title: Router
doc_source: https://docs.langchain.com/oss/python/langchain/multi-agent/router
accessed: 2026-07-25
lc_version: unknown
status: draft
lab:
related:
  - ./04-01-multi-agent-overview.md
  - ./04-02-subagents.md
  - ./04-03-handoffs.md
  - ./04-06-custom-workflow.md
---

# Router (`Command` / `Send` phân phối tới agent)

> Pattern trong đó một bước phân loại đầu vào rồi hướng nó tới các agent chuyên biệt. Hợp khi có nhiều **mảng chuyên biệt (vertical)** — các mảng kiến thức tách bạch, mỗi mảng cần một agent riêng.
> Router chỉ là bước phân loại; khác Subagents ở chỗ Subagents có một agent điều phối giữ ngữ cảnh qua nhiều lượt.
---


**[Router Tutorial](https://docs.langchain.com/oss/python/langchain/multi-agent/router-knowledge-base)**

## 1. Tổng quan

Luồng: đầu vào → **router** phân loại → một hoặc nhiều agent chuyên biệt chạy (song song được) → kết quả được **tổng hợp** thành một câu trả lời.

Ba đặc điểm: router bóc tách câu hỏi; không hoặc nhiều agent chuyên biệt được gọi song song; kết quả gộp thành một phản hồi mạch lạc.

Router phân loại rồi hướng đầu vào: dùng `Command` khi định tuyến tới **một** agent, dùng `Send` khi rẽ song song ra **nhiều** agent.

**Định tuyến tới một agent** (`Command`):

```python
def classify_query(query: str) -> str:                # dùng LLM phân loại, trả về tên agent cần chạy
    ...

def route_query(state: State) -> Command:
    active_agent = classify_query(state["query"])      # phân loại câu hỏi
    return Command(goto=active_agent)                  # goto = tên chặng/agent chạy tiếp
```

**Rẽ song song ra nhiều agent** (`Send`):

```python
class ClassificationResult(TypedDict):
    query: str
    agent: str

def classify_query(query: str) -> list[ClassificationResult]:   # phân loại → danh sách (agent, phần việc)
    ...

def route_query(state: State):
    classifications = classify_query(state["query"])
    return [
        Send(c["agent"], {"query": c["query"]})       # mỗi Send là một nhánh chạy song song, mang phần việc riêng
        for c in classifications
    ]
```

**Kết quả in ra** (dựng lại, cho nhánh song song):

```
# câu hỏi: "So sánh doanh thu quý của GitHub và Notion"
router → [Send("github_agent", {"query": "doanh thu quý GitHub"}),   ← rẽ hai nhánh, mỗi nhánh một mảng
          Send("notion_agent", {"query": "doanh thu quý Notion"})]   ← hai agent chạy đồng thời
github_agent → "GitHub: ..."                                         ← kết quả nhánh 1
notion_agent → "Notion: ..."                                         ← kết quả nhánh 2
synthesize   → "So sánh: ..."                                        ← bước tổng hợp gộp hai kết quả
```

`Command`, `Send`, `State` thuộc tài liệu LangGraph — ở đây chỉ dùng.

---

## 2. Khi nào dùng và phân biệt với Subagents

**Điều kiện sử dụng.** Dùng router khi có các mảng chuyên biệt tách bạch, cần hỏi nhiều nguồn song song, và muốn gộp kết quả thành một câu trả lời.

**Áp dụng thực tế.** Cổng tra cứu tài liệu nội bộ đọc từ ba nguồn — GitHub, Notion, Slack. Người dùng hỏi một câu chạm cả ba nguồn; router phân câu hỏi thành ba phần, gửi song song cho ba agent, rồi tổng hợp thành một câu trả lời duy nhất thay vì bắt người dùng tra ba chỗ.

**Phân biệt Router với Subagents.** Cả hai đều phân việc cho nhiều agent, khác ở cách ra quyết định định tuyến:

| | Router | Subagents (supervisor) |
|---|---|---|
| Bản chất bước định tuyến | Một bước phân loại (một lần gọi LLM hoặc luật), là bước tiền xử lý | Một agent điều phối đầy đủ |
| Giữ ngữ cảnh trò chuyện | Thường không | Có, qua nhiều lượt |
| Điều phối nhiều bước | Không | Có, quyết việc kế tiếp theo ngữ cảnh đang tiến triển |

Dùng **router** khi có nhóm đầu vào rõ ràng và muốn phân loại tất định hoặc nhẹ. Dùng **supervisor** (Subagents) khi cần điều phối linh động, có ý thức về hội thoại, để LLM tự quyết bước kế tiếp theo ngữ cảnh.

---

## 3. Router giữ trạng thái hay không

**Khái niệm.** Router không giữ trạng thái: mỗi yêu cầu định tuyến độc lập, không nhớ gì giữa các lần. Router giữ trạng thái: giữ lịch sử trò chuyện qua các yêu cầu.

**Vai trò.** Trò chuyện nhiều lượt cần nhớ ngữ cảnh, mà router thuần thì không nhớ — nên phải thêm cách giữ trạng thái.

### 3.1 Bọc router thành tool (cách gọn nhất)

**Khái niệm.** Bọc router không-trạng-thái thành một tool để một agent trò chuyện gọi.

**Vai trò.** Agent trò chuyện lo trí nhớ và ngữ cảnh; router giữ nguyên không trạng thái. Tránh được cái khó của việc quản lý lịch sử trò chuyện trên nhiều agent chạy song song.

**Triển khai.**

```python
@tool
def search_docs(query: str) -> str:
    """Search across multiple documentation sources."""
    result = workflow.invoke({"query": query})    # workflow chính là router không-trạng-thái, gọi như một khối
    return result["final_answer"]

conversational_agent = create_agent(
    model,
    tools=[search_docs],                          # agent trò chuyện cầm router như một tool bình thường
    prompt="You are a helpful assistant. Use search_docs to answer questions."
)
```

### 3.2 Cho chính router giữ trạng thái

**Khái niệm.** Nếu cần bản thân router nhớ, dùng cơ chế lưu trạng thái để giữ lịch sử tin nhắn. Khi định tuyến tới agent, lấy tin nhắn trước từ trạng thái và chọn lọc đưa vào ngữ cảnh agent — đây là đòn bẩy context engineering.

Cơ chế lưu trạng thái (persistence) thuộc file trí nhớ ngắn hạn ([xem 03-agent-harness](../03-agent-harness/), nếu có), ở đây chỉ nêu tên.

**!Note:** Router giữ trạng thái đòi tự quản lý lịch sử. Nếu router đổi agent qua các lượt, hội thoại có thể mất liền mạch khi các agent có giọng/prompt khác nhau. Với gọi song song, phải giữ lịch sử ở cấp router (đầu vào và kết quả đã tổng hợp) rồi dùng lịch sử đó trong logic định tuyến. Tài liệu khuyên cân nhắc [Handoffs](./04-03-handoffs.md) hoặc [Subagents](./04-02-subagents.md) thay thế — cả hai có ngữ nghĩa rõ hơn cho hội thoại nhiều lượt.

---

## Tham chiếu chéo

- [04-01 Tổng quan](./04-01-multi-agent-overview.md) — Router đối chiếu bốn pattern còn lại (chạy song song tốt, không giữ trạng thái)
- [04-02 Subagents](./04-02-subagents.md) — phân biệt router với supervisor
- [04-03 Handoffs](./04-03-handoffs.md) — phương án thay khi cần hội thoại nhiều lượt
- [04-06 Custom workflow](./04-06-custom-workflow.md) — router là một ví dụ của custom workflow
- `Command`, `Send`, `State`, persistence: tài liệu LangGraph — `docs.langchain.com/oss/python/langgraph/`