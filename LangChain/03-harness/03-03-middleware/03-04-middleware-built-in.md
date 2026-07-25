---
title: Prebuilt middleware
doc_source: https://docs.langchain.com/oss/python/langchain/middleware/built-in
accessed: 2026-07-24
version: "1.x"
status: draft
lab:
related:
  - ./03-03-middleware-overview.md
  - ./03-05-middleware-custom.md
---

# Middleware dựng sẵn (`langchain.agents.middleware`)

> Mười sáu bản middleware đã viết sẵn, chạy được với mọi nhà cung cấp model, cộng thêm ba bộ riêng cho Anthropic, AWS và OpenAI.
> Cách gắn chúng vào agent nằm ở [03-03](./03-03-middleware-overview.md); cách tự viết một bản mới nằm ở [03-05](./03-05-middleware-custom.md).

---

## 1. Tổng quan 

Tài liệu chia hai loại: loại chạy được với mọi nhà cung cấp LLM, và loại chỉ dùng được với một nhà cung cấp cụ thể. Bảng dưới là loại thứ nhất. Bốn bản cuối (`FilesystemMiddleware`, `SubAgentMiddleware`, và hai bản tìm kiếm) đến từ gói [Deep Agents](https://docs.langchain.com/oss/python/deepagents/overview), không nằm trong `langchain.agents.middleware`.

Tài liệu chia hai loại: loại chạy được với mọi nhà cung cấp LLM, và loại chỉ dùng được với một nhà cung cấp cụ thể. Bốn bản cuối (`FilesystemMiddleware`, `SubAgentMiddleware`, và hai bản tìm kiếm) đến từ gói [Deep Agents](https://docs.langchain.com/oss/python/deepagents/overview), không nằm trong `langchain.agents.middleware`.

| Bản | Việc nó làm | Nhà cung cấp | Mục |
|---|---|---|---|
| `SummarizationMiddleware` | Tóm tắt hội thoại cũ khi sắp chạm trần token | Mọi provider | [2](#2-summarization--tóm-tắt-hội-thoại-khi-sắp-chạm-trần-token) |
| `HumanInTheLoopMiddleware` | Dừng chờ người duyệt lệnh gọi tool | Mọi provider | [3](#3-human-in-the-loop--dừng-chờ-người-duyệt-lệnh-gọi-tool) |
| `ModelCallLimitMiddleware` | Chặn trần số lần gọi model | Mọi provider | [4](#4-model-call-limit--chặn-trần-số-lần-gọi-model) |
| `ToolCallLimitMiddleware` | Chặn trần số lần gọi tool | Mọi provider | [5](#5-tool-call-limit--chặn-trần-số-lần-gọi-tool) |
| `ModelFallbackMiddleware` | Đổi sang model khác khi model chính hỏng | Mọi provider | [6](#6-model-fallback--đổi-sang-model-khác-khi-model-chính-hỏng) |
| `PIIMiddleware` | Phát hiện và xử lý thông tin cá nhân | Mọi provider | [7](#7-pii-detection--phát-hiện-và-xử-lý-thông-tin-cá-nhân) |
| `TodoListMiddleware` | Cấp cho agent năng lực lập và bám danh sách việc | Mọi provider | [8](#8-to-do-list--cấp-cho-agent-một-danh-sách-việc) |
| `LLMToolSelectorMiddleware` | Để một model nhỏ lọc tool trước khi gọi model chính | Mọi provider | [9](#9-llm-tool-selector--để-một-model-nhỏ-lọc-tool-trước) |
| `ToolRetryMiddleware` | Thử lại tool hỏng, giãn dần thời gian chờ | Mọi provider | [10](#10-tool-retry--thử-lại-tool-hỏng) |
| `ModelRetryMiddleware` | Thử lại lệnh gọi model hỏng | Mọi provider | [11](#11-model-retry--thử-lại-lệnh-gọi-model-hỏng) |
| `LLMToolEmulator` | Giả lập kết quả tool bằng LLM để kiểm thử | Mọi provider | [12](#12-llm-tool-emulator--giả-lập-kết-quả-tool-khi-kiểm-thử) |
| `ContextEditingMiddleware` | Xóa bớt kết quả tool cũ khỏi hội thoại | Mọi provider | [13](#13-context-editing--xóa-bớt-kết-quả-tool-cũ) |
| `ShellToolMiddleware` | Mở một phiên shell chạy suốt cho agent | Mọi provider | [14](#14-shell-tool--mở-một-phiên-shell-chạy-suốt) |
| `AnthropicPromptCachingMiddleware` | Cache prefix hội thoại để tiết kiệm token | Chỉ Anthropic | [15](#15-anthropic-prompt-caching--cache-prefix-hội-thoại) |
| `ProviderToolSearchMiddleware` | Đẩy việc chọn tool xuống server của provider | Anthropic, OpenAI | [16](#16-provider-tool-search--tìm-tool-phía-server) |
| `FilesystemFileSearchMiddleware` | Cấp hai tool tìm file theo tên và theo nội dung | Mọi provider | [17](#17-file-search--tìm-file-theo-tên-và-theo-nội-dung) |
| `FilesystemMiddleware` | Cấp cho agent một hệ thống file để ghi nhớ | Mọi provider | [18](#18-filesystem--hệ-thống-file-làm-nơi-ghi-nhớ) |
| `SubAgentMiddleware` | Cho phép sinh ra agent con | Mọi provider | [19](#19-subagent--giao-việc-cho-agent-con) |

Mỗi bản đều được tài liệu mô tả là dùng được cho môi trường thật và có tham số cấu hình riêng.

---

## 2. Summarization — tóm tắt hội thoại khi sắp chạm trần token

**Khái niệm.** `SummarizationMiddleware` tự tóm tắt phần hội thoại cũ khi số token sắp chạm trần, giữ lại các tin nhắn gần đây và nén phần trước đó lại.

**Vai trò.** Cửa sổ ngữ cảnh của model là hữu hạn. Hội thoại dài đến ngưỡng thì hoặc là lỗi, hoặc là phải cắt cụt lịch sử và mất thông tin. Bản này đổi phần lịch sử cũ lấy một bản tóm tắt ngắn, giữ được ý mà không giữ nguyên số token.

Tài liệu nêu ba tình huống dùng: hội thoại chạy dài vượt cửa sổ ngữ cảnh, đối thoại nhiều lượt có lịch sử dày, và ứng dụng mà việc giữ được ngữ cảnh cả cuộc là điều kiện bắt buộc.

**Áp dụng thực tế.** Bàn hỗ trợ kỹ thuật nội bộ: một ca hỏng kéo 40 lượt trao đổi, mỗi lượt kèm một đoạn log dán vào. Đến lượt thứ 25 thì tổng số token vượt trần và agent quên mất phiên bản hệ thống mà người dùng đã khai ở lượt đầu.

**Triển khai.**

```python
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware

agent = create_agent(
    model="gpt-5.4",
    tools=[your_weather_tool, your_calculator_tool],
    middleware=[
        SummarizationMiddleware(
            model="gpt-5.4-mini",         # model viết tóm tắt, tách khỏi model chính cho rẻ
            trigger=("tokens", 4000),     # chạm 4000 token thì tóm tắt
            keep=("messages", 20),        # sau khi tóm tắt, giữ lại 20 tin nhắn gần nhất
        ),
    ],
)
```

**Bảng tham số của `SummarizationMiddleware`**

| Tham số | Kiểu / mặc định | Chứa gì | Dùng khi nào |
|---|---|---|---|
| `model` | `string \| BaseChatModel`, bắt buộc | Model sinh bản tóm tắt | Luôn phải khai |
| `trigger` | `ContextSize \| list[ContextSize] \| None` | Điều kiện kích hoạt | Truyền danh sách thì thỏa **một** điều kiện là chạy |
| `keep` | `ContextSize`, mặc định `('messages', 20)` | Giữ lại bao nhiêu sau khi tóm tắt | Khai đúng **một** trong ba dạng |
| `token_counter` | hàm | Cách đếm token riêng | Mặc định đếm theo ký tự |
| `summary_prompt` | `string` | Mẫu prompt tóm tắt riêng | Mẫu phải chứa chỗ trống `{messages}` |
| `trim_tokens_to_summarize` | số, mặc định `4000` | Trần token đưa vào lệnh tóm tắt | Tin nhắn bị cắt bớt cho vừa trần này trước khi tóm tắt |
| `summary_prefix` | `string` | — | Không còn được khuyến nghị, dùng `summary_prompt` |
| `max_tokens_before_summary` | số | — | Không còn được khuyến nghị, dùng `trigger: ("tokens", value)` |
| `messages_to_keep` | số | — | Không còn được khuyến nghị, dùng `keep: ("messages", value)` |

Cả `trigger` và `keep` nhận một trong ba dạng điều kiện: `fraction` (phần của cửa sổ ngữ cảnh, 0–1), `tokens` (số token tuyệt đối), `messages` (số tin nhắn). Riêng `keep` chỉ được khai đúng một dạng.

```python
SummarizationMiddleware(
    model="gpt-5.4-mini",
    trigger=[                    # danh sách = HOẶC, thỏa điều kiện nào cũng chạy
        ("tokens", 3000),        # chạm 3000 token
        ("messages", 6),         # hoặc chạm 6 tin nhắn
    ],
    keep=("messages", 20),
)

SummarizationMiddleware(
    model="gpt-5.4-mini",
    trigger=("fraction", 0.8),   # dùng hết 80% cửa sổ ngữ cảnh thì tóm tắt
    keep=("fraction", 0.3),      # giữ lại phần bằng 30% cửa sổ
)
```

## 3. Human-in-the-loop — dừng chờ người duyệt lệnh gọi tool

**Khái niệm.** `HumanInTheLoopMiddleware` dừng agent lại trước khi một tool chạy, để người thật duyệt, sửa, hoặc từ chối lệnh gọi đó.

**Vai trò.** Có những lệnh không hoàn tác được: ghi vào cơ sở dữ liệu, chuyển tiền, gửi thư ra ngoài. Model đoán sai một lần là hỏng thật. Bản này biến những tool đó thành loại phải có chữ ký người trước khi chạy.

**Áp dụng thực tế.** Agent trợ lý hộp thư có hai tool: đọc thư và gửi thư. Đọc thư thì cho chạy tự do. Gửi thư thì phải hiện lên cho người xem nội dung, sửa câu chữ nếu cần, rồi mới bấm duyệt.

**Triển khai.**

```python
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver

def your_read_email_tool(email_id: str) -> str:
    """Mock function to read an email by its ID."""
    return f"Email content for ID: {email_id}"

def your_send_email_tool(recipient: str, subject: str, body: str) -> str:
    """Mock function to send an email."""
    return f"Email sent to {recipient} with subject '{subject}'"

agent = create_agent(
    model="gpt-5.4",
    tools=[your_read_email_tool, your_send_email_tool],
    checkpointer=InMemorySaver(),                     # nơi lưu trạng thái, bắt buộc phải có
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "your_send_email_tool": {
                    "allowed_decisions": ["approve", "edit", "reject"],   # ba quyết định cho phép
                },
                "your_read_email_tool": False,                            # tool này chạy thẳng
            }
        ),
    ],
)
```

**!Note:** Bản này **bắt buộc** phải có một nơi lưu trạng thái (`checkpointer`). Trạng thái phải sống sót qua quãng thời gian agent đứng chờ người duyệt — không có chỗ lưu thì không có gì để chạy tiếp.

Cấu hình đầy đủ và các cách tích hợp nằm ở trang riêng: `https://docs.langchain.com/oss/python/langchain/human-in-the-loop`.

---

## 4. Model call limit — chặn trần số lần gọi model

**Khái niệm.** `ModelCallLimitMiddleware` đặt trần cho số lần agent được gọi model.

**Vai trò.** Agent có thể rơi vào vòng lặp không thoát: model gọi tool, tool trả kết quả không như ý, model gọi lại. Mỗi vòng là một lần trả tiền. Bản này cắt vòng lặp bằng một con số cứng.

**Áp dụng thực tế.** Agent tra cứu nội bộ chạy đêm, không ai ngồi canh. Một truy vấn hỏng khiến nó gọi model 400 lần trong hai giờ trước khi có người phát hiện.

**Triển khai.**

```python
from langchain.agents import create_agent
from langchain.agents.middleware import ModelCallLimitMiddleware
from langgraph.checkpoint.memory import InMemorySaver

agent = create_agent(
    model="gpt-5.4",
    checkpointer=InMemorySaver(),      # bắt buộc nếu muốn đếm theo thread
    tools=[],
    middleware=[
        ModelCallLimitMiddleware(
            thread_limit=10,           # tối đa 10 lần gọi model trong cả một thread
            run_limit=5,               # tối đa 5 lần gọi model trong một lần invoke
            exit_behavior="end",       # chạm trần thì dừng êm, không ném lỗi
        ),
    ],
)
```

**Bảng tham số của `ModelCallLimitMiddleware`**

| Tham số | Kiểu / mặc định | Chứa gì |
|---|---|---|
| `thread_limit` | số, mặc định không giới hạn | Trần số lần gọi model trên toàn bộ các lần chạy trong một thread |
| `run_limit` | số, mặc định không giới hạn | Trần số lần gọi model trong một lần gọi `invoke` |
| `exit_behavior` | `string`, mặc định `'end'` | `'end'` dừng êm, `'error'` ném lỗi |

**!Note:** Đếm theo thread cần `checkpointer`. Bỏ quên nó thì con số `thread_limit` không có chỗ để cộng dồn qua các lần gọi.

---

## 5. Tool call limit — chặn trần số lần gọi tool

**Khái niệm.** `ToolCallLimitMiddleware` đặt trần cho số lần gọi tool, áp cho tất cả tool hoặc cho riêng một tool được chỉ tên.

**Vai trò.** Không phải tool nào cũng đắt ngang nhau. Một tool tra nội bộ chạy trăm lần vẫn rẻ; một tool gọi API tìm kiếm bên ngoài tính tiền theo lượt. Bản này cho phép đặt trần riêng cho từng tool bằng cách gắn nhiều bản vào cùng một agent.

**Áp dụng thực tế.** Agent nghiên cứu thị trường có ba tool: tìm kiếm web (0,01 USD/lượt), truy vấn cơ sở dữ liệu nội bộ (miễn phí), và bóc nội dung trang web (chậm, 8 giây/lượt). Một câu hỏi mở khiến nó tìm kiếm 60 lượt trong một lần chạy.

**Triển khai.**

```python
from langchain.agents import create_agent
from langchain.agents.middleware import ToolCallLimitMiddleware

agent = create_agent(
    model="gpt-5.4",
    tools=[search_tool, database_tool],
    middleware=[
        ToolCallLimitMiddleware(thread_limit=20, run_limit=10),      # không khai tool_name = áp cho mọi tool
        ToolCallLimitMiddleware(
            tool_name="search",                                       # chỉ áp cho tool tên "search"
            thread_limit=5,
            run_limit=3,
        ),
    ],
)
```

Gắn nhiều bản cùng lúc là cách tài liệu hướng dẫn để chồng nhiều mức trần khác nhau:

```python
global_limiter   = ToolCallLimitMiddleware(thread_limit=20, run_limit=10)                              # trần chung
search_limiter   = ToolCallLimitMiddleware(tool_name="search", thread_limit=5, run_limit=3)            # riêng tìm kiếm
database_limiter = ToolCallLimitMiddleware(tool_name="query_database", thread_limit=10)                # riêng CSDL
strict_limiter   = ToolCallLimitMiddleware(tool_name="scrape_webpage", run_limit=2,
                                           exit_behavior="error")                                       # chạm trần là ném lỗi
```

**Bảng tham số của `ToolCallLimitMiddleware`**

| Tham số | Kiểu / mặc định | Chứa gì |
|---|---|---|
| `tool_name` | `string` | Tên tool cần giới hạn. Bỏ trống thì áp cho **mọi** tool |
| `thread_limit` | số, `None` = không giới hạn | Trần trên toàn thread, cộng dồn qua nhiều lần gọi cùng một thread ID. Cần `checkpointer` |
| `run_limit` | số, `None` = không giới hạn | Trần trong một lần gọi (một tin nhắn người dùng → một câu trả lời). Về 0 ở mỗi lượt mới |
| `exit_behavior` | `string`, mặc định `'continue'` | Ba giá trị, xem bảng dưới |

Phải khai ít nhất một trong hai: `thread_limit` hoặc `run_limit`.

| `exit_behavior` | Hành vi khi chạm trần |
|---|---|
| `'continue'` (mặc định) | Chặn lệnh gọi vượt trần bằng một tin nhắn lỗi, các tool khác và model chạy tiếp. Model tự quyết định lúc nào dừng dựa trên tin nhắn lỗi đó |
| `'error'` | Ném `ToolCallLimitExceededError`, dừng ngay |
| `'end'` | Dừng ngay bằng một `ToolMessage` cộng một tin nhắn AI cho lệnh gọi vượt trần. Chỉ chạy được khi giới hạn đúng một tool; còn tool khác đang chờ thì ném `NotImplementedError` |

**Kết quả in ra** (dựng lại) — với `exit_behavior='error'` và `run_limit=2`:

```
tool call 1: scrape_webpage(url="...")   ← trong trần, chạy bình thường
tool call 2: scrape_webpage(url="...")   ← lần thứ hai, vẫn trong trần
tool call 3: scrape_webpage(url="...")   ← vượt trần
ToolCallLimitExceededError                ← ném lỗi, agent dừng ngay tại đây
```

**!Note:** Mặc định là `'continue'`, không phải `'error'`. Nghĩa là mặc định agent **không dừng** khi chạm trần — nó chỉ nhận tin nhắn lỗi và tự xoay xở. Ai kỳ vọng "chạm trần thì dừng" mà không đổi tham số này sẽ thấy agent vẫn chạy tiếp.

---

## 6. Model fallback — đổi sang model khác khi model chính hỏng

**Khái niệm.** `ModelFallbackMiddleware` tự chuyển sang model dự phòng khi model chính hỏng, thử lần lượt theo thứ tự khai báo.

**Vai trò.** Nhà cung cấp model có lúc sập, có lúc chặn vì quá tần suất. Bản này giữ agent sống qua sự cố đó, và cũng dùng được để hạ dần xuống model rẻ hơn.

**Triển khai.**

```python
from langchain.agents import create_agent
from langchain.agents.middleware import ModelFallbackMiddleware

agent = create_agent(
    model="gpt-5.4",                                # model chính
    tools=[],
    middleware=[
        ModelFallbackMiddleware(
            "gpt-5.4-mini",                         # hỏng thì thử bản nhỏ cùng nhà cung cấp
            "claude-3-5-sonnet-20241022",           # vẫn hỏng thì đổi hẳn nhà cung cấp
        ),
    ],
)
```

| Tham số | Kiểu | Chứa gì |
|---|---|---|
| `first_model` | `string \| BaseChatModel`, bắt buộc | Model dự phòng thứ nhất |
| `*additional_models` | `string \| BaseChatModel` | Các model dự phòng tiếp theo, thử theo đúng thứ tự truyền vào |

---

## 7. PII detection — phát hiện và xử lý thông tin cá nhân

**Khái niệm.** `PIIMiddleware` dò thông tin cá nhân trong hội thoại và xử lý theo một trong bốn cách: chặn, che, che một phần, hoặc thay bằng chuỗi băm.

**Vai trò.** Log hội thoại thường được lưu lại để gỡ lỗi và huấn luyện. Số thẻ hay email lọt vào log là rủi ro tuân thủ. Bản này chặn ngay ở lớp giữa, không phải sửa từng tool.

**Áp dụng thực tế.** Bàn dịch vụ khách hàng của một công ty tài chính: khách dán cả dãy số thẻ vào ô chat để hỏi giao dịch. Log lưu 90 ngày, và bên kiểm toán hỏi tại sao số thẻ đầy đủ nằm trong đó.

**Triển khai.**

```python
from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware

agent = create_agent(
    model="gpt-5.4",
    tools=[],
    middleware=[
        PIIMiddleware("email", strategy="redact", apply_to_input=True),        # che hẳn email trong tin người dùng
        PIIMiddleware("credit_card", strategy="mask", apply_to_input=True),    # số thẻ chỉ để lộ 4 số cuối
    ],
)
```

**Kết quả in ra** (dựng lại) — dựng từ mô tả bằng chữ của bốn chiến lược, tài liệu không in ví dụ:

```
input:    "Email tôi là an@vd.vn, thẻ 4111-1111-1111-1234"   ← nguyên văn người dùng gõ
output:   "Email tôi là [REDACTED_EMAIL], thẻ ****-****-****-1234"
                        └ strategy="redact" thay bằng nhãn    ← đúng khuôn [REDACTED_{PII_TYPE}]
                                                └ strategy="mask" giữ 4 số cuối   ← che một phần
```

Đây là chỗ rủi ro nhất trong file: khuôn `[REDACTED_{PII_TYPE}]` và dạng `****-****-****-1234` lấy đúng từ tài liệu, nhưng cách hai chiến lược trộn trong cùng một câu là tôi ghép lại. Phải chạy thử mới biết chính xác.

**Bảng tham số của `PIIMiddleware`**

| Tham số | Kiểu / mặc định | Chứa gì |
|---|---|---|
| `pii_type` | `string`, bắt buộc | Loại dựng sẵn (`email`, `credit_card`, `ip`, `mac_address`, `url`) hoặc tên loại tự đặt |
| `strategy` | `string`, mặc định `redact` | `'block'` ném lỗi, `'redact'` thay bằng `[REDACTED_{PII_TYPE}]`, `'mask'` che một phần, `'hash'` thay bằng chuỗi băm cố định |
| `detector` | hàm hoặc regex | Bộ dò riêng. Bỏ trống thì dùng bộ dò sẵn của loại đó |
| `apply_to_input` | `boolean`, mặc định `True` | Kiểm tin nhắn người dùng trước khi gọi model |
| `apply_to_output` | `boolean`, mặc định `False` | Kiểm tin nhắn AI sau khi gọi model |
| `apply_to_tool_results` | `boolean`, mặc định `False` | Kiểm kết quả tool sau khi chạy |

**!Note:** Hai tham số `apply_to_output` và `apply_to_tool_results` mặc định là `False`. Nghĩa là mặc định **chỉ đầu vào được kiểm**. Kết quả tool trả về số thẻ từ cơ sở dữ liệu vẫn đi thẳng vào ngữ cảnh và vào log.

### Tự viết bộ dò cho loại thông tin riêng

Tài liệu nêu ba cách truyền `detector`, đánh số 1 và 2 rồi liệt kê ba khối mã — cách đánh số trong bản gốc không khớp với số khối, điểm này để ngỏ. Ba khối mã là: chuỗi regex, regex đã biên dịch, và hàm tự viết.

```python
PIIMiddleware(
    "api_key",
    detector=r"sk-[a-zA-Z0-9]{32}",       # cách 1: chuỗi regex, dùng cho mẫu đơn giản
    strategy="block",                      # gặp là ném lỗi, không cho đi tiếp
)

PIIMiddleware(
    "phone_number",
    detector=re.compile(r"\+?\d{1,3}[\s.-]?\d{3,4}[\s.-]?\d{4}"),   # cách 2: regex đã biên dịch, dùng khi cần cờ
    strategy="mask",
)
```

```python
def detect_ssn(content: str) -> list[dict[str, str | int]]:
    """Detect SSN with validation."""
    import re
    matches = []
    pattern = r"\d{3}-\d{2}-\d{4}"
    for match in re.finditer(pattern, content):          # duyệt mọi chỗ khớp mẫu trong chuỗi
        ssn = match.group(0)
        first_three = int(ssn[:3])                       # ba số đầu quyết định mã có hợp lệ không
        if first_three not in [0, 666] and not (900 <= first_three <= 999):   # loại các dải không tồn tại
            matches.append({
                "text": ssn,                             # nguyên văn đoạn khớp
                "start": match.start(),                  # vị trí bắt đầu trong chuỗi gốc
                "end": match.end(),                      # vị trí kết thúc
            })
    return matches                                       # trả danh sách; rỗng nghĩa là không tìm thấy gì
```

Hàm dò tự viết nhận vào một chuỗi và trả về danh sách các từ điển có đúng ba khóa `text`, `start`, `end`. Dùng chuỗi regex cho mẫu đơn giản, dùng đối tượng regex khi cần cờ (ví dụ bỏ qua hoa thường), dùng hàm khi phải kiểm tra tính hợp lệ ngoài việc khớp mẫu.

**!Note:** Ví dụ trên có một chỗ lệch giữa chú thích và mã: phần chú thích nói ba số đầu không được là `000`, `666` hoặc `900-999`, nhưng mã so sánh với `[0, 666]` — `int("000")` cho ra `0` nên vẫn khớp ý định. Chép nguyên sang loại mã khác mà giữ cách so sánh này thì dễ sai.

---

## 8. To-do list — cấp cho agent một danh sách việc

**Khái niệm.** `TodoListMiddleware` trang bị cho agent năng lực lập kế hoạch và theo dõi tiến độ, bằng cách tự thêm một tool `write_todos` cộng phần prompt hệ thống hướng dẫn cách dùng.

**Vai trò.** Việc nhiều bước thì agent dễ làm một nửa rồi quên nửa còn lại. Danh sách việc biến kế hoạch thành thứ nằm trong ngữ cảnh, model đọc lại được ở mỗi lượt.

**Triển khai.**

```python
from langchain.agents import create_agent
from langchain.agents.middleware import TodoListMiddleware

agent = create_agent(
    model="gpt-5.4",
    tools=[read_file, write_file, run_tests],
    middleware=[TodoListMiddleware()],      # không cần tham số, tool write_todos được thêm tự động
)
```

| Tham số | Kiểu | Chứa gì |
|---|---|---|
| `system_prompt` | `string` | Prompt hệ thống riêng hướng dẫn cách dùng danh sách việc. Bỏ trống thì dùng bản dựng sẵn |
| `tool_description` | `string` | Mô tả riêng cho tool `write_todos`. Bỏ trống thì dùng bản dựng sẵn |

---

## 9. LLM tool selector — để một model nhỏ lọc tool trước

**Khái niệm.** `LLMToolSelectorMiddleware` dùng một LLM để chọn ra nhóm tool có liên quan trước khi gọi model chính.

**Vai trò.** Agent có 30 tool thì mô tả của cả 30 tool nằm trong mỗi lệnh gọi model — vừa tốn token vừa làm model chọn sai. Bản này cắt danh sách xuống còn vài tool trước khi model chính nhìn thấy.

**Áp dụng thực tế.** Agent nội bộ nối vào 24 hệ thống: nhân sự, kế toán, kho, CRM. Câu hỏi "còn bao nhiêu ngày phép" chỉ cần 2 tool, nhưng mô tả của 24 tool vẫn đi kèm mỗi lượt.

Cơ chế: bản này dùng đầu ra có cấu trúc để hỏi một LLM xem tool nào liên quan tới câu hỏi hiện tại. Khuôn đầu ra có cấu trúc chứa tên và mô tả các tool đang có. Các nhà cung cấp model thường tự nhét phần thông tin cấu trúc này vào prompt hệ thống ở phía sau.

**Triển khai.**

```python
from langchain.agents import create_agent
from langchain.agents.middleware import LLMToolSelectorMiddleware

agent = create_agent(
    model="gpt-5.4",
    tools=[tool1, tool2, tool3, tool4, tool5, ...],
    middleware=[
        LLMToolSelectorMiddleware(
            model="gpt-5.4-mini",          # model làm việc lọc, nên chọn bản rẻ
            max_tools=3,                   # model chính chỉ thấy tối đa 3 tool
            always_include=["search"],     # tool này luôn có mặt, không tính vào max_tools
        ),
    ],
)
```

| Tham số | Kiểu / mặc định | Chứa gì |
|---|---|---|
| `model` | `string \| BaseChatModel` | Model làm việc chọn. Mặc định lấy chính model của agent |
| `system_prompt` | `string` | Hướng dẫn cho model chọn. Bỏ trống thì dùng bản dựng sẵn |
| `max_tools` | số | Trần số tool được chọn. Model chọn thừa thì chỉ lấy `max_tools` đầu tiên. Bỏ trống là không giới hạn |
| `always_include` | `list[string]` | Tool luôn được giữ, không tính vào `max_tools` |

**!Note:** Model chọn nhiều hơn `max_tools` thì phần thừa bị cắt theo **thứ tự trả về**, không theo mức liên quan. Tool cần thiết đứng thứ tư trong danh sách model trả về sẽ bị loại mà không có cảnh báo nào.

---

## 10. Tool retry — thử lại tool hỏng

**Khái niệm.** `ToolRetryMiddleware` tự gọi lại tool khi tool ném lỗi, mỗi lần chờ lâu hơn lần trước theo cấp số nhân (tài liệu gọi là *exponential backoff*).

**Vai trò.** Phần lớn lỗi của tool gọi mạng là lỗi nhất thời: nghẽn, quá tần suất, hết giờ chờ. Thử lại sau một hai giây là xong. Không có bản này thì mỗi lỗi nhất thời đều biến thành một lượt model phải xử lý.

**Áp dụng thực tế.** Tool tra giá chứng khoán gọi API của bên thứ ba. Vào phiên, cứ 20 lượt thì có 1 lượt trả về mã 429 vì quá tần suất. Không thử lại thì model nhận về chuỗi lỗi, tưởng mã đó không tồn tại, rồi trả lời sai cho người dùng.

**Triển khai.**

```python
from langchain.agents import create_agent
from langchain.agents.middleware import ToolRetryMiddleware

agent = create_agent(
    model="gpt-5.4",
    tools=[search_tool, database_tool, api_tool],
    middleware=[
        ToolRetryMiddleware(
            max_retries=3,                              # thử lại tối đa 3 lần sau lần gọi đầu
            backoff_factor=2.0,                         # mỗi lần chờ gấp đôi lần trước
            initial_delay=1.0,                          # lần chờ đầu tiên là 1 giây
            max_delay=60.0,                             # chờ lâu nhất 60 giây, không tăng nữa
            jitter=True,                                # cộng dao động ngẫu nhiên ±25%
            tools=["api_tool"],                         # chỉ áp cho tool này, các tool khác không thử lại
            retry_on=(ConnectionError, TimeoutError),   # chỉ thử lại hai loại lỗi này
            on_failure="continue",
        ),
    ],
)
```

**Bảng tham số của `ToolRetryMiddleware`**

| Tham số | Kiểu / mặc định | Chứa gì |
|---|---|---|
| `max_retries` | số, mặc định `2` | Số lần thử lại sau lần gọi đầu (mặc định là 3 lượt tất cả) |
| `tools` | `list[BaseTool \| str]` | Danh sách tool áp dụng. `None` thì áp cho mọi tool |
| `retry_on` | tuple lớp lỗi hoặc hàm, mặc định `(Exception,)` | Loại lỗi cần thử lại, hoặc hàm nhận lỗi và trả `True` nếu nên thử lại |
| `on_failure` | `string` hoặc hàm, mặc định `return_message` | `'return_message'` trả `ToolMessage` kèm chi tiết lỗi để model tự xử; `'raise'` ném lại lỗi và dừng agent; hoặc hàm nhận lỗi trả về chuỗi làm nội dung `ToolMessage` |
| `backoff_factor` | số, mặc định `2.0` | Hệ số nhân. Mỗi lần thử lại chờ `initial_delay * (backoff_factor ** retry_number)` giây. Đặt `0.0` để chờ đều nhau |
| `initial_delay` | số, mặc định `1.0` | Số giây chờ trước lần thử lại đầu tiên |
| `max_delay` | số, mặc định `60.0` | Trần số giây chờ giữa hai lần thử |
| `jitter` | `boolean`, mặc định `true` | Cộng dao động ngẫu nhiên `±25%` vào thời gian chờ, tránh cả đàn cùng gọi lại một lúc |

**!Note:** Ví dụ đầy đủ trong tài liệu truyền `on_failure="continue"`, nhưng bảng tham số của chính `ToolRetryMiddleware` chỉ liệt kê `'return_message'` và `'raise'` — `'continue'` là giá trị của `ModelRetryMiddleware`. Chỗ này trong tài liệu tự mâu thuẫn, phải chạy thử mới biết giá trị nào được chấp nhận.

---

## 11. Model retry — thử lại lệnh gọi model hỏng

**Khái niệm.** `ModelRetryMiddleware` làm đúng việc của mục 10 nhưng cho lệnh gọi model thay vì lệnh gọi tool.

**Vai trò.** API của model cũng nghẽn và cũng chặn theo tần suất. Đây là bản đối xứng để agent không chết vì một lỗi 503.

**Triển khai.**

```python
from langchain.agents.middleware import ModelRetryMiddleware

def should_retry(error: Exception) -> bool:
    if isinstance(error, TimeoutError):          # hết giờ chờ thì luôn thử lại
        return True
    if hasattr(error, "status_code"):            # lỗi HTTP thì xét theo mã trả về
        return error.status_code in (429, 503)   # 429 quá tần suất, 503 dịch vụ không sẵn sàng
    return False                                 # còn lại thì không thử lại

retry_with_filter = ModelRetryMiddleware(
    max_retries=3,
    retry_on=should_retry,                       # truyền hàm thay vì tuple lớp lỗi
)

constant_backoff = ModelRetryMiddleware(
    max_retries=5,
    backoff_factor=0.0,                          # tắt tăng theo cấp số nhân
    initial_delay=2.0,                           # lần nào cũng chờ đúng 2 giây
)
```

Bảng tham số trùng với `ToolRetryMiddleware` ở `max_retries`, `retry_on`, `backoff_factor`, `initial_delay`, `max_delay`, `jitter`. Khác ở hai điểm: không có tham số `tools`, và `on_failure` có bộ giá trị riêng.

| `on_failure` | Hành vi khi hết lượt thử |
|---|---|
| `'continue'` (mặc định) | Trả về một `AIMessage` kèm chi tiết lỗi, agent chạy tiếp và tự xoay xở |
| `'error'` | Ném lại lỗi, dừng agent |
| hàm tự viết | Nhận lỗi, trả về chuỗi làm nội dung `AIMessage` |

**!Note:** Hai bản retry đặt tên giá trị khác nhau cho cùng một ý. `ToolRetryMiddleware` dùng `'return_message'` và `'raise'`; `ModelRetryMiddleware` dùng `'continue'` và `'error'`. Chép cấu hình từ bản này sang bản kia sẽ hỏng.

---

## 12. LLM tool emulator — giả lập kết quả tool khi kiểm thử

**Khái niệm.** `LLMToolEmulator` thay việc chạy tool thật bằng một câu trả lời do LLM bịa ra cho hợp lý.

**Vai trò.** Kiểm thử luồng agent mà không muốn thật sự gửi thư, thật sự ghi vào cơ sở dữ liệu, hoặc khi tool chưa được viết xong.

**Áp dụng thực tế.** Dựng khung một agent đặt lịch trước khi bên IT mở quyền vào hệ thống lịch. Toàn bộ luồng hội thoại được kiểm thử với kết quả tool do model bịa, chỉ phần cuối là chờ tool thật.

**Triển khai.**

```python
from langchain.agents import create_agent
from langchain.agents.middleware import LLMToolEmulator

agent = create_agent(
    model="gpt-5.4",
    tools=[get_weather, send_email],
    middleware=[LLMToolEmulator()],                          # không truyền gì = giả lập TẤT CẢ tool
)

agent2 = create_agent(
    model="gpt-5.4",
    tools=[get_weather, send_email],
    middleware=[LLMToolEmulator(tools=["get_weather"])],     # chỉ giả lập tool được nêu tên
)

agent4 = create_agent(
    model="gpt-5.4",
    tools=[get_weather, send_email],
    middleware=[LLMToolEmulator(model="claude-sonnet-4-6")], # dùng model khác để bịa kết quả
)
```

| Tham số | Kiểu | Chứa gì |
|---|---|---|
| `tools` | `list[str \| BaseTool]` | `None` (mặc định) giả lập **mọi** tool; `[]` không giả lập tool nào; danh sách thì chỉ giả lập những tool trong đó |
| `model` | `string \| BaseChatModel` | Model sinh kết quả giả. Mặc định lấy model của agent |

**!Note:** Mặc định là giả lập **tất cả** tool. Gắn bản này vào rồi quên gỡ trước khi lên môi trường thật thì agent chạy trơn tru, trả lời trôi chảy, và không có tool nào thật sự chạy.

---

## 13. Context editing — xóa bớt kết quả tool cũ

**Khái niệm.** `ContextEditingMiddleware` xóa kết quả của các lệnh gọi tool cũ khi số token chạm ngưỡng, giữ lại N kết quả gần nhất.

**Vai trò.** Khác với tóm tắt ở mục 2: tóm tắt nén cả hội thoại lại thành văn xuôi, còn bản này chỉ nhắm vào kết quả tool. Kết quả tool là thứ dài nhất và mau cũ nhất trong ngữ cảnh — một lượt tìm kiếm trả về 3000 token mà chỉ có giá trị trong đúng lượt đó.

**Áp dụng thực tế.** Agent rà soát hợp đồng đọc lần lượt 40 file, mỗi lần đọc trả về 2000 token nguyên văn. Đến file thứ 15 thì cửa sổ ngữ cảnh đầy bởi 14 nội dung file mà agent đã tóm tắt xong và không cần nữa.

**Triển khai.**

```python
from langchain.agents import create_agent
from langchain.agents.middleware import ContextEditingMiddleware, ClearToolUsesEdit

agent = create_agent(
    model="gpt-5.4",
    tools=[search_tool, your_calculator_tool, database_tool],
    middleware=[
        ContextEditingMiddleware(
            edits=[
                ClearToolUsesEdit(
                    trigger=2000,               # chạm 2000 token thì bắt đầu xóa
                    keep=3,                     # 3 kết quả tool gần nhất không bao giờ bị xóa
                    clear_tool_inputs=False,    # giữ lại tham số của lệnh gọi, chỉ xóa kết quả
                    exclude_tools=[],           # không tool nào được miễn trừ
                    placeholder="[cleared]",    # chuỗi thay vào chỗ nội dung đã xóa
                ),
            ],
        ),
    ],
)
```

**Kết quả in ra** (dựng lại) — dựng từ mô tả bốn bước xử lý trong tài liệu:

```
ToolMessage(read_file, "Điều 5. Bên A có nghĩa vụ...")   ← kết quả cũ nhất, bị xóa trước
   ↓ sau khi chạm ngưỡng
ToolMessage(read_file, "[cleared]")                       ← nội dung thay bằng placeholder
ToolMessage(read_file, "Điều 12. Thời hạn...")            ← nằm trong 3 kết quả gần nhất, giữ nguyên
ToolMessage(read_file, "Điều 18. Chấm dứt...")            ← như trên
ToolMessage(search,    "3 kết quả khớp...")               ← như trên
```

Bốn bước tài liệu mô tả: theo dõi số token trong hội thoại; chạm ngưỡng thì xóa kết quả tool cũ; giữ lại N kết quả gần nhất; tùy chọn giữ lại tham số của lệnh gọi để còn hiểu ngữ cảnh.

**Bảng tham số**

| Tham số | Kiểu / mặc định | Thuộc về | Chứa gì |
|---|---|---|---|
| `edits` | `list[ContextEdit]`, mặc định `[ClearToolUsesEdit()]` | `ContextEditingMiddleware` | Danh sách chiến lược xóa cần áp dụng |
| `token_count_method` | `string`, mặc định `approximate` | `ContextEditingMiddleware` | `'approximate'` hoặc `'model'` |
| `trigger` | số, mặc định `100000` | `ClearToolUsesEdit` | Ngưỡng token kích hoạt việc xóa |
| `clear_at_least` | số, mặc định `0` | `ClearToolUsesEdit` | Số token tối thiểu phải thu hồi mỗi lần chạy. `0` nghĩa là xóa vừa đủ |
| `keep` | số, mặc định `3` | `ClearToolUsesEdit` | Số kết quả tool gần nhất không bao giờ bị xóa |
| `clear_tool_inputs` | `boolean`, mặc định `False` | `ClearToolUsesEdit` | `True` thì tham số của lệnh gọi trên tin nhắn AI bị thay bằng đối tượng rỗng |
| `exclude_tools` | `list[string]`, mặc định `()` | `ClearToolUsesEdit` | Tên các tool không bao giờ bị xóa kết quả |
| `placeholder` | `string`, mặc định `[cleared]` | `ClearToolUsesEdit` | Chuỗi thay vào chỗ nội dung đã xóa |

---

## 14. Shell tool — mở một phiên shell chạy suốt

**Khái niệm.** `ShellToolMiddleware` cấp cho agent một phiên shell duy trì qua nhiều lệnh, để chạy lệnh hệ thống tuần tự.

**Vai trò.** Có việc chỉ làm được bằng dòng lệnh: chạy kiểm thử, dựng gói, thao tác file hàng loạt. Phiên chạy suốt nghĩa là thư mục hiện tại và biến môi trường được giữ giữa các lệnh, không phải khai lại mỗi lượt.

**Triển khai.**

```python
from langchain.agents import create_agent
from langchain.agents.middleware import (
    ShellToolMiddleware,
    HostExecutionPolicy,
    DockerExecutionPolicy,
    RedactionRule,
)

agent_docker = create_agent(
    model="gpt-5.4",
    tools=[],
    middleware=[
        ShellToolMiddleware(
            workspace_root="/workspace",                       # thư mục gốc của phiên shell
            startup_commands=["pip install requests",          # chạy tuần tự ngay sau khi mở phiên
                              "export PYTHONPATH=/workspace"],
            execution_policy=DockerExecutionPolicy(
                image="python:3.11-slim",                       # mỗi lần chạy agent là một container riêng
                command_timeout=60.0,                           # lệnh quá 60 giây thì cắt
            ),
        ),
    ],
)
```

**Bảng tham số của `ShellToolMiddleware`**

| Tham số | Kiểu | Chứa gì |
|---|---|---|
| `workspace_root` | `str \| Path \| None` | Thư mục gốc của phiên. Bỏ trống thì một thư mục tạm được tạo lúc agent khởi động và xóa khi agent kết thúc |
| `startup_commands` | tuple / list / str / `None` | Lệnh chạy tuần tự sau khi mở phiên |
| `shutdown_commands` | tuple / list / str / `None` | Lệnh chạy trước khi đóng phiên |
| `execution_policy` | `BaseExecutionPolicy \| None` | Chính sách chạy, xem bảng dưới |
| `redaction_rules` | tuple / list `RedactionRule` / `None` | Quy tắc che đầu ra lệnh trước khi trả về cho model |
| `tool_description` | `str \| None` | Mô tả riêng cho tool shell |
| `shell_command` | `Sequence[str] \| str \| None` | Chương trình shell dùng để mở phiên. Mặc định `/bin/bash` |
| `env` | `Mapping[str, Any] \| None` | Biến môi trường cấp cho phiên. Giá trị được ép về chuỗi trước khi chạy |

| Chính sách chạy | Mức cô lập |
|---|---|
| `HostExecutionPolicy` (mặc định) | Quyền đầy đủ trên máy chủ. Hợp với môi trường tin cậy, khi agent vốn đã chạy trong container hoặc máy ảo |
| `DockerExecutionPolicy` | Mở một container Docker riêng cho mỗi lần chạy agent, cô lập chặt hơn |
| `CodexSandboxExecutionPolicy` | Dùng lại sandbox của Codex CLI, siết thêm ở tầng lời gọi hệ thống và hệ thống file |

**!Note:** Quy tắc che (`redaction_rules`) chạy **sau khi lệnh đã thực thi**. Nó không ngăn được việc dữ liệu bí mật bị đưa ra ngoài khi dùng `HostExecutionPolicy` — nó chỉ làm sạch phần văn bản trả về cho model.

**!Note:** Phiên shell chạy suốt hiện **không dùng được** cùng tín hiệu dừng chờ người duyệt (mục 3). Tài liệu ghi đây là hạn chế đang chờ bổ sung. Ai định vừa cho agent chạy lệnh vừa bắt duyệt từng lệnh thì phương án này chưa dùng được.

---

## 15. File search — tìm file theo tên và theo nội dung

**Khái niệm.** `FilesystemFileSearchMiddleware` thêm hai tool tìm kiếm trên hệ thống file: `glob_search` tìm theo mẫu tên file, `grep_search` tìm theo nội dung bằng regex.

**Vai trò.** Agent làm việc trên một kho mã lớn cần biết file nào tồn tại trước khi đọc. Không có tool tìm thì agent phải đoán đường dẫn.

**Triển khai.**

```python
from langchain.agents import create_agent
from langchain.agents.middleware import FilesystemFileSearchMiddleware
from langchain.messages import HumanMessage

agent = create_agent(
    model="gpt-5.4",
    tools=[],
    middleware=[
        FilesystemFileSearchMiddleware(
            root_path="/workspace",      # mọi thao tác file tính tương đối so với đường dẫn này
            use_ripgrep=True,            # dùng ripgrep cho nhanh, thiếu thì lùi về regex của Python
            max_file_size_mb=10,         # file lớn hơn 10MB thì bỏ qua
        ),
    ],
)

result = agent.invoke({
    "messages": [HumanMessage("Find all Python files containing 'async def'")]
})
# Agent sẽ tự dùng:
# 1. glob_search(pattern="**/*.py")                       tìm file Python
# 2. grep_search(pattern="async def", include="*.py")     tìm hàm bất đồng bộ trong số đó
```

| Tham số | Kiểu / mặc định | Chứa gì |
|---|---|---|
| `root_path` | `str`, bắt buộc | Thư mục gốc để tìm |
| `use_ripgrep` | `bool`, mặc định `True` | Dùng ripgrep. Không có ripgrep thì lùi về regex của Python |
| `max_file_size_mb` | `int`, mặc định `10` | Trần dung lượng file được tìm, tính bằng MB |

Tool `glob_search` nhận mẫu dạng `**/*.py` hoặc `src/**/*.ts`, trả về danh sách đường dẫn sắp theo thời gian sửa. Tool `grep_search` hỗ trợ đầy đủ cú pháp regex, lọc theo mẫu file qua tham số `include`, và có ba kiểu đầu ra: `files_with_matches`, `content`, `count`.

---

## 16. Filesystem — hệ thống file làm nơi ghi nhớ

**Khái niệm.** `FilesystemMiddleware` đến từ gói Deep Agents, cấp bốn tool để agent đọc ghi file: `ls` liệt kê, `read_file` đọc cả file hoặc một số dòng, `write_file` ghi file mới, `edit_file` sửa file đã có.

**Vai trò.** Tài liệu nêu thẳng vấn đề: tool trả về kết quả dài ngắn không đoán trước được — `web_search` và RAG là hai ví dụ — và kết quả dài làm đầy cửa sổ ngữ cảnh rất nhanh. Ghi ra file rồi đọc lại từng phần là cách né chuyện đó.

**Triển khai.**

```python
from langchain.agents import create_agent
from deepagents.middleware.filesystem import FilesystemMiddleware

# FilesystemMiddleware đã nằm sẵn trong create_deep_agent; đoạn này dành cho agent tự dựng.
agent = create_agent(
    model="claude-sonnet-4-6",
    middleware=[
        FilesystemMiddleware(
            backend=None,                                    # None thì dùng StateBackend, ghi vào trạng thái graph
            system_prompt="Write to the filesystem when...", # phần thêm vào prompt hệ thống
            custom_tool_descriptions={                       # mô tả riêng cho từng tool
                "ls": "Use the ls tool when...",
                "read_file": "Use the read_file tool to..."
            }
        ),
    ],
)
```

### Trí nhớ ngắn hạn và trí nhớ dài hạn

**Khái niệm.** Mặc định bốn tool trên ghi vào một "hệ thống file" nằm trong trạng thái của graph — mất khi thread kết thúc. Muốn dữ liệu sống qua nhiều thread thì cấu hình một `CompositeBackend` để dẫn một số đường dẫn (ví dụ `/memories/`) sang `StoreBackend`.

**Vai trò.** Đây là ranh giới giữa "ghi tạm để khỏi phình ngữ cảnh" và "nhớ lâu dài về người dùng này".

```python
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

agent = create_agent(
    model="claude-sonnet-4-6",
    store=store,                                          # kho lưu dài hạn, khai ở cấp agent
    middleware=[
        FilesystemMiddleware(
            backend=CompositeBackend(
                default=StateBackend(),                   # mặc định ghi vào trạng thái, mất theo thread
                routes={"/memories/": StoreBackend()}     # riêng /memories/ thì ghi vào kho lâu dài
            ),
        ),
    ],
)
```

**!Note:** Ranh giới nằm ở tiền tố đường dẫn, không nằm ở tên tool. File có tiền tố `/memories/` được lưu lâu dài và sống qua các thread khác nhau; file không có tiền tố này nằm trong trạng thái tạm. Agent ghi nhầm `/memory/note.md` thay vì `/memories/note.md` thì lệnh ghi vẫn thành công, chỉ là hôm sau không còn gì.

---

## 17. Subagent — giao việc cho agent con

**Khái niệm.** `SubAgentMiddleware`, cũng từ Deep Agents, cấp một tool `task` để agent chính giao việc cho các agent con.

**Vai trò.** Giao việc cho agent con là cách cô lập ngữ cảnh: agent chính chỉ nhận về câu trả lời gọn, không phải nuốt toàn bộ các lệnh gọi tool trung gian của việc đó.

**Triển khai.**

```python
from langchain.tools import tool
from langchain.agents import create_agent
from deepagents.middleware.subagents import SubAgentMiddleware

@tool
def get_weather(city: str) -> str:
    """Get the weather in a city."""
    return f"The weather in {city} is sunny."

agent = create_agent(
    model="claude-sonnet-4-6",
    middleware=[
        SubAgentMiddleware(
            default_model="claude-sonnet-4-6",      # model mặc định cho các agent con
            default_tools=[],                       # tool mặc định cho các agent con
            subagents=[
                {
                    "name": "weather",                                       # tên agent chính dùng để gọi
                    "description": "This subagent can get weather in cities.",  # mô tả để agent chính biết khi nào gọi
                    "system_prompt": "Use the get_weather tool to get the weather in a city.",
                    "tools": [get_weather],                                  # tool riêng của agent con
                    "model": "gpt-5.4",                                      # model riêng, đè lên default_model
                    "middleware": [],                                        # middleware riêng của agent con
                }
            ],
        )
    ],
)
```

Một agent con được định nghĩa bằng bốn thứ: **name**, **description**, **system prompt**, **tools**. Thêm được **model** riêng và **middleware** riêng — phần middleware riêng có ích khi muốn cấp cho agent con một khóa trạng thái dùng chung với agent chính.

Việc phức tạp hơn thì truyền vào một graph LangGraph đã dựng sẵn, bọc trong `CompiledSubAgent`:

```python
from deepagents import CompiledSubAgent

weather_subagent = CompiledSubAgent(
    name="weather",
    description="This subagent can get weather in cities.",
    runnable=weather_graph,        # graph đã compile, thay cho phần khai báo bằng từ điển
)
```

**!Note:** Ngoài các agent con tự khai, agent chính **luôn** có sẵn một agent con `general-purpose`. Agent con này mang đúng chỉ dẫn và đúng bộ tool của agent chính. Mục đích của nó là cô lập ngữ cảnh: giao một việc rắc rối cho nó rồi nhận về câu trả lời gọn, không kèm rác từ các lệnh gọi tool trung gian.

---

## 18. Middleware theo nhà cung cấp

Ba bộ riêng, mỗi bộ có trang tài liệu riêng. Trang này chỉ nêu tên và đặt link nên file này cũng dừng ở đó.

| Nhà cung cấp | Nội dung |
|---|---|
| Anthropic | Đệm prompt, tool bash, trình soạn văn bản, bộ nhớ, và tìm kiếm file cho các model Claude |
| AWS | Đệm prompt cho model trên Amazon Bedrock |
| OpenAI | Kiểm duyệt nội dung cho model OpenAI |

Đường dẫn: `https://docs.langchain.com/oss/python/integrations/middleware/<tên nhà cung cấp>`.

---

## 19. Chọn bản nào cho việc gì

Ngữ cảnh phình to: dùng [`SummarizationMiddleware`](#2-summarization--tóm-tắt-hội-thoại-khi-sắp-chạm-trần-token) khi cần giữ ý của cả cuộc trao đổi, dùng [`ContextEditingMiddleware`](#13-context-editing--xóa-bớt-kết-quả-tool-cũ) khi thứ chiếm chỗ là kết quả tool và những kết quả đó hết giá trị ngay sau khi dùng. Hai bản này gắn được cùng lúc, tài liệu không nêu xung đột nào.

Chặn chi phí: [`ModelCallLimitMiddleware`](#4-model-call-limit--chặn-trần-số-lần-gọi-model) chặn ở phía model, [`ToolCallLimitMiddleware`](#5-tool-call-limit--chặn-trần-số-lần-gọi-tool) chặn ở phía tool và chặn được riêng từng tool. Cả hai đều cần `checkpointer` nếu muốn đếm theo thread.

Chống hỏng hóc: [`ToolRetryMiddleware`](#10-tool-retry--thử-lại-tool-hỏng) và [`ModelRetryMiddleware`](#11-model-retry--thử-lại-lệnh-gọi-model-hỏng) xử lý lỗi nhất thời, [`ModelFallbackMiddleware`](#6-model-fallback--đổi-sang-model-khác-khi-model-chính-hỏng) xử lý lỗi kéo dài của cả một nhà cung cấp.


...........

---

## Tham chiếu chéo

- [03-03 Middleware tổng quan](./03-03-middleware-overview.md) — cách gắn các bản này vào `create_agent`
- [03-05 Custom middleware](./03-05-middleware-custom.md) — hook và thứ tự chạy, cần đọc khi gắn nhiều bản cùng lúc
- Trang Human-in-the-loop: `https://docs.langchain.com/oss/python/langchain/human-in-the-loop`
- Trang Deep Agents: `https://docs.langchain.com/oss/python/deepagents/overview`
- Trang gốc: `https://docs.langchain.com/oss/python/langchain/middleware/built-in`