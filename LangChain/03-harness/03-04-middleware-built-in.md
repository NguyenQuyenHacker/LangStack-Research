---
title: Middleware dựng sẵn
doc_source: https://docs.langchain.com/oss/python/langchain/middleware/built-in
accessed: 2026-07-22
lc_version: "1.x (điều kiện `fraction` của Summarization cần langchain>=1.1)"
status: draft
lab:
related:
  - ./middleware-overview.md
  - ./middleware-custom.md
  - ./agents.md
  - ./tools.md
---

# Middleware dựng sẵn

> 16 middleware có sẵn, cắm vào `create_agent` là chạy. Đây là trang tra cứu, không phải trang để đọc từ đầu tới cuối.
> Cách nhóm ở mục 4–9 dưới đây **là của tôi**; trang gốc liệt kê phẳng thành một bảng, không chia nhóm.

**Hai điều đọc trước khi tra:**

Không phải cái nào cũng nằm trong package `langchain`. `FilesystemMiddleware` và `SubAgentMiddleware` đến từ package **`deepagents`**, import từ `deepagents.middleware...`. Cài `langchain` thôi thì không có.

Trang gốc **không nói mỗi middleware dùng hook nào**. Muốn biết cái nào chen vào chỗ nào trong vòng lặp thì phải đọc [middleware-custom](./middleware-custom.md) hoặc mã nguồn.

---

## 0. Từ điển thuật ngữ

| Từ | Nghĩa dễ hiểu |
|---|---|
| **context window** | Sức chứa tối đa của model cho một lần gọi, đo bằng token. Vượt là lỗi. |
| **token** | Đơn vị model đếm văn bản. Xấp xỉ 3–4 ký tự tiếng Anh một token. |
| **thread** | Một cuộc hội thoại, kéo dài qua nhiều lần `invoke`. |
| **run** | Một lần `invoke`: một câu của người dùng cho tới khi agent trả lời xong. |
| **checkpointer** | Bộ lưu trạng thái giữa các lần `invoke`. Không có nó thì mọi thứ tính theo thread đều không nhớ được. |
| **backoff** | Chờ trước khi thử lại. **Exponential backoff** là mỗi lần chờ gấp bội lần trước: 1s → 2s → 4s. |
| **jitter** | Cộng thêm một khoảng ngẫu nhiên vào thời gian chờ, để nhiều máy cùng lỗi không cùng thử lại một lúc. |
| **thundering herd** | Cảnh hàng loạt máy cùng thử lại đúng một thời điểm, đè sập server vừa hồi phục. |
| **redact / mask / hash** | Ba cách che dữ liệu nhạy cảm: **redact** thay bằng nhãn, **mask** che một phần giữ lại đuôi, **hash** thay bằng chuỗi băm cố định. |
| **glob** | Tìm file theo khuôn tên: `**/*.py`. |
| **grep** | Tìm nội dung bên trong file theo regex. |
| **ripgrep** | Công cụ grep viết lại cho nhanh. |
| **sandbox** | Vùng chạy bị rào lại, code bên trong không đụng được ra ngoài. |
| **subagent** | Một agent con được agent chính giao việc, chạy trong ngữ cảnh riêng rồi trả về kết quả gọn. |
| **backend** | Chỗ dữ liệu thật sự nằm. `StateBackend` nằm trong State, `StoreBackend` nằm trong Store. |
| **emulate** | Giả lập. Thay vì chạy tool thật, cho một model bịa ra kết quả nghe hợp lý để thử nghiệm. |

---

## 1. Bảng tra nhanh

| Middleware | Làm gì | Mục |
|---|---|---|
| `SummarizationMiddleware` | Tóm tắt lịch sử khi sắp tràn context | 4.1 |
| `ContextEditingMiddleware` | Xoá kết quả tool cũ, giữ lại N cái gần nhất | 4.2 |
| `FilesystemMiddleware` ⚑ | Cho agent một hệ file để cất bớt context ra ngoài | 4.3 |
| `ModelCallLimitMiddleware` | Giới hạn số lần gọi model | 5.1 |
| `ToolCallLimitMiddleware` | Giới hạn số lần gọi tool, chung hoặc theo từng tool | 5.2 |
| `ModelFallbackMiddleware` | Model chính hỏng thì lùi sang model khác | 6.1 |
| `ToolRetryMiddleware` | Thử lại tool lỗi, có backoff | 6.2 |
| `ModelRetryMiddleware` | Thử lại model lỗi, có backoff | 6.3 |
| `HumanInTheLoopMiddleware` | Dừng chờ người duyệt trước tool nguy hiểm | 7.1 |
| `PIIMiddleware` | Phát hiện và che thông tin cá nhân | 7.2 |
| `LLMToolSelectorMiddleware` | Dùng model nhanh lọc tool liên quan trước | 8.1 |
| `TodoListMiddleware` | Cấp cho agent tool lập và theo dõi việc | 8.2 |
| `ShellToolMiddleware` | Mở một phiên shell bền cho agent gõ lệnh | 8.3 |
| `FilesystemFileSearchMiddleware` | Cấp hai tool glob và grep trên hệ file | 8.4 |
| `SubAgentMiddleware` ⚑ | Cho agent quyền sinh agent con | 8.5 |
| `LLMToolEmulator` | Giả lập tool bằng model, để test | 9 |

⚑ = đến từ package `deepagents`, không phải `langchain`.

---

## 2. Gặp vấn đề gì thì tra cái nào

Bảng này là của tôi, không có trong doc.

| Vấn đề thực tế | Middleware |
|---|---|
| Hội thoại dài, tràn context window | Summarization, Context editing |
| Tool trả kết quả dài loằng ngoằng làm phình context | Context editing, Filesystem |
| Sợ agent chạy vòng vô hạn, đốt tiền API | Model call limit |
| Một tool cụ thể tốn tiền, cần chặn riêng | Tool call limit theo `tool_name` |
| API bên ngoài chập chờn | Tool retry |
| Provider model sập | Model fallback, Model retry |
| Hành động không thể hoàn tác (gửi tiền, gửi mail, xoá dữ liệu) | Human-in-the-loop |
| Dữ liệu khách hàng nhạy cảm, có nghĩa vụ tuân thủ | PII detection |
| Có 30 tool, model gọi lung tung | LLM tool selector |
| Việc nhiều bước, agent quên mất đang làm tới đâu | To-do list |
| Muốn thử agent mà chưa có tool thật | LLM tool emulator |

---

## 3. Hai khái niệm dùng chung nhiều chỗ

### 3.1 `thread_limit` so với `run_limit`

| | Đếm phạm vi nào | Khi nào reset |
|---|---|---|
| `run_limit` | Một lần `invoke` | Mỗi câu mới của người dùng |
| `thread_limit` | Cả cuộc hội thoại, qua nhiều lần `invoke` | Không reset trong cùng thread |

**Bài toán cụ thể.** `run_limit=5` chặn agent lặp vô hạn trong một câu hỏi. `thread_limit=20` chặn một khách hàng hỏi 40 câu liên tiếp trong cùng phiên chat làm đội chi phí.

### 3.2 Cái nào bắt buộc có checkpointer

| Middleware | Cần checkpointer? |
|---|---|
| `HumanInTheLoopMiddleware` | **Bắt buộc.** Không có thì dừng xong không khôi phục được |
| `ModelCallLimitMiddleware` | Bắt buộc nếu dùng `thread_limit` |
| `ToolCallLimitMiddleware` | Bắt buộc nếu dùng `thread_limit` |

Điểm chung: cái gì phải nhớ qua nhiều lần `invoke` thì cần checkpointer. Câu hỏi treo từ file [middleware-overview](./middleware-overview.md) về HITL có cần checkpointer không — trang này trả lời rồi, có, và ghi hẳn trong khung cảnh báo.

---

## 4. Nhóm quản lý context

### 4.1 Summarization

**Là gì.** Theo dõi độ dài hội thoại, tới ngưỡng thì gọi một model khác tóm tắt phần cũ, giữ nguyên phần gần đây.

**Dùng khi.** Hội thoại chạy dài vượt context window; đối thoại nhiều lượt; ứng dụng cần giữ lại toàn bộ mạch chuyện.

```python
SummarizationMiddleware(
    model="gpt-5.4-mini",
    trigger=("tokens", 4000),
    keep=("messages", 20),
)
```

Hai tham số cốt lõi đều nhận một tuple `(loại, giá trị)`, loại có ba lựa chọn:

| Loại | Nghĩa |
|---|---|
| `fraction` | Tỷ lệ trên context size của model, 0–1 |
| `tokens` | Số token tuyệt đối |
| `messages` | Số message |

`trigger` nhận **một** tuple hoặc **một list** tuple; list nghĩa là hoặc — chạm bất kỳ điều kiện nào là tóm tắt. `keep` chỉ nhận đúng một tuple.

```python
# chạm 3000 token HOẶC 6 message thì tóm tắt
trigger=[("tokens", 3000), ("messages", 6)]

# theo tỷ lệ: đầy 80% thì tóm tắt, giữ lại 30%
trigger=("fraction", 0.8), keep=("fraction", 0.3)
```

**Bẫy.** `fraction` dựa vào profile data của model và cần `langchain>=1.1`. Không có profile thì phải khai tay:

```python
model = init_chat_model("gpt-5.4", profile={"max_input_tokens": 100_000})
```

Tham số khác: `token_counter` (mặc định đếm theo ký tự, không phải token thật), `summary_prompt` (phải chứa chỗ trống `{messages}`), `trim_tokens_to_summarize` (mặc định 4000).

Ba tham số đã bỏ, gặp trong code cũ thì biết đường thay: `summary_prefix` → `summary_prompt`; `max_tokens_before_summary` → `trigger=("tokens", n)`; `messages_to_keep` → `keep=("messages", n)`.

### 4.2 Context editing

**Là gì.** Khác Summarization ở chỗ nó **xoá** chứ không tóm tắt, và chỉ xoá kết quả tool cũ.

**Dùng khi.** Hội thoại có nhiều lần gọi tool, kết quả tool cũ không còn dùng nữa nhưng vẫn chiếm chỗ.

```python
ContextEditingMiddleware(
    edits=[ClearToolUsesEdit(trigger=100000, keep=3)],
)
```

`ClearToolUsesEdit` là chiến lược duy nhất được nêu. Tham số:

| Tham số | Mặc định | Nghĩa |
|---|---|---|
| `trigger` | 100000 | Vượt bao nhiêu token thì dọn |
| `keep` | 3 | Giữ lại mấy kết quả tool gần nhất, không bao giờ xoá |
| `clear_at_least` | 0 | Mỗi lần dọn phải thu về tối thiểu bao nhiêu token; 0 nghĩa là dọn vừa đủ |
| `clear_tool_inputs` | False | Có xoá luôn đối số của lần gọi tool không |
| `exclude_tools` | () | Tool nào không bao giờ bị dọn |
| `placeholder` | `[cleared]` | Chữ thay vào chỗ đã xoá |

Ở cấp middleware còn `token_count_method`: `approximate` (mặc định) hoặc `model`.

**Chọn giữa 4.1 và 4.2.** Summarization giữ lại ý nhưng tốn một lần gọi model. Context editing không tốn gì nhưng mất luôn nội dung. Doc không so sánh hai cái, đây là nhận xét của tôi.

### 4.3 Filesystem ⚑

**Vấn đề nó giải.** Tool trả kết quả dài không đoán trước được — `web_search`, RAG — làm đầy context rất nhanh.

**Cách giải.** Cho agent bốn tool để cất nội dung ra ngoài rồi đọc lại khi cần: `ls`, `read_file`, `write_file`, `edit_file`.

```python
from deepagents.middleware.filesystem import FilesystemMiddleware

agent = create_agent(
    model="claude-sonnet-4-6",
    middleware=[FilesystemMiddleware()],
)
```

Mặc định "hệ file" này nằm trong State, hết lượt là mất. Muốn giữ lâu thì đổi backend:

```python
FilesystemMiddleware(
    backend=CompositeBackend(
        default=StateBackend(),
        routes={"/memories/": StoreBackend()},
    ),
)
```

File có tiền tố `/memories/` đi vào Store và sống qua các thread khác nhau. File khác vẫn nằm trong State và mất theo lượt. Cơ chế định tuyến theo đường dẫn, không phải theo lệnh gọi.

`FilesystemMiddleware` đã có sẵn trong `create_deep_agent`, chỉ phải khai tay khi tự dựng agent.

---

## 5. Nhóm kiểm soát chi phí và vòng lặp

### 5.1 Model call limit

```python
ModelCallLimitMiddleware(thread_limit=10, run_limit=5, exit_behavior="end")
```

| Tham số | Mặc định | Nghĩa |
|---|---|---|
| `thread_limit` | không giới hạn | Tối đa bao nhiêu lần gọi model trong cả thread |
| `run_limit` | không giới hạn | Tối đa bao nhiêu lần trong một lần `invoke` |
| `exit_behavior` | `end` | `end` dừng êm, `error` ném exception |

### 5.2 Tool call limit

Khác Model call limit ở chỗ **giới hạn được theo từng tool**. Cách dùng: cắm nhiều instance, mỗi cái một phạm vi.

```python
middleware=[
    ToolCallLimitMiddleware(thread_limit=20, run_limit=10),                    # chung mọi tool
    ToolCallLimitMiddleware(tool_name="search", thread_limit=5, run_limit=3),  # riêng tool search
]
```

Không truyền `tool_name` thì áp cho toàn bộ tool. Phải khai ít nhất một trong hai giới hạn.

`exit_behavior` ở đây có **ba** giá trị, khác Model call limit:

| Giá trị | Chuyện gì xảy ra |
|---|---|
| `continue` (mặc định) | Chặn lần gọi vượt hạn bằng thông báo lỗi, các tool khác và model chạy tiếp; model tự đọc lỗi rồi quyết dừng |
| `error` | Ném `ToolCallLimitExceededError`, dừng ngay |
| `end` | Dừng ngay kèm `ToolMessage` và AI message. **Chỉ dùng được khi giới hạn đúng một tool**; còn tool khác đang chờ thì ném `NotImplementedError` |

---

## 6. Nhóm chống lỗi tạm thời

Ba middleware này dễ lẫn nhau. Phân biệt: **fallback** đổi sang model khác, **retry** thử lại chính cái vừa lỗi.

### 6.1 Model fallback

```python
ModelFallbackMiddleware("gpt-5.4-mini", "claude-3-5-sonnet-20241022")
```

Truyền theo thứ tự, hỏng cái này thì thử cái kế. Không có tham số nào khác.

### 6.2 Tool retry

```python
ToolRetryMiddleware(max_retries=3, backoff_factor=2.0, initial_delay=1.0)
```

| Tham số | Mặc định | Nghĩa |
|---|---|---|
| `max_retries` | 2 | Số lần thử **thêm** sau lần đầu. Mặc định là tổng 3 lần |
| `tools` | None | Chỉ áp cho các tool này; None là áp hết |
| `retry_on` | `(Exception,)` | Tuple loại exception, hoặc một hàm nhận exception trả về True/False |
| `on_failure` | `return_message` | Hết lượt thử thì làm gì |
| `backoff_factor` | 2.0 | Hệ số nhân. Chờ = `initial_delay * (backoff_factor ** lần_thử)`. Đặt 0.0 thì chờ đều |
| `initial_delay` | 1.0 | Giây chờ trước lần thử đầu |
| `max_delay` | 60.0 | Trần thời gian chờ |
| `jitter` | True | Cộng ngẫu nhiên ±25% để tránh thundering herd |

`on_failure`: `return_message` trả `ToolMessage` báo lỗi cho model tự xử; `raise` ném tiếp và dừng agent; hoặc truyền một hàm nhận exception trả về chuỗi.

### 6.3 Model retry

Bộ tham số gần y hệt 6.2, trừ hai chỗ:

- không có tham số `tools` (đương nhiên, nó bọc model chứ không bọc tool)
- `on_failure` **mặc định là `continue`**, và tập giá trị là `continue` / `error` / hàm — không phải `return_message` / `raise` như Tool retry

Hai middleware anh em mà đặt tên giá trị khác nhau. Ghi nhớ chỗ này, dễ viết nhầm.

---

## 7. Nhóm an toàn và tuân thủ

### 7.1 Human-in-the-loop

**Dùng khi.** Thao tác không hoàn tác được: ghi database, giao dịch tiền; quy trình bắt buộc có người duyệt; hội thoại dài cần người lái.

```python
agent = create_agent(
    model="gpt-5.4",
    tools=[your_read_email_tool, your_send_email_tool],
    checkpointer=InMemorySaver(),
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "your_send_email_tool": {"allowed_decisions": ["approve", "edit", "reject"]},
                "your_read_email_tool": False,
            }
        ),
    ],
)
```

Đọc `interrupt_on` như một bảng phân loại rủi ro: khoá là **tên tool**, giá trị `False` nghĩa là cho chạy thẳng, giá trị là dict nghĩa là phải dừng chờ người. Ba quyết định người duyệt được đưa ra: duyệt, sửa đối số rồi duyệt, hoặc từ chối.

Checkpointer bắt buộc.

### 7.2 PII detection

**Dùng khi.** Y tế, tài chính có yêu cầu tuân thủ; cần làm sạch log; bất cứ chỗ nào chạm dữ liệu nhạy cảm của người dùng.

```python
middleware=[
    PIIMiddleware("email", strategy="redact", apply_to_input=True),
    PIIMiddleware("credit_card", strategy="mask", apply_to_input=True),
]
```

Mỗi loại PII là một instance riêng.

**Loại có sẵn:** `email`, `credit_card`, `ip`, `mac_address`, `url`.

**Bốn chiến lược:**

| Chiến lược | Kết quả |
|---|---|
| `block` | Ném exception khi phát hiện |
| `redact` (mặc định) | Thay bằng `[REDACTED_{PII_TYPE}]` |
| `mask` | Che một phần, ví dụ `****-****-****-1234` |
| `hash` | Thay bằng chuỗi băm cố định |

**Ba chỗ kiểm:** `apply_to_input` (message người dùng, trước khi gọi model — mặc định True), `apply_to_output` (message AI trả về — mặc định False), `apply_to_tool_results` (kết quả tool — mặc định False).

Hai cái sau tắt mặc định. Muốn chặn PII rò ra từ database qua tool thì phải bật `apply_to_tool_results` bằng tay.

**Loại PII tự định nghĩa** qua tham số `detector`, ba cách:

```python
# 1. chuỗi regex
PIIMiddleware("api_key", detector=r"sk-[a-zA-Z0-9]{32}", strategy="block")

# 2. regex đã biên dịch — dùng khi cần cờ, ví dụ không phân biệt hoa thường
PIIMiddleware("phone_number", detector=re.compile(r"\+?\d{1,3}[\s.-]?\d{3,4}[\s.-]?\d{4}"), strategy="mask")

# 3. hàm tự viết — dùng khi cần kiểm tra tính hợp lệ, không chỉ khớp khuôn
PIIMiddleware("ssn", detector=detect_ssn, strategy="hash")
```

Hàm tự viết nhận một chuỗi, trả về list dict có ba khoá `text`, `start`, `end`:

```python
def detector(content: str) -> list[dict[str, str | int]]:
    return [{"text": "matched_text", "start": 0, "end": 12}]
```

Ví dụ SSN trong doc minh hoạ đúng chỗ regex không làm được: khớp khuôn `\d{3}-\d{2}-\d{4}` xong còn phải loại ba số đầu là 000, 666, hoặc 900–999 vì đó là dải không hợp lệ.

---

## 8. Nhóm mở rộng năng lực

### 8.1 LLM tool selector

**Vấn đề.** Agent có 10 tool trở lên, mỗi câu hỏi chỉ liên quan vài cái. Mô tả của toàn bộ tool vẫn bị nhồi vào mỗi lần gọi model, tốn token và làm model phân tán.

**Cách giải.** Gọi một model nhỏ hỏi trước "câu này cần tool nào", rồi chỉ đưa số tool đó cho model chính.

```python
LLMToolSelectorMiddleware(
    model="gpt-5.4-mini",
    max_tools=3,
    always_include=["search"],
)
```

`model` mặc định lấy chính model của agent — nên khai một model rẻ hơn. `max_tools` chọn nhiều hơn thì cắt lấy phần đầu. `always_include` luôn có mặt và **không tính vào** `max_tools`.

Cơ chế bên dưới là structured output: schema liệt kê tên và mô tả các tool, model chọn ra tên.

### 8.2 To-do list

Cấp cho agent một tool `write_todos` cùng system prompt hướng dẫn cách lập kế hoạch. Dùng cho việc nhiều bước cần phối hợp nhiều tool, hoặc việc chạy lâu cần nhìn thấy tiến độ.

```python
TodoListMiddleware()
```

Hai tham số tuỳ chọn: `system_prompt` và `tool_description`, đều có bản dựng sẵn.

### 8.3 Shell tool

Mở một phiên shell **bền** — các lệnh chạy nối tiếp trong cùng một phiên, không phải mỗi lệnh một tiến trình mới.

```python
ShellToolMiddleware(
    workspace_root="/workspace",
    execution_policy=HostExecutionPolicy(),
)
```

Ba mức cách ly, chọn theo mức tin cậy của môi trường:

| Policy | Mức cách ly |
|---|---|
| `HostExecutionPolicy` (mặc định) | Toàn quyền trên máy host. Chỉ dùng khi agent đã nằm sẵn trong container hoặc VM |
| `DockerExecutionPolicy` | Mỗi lượt chạy dựng một container Docker riêng |
| `CodexSandboxExecutionPolicy` | Dùng sandbox của Codex CLI, siết thêm syscall và hệ file |

Tham số khác: `startup_commands` / `shutdown_commands`, `redaction_rules`, `shell_command` (mặc định `/bin/bash`), `env`, `tool_description`.

**Hai cảnh báo trong doc:**

`redaction_rules` chạy **sau** khi lệnh đã thực thi. Nó chỉ làm sạch đầu ra trước khi trả cho model, **không** ngăn được việc dữ liệu nhạy cảm bị đưa ra ngoài khi dùng `HostExecutionPolicy`.

Phiên shell bền hiện **không chạy được cùng interrupt** — tức là không kết hợp được với Human-in-the-loop. Doc nói sẽ hỗ trợ sau.

### 8.4 File search

Cấp hai tool tìm kiếm trên hệ file:

- **glob** — tìm file theo khuôn tên (`**/*.py`, `src/**/*.ts`), trả về đường dẫn sắp theo thời gian sửa
- **grep** — tìm nội dung theo regex, lọc thêm bằng tham số `include`, ba kiểu đầu ra: `files_with_matches`, `content`, `count`

```python
FilesystemFileSearchMiddleware(
    root_path="/workspace",
    use_ripgrep=True,
    max_file_size_mb=10,
)
```

`root_path` bắt buộc, mọi thao tác tính tương đối theo nó. `use_ripgrep=True` là mặc định, không có ripgrep thì tự lùi về regex của Python. File lớn hơn `max_file_size_mb` bị bỏ qua.

Đừng lẫn với 4.3: `FilesystemMiddleware` cho agent **ghi** file để cất context; `FilesystemFileSearchMiddleware` chỉ cho **tìm** trên hệ file có sẵn.

### 8.5 Subagent ⚑

**Vấn đề nó giải.** Việc phức tạp sinh ra hàng chục lượt gọi tool trung gian, đống rác đó nằm hết trong context của agent chính.

**Cách giải.** Giao cho một agent con qua tool `task`. Agent con chạy trong ngữ cảnh riêng, chỉ trả về kết quả gọn.

```python
from deepagents.middleware.subagents import SubAgentMiddleware

SubAgentMiddleware(
    default_model="claude-sonnet-4-6",
    default_tools=[],
    subagents=[
        {
            "name": "weather",
            "description": "This subagent can get weather in cities.",
            "system_prompt": "Use the get_weather tool to get the weather in a city.",
            "tools": [get_weather],
            "model": "gpt-5.4",
            "middleware": [],
        }
    ],
)
```

Bốn trường bắt buộc: `name`, `description`, `system_prompt`, `tools`. Hai trường thêm: `model` và `middleware` riêng cho agent con — hữu ích khi muốn agent con có thêm một khoá State dùng chung với agent chính.

Trường hợp phức tạp hơn thì bọc một graph LangGraph tự dựng bằng `CompiledSubAgent`.

Agent chính **luôn** có sẵn một subagent tên `general-purpose`, cùng chỉ dẫn và cùng bộ tool với agent chính. Nó tồn tại chỉ để cách ly ngữ cảnh: quăng việc rối sang đó, nhận về câu trả lời gọn.

---

## 9. LLM tool emulator

Thay việc chạy tool thật bằng một model bịa ra kết quả nghe hợp lý. Dùng để thử agent khi tool thật chưa có, đắt, hoặc không nên chạy thật.

```python
LLMToolEmulator()                              # giả lập TẤT CẢ tool
LLMToolEmulator(tools=["get_weather"])         # chỉ giả lập tool này
LLMToolEmulator(model="claude-sonnet-4-6")     # dùng model khác để bịa
```

`tools=None` (mặc định) là giả lập hết — đây là mặc định nguy hiểm nếu cắm nhầm vào agent thật. `tools=[]` là không giả lập cái nào.

---

## 10. Middleware riêng theo provider

| Provider | Có gì |
|---|---|
| Anthropic | Prompt caching, bash tool, text editor, memory, file search |
| AWS | Prompt caching cho Bedrock |
| OpenAI | Kiểm duyệt nội dung |

Chi tiết nằm ở trang integrations của từng provider, không phải trang này.

---

## Cần kiểm chứng thêm

- [ ] **Doc mâu thuẫn với chính nó ở `ToolRetryMiddleware`.** Bảng tham số ghi `on_failure` nhận `return_message` / `raise` / hàm, nhưng ví dụ đầy đủ ngay bên dưới lại viết `on_failure="continue"` — giá trị không có trong bảng. Xác minh: reference `ToolRetryMiddleware`, hoặc chạy thử xem `"continue"` có bị từ chối không.
- [ ] Mỗi middleware dùng hook nào. Trang này không nói. Từ blog LangChain: Summarization dùng `before_model`, PII dùng `before_model` + `after_model`, LLM tool selector và Model retry dùng `wrap_model_call`. Chưa xác nhận cho 12 cái còn lại. Xác minh: [middleware-custom](./middleware-custom.md) hoặc mã nguồn.
- [ ] Thứ tự cắm middleware có ảnh hưởng kết quả không, ví dụ PII đặt trước hay sau Summarization. Doc im lặng dù mục 5.2 cho thấy cắm nhiều instance cùng loại là chuyện bình thường. Xác minh: trang Custom middleware mục thứ tự chạy hook.
- [ ] `token_counter` của Summarization mặc định "đếm theo ký tự". Chưa rõ quy đổi ra token thế nào và sai số bao nhiêu. Xác minh: mã nguồn.
- [ ] Quan hệ giữa `ToolRetryMiddleware` và `handle_tool_errors` của `ToolNode` (xem [tools](./tools.md) mục 5.1) — cái nào chạy trước, retry xong mới tới bắt lỗi hay ngược lại. Câu hỏi này treo từ hai file trước, trang này vẫn không trả lời.
- [ ] `exit_behavior="end"` của Tool call limit "chỉ dùng được khi giới hạn đúng một tool". Chưa rõ "một tool" nghĩa là chỉ có một instance middleware, hay chỉ có một tool call đang chờ. Xác minh: chạy thử với hai tool call song song.
- [ ] Tên model trong ví dụ (`gpt-5.4`, `gemini-3.5-flash`) — cùng nghi vấn đã ghi ở [agents](./agents.md).

---

## Tham chiếu chéo

| File | Bổ sung cho mục nào |
|---|---|
| [middleware-overview](./middleware-overview.md) | Mục 3.2 — checkpointer; bộ hook |
| [middleware-custom](./middleware-custom.md) | Toàn bộ — hook nào, thứ tự chạy ra sao |
| [agents](./agents.md) | Mục 5, 8.1 — `wrap_model_call` lọc tool viết tay, so với LLM tool selector |
| [tools](./tools.md) | Mục 6.2 — retry so với `handle_tool_errors` của `ToolNode` |