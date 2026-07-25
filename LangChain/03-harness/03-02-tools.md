---
title: Tools
doc_source: https://docs.langchain.com/oss/python/langchain/tools
status: draft
lab:
related:
  - ./03-01-agents.md
---

# Tools (`@tool`, `ToolRuntime`, `ToolNode`)

> Trang này gồm bốn phần tách bạch: khai báo tool, lấy dữ liệu lúc chạy qua `ToolRuntime`, chọn kiểu giá trị tool trả về, và xử lý lỗi tool.
> Phần agent quyết định gọi tool nào, vòng lặp ReAct chạy ra sao nằm ở [03-01 agents](./03-01-agents.md).

---

## 1. Tổng quan

Tool là hàm có kiểu dữ liệu vào/ra rõ ràng, được đưa kèm vào lời gọi chat model. Model đọc mô tả rồi tự quyết định gọi tool nào và truyền tham số gì — tool không tự chạy, agent cũng không chọn hộ.

```python
from langchain.tools import tool

@tool
def search_database(query: str, limit: int = 10) -> str:   # type hint sinh ra schema tham số, bỏ đi thì không khai báo được tool
    """Search the customer database for records matching the query.

    Args:
        query: Search terms to look for
        limit: Maximum number of results to return
    """
    return f"Found {limit} results for '{query}'"          # thân hàm model không nhìn thấy, chỉ chạy sau khi model đã quyết gọi
```

**Kết quả in ra** :

```
name:        search_database                                      ← lấy từ tên hàm, không phải khai báo thêm
description: Search the customer database for records matching…   ← lấy từ docstring, đây là thứ model đọc để quyết định
args:        {'query': str, 'limit': int (mặc định 10)}           ← dựng từ type hint và giá trị mặc định ở chữ ký hàm
```

Khác hàm Python thường ở đúng hai chỗ: docstring không còn là chú thích cho người đọc mà là mô tả gửi cho model, và type hint không còn là gợi ý mà là thứ bắt buộc để dựng schema.


**!Note:** Đặt tên tool theo `snake_case` (`web_search`, không phải `Web Search`). Một số nhà cung cấp model báo lỗi hoặc từ chối tên chứa dấu cách và ký tự đặc biệt. Giữ trong phạm vi chữ, số, gạch dưới, gạch nối thì chạy được ở nhiều nhà cung cấp hơn. Quy tắc này cả hai bản đều nhắc.

---

## 2. Khai báo tool

### 2.1 Đặt lại tên tool

**Khái niệm.** Tham số đầu tiên của `@tool` là tên tool, ghi đè tên hàm.

**Vai trò.** Tên hàm phục vụ người viết code, tên tool phục vụ model. Hai mục đích khác nhau nên không nhất thiết trùng.

**Áp dụng thực tế.** Module đã có hàm nội bộ tên `search`, nhưng gửi cho model chữ `search` trơ trọi thì nó không biết tìm ở đâu. Đặt lại thành `web_search` mà không phải đổi tên hàm rồi sửa mọi chỗ gọi trong code.

**Triển khai.**

```python
@tool("web_search")                       # tên gửi cho model, ghi đè tên hàm bên dưới
def search(query: str) -> str:            # tên hàm giữ nguyên cho code nội bộ dùng
    """Search the web for information."""
    return f"Results for: {query}"

print(search.name)                        # đọc lại tên thật sự đang được đăng ký
```

**Kết quả in ra:**

```
web_search    ← tên trong decorator thắng, chữ `search` không còn xuất hiện với model
```

### 2.2 Đặt lại mô tả tool

**Khái niệm.** Tham số `description=` ghi đè mô tả tự sinh từ docstring.

**Vai trò.** Docstring viết cho người bảo trì code, mô tả viết cho model. Khi hai nhu cầu lệch nhau thì tách ra.

**Áp dụng thực tế.** Docstring cần ghi rõ hàm dùng `eval` nên chỉ nhận biểu thức đã kiểm tra — thông tin cho người review code. Model thì cần một câu chỉ dẫn khi nào dùng: gặp bài toán số thì gọi tool này thay vì tự tính nhẩm.

**Triển khai.**

```python
@tool("calculator", description="Performs arithmetic calculations. Use this for any math problems.")   # câu này mới là thứ model đọc
def calc(expression: str) -> str:
    """Evaluate mathematical expressions."""            # docstring vẫn còn, nhưng đã bị description ghi đè
    return str(eval(expression))
```

**Kết quả in ra** :

```
name:        calculator                                                ← từ tham số đầu của decorator
description: Performs arithmetic calculations. Use this for any math…  ← từ description=, không phải từ docstring
```

**!Note:** Khi đã truyền `description=`, sửa docstring không còn tác dụng gì với model. Người bảo trì sau này viết lại docstring cho chuẩn rồi tưởng đã đổi chỉ dẫn cho model — lỗi im lặng, code chạy nhưng hành vi model không đổi. Căn cứ: `description=` được mô tả là ghi đè mô tả tự sinh. Đây là suy luận về hệ quả, tài liệu không nói thẳng.

### 2.3 Khai schema phức tạp bằng Pydantic

**Khái niệm.** nhận một model Pydantic làm schema tham số thay cho schema dựng tự động từ chữ ký hàm.

**Vai trò.** Chữ ký hàm(function signature) thường chỉ nói được kiểu dữ liệu. Pydantic giúp gắn thêm mô tả chi tiết, giá trị mặc định và ép buộc danh mục giá trị cụ thể, giúp AI gọi hàm chính xác mà không tự ý bịa thêm dữ liệu lung tung.

**Áp dụng thực tế.** Tool tra thời tiết phục vụ người dùng nhiều nước. Không ràng buộc `units` thì model tự chế ra `"C"`, `"độ C"`, `"metric"` — mỗi lần một kiểu, và hàm phải viết nhánh xử lý cho từng biến thể. Khai `Literal["celsius", "fahrenheit"]` thì chỉ còn hai giá trị.

**Triển khai.**

```python
class WeatherInput(BaseModel):
    """Input for weather queries."""
    location: str = Field(description="City name or coordinates")     # mô tả riêng cho từng tham số, chữ ký hàm không làm được
    units: Literal["celsius", "fahrenheit"] = Field(
        default="celsius",
        description="Temperature unit preference"
    )                                                                 # Literal khóa tập giá trị, model không tự chế giá trị khác
    include_forecast: bool = Field(
        default=False,
        description="Include 5-day forecast"
    )

@tool(args_schema=WeatherInput)                                       # schema lấy từ Pydantic, không dựng từ chữ ký hàm nữa
def get_weather(location: str, units: str = "celsius", include_forecast: bool = False) -> str:
    """Get current weather and optional forecast."""                  # chữ ký hàm vẫn phải khai lại đủ tham số để nhận giá trị
    temp = 22 if units == "celsius" else 72
    result = f"Current weather in {location}: {temp} degrees {units[0].upper()}"
    if include_forecast:
        result += "\nNext 5 days: Sunny"
    return result
```

---

## 3. `ToolRuntime` — dữ liệu tool lấy được lúc chạy

**Khái niệm.** [`ToolRuntime`](https://reference.langchain.com/python/langchain/tools/#langchain.tools.ToolRuntime) là tham số đặc biệt: thêm `runtime: ToolRuntime` vào dòng `def` của tool thì LangChain tự điền giá trị, và tham số này bị cắt khỏi schema gửi cho model. Model không nhìn thấy nó, không điền được gì vào đó.

**Vai trò.**

> Đưa dữ liệu ngoài câu chữ vào tool

- Model chỉ truyền được thứ nó biết, tức thứ có trong hội thoại
- Ai đang đăng nhập, khách hỏi gì tháng trước — không nằm trong hội thoại
- Không dùng biến toàn cục được: một tiến trình phục vụ nhiều khách cùng lúc, sẽ đè lên nhau
- `ToolRuntime` theo từng lượt gọi nên không lẫn dữ liệu giữa hai người

> Chặn model đụng vào dữ liệu nhạy cảm

- LangChain quét dòng `def` để dựng schema gửi model
- Gặp kiểu `ToolRuntime` thì bỏ qua, không đưa vào schema
- Model không thấy tham số này nên không điền sai được
- Khác với việc dặn trong prompt "đừng bịa `user_id`" — cách đó phụ thuộc model có nghe lời hay không

**Thành phần.** Một object gom sẵn dữ liệu của lần chạy hiện tại. Danh mục đầy đủ ở [Access context](https://docs.langchain.com/oss/python/langchain/tools#access-context).

| Thành phần | Chứa gì | Dùng khi nào | Doc |
|---|---|---|---|
| `runtime.state` | Bộ nhớ ngắn hạn — dữ liệu thay đổi được, sống trong một cuộc hội thoại (danh sách message, biến đếm, trường tự định nghĩa) | Đọc lịch sử hội thoại, đếm số lần gọi tool | [read](https://docs.langchain.com/oss/python/langchain/tools#access-state) · [write](https://docs.langchain.com/oss/python/langchain/tools#update-state) |
| `runtime.context` | Cấu hình bất biến truyền vào lúc gọi agent (mã người dùng, thông tin phiên) | Cá nhân hóa kết quả theo danh tính người dùng | [Context](https://docs.langchain.com/oss/python/langchain/tools#context) |
| `runtime.store` | Bộ nhớ dài hạn — dữ liệu sống qua nhiều cuộc hội thoại | Lưu sở thích người dùng, giữ kho tri thức | [Store](https://docs.langchain.com/oss/python/langchain/tools#long-term-memory-store) |
| `runtime.stream_writer` | Kênh phát thông báo trong lúc tool đang chạy | Hiện tiến độ cho tác vụ chạy lâu | [Stream writer](https://docs.langchain.com/oss/python/langchain/tools#stream-writer) |
| `runtime.execution_info` | Danh tính lần chạy và trạng thái thử lại (thread id, run id, số lần thử) | Ghi log, đổi hành vi khi đang chạy lại lần thứ n | [Execution info](https://docs.langchain.com/oss/python/langchain/tools#execution-info) |
| `runtime.server_info` | Dữ liệu riêng của LangGraph Server (assistant id, graph id, người dùng đã xác thực) | Chỉ khi tool chạy trên LangGraph Server | [Server info](https://docs.langchain.com/oss/python/langchain/tools#server-info) |
| `runtime.config` | `RunnableConfig` của lần chạy | Đọc callback, tag, metadata | [RunnableConfig](https://reference.langchain.com/python/langchain-core/runnables/config/RunnableConfig) |
| `runtime.tool_call_id` | Mã định danh của đúng lượt gọi tool đang chạy | Gắn `ToolMessage` trả về đúng lượt gọi; ghi log đối chiếu | [Update state](https://docs.langchain.com/oss/python/langchain/tools#update-state) |

Ba thứ đầu là phần dùng thường xuyên. `execution_info` và `server_info` phục vụ vận hành và chỉ có ở phiên bản mới — ứng dụng chạy cục bộ **bỏ qua hai thành phần này hoàn toàn**, đây là tính năng cho trường hợp đặc biệt.

---

## 5. Năm kiểu giá trị tool trả về

| | Chuỗi | Object | Khối nội dung | `Command` | `return_direct=True` |
|---|---|---|---|---|---|
| Model nhận gì | văn bản | dữ liệu đã tuần tự hóa, đọc được từng trường | chữ + ảnh trong một kết quả | chỉ phần `ToolMessage`, nếu tool có kèm | không nhận, kết quả đi thẳng ra người dùng |
| State có đổi | không | không | không | **có** | không |
| Vòng lặp agent | chạy tiếp | chạy tiếp | chạy tiếp | chạy tiếp | **dừng ngay** |

---

### 5.1 Trả chuỗi

**Khái niệm.** Giá trị trả về được bọc thành `ToolMessage` và đưa vào hội thoại.

**Vai trò.** Đưa kết quả về dạng model đọc hiểu được để nói tiếp. Dùng khi kết quả vốn đã là câu chữ cho người đọc và model còn phải xử lý thêm — diễn giải, hỏi lại, hoặc nối sang tool khác.

```python
@tool
def get_weather(city: str) -> str:
    """Get weather for a city."""
    return f"It is currently sunny in {city}."     # thành ToolMessage, không trường state nào bị đụng tới
```

**Kết quả** :

```
ToolMessage("It is currently sunny in Hanoi.")   ← model đọc nguyên câu rồi tự quyết bước sau
```

---

### 5.2 Trả object

**Khái niệm.** Trả `dict` hoặc object khác; LangChain tuần tự hóa rồi gửi lại cho model.

**Vai trò.** Cho model trích thẳng đúng trường cần thay vì đọc hiểu văn xuôi để rút số ra — chỗ nó hay rút nhầm. Dùng khi bước suy luận sau cần một giá trị cụ thể chứ không cần cả câu.

```python
@tool
def get_weather_data(city: str) -> dict:
    """Get structured weather data for a city."""
    return {
        "city": city,
        "temperature_c": 22,                       # trường tách bạch, model trích thẳng
        "conditions": "sunny",
    }
```

**Kết quả** :

```
ToolMessage('{"city": "Hanoi", "temperature_c": 22, "conditions": "sunny"}')   ← model đọc được đúng temperature_c
```

---

### 5.3 Trả khối nội dung đa phương tiện

**Khái niệm.** Trả về danh sách khối nội dung chuẩn thay vì chuỗi, để model nhận chữ và ảnh trong cùng một kết quả tool.

**Vai trò.** Giữ nguyên thứ không diễn đạt được bằng chữ. Mô tả ảnh chụp màn hình bằng lời là mất đúng thứ model cần nhìn. Dùng khi kết quả gồm hình ảnh, âm thanh, hoặc phương tiện khác.

```python
@tool
def capture_screenshot() -> list[dict]:
    """Capture a screenshot of the current page."""
    return [
        {"type": "text", "text": "Screenshot of the current page:"},   # khối chữ dẫn trước để model biết ảnh là gì
        {"type": "image", "url": "https://example.com/page.png"},      # khối ảnh
    ]
```

**Kết quả** :

```
ToolMessage(content=[{text}, {image}])           ← một message chứa hai khối, không phải hai message
message.content_blocks                           ← đọc lại danh sách khối đã chuẩn hóa sau khi tool chạy xong
```

**!Note:** Model phải hỗ trợ đúng loại phương tiện được trả về. Tài liệu yêu cầu kiểm tra năng lực model trước khi trả ảnh, âm thanh, video — không mô tả model không hỗ trợ thì hỏng ở đâu.

---

### 5.4 Trả `Command`

**Khái niệm.** Trả về một lệnh sửa state thay vì dữ liệu. Xem cơ chế ở [mục 3.2](#32-ghi-vào-state-bằng-command).

**Vai trò.** Ghi kết quả vào trường state để các chặng sau đọc thẳng, thay vì để nó nằm lẫn trong đoạn hội thoại và bắt model lục lại. Dùng khi tool vừa trả dữ liệu vừa đổi trạng thái ứng dụng.

```python
@tool
def set_language(language: str, runtime: ToolRuntime) -> Command:
    """Set the preferred response language."""
    return Command(
        update={
            "preferred_language": language,        # chặng sau trong cùng lần chạy đọc được ngay giá trị mới
            "messages": [
                ToolMessage(
                    content=f"Language set to {language}.",   # để model biết tool đã chạy xong
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )
```

**Kết quả** :

```
state["preferred_language"] = "vi"               ← trường được ghi, các chặng sau đọc thẳng
ToolMessage("Language set to vi.")               ← phần duy nhất model nhìn thấy
```

**!Note:** Quên kèm `ToolMessage` thì state vẫn được sửa nhưng model không nhận phản hồi nào cho lệnh gọi nó vừa phát ra. Lỗi im lặng — chức năng chạy đúng, agent trả lời như thể chưa làm gì.

---

### 5.5 Trả thẳng, cắt vòng lặp

**Khái niệm.** Bật `return_direct=True` thì agent trả kết quả tool cho người gọi ngay, bỏ qua lượt gọi model tiếp theo.

**Vai trò.** Giữ kết quả nguyên văn và bỏ được một lượt gọi model. Số dư, mã hồ sơ, ngày đáo hạn — model không có cơ hội diễn đạt lại hay làm sai lệch. Không dùng khi kết quả còn cần tóm tắt, suy luận, hoặc nối sang tool khác.

```python
@tool(return_direct=True)                          # cờ đặt ngay ở decorator, không phải ở create_agent
def fetch_order_status(order_id: str) -> str:
    """Fetch the current status of a customer order."""
    return f"Order {order_id} is shipped and will arrive in 2 days."
```

**Kết quả** (lấy từ chú thích trong tài liệu):

```
Order 12345 is shipped and will arrive in 2 days.   ← nguyên văn tool trả về, không qua thêm lượt gọi model nào
```

**!Note:** Model gọi nhiều tool trong một lượt thì cờ này chỉ có tác dụng khi **tất cả** tool được gọi đều bật. Bật cho một tool rồi tin nó luôn cắt vòng lặp là hiểu sai — chỉ cần model gọi kèm một tool thường là vòng lặp chạy tiếp.

---

## 6. Xử lý lỗi tool

**Khái niệm.** Lỗi tool không bắt trong thân tool mà bắt ở tầng middleware, bằng hook `wrap_tool_call`. Hook này bọc quanh lời gọi tool: tool ném ngoại lệ thì middleware hứng, đổi thành `ToolMessage` rồi trả cho model.

**Vai trò.** Không bắt thì ngoại lệ ném thẳng ra ngoài và cả lần chạy dừng — người dùng thấy phiên chết giữa chừng. Bắt và trả thành message thì model đọc được lỗi, có cơ hội sửa tham số rồi gọi lại. Đặt ở middleware nên một lần khai là phủ mọi tool của agent, và bản thân tool giữ được phần code sạch.

**Áp dụng thực tế.** Model gọi tool tra cứu với mã doanh nghiệp sai định dạng. Không bắt thì cả phiên tư vấn dừng ở đó. Bắt và trả câu "mã phải gồm 10 chữ số" thì model sửa mã, gọi lại, người dùng không thấy gì bất thường.

**Triển khai.**

```python
@wrap_tool_call                                                # decorator biến hàm thường thành middleware, không cần dựng class
def handle_tool_errors(
    request: ToolCallRequest,                                  # thông tin lượt gọi: tên tool, tham số, id
    handler: Callable[[ToolCallRequest], ToolMessage],         # handler chính là lời gọi tool thật
) -> ToolMessage:
    """Convert tool exceptions into ToolMessages the model can handle."""
    try:
        return handler(request)                                # để nguyên trong try, lỗi của tool sẽ nổ ở dòng này
    except Exception as e:
        return ToolMessage(
            content=f"Tool error: Please check your input and try again. ({e})",   # model nhận câu này thay vì lần chạy bị dừng
            tool_call_id=request.tool_call["id"],              # lấy id từ request, không tự sinh — sai id thì model không ghép được
        )

agent = create_agent(
    model="…",
    tools=[],
    middleware=[handle_tool_errors],                           # gắn ở tầng agent nên phủ toàn bộ tool
)
```

**Kết quả in ra** :

```
không có middleware → ValueError ném ra ngoài, lần chạy dừng            ← người dùng thấy phiên chết giữa chừng
có middleware       → ToolMessage("Tool error: … (invalid literal…)")   ← model đọc được lỗi và gọi lại với tham số đã sửa
```

**!Note:** Bắt `Exception` là bắt tất cả. Mất kết nối cơ sở dữ liệu, hết hạn mức API cũng thành một câu chữ mà model cố "sửa" bằng cách gọi lại. Lỗi hạ tầng bị nuốt, log đầy những lượt gọi lại vô ích, còn cảnh báo thật thì không ai nhận được. Lọc theo loại ngoại lệ trước khi bắt.

**Ngoài phạm vi trang này:** cơ chế thử lại tự động, thứ tự chạy khi xếp nhiều middleware chồng nhau, và cách `ToolNode` xử lý lỗi trong đồ thị LangGraph. Ba thứ đó nằm ở trang Middleware và trang Graph API.

---

## 7. Chọn tool động

**Khái niệm.** Danh sách tool gửi cho model được tính lại trước mỗi lượt gọi, thay vì cố định từ lúc tạo agent.

**Vai trò.** Danh sách tool là một phần của prompt. Quá nhiều thì model bị ngợp và chọn sai; quá ít thì agent làm được ít việc. Lọc động biến việc phân quyền từ lời dặn trong prompt thành ràng buộc cứng — model không thấy tool thì không gọi được, không cần trông vào việc nó nghe lời.

**Áp dụng thực tế.** Agent hỗ trợ khách có 4 tool đọc và 3 tool ghi, trong đó có tool chuyển tiền. Khách chưa xác thực mà model vẫn thấy tool chuyển tiền thì tuyến phòng thủ duy nhất là một câu trong system prompt. Cắt tool khỏi danh sách thì rủi ro đó biến mất.

**Điểm phải nắm trước.** Việc lọc đặt ở `wrap_model_call` — hook bọc quanh **từng lượt gọi model**, không chạy một lần lúc khởi động. Lượt 1 khách chưa xác thực thì thấy 4 tool, lượt 5 đã xác thực thì thấy 7 tool, vẫn cùng một agent.

Hai cách, phân biệt bằng một câu hỏi: **tool đã tồn tại từ lúc tạo agent chưa?**

---

### 7.1 Lọc danh sách tool đã đăng ký sẵn

**Khái niệm.** Đăng ký hết tool vào `create_agent` từ đầu, mỗi lượt gọi model lọc bớt bằng `@wrap_model_call`.

**Vai trò.** Tool vẫn nằm trong agent, chỉ bị ẩn khỏi model ở những lượt mà người dùng không đủ quyền để sử dụng.

> **Lợi ích:** không phải dựng riêng một agent cho mỗi nhóm quyền, danh sách gửi cho model ngắn lại nên nó ít chọn nhầm tool hơn.

```python
@dataclass
class Context:
    user_role: str

@wrap_model_call                                                   # bọc quanh mỗi lượt gọi model
def context_based_tools(
    request: ModelRequest,                                         # gói sắp gửi cho model: messages, tools, model…
    handler: Callable[[ModelRequest], ModelResponse]               # handler là lời gọi model thật
) -> ModelResponse:
    """Filter tools based on Runtime Context permissions."""
    if request.runtime is None or request.runtime.context is None:
        user_role = "viewer"                                       # thiếu context thì rơi về vai trò hạn chế nhất
    else:
        user_role = request.runtime.context.user_role              # lấy quyền từ context, không lấy từ lời người dùng

    if user_role == "admin":
        pass                                                       # giữ nguyên danh sách
    elif user_role == "editor":
        tools = [t for t in request.tools if t.name != "delete_data"]
        request = request.override(tools=tools)                    # override sinh request MỚI, không sửa bản cũ
    else:
        tools = [t for t in request.tools if t.name.startswith("read_")]
        request = request.override(tools=tools)

    return handler(request)                                        # truyền bản đã lọc, đưa nhầm bản cũ là mất tác dụng

agent = create_agent(
    model="gpt-5.5",
    tools=[read_data, write_data, delete_data],                    # đăng ký đủ ở đây, lọc làm ở middleware
    middleware=[context_based_tools],
    context_schema=Context                                         # thiếu dòng này thì runtime.context không có kiểu để đọc
)
```

**Kết quả** (dựng lại):

```
admin  → 3 tool gửi cho model                        ← giữ nguyên
editor → 2 tool, delete_data biến mất khỏi schema    ← model không thấy nên không gọi được
viewer → chỉ tool tên bắt đầu bằng read_             ← quy ước đặt tên thành cơ chế phân quyền
```

---

### 7.2 Đăng ký tool ngay lúc chạy

**Khái niệm.** Tool được thêm vào agent trong lúc chạy, không có mặt trong `tools=[...]` lúc tạo agent. Cần **hai** hook: `wrap_model_call` chèn tool vào danh sách gửi cho model, `wrap_tool_call` chỉ cho agent biết chạy tool đó bằng hàm nào.

**Vai trò.** Gỡ ràng buộc phải biết trước danh sách tool lúc viết code. Danh sách được nạp lúc chạy, từ nguồn bên ngoài, và thay đổi mà không phải sửa code hay deploy lại.

**Bài toán nó giải quyết.** Viết `create_agent(tools=[...])` là phải liệt kê tool ra tại thời điểm gõ dòng đó. Nhưng có những tool khi ấy chưa tồn tại — không phải chưa viết, mà là chưa biết chúng là gì. Ba tình huống tài liệu nêu:

1. **Tool nạp từ máy chủ MCP.** Agent cắm vào một MCP server. Server đó phơi ra tool nào là do bên vận hành server quyết, và họ thêm bớt bất cứ lúc nào. Code của agent chỉ biết địa chỉ server, không biết danh sách — phải gọi lên hỏi lúc chạy mới có. Không có cơ chế này thì mỗi lần server thêm một tool là phải sửa code, build lại, deploy lại agent.

2. **Tool sinh theo dữ liệu người dùng.** Mỗi khách có bộ mẫu báo cáo riêng, mỗi mẫu thành một tool. Khách A có 3 mẫu, khách B có 11, và họ tự thêm mẫu mới trong giao diện. Danh sách phụ thuộc vào ai đang đăng nhập nên không liệt kê sẵn được — chỉ biết sau khi đã xác định người dùng của lượt chạy.

3. **Tool lấy từ kho tool từ xa.** Một đội khác quản lý registry tool dùng chung, thêm bớt theo nhịp của họ. Agent lấy về lúc chạy thay vì phải bám theo mỗi lần registry đổi.

**Vì sao phải hai hook.** Agent giữ một bảng tra `tên tool → hàm thật`, dựng một lần từ `tools=[...]`. Model gọi tool nào thì agent tra bảng này để biết chạy gì. Tool chèn vào lúc chạy không nằm trong bảng đó — nên ngoài việc cho model thấy tool, còn phải chỉ đường cho agent thực thi.

**!Note:** Làm việc thứ nhất mà quên việc thứ hai là lỗi khó lần nhất ở mục này. Model thấy tool, model gọi tool, agent tra bảng không có tên đó nên không chạy được — trong khi model vẫn tin tool tồn tại và gọi lại. Lỗi không lộ lúc khởi động, chỉ nổ đúng lượt đầu tiên model chạm vào tool động. Tài liệu nêu rõ `wrap_tool_call` là bắt buộc với tool đăng ký lúc chạy.

---

## 8. Headless tools — tool chạy ở nơi khác, không chạy trong tiến trình

**Khái niệm.** Tool chỉ khai phần định nghĩa — tên, mô tả, schema tham số — không có thân hàm. Gọi `tool(name=..., description=..., args_schema=...)` với đúng ba thứ đó thì LangChain trả về một `HeadlessTool`. Model gọi tool loại này thì lần chạy **dừng lại** thay vì thực thi tại chỗ, phát ra một payload để bên ngoài xử lý, rồi **chạy tiếp** khi nhận được kết quả.

**Vai trò.** Đưa phần thực thi ra khỏi tiến trình chạy agent, sang nơi thực sự làm được việc đó. Model vẫn thấy một tool bình thường và gọi như mọi tool khác — phần khác biệt nằm hoàn toàn ở tầng dưới.

**Bài toán nó giải quyết.** Tool thường có thân hàm chạy trên máy chủ, nên chỉ làm được những gì máy chủ làm được. Ba loại việc nằm ngoài phạm vi đó:

*Việc phụ thuộc thiết bị hoặc giao diện của người dùng.* Lấy vị trí, đọc bộ nhớ cục bộ của trình duyệt, đọc clipboard, vẽ canvas, mở hộp chọn file. Máy chủ không có trình duyệt, không có màn hình, không có thiết bị của khách.

*Dữ liệu không nên rời khỏi máy người dùng.* Ghi chú cá nhân lưu trong trình duyệt, file khách vừa chọn. Tải lên máy chủ chỉ để đọc một trường là tạo thêm rủi ro không cần thiết.

*Việc cần người quyết hoặc cần một dịch vụ khác làm.* Bước duyệt của con người, hoặc lệnh phải chạy trong một hệ thống nội bộ khác.

**Bốn bước theo tài liệu.**

1. Khai tool bằng `tool(name=..., description=..., args_schema=...)` từ `langchain.tools` — chỉ có schema, không có phần chạy trong tiến trình
2. Đăng ký tool đó với `create_agent` hoặc đồ thị LangGraph, để model gọi được như tool thường
3. Bắt payload khi tool bị gọi. Thay vì chạy, đồ thị dừng và phát ra payload dạng `{"type": "tool", "tool_call": {"id", "name", "args"}}`
4. Cho đồ thị chạy tiếp sau khi ứng dụng, dịch vụ khác, hoặc người duyệt đã làm xong phần việc

**!Note:** Phía Python **không có** API `.implement()`. Muốn chạy tool ở trình duyệt thì phải khai lại schema ở frontend rồi gắn `.implement(...)` bên đó — tức là hai bản khai, một ở server một ở client, và tên với schema phải khớp nhau. Đọc ví dụ JavaScript rồi đi tìm `.implement()` trong Python là ngõ cụt.

**Quan hệ với dừng chờ người duyệt.** Bước 3 và 4 là cùng một cơ chế dừng/chạy tiếp của LangGraph. Nghĩa là headless tool không chỉ dùng cho luồng trình duyệt — bất cứ chỗ nào cần chèn một bước ngoài tiến trình, kể cả bước người xét duyệt, đều dùng được khuôn này.

**Ngoài phạm vi trang này:** cách frontend bắt tín hiệu dừng và gửi kết quả về (thuộc SDK JavaScript), callback `onTool` theo dõi vòng đời, và ví dụ chạy đầu-cuối với `useStream`. Ba thứ đó nằm ở trang Headless tools phía frontend.

---

## 9. `ToolNode` — chạy tool trong đồ thị tự dựng

**Khái niệm.** `ToolNode` là chặng dựng sẵn của LangGraph, nhận danh sách tool và lo phần thực thi: chạy song song nhiều tool, bắt lỗi, tiêm state.

**Vai trò.** Đây chính là viên gạch mà `create_agent` dùng bên trong. Tự dựng quy trình riêng và cần điều khiển chi tiết cách tool được gọi thì lắp thẳng `ToolNode` vào đồ thị.

**Áp dụng thực tế.** Quy trình duyệt hồ sơ có ba chặng cố định — kiểm tra pháp lý, chấm điểm tín dụng, sinh tờ trình — chỉ chặng giữa mới cần model gọi tool. Dùng `create_agent` cho cả quy trình thì mất tính xác định của hai chặng kia.

**Triển khai.**

```python
tool_node = ToolNode([search, calculator])                 # gom tool lại thành một chặng chạy được

builder = StateGraph(MessagesState)
builder.add_node("llm", call_llm)                          # chặng gọi model, tự viết
builder.add_node("tools", tool_node)                       # chặng chạy tool, dùng sẵn

builder.add_edge(START, "llm")
builder.add_conditional_edges("llm", tools_condition)      # model có tool_calls thì sang "tools", không có thì kết thúc
builder.add_edge("tools", "llm")                           # chạy tool xong quay lại model — đây là chỗ tạo ra vòng lặp

graph = builder.compile()
```

`tools_condition` là hàm điều kiện dựng sẵn, xét message cuối của model có lệnh gọi tool hay không. Đây là mảnh ghép biến đồ thị thành vòng lặp agent.

**Kết quả in ra** :

```
llm   → message có tool_calls      ← tools_condition rẽ sang "tools"
tools → [ToolMessage, ToolMessage] ← model gọi hai tool cùng lượt thì chạy song song, trả về hai kết quả
llm   → message không tool_calls   ← tools_condition rẽ sang END, vòng lặp dừng
```

**!Note:** Chặng chạy tool phải đặt tên `"tools"`. `tools_condition` trả về đúng tên này; đặt tên khác thì đồ thị không tìm thấy chặng đích. Đây là suy luận từ chú thích trong ví dụ (`Routes to "tools" or END`), chưa được xác nhận bằng mô tả trực tiếp.

Tool chạy dưới `ToolNode` vẫn đọc được trạng thái đồ thị qua `ToolRuntime`, giống hệt khi chạy dưới `create_agent` — chuyển từ agent dựng sẵn sang đồ thị tự dựng không phải viết lại tool.

```python
@tool
def get_message_count(runtime: ToolRuntime) -> str:
    """Get the number of messages in the conversation."""
    messages = runtime.state["messages"]                   # state ở đây là state của đồ thị, không phải của agent dựng sẵn
    return f"There are {len(messages)} messages."

tool_node = ToolNode([get_message_count])                  # ToolNode lo phần tiêm, tool không khai báo gì thêm
```

**Kết quả in ra** :

```
There are 7 messages.     ← đếm cả message của người, của model và của tool trong state hiện tại
```

---

## 10. Tool có sẵn và tool chạy phía nhà cung cấp

LangChain có sẵn một bộ tool và toolkit cho các việc phổ biến: tìm kiếm web, chạy code, truy vấn cơ sở dữ liệu. Danh sách đầy đủ ở trang [tools and toolkits](https://docs.langchain.com/oss/python/integrations/tools).

Một số chat model có tool chạy ngay phía nhà cung cấp — tìm kiếm web, trình chạy code — không cần tự định nghĩa và cũng không cần tự vận hành. Cách bật nằm ở trang tích hợp của từng model và trang [Models](https://docs.langchain.com/oss/python/langchain/models#server-side-tool-use), không thuộc phạm vi trang này.

---

## Tham chiếu chéo

- [03-01 agents](./03-01-agents.md) — `create_agent`, cách agent chọn tool và vòng lặp ReAct
- Trang Models, mục Tool calling: `https://docs.langchain.com/oss/python/langchain/models#tool-calling`
- Trang Middleware (nơi đặt `wrap_tool_call`, `wrap_model_call`): `https://docs.langchain.com/oss/python/langchain/middleware/overview`
- Trang Streaming (liên quan hàm phát tiến độ): `https://docs.langchain.com/oss/python/langchain/streaming`
- Trang Short-term memory (trường state của agent): `https://docs.langchain.com/oss/python/langchain/short-term-memory`
- Trang LangGraph Graph API, mục reducers: `https://docs.langchain.com/oss/python/langgraph/graph-api#reducers`
- Trang Headless tools phía frontend: `https://docs.langchain.com/oss/javascript/langchain/frontend/headless-tools`