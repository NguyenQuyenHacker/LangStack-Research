---
title: Integration testing
doc_source: https://docs.langchain.com/oss/python/langchain/test/integration-testing
accessed: 2026-07-25
lc_version: unknown
status: draft
lab:
related:
  - ./test-01-tong-quan.md
  - ./test-02-unit-testing.md
  - ./test-04-evals.md
---

# Integration testing

> Kiểm thử agent với API model thật: tách khỏi unit test, quản API key, khẳng định theo cấu trúc, kiểm soát chi phí, và ghi lại/phát lại lời gọi HTTP.
> Khác [unit test](./test-02-unit-testing.md) ở chỗ gọi mạng thật; khác [evals](./test-04-evals.md) ở chỗ chỉ kiểm đúng/sai cơ bản chứ không chấm điểm chất lượng.

---

## 1. Tổng quan

Integration test kiểm agent chạy đúng khi ráp với API model và dịch vụ ngoài. Khác unit test (dùng bản giả), nó **gọi mạng thật** để xác nhận: các thành phần ăn khớp, key hợp lệ, độ trễ chịu được.

Vì câu trả lời của LLM không tất định, integration test cần chiến lược khác test phần mềm thường. Trang này gom năm việc: tách test, quản key, khẳng định thế nào, giảm chi phí, và ghi/phát lại HTTP.

---

## 2. Tách unit test và integration test

### Khái niệm

Đánh **nhãn (marker)** cho integration test bằng `pytest` để tách nó khỏi unit test, và mặc định **không chạy** nhóm này.

### Vai trò

Integration test chậm và cần API key. Nếu để lẫn với unit test thì mỗi lần lưu file đều chạy cả nhóm chậm và tốn tiền. Tách ra để: unit test chạy mỗi lần sửa, integration test chỉ chạy trong CI hoặc trước khi deploy.

### Áp dụng thực tế

Nhóm bạn commit hàng chục lần một ngày. Mỗi lần lưu file, bộ test tự chạy. Nếu integration test không tách, mỗi lần lưu là vài lời gọi API thật — cuối tháng hóa đơn phồng lên vì test, không phải vì production.

### Triển khai

```python
import pytest

@pytest.mark.integration                                                         # dán nhãn "integration" lên test này
def test_agent_with_real_model():
    agent = create_agent("claude-sonnet-4-6", tools=[get_weather])               # model thật, gọi API thật
    result = agent.invoke({
        "messages": [HumanMessage(content="What's the weather in SF?")]
    })
    assert len(result["messages"]) > 1                                           # có nhiều hơn 1 message → agent đã làm gì đó, không chỉ echo
```

Khai báo nhãn cho `pytest` và loại nhóm này khỏi lần chạy mặc định:

```ini
# pytest.ini
[pytest]
markers =
    integration: tests that call real LLM APIs
addopts = -m "not integration"                                                   # mặc định: chạy mọi test TRỪ nhóm integration
```

```toml
# pyproject.toml (cách khác, tương đương)
[tool.pytest.ini_options]
markers = [
  "integration: tests that call real LLM APIs"
]
addopts = "-m 'not integration'"
```

Khi cần, gọi nhóm integration một cách tường minh:

```bash
pytest -m integration                                                            # chỉ chạy nhóm có nhãn integration
```

**!Note:** Model `claude-sonnet-4-6` trong ví dụ là chuỗi định danh model của tài liệu. Chuỗi model đổi theo thời điểm và theo nhà cung cấp — dùng đúng model bạn có quyền truy cập, đừng chép cứng.

---

## 3. Quản lý API key

### Khái niệm

Integration test cần key thật. Nạp key từ **biến môi trường** để nó không lọt vào mã nguồn, và dùng một fixture `conftest.py` để kiểm key có tồn tại không trước khi chạy.

### Vai trò

Hai rủi ro cần chặn: (1) key bị commit lên git → lộ bí mật; (2) test chạy khi thiếu key → hỏng với lỗi khó hiểu thay vì bỏ qua gọn gàng. Fixture kiểm key giải quyết cả hai.

### Áp dụng thực tế

Đồng nghiệp mới clone repo về, chưa cấu hình key, chạy `pytest`. Nếu không có lớp kiểm key, integration test nổ với lỗi xác thực rối rắm. Có fixture kiểm key thì test tự **bỏ qua** (skip) kèm thông báo rõ "chưa đặt OPENAI_API_KEY".

### Triển khai

```python
# conftest.py
import os
import pytest

@pytest.fixture(autouse=True)                                                    # autouse=True: tự áp cho mọi test, không cần khai báo từng chỗ
def check_api_keys():
    if not os.environ.get("OPENAI_API_KEY"):                                     # đọc key từ biến môi trường, không hard-code
        pytest.skip("OPENAI_API_KEY not set")                                    # thiếu key → bỏ qua test, không để nó nổ
```

Khi phát triển ở máy cá nhân, cất key trong file `.env` rồi nạp bằng `python-dotenv`:

```bash
# .env
OPENAI_API_KEY=sk-...
```

```python
# conftest.py
from dotenv import load_dotenv

load_dotenv()                                                                    # đọc .env, nạp các biến vào môi trường tiến trình
```

**!Note:** Thêm `.env` vào `.gitignore` để không commit nhầm key. Trên CI thì không dùng `.env` — bơm key qua kho bí mật của nhà cung cấp CI (ví dụ GitHub Actions secrets).

---

## 4. Khẳng định theo cấu trúc, không theo nội dung

### Khái niệm

Câu trả lời LLM đổi mỗi lần chạy. Vì vậy đừng khẳng định "output phải bằng chuỗi X". Thay vào đó kiểm các **tính chất cấu trúc**: loại message, tên tool được gọi, hình dạng tham số, số lượng message.

### Vai trò

Khẳng định theo chuỗi chính xác sẽ hỏng ngay lần chạy sau vì model diễn đạt khác đi, dù hành vi vẫn đúng. Khẳng định theo cấu trúc bắt được cái thật sự cần kiểm (agent có gọi đúng tool không) mà không vỡ vì chữ nghĩa thay đổi.

### Áp dụng thực tế

Bạn cần chắc agent gọi tool `get_weather` khi được hỏi thời tiết. Câu chốt cuối của model có thể là "It's sunny, 75°F" hôm nay và "Currently 75 degrees and clear" ngày mai — cả hai đều đúng. Nên bạn kiểm "có tool call tên `get_weather` không" và "message cuối là `AIMessage` và có nội dung", chứ không so từng chữ.

### Triển khai

```python
def test_agent_calls_weather_tool():
    agent = create_agent("claude-sonnet-4-6", tools=[get_weather])
    result = agent.invoke({
        "messages": [HumanMessage(content="What's the weather in SF?")]
    })

    messages = result["messages"]
    tool_calls = [                                                               # gom mọi tool call rải trong các message
        tc
        for msg in messages
        if hasattr(msg, "tool_calls")                                            # chỉ message nào có thuộc tính tool_calls
        for tc in (msg.tool_calls or [])                                         # "or []" phòng tool_calls là None
    ]

    assert any(tc["name"] == "get_weather" for tc in tool_calls)                 # kiểm CÓ gọi get_weather, không kiểm gọi mấy lần
    assert isinstance(messages[-1], AIMessage)                                   # message cuối là câu của model, không phải tool
    assert len(messages[-1].content) > 0                                         # câu cuối không rỗng
```

**!Note:** `hasattr(msg, "tool_calls")` và `msg.tool_calls or []` là để phòng hai loại message khác nhau: message của người dùng / của tool không có `tool_calls`, và ngay message của model cũng có thể để `tool_calls = None` khi không gọi tool nào. Bỏ hai lớp phòng này thì test nổ `AttributeError` hoặc `TypeError` với input hợp lệ.

Với khẳng định quỹ đạo chặt chẽ hơn (khớp theo thứ tự, theo tập con...), dùng bộ evaluator của AgentEvals — xem [test-04](./test-04-evals.md).

---

## 5. Giảm chi phí và độ trễ

### Khái niệm

Integration test gọi API thật nên tốn tiền và thời gian thật. Bốn cách kìm lại.

### Vai trò

Bộ test phình to thì mỗi lần chạy CI vừa lâu vừa đắt, đến mức người ta ngại chạy. Bốn cách dưới giữ cho bộ test đủ rẻ để chạy đều.

### Bốn cách tài liệu nêu

Dùng **model nhỏ hơn** cho test chỉ cần kiểm việc gọi tool và cấu trúc câu trả lời (tài liệu nêu `gemini-3.1-flash-lite` hoặc tương đương). Chặn **độ dài câu trả lời** để tránh completion dài, đắt. **Giới hạn phạm vi** — mỗi test một hành vi, tránh kịch bản đầu-cuối xâu nhiều lời gọi model khi một lượt là đủ. **Chạy có chọn lọc** — tận dụng cách tách ở mục 2 để integration test chỉ chạy trong CI hoặc trước deploy, không chạy mỗi lần lưu file.

### Triển khai

```python
agent = create_agent(
    "gemini-3.1-flash-lite",                                                     # model nhỏ, rẻ, đủ để kiểm gọi tool + cấu trúc
    tools=[get_weather],
    model_kwargs={"max_tokens": 256},                                            # chặn câu trả lời ở 256 token → không có completion dài đắt
)
```

**!Note:** Tài liệu tự lệch tên tham số ở đây: đoạn văn viết "Set `maxTokens`" (kiểu camelCase) nhưng code lại dùng `max_tokens` (snake_case) đặt trong `model_kwargs`. Trong Python của LangChain, snake_case là dạng đúng — bám theo code, bỏ qua chữ `maxTokens` trong prose. Điểm này cần đối chiếu khi chạy thử với đúng nhà cung cấp model.

---

## 6. Ghi lại và phát lại lời gọi HTTP (VCR)

### Khái niệm

Ghi lại cặp request/response HTTP ở **lần chạy đầu**, rồi **phát lại** ở các lần sau mà không gọi mạng thật. Sau lần ghi đầu tiên, test hết tốn tiền và độ trễ.

### Vai trò

Có những test cần chạy rất thường xuyên trong CI. Gọi API thật mỗi lần thì vừa chậm vừa đắt và phụ thuộc mạng. Ghi một lần rồi phát lại giữ được tính "chạy thật" của lần đầu mà các lần sau nhanh, rẻ, ổn định.

### Áp dụng thực tế

Test kiểm quỹ đạo gọi tool của agent, chạy trên mỗi pull request. Lần đầu: gọi model thật, ghi lại toàn bộ trao đổi vào một file "cassette". Từ đó về sau, CI phát lại cassette — hàng trăm lần chạy không tốn thêm một lời gọi API nào.

### Cách dựng

Công cụ: `vcrpy` ghi cặp request/response vào file YAML gọi là **cassette**; plugin `pytest-recording` ráp nó vào `pytest`.

Trước hết, lọc thông tin nhạy cảm khỏi cassette (nếu không, key sẽ nằm nguyên trong file YAML được commit):

```python
# conftest.py
import pytest

@pytest.fixture(scope="session")
def vcr_config():
    return {
        "filter_headers": [                                                      # thay giá trị các header bí mật bằng "XXXX" trước khi ghi
            ("authorization", "XXXX"),
            ("x-api-key", "XXXX"),
        ],
        "filter_query_parameters": [                                             # thay các tham số key trên URL bằng "XXXX"
            ("api_key", "XXXX"),
            ("key", "XXXX"),
        ],
    }
```

Khai báo nhãn `vcr` cho project và đặt chế độ ghi:

```ini
# pytest.ini
[pytest]
markers =
    vcr: record/replay HTTP via VCR
addopts = --record-mode=once                                                     # "once": ghi ở lần đầu, phát lại ở các lần sau
```

```toml
# pyproject.toml (tương đương)
[tool.pytest.ini_options]
markers = [
  "vcr: record/replay HTTP via VCR"
]
addopts = "--record-mode=once"
```

Dán nhãn `vcr` lên test:

```python
@pytest.mark.vcr()                                                               # bật ghi/phát lại HTTP cho test này
def test_agent_trajectory():
    agent = create_agent("claude-sonnet-4-6", tools=[get_weather])
    result = agent.invoke({
        "messages": [HumanMessage(content="What's the weather in SF?")]
    })
    assert any(                                                                  # kiểm có tool call get_weather (khẳng định theo cấu trúc, mục 4)
        tc["name"] == "get_weather"
        for msg in result["messages"]
        if hasattr(msg, "tool_calls")
        for tc in (msg.tool_calls or [])
    )
```

Lần chạy đầu gọi mạng thật và sinh file cassette trong `tests/cassettes/`. Các lần sau phát lại từ file đó.

**!Note:** Cassette cũ thì test **hỏng im lặng theo kiểu ngược đời** — không phải sai code mà là cassette lỗi thời. Khi bạn đổi prompt, thêm tool, hoặc đổi quỹ đạo kỳ vọng, cassette đã ghi không còn khớp và test **sẽ fail**. Cách xử lý: xóa file cassette tương ứng rồi chạy lại để ghi mới. Nếu quên, bạn sẽ ngồi sửa code trong khi lỗi thật nằm ở file YAML cũ.

---

## Tham chiếu chéo

- [test-01-tong-quan.md](./test-01-tong-quan.md) — vị trí integration test trong ba cách kiểm thử
- [test-02-unit-testing.md](./test-02-unit-testing.md) — cách kiểm không gọi mạng, để đối chiếu
- [test-04-evals.md](./test-04-evals.md) — bước tiếp theo: chấm điểm quỹ đạo (khớp theo thứ tự, tập con...)
- Tài liệu gốc: `https://docs.langchain.com/oss/python/langchain/test/integration-testing`
- Hạ tầng test khi đóng góp cho chính LangChain: `https://docs.langchain.com/oss/python/contributing/code#running-tests`