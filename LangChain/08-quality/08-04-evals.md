---
title: Agent Evals
doc_source: https://docs.langchain.com/oss/python/langchain/test/evals
accessed: 2026-07-25
lc_version: unknown
status: draft
lab:
related:
  - ./08-01-testing-overview.md
  - ./08-03-integration-testing.md
---

# Agent Evals (`agentevals`)

> Chấm điểm agent bằng cách đánh giá quỹ đạo thực thi (trajectory) — chuỗi message và tool call nó sinh ra — theo hai hướng: đối chiếu tất định hoặc để LLM chấm.
> Khác [integration test](./08-03-integration-testing.md) ở chỗ không chỉ kiểm đúng/sai cơ bản mà chấm điểm hành vi theo một mốc chuẩn hoặc thang đánh giá, để bắt hồi quy khi đổi prompt/tool/model.
> URL bạn đưa (`/langchain/evals`) trỏ chuyển sang trang chuẩn này (`/langchain/test/evals`); tên trang gốc là "Agent Evals".

---

## 1. Tổng quan

Eval đo agent chạy tốt tới đâu bằng cách đánh giá **quỹ đạo thực thi**: chuỗi message và tool call mà agent tạo ra. Khác integration test (chỉ xác nhận đúng cơ bản), eval chấm điểm hành vi so với một mốc chuẩn (reference) hoặc một thang đánh giá — hữu ích để bắt hồi quy khi bạn đổi prompt, tool hay model.

Cốt lõi: một **evaluator** là một hàm nhận output của agent (và có thể nhận thêm output chuẩn) rồi trả về điểm.

```python
def evaluator(*, outputs: dict, reference_outputs: dict):                        # nhận output thật + output chuẩn để đối chiếu
    output_messages = outputs["messages"]
    reference_messages = reference_outputs["messages"]
    score = compare_messages(output_messages, reference_messages)                # compare_messages là chỗ bạn tự định nghĩa cách so
    return {"key": "evaluator_score", "score": score}                           # trả về dict có "key" (tên tiêu chí) và "score" (điểm)
```

Gói `agentevals` cho sẵn các evaluator dựng sẵn cho quỹ đạo agent, theo hai hướng:

| Hướng | Chọn khi |
|---|---|
| Trajectory match (đối chiếu quỹ đạo, tất định) | Bạn biết trước các tool call kỳ vọng, muốn kiểm nhanh, tất định, không tốn tiền |
| LLM-as-judge (để LLM chấm) | Bạn muốn đánh giá chất lượng và lập luận tổng thể mà không có kỳ vọng chặt |

---

## 2. Cài AgentEvals

```bash
pip install agentevals
```

Hoặc clone thẳng repo `agentevals` (`https://github.com/langchain-ai/agentevals`).

---

## 3. Trajectory match — đối chiếu quỹ đạo với mốc chuẩn

### Khái niệm

Hàm `create_trajectory_match_evaluator` so quỹ đạo thật của agent với một quỹ đạo chuẩn (reference) mà bạn viết sẵn. Có **bốn chế độ** khớp, đặt qua tham số `trajectory_match_mode`.

### Vai trò

Khi bạn biết trước agent *nên* gọi những tool nào, đối chiếu tất định là cách kiểm rẻ và chắc nhất: không gọi LLM chấm, chạy nhanh, kết quả không đổi giữa các lần. Bốn chế độ tồn tại vì mức độ nghiêm ngặt cần khác nhau — có lúc phải đúng thứ tự, có lúc chỉ cần đủ tool.

### Bốn chế độ khớp

| Chế độ | Khớp thế nào | Dùng khi |
|---|---|---|
| `strict` | Cùng cấu trúc message và cùng tool call, **đúng thứ tự** (nội dung chữ được phép khác) | Bắt buộc một trình tự cụ thể, ví dụ phải tra chính sách trước khi cấp phép |
| `unordered` | Cùng tool call như mốc chuẩn nhưng **thứ tự tùy ý** | Kiểm đã lấy đủ thông tin, không quan tâm thứ tự |
| `subset` | Agent chỉ gọi tool nằm trong mốc chuẩn, **không thừa** | Chắc agent không vượt phạm vi cho phép |
| `superset` | Agent gọi **ít nhất** các tool trong mốc chuẩn, cho phép thừa | Chắc các hành động tối thiểu bắt buộc đều được làm |

Các ví dụ dưới dùng chung một agent có tool `get_weather`:

```python
from langchain.agents import create_agent
from langchain.tools import tool
from langchain.messages import HumanMessage, AIMessage, ToolMessage
from agentevals.trajectory.match import create_trajectory_match_evaluator


@tool
def get_weather(city: str):
    """Get weather information for a city."""
    return f"It's 75 degrees and sunny in {city}."

agent = create_agent("claude-sonnet-4-6", tools=[get_weather])
```

### 3.1 `strict` — đúng trình tự

**Áp dụng thực tế.** Agent xử lý yêu cầu hoàn tiền phải **tra chính sách trước, rồi mới cấp phép** — không được đảo. `strict` bắt đúng trình tự này: cùng chuỗi message, cùng tool call, đúng thứ tự; chỉ chữ nghĩa trong nội dung được phép khác.

**Triển khai.**

```python
evaluator = create_trajectory_match_evaluator(
    trajectory_match_mode="strict",                                             # đòi khớp đúng thứ tự
)

def test_weather_tool_called_strict():
    result = agent.invoke({
        "messages": [HumanMessage(content="What's the weather in San Francisco?")]
    })

    reference_trajectory = [                                                     # quỹ đạo CHUẨN mình viết tay để đối chiếu
        HumanMessage(content="What's the weather in San Francisco?"),
        AIMessage(content="", tool_calls=[
            {"id": "call_1", "name": "get_weather", "args": {"city": "San Francisco"}}
        ]),
        ToolMessage(content="It's 75 degrees and sunny in San Francisco.", tool_call_id="call_1"),
        AIMessage(content="The weather in San Francisco is 75 degrees and sunny."),
    ]

    evaluation = evaluator(
        outputs=result["messages"],                                             # quỹ đạo thật của agent
        reference_outputs=reference_trajectory                                  # quỹ đạo chuẩn
    )
    assert evaluation["score"] is True                                          # khớp → score True
```

**Kết quả in ra** (tài liệu có sẵn):

```
{
    'key': 'trajectory_strict_match',   ← tên tiêu chí, khác tên ở mỗi chế độ
    'score': True,                       ← khớp đúng thứ tự → True
    'comment': None,                     ← chế độ match không kèm giải thích
}
```

### 3.2 `unordered` — đủ tool, thứ tự tùy ý

**Áp dụng thực tế.** Agent tra cả thời tiết lẫn sự kiện của một thành phố bằng hai tool khác nhau. Bạn cần chắc **cả hai** đều được gọi, nhưng gọi cái nào trước không quan trọng. `unordered` khớp đúng ý này.

**Triển khai.**

```python
@tool
def get_events(city: str):
    """Get events happening in a city."""
    return f"Concert at the park in {city} tonight."

agent = create_agent("claude-sonnet-4-6", tools=[get_weather, get_events])

evaluator = create_trajectory_match_evaluator(
    trajectory_match_mode="unordered",                                          # đòi đủ tool, bỏ qua thứ tự
)

def test_multiple_tools_any_order():
    result = agent.invoke({
        "messages": [HumanMessage(content="What's happening in SF today?")]
    })

    reference_trajectory = [
        HumanMessage(content="What's happening in SF today?"),
        AIMessage(content="", tool_calls=[
            {"id": "call_1", "name": "get_events", "args": {"city": "SF"}},
            {"id": "call_2", "name": "get_weather", "args": {"city": "SF"}},
        ]),
        ToolMessage(content="Concert at the park in SF tonight.", tool_call_id="call_1"),
        ToolMessage(content="It's 75 degrees and sunny in SF.", tool_call_id="call_2"),
        AIMessage(content="Today in SF: 75 degrees and sunny with a concert at the park tonight."),
    ]

    evaluation = evaluator(
        outputs=result["messages"],
        reference_outputs=reference_trajectory,
    )
    assert evaluation["score"] is True                                          # gọi đủ get_events + get_weather, bất kể thứ tự → True
```

### 3.3 `subset` và `superset` — khớp một phần

**Áp dụng thực tế.** `superset`: bạn chỉ cần chắc agent gọi **ít nhất** `get_weather`, gọi thêm tool khác cũng chấp nhận (ví dụ gọi thêm `get_detailed_forecast`). `subset`: ngược lại, chắc agent **không gọi tool nào ngoài** danh sách chuẩn — chặn agent làm quá phạm vi.

**Triển khai** (ví dụ dưới minh họa `superset`):

```python
@tool
def get_detailed_forecast(city: str):
    """Get detailed weather forecast for a city."""
    return f"Detailed forecast for {city}: sunny all week."

agent = create_agent("claude-sonnet-4-6", tools=[get_weather, get_detailed_forecast])

evaluator = create_trajectory_match_evaluator(
    trajectory_match_mode="superset",                                           # đòi ít nhất các tool trong mốc chuẩn, cho thừa
)

def test_agent_calls_required_tools_plus_extra():
    result = agent.invoke({
        "messages": [HumanMessage(content="What's the weather in Boston?")]
    })

    reference_trajectory = [                                                     # mốc chuẩn CHỈ đòi get_weather; agent gọi thêm vẫn đạt
        HumanMessage(content="What's the weather in Boston?"),
        AIMessage(content="", tool_calls=[
            {"id": "call_1", "name": "get_weather", "args": {"city": "Boston"}},
        ]),
        ToolMessage(content="It's 75 degrees and sunny in Boston.", tool_call_id="call_1"),
        AIMessage(content="The weather in Boston is 75 degrees and sunny."),
    ]

    evaluation = evaluator(
        outputs=result["messages"],
        reference_outputs=reference_trajectory,
    )
    assert evaluation["score"] is True
```

> **Về kết quả các test ở mục 3.2 và 3.3.** Tài liệu chỉ in kết quả cho ví dụ `strict` (mục 3.1). Ba ví dụ còn lại tài liệu chỉ có `assert evaluation["score"] is True` chứ không in dict kết quả. Không dựng lại dict ở đây để tránh đoán sai giá trị `key` của từng chế độ — chỉ biết chắc `score` là `True` khi khớp.

**!Note:** Mặc định, hai tool call chỉ được coi là bằng nhau khi **cùng tool và cùng tham số**. Muốn nới lỏng cách so tham số thì đặt `tool_args_match_mode` và/hoặc `tool_args_match_overrides`. Chi tiết nằm ở repo `agentevals`, không thuộc phạm vi trang này.

---

## 4. LLM-as-judge — để LLM chấm quỹ đạo

### Khái niệm

Hàm `create_trajectory_llm_as_judge` dùng một LLM để đánh giá đường đi thực thi của agent. Khác trajectory match, nó **không bắt buộc** có quỹ đạo chuẩn — nhưng cấp được thì vẫn nhận.

### Vai trò

Có những thứ không thể đối chiếu tất định: "agent lập luận có hợp lý không", "cách nó xử lý tổng thể có tốt không". Không có một quỹ đạo chuẩn duy nhất đúng. Lúc đó để một LLM đọc cả đường đi và chấm, dựa trên một prompt đánh giá dựng sẵn.

### 4.1 Không có quỹ đạo chuẩn

```python
from agentevals.trajectory.llm import create_trajectory_llm_as_judge, TRAJECTORY_ACCURACY_PROMPT

evaluator = create_trajectory_llm_as_judge(
    model="openai:o3-mini",                                                     # LLM đóng vai giám khảo chấm điểm
    prompt=TRAJECTORY_ACCURACY_PROMPT,                                          # prompt đánh giá dựng sẵn, không cần mốc chuẩn
)

def test_trajectory_quality():
    result = agent.invoke({
        "messages": [HumanMessage(content="What's the weather in Seattle?")]
    })

    evaluation = evaluator(
        outputs=result["messages"],                                            # chỉ cần output thật, không cần reference
    )
    assert evaluation["score"] is True
```

### 4.2 Có quỹ đạo chuẩn

Khi có mốc chuẩn, dùng prompt dựng sẵn `TRAJECTORY_ACCURACY_PROMPT_WITH_REFERENCE`:

```python
from agentevals.trajectory.llm import create_trajectory_llm_as_judge, TRAJECTORY_ACCURACY_PROMPT_WITH_REFERENCE

evaluator = create_trajectory_llm_as_judge(
    model="openai:o3-mini",
    prompt=TRAJECTORY_ACCURACY_PROMPT_WITH_REFERENCE,                          # prompt biến thể: có so với quỹ đạo chuẩn
)
evaluation = evaluator(
    outputs=result["messages"],
    reference_outputs=reference_trajectory,                                    # cấp thêm quỹ đạo chuẩn để giám khảo đối chiếu
)
```

**!Note:** Model `openai:o3-mini` trong ví dụ là chuỗi định danh model giám khảo của tài liệu; dùng model bạn có quyền truy cập. Vì đây là LLM chấm, kết quả **không tất định** như trajectory match — cùng một quỹ đạo có thể ra điểm khác nhau giữa các lần chạy. Đây là suy luận từ bản chất "LLM chấm" (căn cứ: mục 1 phân LLM-as-judge vào nhóm không có kỳ vọng chặt, đối lập với nhóm tất định); cần đối chiếu khi chạy thử.

### 4.3 Bản async

Mọi evaluator của `agentevals` chạy được với asyncio. Bản async lấy bằng cách thêm `async` ngay sau `create_` trong tên hàm.

```python
from agentevals.trajectory.llm import create_async_trajectory_llm_as_judge, TRAJECTORY_ACCURACY_PROMPT
from agentevals.trajectory.match import create_async_trajectory_match_evaluator

async_judge = create_async_trajectory_llm_as_judge(                            # create_ → create_async_
    model="openai:o3-mini",
    prompt=TRAJECTORY_ACCURACY_PROMPT,
)

async_evaluator = create_async_trajectory_match_evaluator(                     # cũng chèn "async" sau "create_"
    trajectory_match_mode="strict",
)

async def test_async_evaluation():
    result = await agent.ainvoke({                                             # bản async gọi bằng ainvoke, không phải invoke
        "messages": [HumanMessage(content="What's the weather?")]
    })

    evaluation = await async_judge(outputs=result["messages"])                 # await vì giám khảo là hàm async
    assert evaluation["score"] is True
```

---

## 5. Chạy evals trong LangSmith

Để theo dõi các lần thí nghiệm theo thời gian, ghi kết quả evaluator lên LangSmith. Trước hết đặt biến môi trường:

```bash
export LANGSMITH_API_KEY="your_langsmith_api_key"
export LANGSMITH_TRACING="true"                                                # bật ghi vết lên LangSmith
```

Trang này nêu **hai cách** chạy eval trên LangSmith: tích hợp `pytest`, và hàm `evaluate`. Cả hai đều **trỏ sang cây tài liệu LangSmith riêng** — cơ chế LangSmith không thuộc phạm vi trang này.

**Cách 1 — tích hợp pytest.** Dán `@pytest.mark.langsmith` lên test, dùng `langsmith.testing` để log input/output/reference, rồi chạy `pytest test_trajectory.py --langsmith-output`.

**Cách 2 — hàm `evaluate`.** Tạo một dataset trên LangSmith (mỗi dòng gồm `input` là `{"messages": [...]}` và `output` là message history kỳ vọng), rồi gọi `client.evaluate(run_agent, data="ten_dataset", evaluators=[...])`.

> Hai đoạn trên tóm ở mức trang evals mô tả. Chi tiết cách dùng `pytest` với LangSmith và cách dựng dataset nằm ở tài liệu LangSmith (`/langsmith/pytest`, `/langsmith/manage-datasets`) — khi làm file cho phần LangSmith thì viết ở đó, không viết ở đây để hai file khỏi mâu thuẫn.

---

## Tham chiếu chéo

- [08-01 Testing — tổng quan](./08-01-testing-overview.md) — vị trí evals trong ba cách kiểm thử
- [08-03 Integration testing](./08-03-integration-testing.md) — mục 4 (khẳng định theo cấu trúc) trỏ sang các evaluator ở file này
- Tài liệu gốc: `https://docs.langchain.com/oss/python/langchain/test/evals`
- Repo `agentevals` (chi tiết `tool_args_match_mode`, LLM-as-judge): `https://github.com/langchain-ai/agentevals`
- Phần LangSmith (chưa nghiên cứu): `/langsmith/pytest`, `/langsmith/manage-datasets`