---
title: Subagents
doc_source: https://docs.langchain.com/oss/python/langchain/multi-agent/subagents
accessed: 2026-07-25
lc_version: unknown
status: draft
lab:
related:
  - ./04-01-multi-agent-overview.md
  - ./04-03-handoffs.md
  - ./04-05-router.md
---

# Subagents (`create_agent` lồng trong `@tool`)

> Pattern trong đó một agent chính — tài liệu gọi là **supervisor** (agent điều phối) — gọi các agent con như thể chúng là tool. Agent chính quyết gọi agent con nào, đưa đầu vào gì, ghép kết quả ra sao.
> Khác với [Router](./04-05-router.md) ở chỗ agent điều phối là một agent đầy đủ, giữ ngữ cảnh trò chuyện qua nhiều lượt; router chỉ là một bước phân loại rồi phân phối.

---

## 1. Tổng quan

Agent con **không giữ trạng thái** (stateless) — chúng không nhớ lần gọi trước; toàn bộ trí nhớ cuộc trò chuyện do **agent chính** giữ. Nhờ vậy có **cô lập ngữ cảnh**: mỗi lần gọi agent con chạy trong một cửa sổ ngữ cảnh sạch, không làm phình ngữ cảnh của cuộc trò chuyện chính.

Cơ chế lõi là bọc một agent con thành tool để agent chính gọi được:

```python
subagent = create_agent(model="google_genai:gemini-3.5-flash", tools=[...])   # agent con: một agent đầy đủ, có model và tool riêng

@tool("research", description="Research a topic and return findings")          # description là thứ agent chính đọc để quyết khi nào gọi
def call_research_agent(query: str):                                           # tham số query = phần việc agent chính giao xuống
    result = subagent.invoke({"messages": [{"role": "user", "content": query}]})  # gọi agent con, đóng gói query thành tin nhắn người dùng
    return result["messages"][-1].content                                     # chỉ trả về nội dung tin nhắn cuối — phần agent chính cần

main_agent = create_agent(model="google_genai:gemini-3.5-flash", tools=[call_research_agent])  # agent chính coi call_research_agent như một tool bình thường
```

**Kết quả in ra**:

```
# main_agent.invoke({"messages": [{"role": "user", "content": "Thời tiết Tokyo?"}]})
[HumanMessage]  "Thời tiết Tokyo?"                          ← đầu vào người dùng gửi agent chính
[AIMessage]     tool_calls=[research(query="Tokyo weather")] ← agent chính quyết gọi agent con "research"
[ToolMessage]   "Hiện 22°C, nắng"                           ← nội dung message cuối của agent con, trả ngược lên
[AIMessage]     "Tokyo đang 22°C và nắng."                  ← agent chính ghép kết quả thành câu trả lời cuối
```

---

## 2. Đặc điểm và khi nào dùng

**Khái niệm.** Điều khiển tập trung: mọi định tuyến đi qua agent chính. Agent con không nói trực tiếp với người dùng — chúng trả kết quả về agent chính. Agent con được gọi qua tool. Agent chính gọi được nhiều agent con trong một lượt (song song).

**Vai trò.** Dùng khi có nhiều mảng tách bạch (ví dụ: lịch, email, CRM, cơ sở dữ liệu), khi agent con không cần trò chuyện trực tiếp với người dùng, hoặc khi muốn điều khiển luồng tập trung. Vài tool đơn giản thì dùng agent đơn cho gọn.

**Áp dụng thực tế.** Trợ lý nội bộ của một công ty chứng khoán: agent chính nhận câu "tổng hợp tình hình khách hàng X". Nó gọi agent con `crm` lấy hồ sơ, agent con `database` lấy số dư tài khoản, agent con `email` lấy các trao đổi gần nhất — ba agent con chạy trong ngữ cảnh riêng, không agent con nào thấy hồ sơ của việc kia. Agent chính ghép ba kết quả thành một bản tóm tắt.

> Agent con thường trả kết quả về agent chính, nhưng vẫn cho người dùng xen vào giữa việc được: dùng **interrupt** (tín hiệu dừng) bên trong agent con để tạm dừng và hỏi thêm người dùng — ví dụ khi cần xác nhận trước khi tiếp tục.

---

## 3. Các quyết định thiết kế

Năm nhóm quyết định khi dựng pattern này. Bảng dưới định vị, chi tiết ở các mục sau.

| Quyết định | Các lựa chọn |
|---|---|
| Đồng bộ / bất đồng bộ | Đồng bộ (chờ) so với bất đồng bộ (chạy nền) |
| Cách lộ agent con thành tool | Một tool cho mỗi agent, hoặc một tool điều phối chung |
| Cho agent chính biết có agent con nào | Liệt kê trong prompt, ràng buộc enum, hoặc tìm qua tool |
| Đầu vào cho agent con | Chỉ câu hỏi, hoặc kèm đầy đủ ngữ cảnh |
| Đầu ra từ agent con | Chỉ kết quả agent con, hoặc kèm dữ liệu trạng thái khác |

---

## 4. Đồng bộ hay bất đồng bộ

**Khái niệm.** Đồng bộ: agent chính chờ agent con xong mới đi tiếp. Bất đồng bộ: agent chính khởi động một việc chạy nền rồi tiếp tục, không chờ.

**Vai trò.** Chọn theo việc agent chính có cần kết quả agent con để đi tiếp hay không.

| Chế độ | Hành vi agent chính | Hợp khi | Đánh đổi |
|---|---|---|---|
| Đồng bộ | Chờ agent con xong | Cần kết quả để đi tiếp | Đơn giản, nhưng chặn cuộc trò chuyện |
| Bất đồng bộ | Chạy tiếp trong khi agent con chạy nền | Việc độc lập, người dùng không nên phải chờ | Phản hồi nhanh, nhưng phức tạp hơn |

> Đây **không phải** `async`/`await` của Python. "Bất đồng bộ" ở đây nghĩa là agent chính khởi động một việc nền (thường ở tiến trình hoặc dịch vụ riêng) rồi chạy tiếp mà không bị chặn.

**Đồng bộ (mặc định).** Mặc định agent con gọi đồng bộ. Dùng khi hành động kế tiếp của agent chính phụ thuộc kết quả agent con, khi các việc có ràng buộc thứ tự (lấy dữ liệu → phân tích → trả lời), hoặc khi agent con lỗi thì nên chặn luôn câu trả lời. Đổi lại: người dùng không thấy phản hồi nào cho tới khi mọi agent con xong; việc chạy lâu làm đứng cuộc trò chuyện.

**Bất đồng bộ.** Dùng khi việc của agent con độc lập với mạch trò chuyện — agent chính không cần kết quả để tiếp tục nói chuyện với người dùng. Agent chính khởi động việc nền và vẫn phản hồi được.

**Áp dụng thực tế.** Agent nhận yêu cầu "rà hợp đồng M&A 150 trang". Nó khởi động agent con `legal_reviewer` chạy nền, nhận về một mã việc `job_123`, rồi báo người dùng "Đã bắt đầu rà (job_123)". Người dùng hỏi tiếp "xong chưa?" thì agent chính tra trạng thái theo mã việc. Rà xong, agent chính lấy kết quả và trả về.

Cách dựng bất đồng bộ theo tài liệu gồm ba tool: một tool khởi động việc (trả mã việc), một tool tra trạng thái (pending/running/completed/failed), một tool lấy kết quả khi xong. Khi việc hoàn tất, ứng dụng cần tự báo người dùng — ví dụ hiện một thông báo mà khi bấm sẽ gửi một tin nhắn kiểu "Kiểm tra job_123 và tóm tắt kết quả".

---

## 5. Lộ agent con thành tool — theo từng agent hay một tool điều phối chung

| Cách | Hợp khi | Đánh đổi |
|---|---|---|
| Một tool cho mỗi agent | Cần chỉnh chi tiết đầu vào/đầu ra từng agent con | Dựng nhiều hơn, đổi lại tùy biến được nhiều |
| Một tool điều phối chung | Nhiều agent, nhiều nhóm phát triển, ưu tiên quy ước hơn cấu hình | Ghép gọn hơn, đổi lại ít tùy biến từng agent |

### 5.1 Một tool cho mỗi agent

**Khái niệm.** Mỗi agent con được bọc thành một tool riêng, có tên và mô tả riêng.

**Vai trò.** Agent chính gọi tool của agent con khi thấy việc khớp với mô tả tool đó, nhận kết quả, rồi điều phối tiếp. Cách này cho quyền chỉnh từng agent con một.

**Triển khai.**

```python
subagent = create_agent(model="...", tools=[...])              # một agent con

@tool("subagent_name", description="subagent_description")     # tên + mô tả là "cần câu" để agent chính chọn đúng tool
def call_subagent(query: str):
    result = subagent.invoke({"messages": [{"role": "user", "content": query}]})  # đóng gói query thành tin nhắn, gọi agent con
    return result["messages"][-1].content                      # trả về nội dung message cuối

main_agent = create_agent(model="...", tools=[call_subagent])  # agent chính cầm tool này như mọi tool khác
```

### 5.2 Một tool điều phối chung (`task`)

**Khái niệm.** Thay vì mỗi agent con một tool, dùng **một** tool `task` có tham số. Tên agent được truyền vào; phần việc được truyền như tin nhắn người dùng gửi cho agent con; message cuối của agent con trả về làm kết quả tool.

**Vai trò.** Dùng khi muốn chia việc phát triển agent cho nhiều nhóm, cần cô lập việc phức tạp sang cửa sổ ngữ cảnh riêng, cần thêm agent mới mà không phải sửa bộ điều phối, hoặc thích quy ước hơn tùy biến. Đổi sự linh động trong context engineering lấy sự gọn khi ghép agent và cô lập ngữ cảnh mạnh.

**Triển khai.**

```python
research_agent = create_agent(model="gpt-5.4", prompt="You are a research specialist...")   # agent con do nhóm A dựng
writer_agent   = create_agent(model="gpt-5.4", prompt="You are a writing specialist...")     # agent con do nhóm B dựng

SUBAGENTS = {"research": research_agent, "writer": writer_agent}   # sổ đăng ký: tên → agent con

@tool
def task(agent_name: str, description: str) -> str:               # một tool duy nhất, chọn agent con qua agent_name
    """Launch an ephemeral subagent for a task.
    Available agents:
    - research: Research and fact-finding
    - writer: Content creation and editing
    """                                                           # docstring này chính là chỗ liệt kê agent cho model đọc
    agent = SUBAGENTS[agent_name]                                 # tra agent con theo tên
    result = agent.invoke({"messages": [{"role": "user", "content": description}]})  # description trở thành tin nhắn người dùng
    return result["messages"][-1].content

main_agent = create_agent(
    model="gpt-5.4",
    tools=[task],                                                 # agent chính chỉ cầm đúng một tool điều phối
    system_prompt=("You coordinate specialized sub-agents. "
                   "Available: research (fact-finding), writer (content creation). "
                   "Use the task tool to delegate work."),
)
```

> Điểm đáng chú ý của cách này: agent con có thể có **đúng năng lực** như agent chính. Khi đó việc gọi agent con thực chất chỉ để **cô lập ngữ cảnh** — cho việc nhiều bước chạy trong cửa sổ riêng, không làm phình lịch sử của agent chính; xong việc, agent con trả về đúng một bản tóm tắt gọn.

**!Note:** Với `SUBAGENTS[agent_name]`, nếu model gọi `task` với `agent_name` không có trong sổ đăng ký thì code văng `KeyError`. Tài liệu không xử lý trường hợp này — cần tự thêm kiểm tra tên hợp lệ.

---

## 6. Cho agent chính biết có agent con nào

**Khái niệm.** Tên và mô tả của agent con là cách chính để agent chính biết khi nào gọi ai. Đây là đòn bẩy prompt — chọn kỹ.

- **Tên**: cách agent chính gọi agent con. Rõ ràng, thiên về hành động (`research_agent`, `code_reviewer`).
- **Mô tả**: agent chính biết gì về năng lực agent con. Nêu cụ thể agent con xử lý việc gì và khi nào nên dùng.

Riêng với [một tool điều phối chung](#52-một-tool-điều-phối-chung-task), phải cho agent chính biết thêm danh sách agent con gọi được. Ba cách:

| Cách | Hợp khi | Đánh đổi |
|---|---|---|
| Liệt kê trong system prompt | Danh sách nhỏ, cố định (< 10 agent) | Đơn giản, nhưng đổi agent thì phải sửa prompt |
| Ràng buộc enum trên tham số | Danh sách nhỏ, cố định (< 10 agent) | An toàn kiểu, rõ ràng, nhưng đổi agent thì phải sửa code |
| Tìm qua tool | Sổ đăng ký lớn hoặc đổi động | Linh động, mở rộng tốt, nhưng thêm phức tạp |

### 6.1 Liệt kê trong system prompt

Ghi thẳng danh sách agent vào system prompt của agent chính.

```python
main_agent = create_agent(
    model="...",
    tools=[task],
    system_prompt=("You coordinate specialized sub-agents. "
                   "Available agents:\n"
                   "- research: Research and fact-finding\n"      # mỗi dòng là một agent con + mô tả
                   "- writer: Content creation and editing\n"
                   "- reviewer: Code and document review\n"
                   "Use the task tool to delegate work."),
)
```

### 6.2 Ràng buộc enum trên tham số `agent_name`

Ép `agent_name` chỉ nhận các giá trị định sẵn. Cho an toàn kiểu và làm danh sách agent hiện rõ trong lược đồ tool.

```python
from enum import Enum

class AgentName(str, Enum):        # liệt kê agent hợp lệ dưới dạng enum
    RESEARCH = "research"
    WRITER = "writer"
    REVIEWER = "reviewer"

@tool
def task(agent_name: AgentName, description: str) -> str:   # agent_name kiểu AgentName → chỉ nhận giá trị trong enum
    """Launch an ephemeral subagent for a task."""
    # ...
```

### 6.3 Tìm agent qua tool

Cung cấp một tool riêng (ví dụ `list_agents`) để agent chính tự tra danh sách agent khi cần. Đây là **hé lộ dần** — chỉ nạp thông tin agent lúc cần, giữ prompt gọn; hợp với sổ đăng ký lớn (> 10 agent) hoặc đổi động.

```python
@tool
def list_agents(query: str = "") -> str:                    # tool để agent chính tra danh sách khi cần
    """List available subagents, optionally filtered by query."""
    agents = search_agent_registry(query)                   # tra sổ đăng ký (đổi động được)
    return format_agent_list(agents)

@tool
def task(agent_name: str, description: str) -> str:
    """Launch an ephemeral subagent for a task."""
    # ...

main_agent = create_agent(
    model="...",
    tools=[task, list_agents],                              # agent chính cầm cả hai: tra danh sách rồi mới gọi
    system_prompt="Use list_agents to discover available subagents, then use task to invoke them."
)
```

---

## 7. Đầu vào cho agent con

**Khái niệm.** Chỉnh ngữ cảnh mà agent con nhận để làm việc. Thêm được đầu vào khó nhét vào prompt tĩnh — toàn bộ lịch sử tin nhắn, kết quả trước đó, hay dữ liệu kèm việc — bằng cách lấy từ trạng thái của agent.

**Vai trò.** Đôi khi agent con cần hơn một câu query để làm tốt; nó cần thấy đoạn hội thoại trước hoặc một kết quả đã có.

**Triển khai.**

```python
class CustomState(AgentState):        # mở rộng trạng thái để mang thêm khóa dữ liệu riêng
    example_state_key: str

@tool("subagent1_name", description="subagent1_description")
def call_subagent1(query: str, runtime: ToolRuntime[None, CustomState]):   # runtime cho phép đọc trạng thái hiện tại
    subagent_input = some_logic(query, runtime.state["messages"])          # trộn query với lịch sử tin nhắn thành đầu vào phù hợp
    result = subagent1.invoke({
        "messages": subagent_input,
        "example_state_key": runtime.state["example_state_key"]            # truyền thêm khóa trạng thái — phải khai báo ở cả hai lược đồ
    })
    return result["messages"][-1].content
```

`ToolRuntime` và `AgentState` thuộc tầng tool/agent, đã mô tả ở file tool ([03-02](../03-agent-harness/03-02-tools.md)) — ở đây chỉ dùng lại.

**!Note:** Khóa `example_state_key` phải được khai báo trong lược đồ trạng thái của **cả** agent chính lẫn agent con. Khai báo thiếu một bên → khóa không truyền qua được, agent con nhận thiếu dữ liệu mà không báo lỗi.

---

## 8. Đầu ra từ agent con

**Khái niệm.** Chỉnh thứ agent chính nhận về để ra quyết định tốt. Hai hướng: (1) prompt agent con nêu rõ phải trả về gì; (2) định dạng lại trong code trước khi trả.

**Vai trò.** Một lỗi thường gặp: agent con gọi tool hoặc suy luận nhiều nhưng không đưa kết quả vào message cuối — mà agent chính chỉ thấy message cuối. Nhắc agent con điều này trong prompt là cách sửa đơn giản nhất.

**Triển khai** (hướng định dạng trong code — trả thêm dữ liệu trạng thái kèm text cuối):

```python
@tool("subagent1_name", description="subagent1_description")
def call_subagent1(query: str, tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:  # trả về Command để cập nhật cả trạng thái
    result = subagent1.invoke({"messages": [{"role": "user", "content": query}]})
    return Command(update={
        "example_state_key": result["example_state_key"],     # đẩy thêm khóa trạng thái từ agent con lên agent chính
        "messages": [
            ToolMessage(
                content=result["messages"][-1].content,       # text cuối của agent con
                tool_call_id=tool_call_id                     # gắn đúng id để khớp cặp gọi–đáp của tool
            )
        ]
    })
```

`Command` (cập nhật trạng thái đồ thị) thuộc tài liệu LangGraph — ở đây chỉ dùng, không giải thích cơ chế.

---

## 9. Nơi lưu trạng thái và việc đọc trạng thái lồng nhau

Mặc định agent con dùng chế độ **kế thừa nơi lưu trạng thái (checkpointer)** — mỗi lần gọi bắt đầu với trạng thái mới, hỗ trợ interrupt, và chạy song song an toàn. Nếu cần agent con giữ lịch sử trò chuyện riêng qua nhiều lần gọi thì dựng nó với `checkpointer=True` (chế độ continuations).

Vì agent con được gọi bên trong hàm tool, LangGraph không phát hiện tĩnh chúng được. Hệ quả: `get_state` với `subgraphs` sẽ không trả trạng thái agent con. Cần đọc trạng thái đồ thị lồng (ví dụ trong lúc interrupt) thì phải gọi agent con từ một hàm chặng trong đồ thị tùy biến thay vì từ tool.

> Chi tiết các chế độ lưu trạng thái, cách chúng ảnh hưởng tới việc thấy trạng thái con, đều nằm ở trang **subgraph persistence** của LangGraph. Nếu ứng dụng chỉ gọi agent con qua tool và không cần đọc trạng thái lồng thì **bỏ qua mục này hoàn toàn** — đây là phần cho trường hợp đặc biệt.

---

## Tham chiếu chéo

- [04-01 Tổng quan](./04-01-multi-agent-overview.md) — Subagents đối chiếu với bốn pattern còn lại
- [04-05 Router](./04-05-router.md) — phân biệt supervisor với router (mục "Router vs Subagents")
- [04-03 Handoffs](./04-03-handoffs.md) — cách chuyển quyền có giữ trạng thái
- Tool, `ToolRuntime`, `AgentState`: [03-02](../03-agent-harness/03-02-tools.md)
- `Command`, `get_state`, interrupt, subgraph persistence: tài liệu LangGraph — `docs.langchain.com/oss/python/langgraph/`
- Deep Agents (built-in subagent): `docs.langchain.com/oss/python/deepagents/subagents`