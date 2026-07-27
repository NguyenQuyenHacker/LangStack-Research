---
title: Handoffs
doc_source: https://docs.langchain.com/oss/python/langchain/multi-agent/handoffs
accessed: 2026-07-25
lc_version: unknown
status: draft
lab: ../labs/lab-04-multi-agent-handoff/
related:
  - ./04-01-multi-agent-overview.md
  - ./04-02-subagents.md
  - ./04-05-router.md
---

# Handoffs (`Command` cập nhật biến trạng thái)

> Pattern để **chuyển giao quyền điều khiển** trong một cuộc trò chuyện — chuyển sang agent khác, hoặc cho chính agent đang chạy đổi sang giai đoạn khác. Điểm chốt: các agent ngang hàng, không có agent chính điều phối như [Subagents](./04-02-subagents.md).
> Từ **handoffs** do [OpenAI](https://openai.github.io/openai-agents-python/handoffs/) đặt, chỉ việc dùng một lệnh gọi tool (kiểu `transfer_to_sales_agent`) để trao quyền giữa các agent hoặc giữa các trạng thái.

---
**[Handoffs Tutorial](https://docs.langchain.com/oss/python/langchain/multi-agent/handoffs-customer-support)**

## 1. Tổng quan

Hình dung một tổng đài. Chuyên viên trực máy tiếp bạn trước, thấy câu hỏi lệch mảng thì **chuyển máy** cho chuyên viên phù hợp — bạn vẫn nói chuyện liền mạch, chỉ là người tiếp đã đổi. Handoff là đúng động tác "chuyển máy" đó, nhưng giữa các agent.

Cơ chế thật ra rất gọn, xoay quanh **một biến trạng thái**:

- Có một biến ghi *đang ở giai đoạn nào* hoặc *đang đến lượt agent nào* — tài liệu đặt tên `current_step` hoặc `active_agent`.
- Agent có những tool đặc biệt **không làm việc nghiệp vụ, chỉ để chuyển quyền**. Khi tool đó chạy, nó **đổi giá trị biến** này.
- Ở mỗi lần gọi model tiếp theo, hệ **đọc biến** để quyết dùng cấu hình nào / cho agent nào tiếp lời.
- Biến này được **lưu lại qua các lượt**, nên cuộc trò chuyện luôn nhớ nó đang ở đâu.

Nói ngắn: biến trạng thái là **phương tiện để chuyển**, không phải cái khung cố định mà việc chuyển diễn ra bên trong. Trình tự là: *gọi tool chuyển quyền → biến đổi giá trị → hệ đọc biến → agent/giai đoạn tương ứng tiếp nhận.*

Đây là tool chuyển quyền tối giản — nó chỉ trả về một `Command` để đổi biến:

```python
@tool
def transfer_to_specialist(runtime) -> Command:                 # tool "chuyển quyền": không làm nghiệp vụ, chỉ đổi trạng thái
    """Transfer to the specialist agent."""
    return Command(
        update={
            "messages": [
                ToolMessage(
                    content="Transferred to specialist",
                    tool_call_id=runtime.tool_call_id            # id khớp với lệnh gọi tool, để đóng cặp gọi–đáp
                )
            ],
            "current_step": "specialist"                        # đổi biến trạng thái → kích hoạt đổi hành vi
        }
    )
```

**Kết quả in ra** (dựng lại):

```
# trạng thái trước:  current_step = "triage"
[AIMessage]   tool_calls=[transfer_to_specialist()]   ← agent quyết chuyển quyền
[ToolMessage] "Transferred to specialist"             ← đáp cho lệnh gọi tool, đóng cặp
# trạng thái sau:   current_step = "specialist"       ← biến đã đổi, lượt sau hệ đọc biến này để đổi hành vi
```

**Vì sao phải kèm `ToolMessage`?** Khi model gọi một tool, nó **chờ một câu trả lời cho lệnh gọi đó**. `ToolMessage` có `tool_call_id` khớp chính là câu trả lời khép lại cặp gọi–đáp; thiếu nó thì lịch sử trò chuyện thành dị dạng. Bắt buộc mỗi khi tool chuyển quyền có cập nhật `messages`.

`Command` và `ToolMessage` thuộc tài liệu LangGraph — ở đây chỉ dùng.

---

## 2. Hai kiểu handoff

Cùng tên "handoffs" nhưng tài liệu gộp **hai kiểu** khác nhau. Nắm rõ khác biệt này trước khi đọc code:

| | Kiểu A — một agent tự đổi vai | Kiểu B — nhiều agent trao quyền cho nhau |
|---|---|---|
| Có mấy agent | Một | Nhiều, tách rời, mỗi agent một nghiệp vụ |
| Khi chuyển thì đổi gì | Chính agent đó đổi prompt + bộ tool | Chuyển hẳn sang agent khác tiếp lời |
| Biến trạng thái | `current_step` (đang ở bước nào) | `active_agent` (đang đến lượt agent nào) |
| Cách dựng | Một agent + middleware | Nhiều agent thành các chặng trong một đồ thị |
| Độ phức tạp | Đơn giản hơn | Phức tạp hơn |

Ví dụ để phân biệt: một nhân viên tổng đài **tự đổi vai** — lúc đầu chỉ hỏi thông tin, sau mới tư vấn — là kiểu A. Nhân viên đó **chuyển máy** sang một chuyên viên khác là kiểu B.

Tài liệu khuyên: **dùng kiểu A cho phần lớn tình huống** vì đơn giản. Chỉ dùng kiểu B khi mỗi agent cần cài đặt riêng phức tạp — ví dụ một agent bản thân đã là cả một quy trình nhiều bước (có bước phản tư, truy hồi...).

Chi tiết từng kiểu ở mục 4 và mục 5.

---

## 3. Khi nào dùng handoffs

**Điều kiện**: 
Hands sử dụng tốt nhất trong 3 trường hợp sau:
1. Cần ép thứ tự. Chỉ mở khóa năng lực sau khi đã thỏa điều kiện trước đó. Ví dụ: phải thẩm định tư cách khách xong mới cho tư vấn cơ cấu; phải lấy mã bảo hành xong mới cho xử lý hoàn tiền.

2. Agent cần trò chuyện thẳng với người dùng qua nhiều giai đoạn. Người dùng nói chuyện liên tục, còn agent tự đổi vai (hoặc trao cho agent khác) giữa chừng mà mạch hội thoại vẫn liền.

3. Dựng luồng hội thoại nhiều bước. Cuộc trò chuyện đi qua các giai đoạn nối tiếp, mỗi giai đoạn một nhiệm vụ.

**Áp dụng thực tế.** Chatbot tư vấn phát hành trái phiếu. Khách nhắn "tôi muốn phát hành trái phiếu". Chatbot **không** tư vấn phương án ngay. Ở giai đoạn đầu (`triage`) nó chỉ có tool hỏi tư cách: riêng lẻ hay ra công chúng, đã có báo cáo tài chính kiểm toán chưa. Khách trả lời xong, tool ghi nhận thông tin và đổi biến sang giai đoạn `specialist`; lúc này chatbot mới mở khóa khả năng tư vấn cơ cấu giao dịch, đề xuất tài sản bảo đảm. Khách **không thể** đòi tư vấn phương án khi chưa qua bước thẩm định tư cách — đúng như quy trình thật, chưa thẩm định khách thì chưa bàn cơ cấu.

---

## 4. Kiểu A — một agent tự đổi cấu hình (middleware)

**Khái niệm.** Chỉ có một agent. Nó không chuyển sang agent nào; nó **tự đổi prompt và bộ tool của chính mình** theo biến trạng thái. Cái quyết định đổi ra sao là một lớp trung gian gọi là **middleware**.

Middleware là lớp chen giữa agent và model, chặn mỗi lần agent chuẩn bị gọi model để chỉnh cấu hình. Cơ chế đầy đủ của middleware nằm ở file [03-03](../03-agent-harness/03-03-middleware-overview.md); ở đây chỉ cần biết nó dùng hook `wrap_model_call` để sửa prompt và tool ngay trước khi gọi model.

**Vai trò.** Vì chỉ có một agent, lịch sử tin nhắn chảy tự nhiên, không phải tự tay quyết tin nhắn nào truyền đi — nên gọn hơn kiểu B nhiều.

**Triển khai** (ví dụ đầy đủ — chăm sóc khách hàng):

```python
class SupportState(AgentState):        # trạng thái mang bước hiện tại + dữ liệu thu được
    current_step: str = "triage"       # bắt đầu ở bước phân loại
    warranty_status: str | None = None

@tool
def record_warranty_status(status: str, runtime: ToolRuntime[None, SupportState]) -> Command:  # vừa ghi dữ liệu vừa chuyển bước
    """Record warranty status and transition to next step."""
    return Command(update={
        "messages": [ToolMessage(content=f"Warranty status recorded: {status}",
                                 tool_call_id=runtime.tool_call_id)],   # đóng cặp gọi–đáp
        "warranty_status": status,                                      # lưu dữ liệu nghiệp vụ
        "current_step": "specialist"                                    # chuyển bước
    })

@wrap_model_call                                                        # hook chặn ngay trước mỗi lần gọi model
def apply_step_config(request: ModelRequest, handler) -> ModelResponse:
    step = request.state.get("current_step", "triage")                 # đọc bước hiện tại từ trạng thái
    configs = {
        "triage":     {"prompt": "Collect warranty information...",     # mỗi bước một prompt + một bộ tool riêng
                       "tools": [record_warranty_status]},
        "specialist": {"prompt": "Provide solutions based on warranty: {warranty_status}",
                       "tools": [provide_solution, escalate]},
    }
    config = configs[step]
    request = request.override(                                         # ghi đè cấu hình cho đúng lần gọi model này
        system_prompt=config["prompt"].format(**request.state),        # nhét dữ liệu trạng thái vào prompt
        tools=config["tools"]
    )
    return handler(request)                                            # gọi tiếp với cấu hình đã chỉnh

agent = create_agent(
    model,
    tools=[record_warranty_status, provide_solution, escalate],        # khai báo đủ mọi tool có thể dùng ở mọi bước
    state_schema=SupportState,
    middleware=[apply_step_config],
    checkpointer=InMemorySaver()                                       # lưu trạng thái qua các lượt — bắt buộc để current_step còn lại
)
```

Đọc code trên theo ba mảnh: (1) `record_warranty_status` là tool chuyển bước — ghi dữ liệu xong thì đổi `current_step`➜ (2) `apply_step_config` là middleware — trước mỗi lần gọi model, nó đọc `current_step` rồi thay prompt và tool cho khớp bước đó ➜ (3) `create_agent` ráp cả hai lại, kèm `checkpointer` để biến sống qua các lượt.

**Kết quả in ra** (dựng lại):

```
# bước triage: chỉ có record_warranty_status
[user]      "Tôi muốn hoàn tiền"
[AIMessage] "Cho tôi xin mã bảo hành trước đã."                  ← prompt bước triage lái model đi thu thông tin, chưa lộ tool hoàn tiền
[user]      "Mã WR-1023, còn hạn"
[AIMessage] tool_calls=[record_warranty_status(status="valid")]  ← ghi nhận rồi chuyển bước
[ToolMessage] "Warranty status recorded: valid"
# current_step → "specialist": lần gọi model kế đọc prompt+tool của bước specialist
[AIMessage] "Bảo hành còn hạn. Tôi xử lý hoàn tiền cho bạn."     ← giờ mới có tool provide_solution/escalate
```

**!Note:** `checkpointer` là bắt buộc ở kiểu này. Không có nó, `current_step` không sống qua lượt — mỗi lượt lại về `triage`, agent chạy trơn tru nhưng mãi không chuyển bước. Lỗi im lặng — code chạy nhưng sai.

**!Note:** `wrap_model_call`, `ModelRequest`, `ModelResponse` là cơ chế middleware, thuộc file [03-03](../03-agent-harness/03-03-middleware-overview.md). Đường dẫn import chính xác cần đối chiếu file đó, không suy từ trang này.

---

## 5. Kiểu B — nhiều agent trao quyền cho nhau

**Khái niệm.** Nhiều agent tách rời, mỗi agent là một **chặng** riêng trong một đồ thị. Tool chuyển quyền đi từ chặng này sang chặng kia bằng `Command.PARENT`, chỉ đích danh chặng chạy tiếp.

**Vai trò.** Cần khi mỗi agent là một cài đặt riêng phức tạp. Đổi lại, phải **tự tay quyết tin nhắn nào truyền qua** cho agent nhận — sai chỗ này thì agent nhận thấy lịch sử trò chuyện dị dạng hoặc ngữ cảnh phình to.

**Triển khai** (tool chuyển từ agent hiện tại sang agent sales):

```python
@tool
def transfer_to_sales(runtime: ToolRuntime) -> Command:
    """Transfer to the sales agent."""
    last_ai_message = next(                                          # lấy AIMessage gần nhất — chính là message chứa lệnh gọi chuyển quyền
        msg for msg in reversed(runtime.state["messages"]) if isinstance(msg, AIMessage)
    )
    transfer_message = ToolMessage(                                 # đáp nhân tạo cho lệnh gọi tool, để đóng cặp
        content="Transferred to sales agent", tool_call_id=runtime.tool_call_id,
    )
    return Command(
        goto="sales_agent",                                         # chỉ đích danh chặng (agent) chạy tiếp
        update={
            "active_agent": "sales_agent",                          # cập nhật biến "đang đến lượt agent nào"
            "messages": [last_ai_message, transfer_message],        # chỉ truyền đúng cặp này, không truyền cả lịch sử agent trước
        },
        graph=Command.PARENT                                        # điều hướng ở đồ thị cha, không trong đồ thị con
    )
```

`Command.PARENT`, `goto`, `StateGraph` thuộc LangGraph — ở đây chỉ dùng, cơ chế đồ thị nằm ở tài liệu LangGraph.

---

## 6. Giữ lịch sử trò chuyện hợp lệ khi chuyển quyền

Mục này chỉ liên quan **kiểu B**. Với kiểu A, lịch sử tin nhắn chảy tự nhiên trong một agent nên không phải lo.

**Vấn đề.** Model chờ mỗi lệnh gọi tool phải có câu trả lời đi kèm. Khi dùng `Command.PARENT` để chuyển sang agent khác, phải truyền **cả hai** message này thành một cặp:

1. `AIMessage` chứa lệnh gọi tool (message kích hoạt việc chuyển quyền)
2. `ToolMessage` xác nhận đã chuyển (câu trả lời nhân tạo cho lệnh gọi đó)

Thiếu cặp này, agent nhận thấy cuộc trò chuyện dở dang và có thể lỗi hoặc hành xử lạ.

**Vì sao không truyền hết tin nhắn của agent trước?** Bê nguyên cả hội thoại cũ thường gây rối: agent nhận bị nhiễu bởi suy luận nội bộ không liên quan, lại tốn thêm token. Chỉ truyền đúng cặp chuyển quyền thì đồ thị cha giữ được ngữ cảnh gọn, tập trung vào điều phối cấp cao. Nếu agent nhận cần thêm ngữ cảnh, hãy **tóm tắt** việc của agent trước vào nội dung `ToolMessage`, thay vì bê nguyên lịch sử.

**Khi trả quyền về người dùng.** Lúc kết thúc lượt, đảm bảo message cuối là `AIMessage`. Điều này giữ lịch sử hợp lệ và báo cho giao diện biết agent đã xong việc.

---

## 7. Ba điểm cân nhắc khi thiết kế

- **Lọc ngữ cảnh** — mỗi agent nhận đầy đủ lịch sử, phần đã lọc, hay bản tóm tắt? Vai trò khác nhau cần ngữ cảnh khác nhau.
- **Ngữ nghĩa của tool chuyển quyền** — nó chỉ đổi trạng thái định tuyến, hay còn làm việc phụ? Ví dụ `transfer_to_sales()` có nên đồng thời tạo phiếu hỗ trợ không, hay đó là hành động tách riêng.
- **Tiết kiệm token** — cân giữa ngữ cảnh đầy đủ và chi phí token. Hội thoại càng dài thì tóm tắt và truyền ngữ cảnh chọn lọc càng quan trọng.

---

## Tham chiếu chéo

- [04-01 Tổng quan](./04-01-multi-agent-overview.md) — Handoffs đối chiếu bốn pattern còn lại (chú ý: kém khi cần chạy song song nhiều mảng)
- [04-02 Subagents](./04-02-subagents.md) — khác biệt: Subagents có agent chính điều phối; Handoffs thì các agent ngang hàng trao quyền
- [04-05 Router](./04-05-router.md) — router giữ trạng thái thì tài liệu khuyên cân nhắc Handoffs thay thế
- Middleware, `wrap_model_call`: [03-03](../03-agent-harness/03-03-middleware-overview.md)
- Tool, `ToolRuntime`: [03-02](../03-agent-harness/03-02-tools.md)
- `Command`, `Command.PARENT`, `StateGraph`, `ToolMessage`: tài liệu LangGraph — `docs.langchain.com/oss/python/langgraph/`


