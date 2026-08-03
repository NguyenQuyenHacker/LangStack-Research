---
title: Observability — Features — Bảo mật dữ liệu (Masking)
doc_source: https://langfuse.com/docs/observability/features/masking
accessed: 2026-08-01
version: v4
status: draft
lab:
related:
  - ./01-05-00-index.md
---

# Masking — che dữ liệu nhạy cảm trước khi rời ứng dụng

> Masking là hàm ta cắm vào Langfuse để redact input/output/metadata **ngay tại máy ta**, trước khi trace được gửi lên server Langfuse.
> Với LangChain, masking không nằm trên `CallbackHandler` — nó nằm ở span processor / Langfuse client; span do LangChain sinh ra tự động đi qua đó. Xem [mục 2](#2-với-langchain--masking-nằm-ở-đâu).

---

## 1. Tổng quan

Trace của một app LLM ghi lại nguyên văn prompt, câu trả lời và metadata. Với app tài chính, những trường này rất dễ chứa số thẻ, số tài khoản, số CMND/CCCD, email, số điện thoại của khách. Nếu gửi thẳng lên một hệ quan sát (observability) bên ngoài thì đó là dữ liệu nhạy cảm rời khỏi vòng kiểm soát của ta.

Masking lo đúng chuyện đó: nó là một **hàm chặn ở phía client**, nhận dữ liệu sắp gửi đi và trả về bản đã che. Ba việc tài liệu nêu masking dùng để làm:

1. Redact thông tin nhạy cảm trong input, output, metadata của trace/observation.
2. Biến đổi (transform) OpenTelemetry span attributes trước khi export.
3. Lọc dữ liệu ở mức chi tiết cho yêu cầu tuân thủ / quyền riêng tư.

Điểm mấu chốt cần nắm ngay: **giá trị thật trong app không đổi, chỉ bản gửi lên Langfuse bị che.** Tài liệu khẳng định rõ ở ví dụ credit card — kết quả `print()` trong ứng dụng vẫn in ra số thẻ đầy đủ, còn span attributes gửi lên Langfuse mới là bản đã redact.

```python
from langfuse import Langfuse, observe

@observe()                                          # observe() sinh span cho hàm này
def process_payment():
    return "Customer paid with card number 4111 1111 1111 1111."

result = process_payment()
print(result)
```

**Kết quả in ra** (nguyên văn từ tài liệu):

```
Customer paid with card number 4111 1111 1111 1111.   ← print trong app: SỐ THẬT, không bị che
```

Số thẻ trên màn hình vẫn nguyên vì masking chỉ tác động lên luồng export lên Langfuse, không đụng vào giá trị hàm trả về. Đây là chỗ dễ hiểu nhầm nhất — thấy `print` ra số thật rồi tưởng masking không chạy.

---

## 2. Với LangChain — masking nằm ở đâu

Đây là câu hỏi thực dụng nhất khi ta dùng LangChain: cắm hàm masking vào chỗ nào. Câu trả lời của tài liệu (bản JS/TS): **cắm vào `LangfuseSpanProcessor`, không cắm vào `CallbackHandler`.** Span mà `CallbackHandler` của LangChain sinh ra tự động chảy qua span processor, nên không cần cấu hình masking riêng cho LangChain.

Nghĩa là handler giữ nguyên như bình thường; toàn bộ logic che dữ liệu gom về một chỗ duy nhất là processor.

```typescript
import { NodeSDK } from "@opentelemetry/sdk-node";
import { LangfuseSpanProcessor } from "@langfuse/otel";
import { CallbackHandler } from "@langfuse/langchain";

const spanProcessor = new LangfuseSpanProcessor({
  mask: ({ data }) => {                                     // data = JSON đã stringify của input/output/metadata
    if (typeof data === "string" && data.startsWith("SECRET_")) {
      return "REDACTED";                                    // giá trị thay thế được gửi lên Langfuse
    }
    return data;                                            // không khớp thì trả nguyên, không che
  },
});

const sdk = new NodeSDK({ spanProcessors: [spanProcessor] });
sdk.start();

const handler = new CallbackHandler();                      // handler KHÔNG cần cấu hình masking gì thêm
```

Hàm `mask` ở đây nhận một object `{ data }`, trong đó `data` là **chuỗi JSON đã stringify** của giá trị attribute, và trả về dữ liệu đã che. Nó được áp cho `input`, `output`, `metadata` của **mọi** observation.

> [!note]
> `data` là chuỗi JSON đã stringify, không phải object gốc. Muốn lọc theo cấu trúc (ví dụ chỉ che một field) thì phải tự parse chuỗi trong hàm `mask`, che xong stringify lại rồi trả về — nếu không sẽ redact theo pattern trên toàn chuỗi.

**Về LangChain chạy trên Python.** Trang tài liệu chỉ tách một tab "LangChain (JS/TS)" — **không có** tab LangChain cho Python. Suy luận: khi dùng LangChain qua SDK Python, span của LangChain đi qua span processor của Langfuse Python SDK, nên masking sẽ dùng chính hai hook Python ở [mục 3](#3-hai-hook-masking-của-python-sdk) (`mask_otel_spans` / `mask`) chứ không có cơ chế riêng. Căn cứ: cả hai bản SDK đều đặt masking ở tầng processor/client, và `mask_otel_spans` bắt attributes của "third-party instrumentations" ở khâu export — LangChain là một instrumentation như vậy. Đây là suy luận, chưa được tài liệu xác nhận trực tiếp; cần đối chiếu khi triển khai.

---

## 3. Hai hook masking của Python SDK

Nếu stack của ta là Python, có hai hook và chúng khác nhau ở **thời điểm chạy** và **phạm vi dữ liệu bắt được** — chọn nhầm thì có dữ liệu lọt qua mà không bị che.

| Hook | Trạng thái | Chạy khi nào | Bắt được dữ liệu gì |
|---|---|---|---|
| `mask_otel_spans` | Khuyến nghị | Ở khâu export, sau khi Langfuse đã quyết span nào được export và sau khi xử lý media | Raw OTel span attributes từ span của Langfuse SDK **và** từ instrumentation bên thứ ba do client này export |
| `mask` | Legacy | Đồng bộ, ngay khi attributes của Langfuse SDK được tạo | Chỉ dữ liệu đặt qua API của Langfuse SDK: `start_observation()`, `update()`, `set_trace_io()` |

Khác biệt cốt lõi nằm ở cột cuối: `mask` **không** soi được attributes thô từ instrumentation bên thứ ba (LangChain, OpenAI...), còn `mask_otel_spans` chạy ở khâu export nên bắt được cả những cái đó. Với setup Python mới, tài liệu nói thẳng: ưu tiên `mask_otel_spans`.

---

## 4. `mask_otel_spans` hoạt động ra sao

`mask_otel_spans` nhận một **lô (batch)** span sắp export, và trả về các **patch thưa** — chỉ mô tả span nào cần đổi, đổi attribute nào. Đây là hook được khuyến nghị nên cần nắm kỹ hợp đồng của nó.

Ví von: nó giống một khâu kiểm hóa cuối băng chuyền trước khi hàng rời kho. Kiểm hóa xem từng kiện, chỉ dán lại nhãn cho kiện nào có vấn đề (patch thưa), không đụng vào kiện đã sạch, và chỉ được sửa nhãn — không được đổi mã kiện, đổi tuyến hay gỡ kiện ra khỏi lô.

```python
from typing import Optional
from langfuse import Langfuse
from langfuse.types import (
    MaskOtelSpansParams,
    MaskOtelSpansResult,
    OtelSpanPatch,
)

def mask_otel_spans(*, params: MaskOtelSpansParams) -> Optional[MaskOtelSpansResult]:
    patches = {}

    for identifier, span in params.spans.items():           # duyệt từng span trong lô export
        if span.instrumentation_scope_name == "openai":     # chỉ đụng span do instrumentation "openai" sinh
            patches[identifier] = OtelSpanPatch(
                delete_attributes=(                          # xóa hẳn hai attribute chứa nội dung prompt/completion
                    "gen_ai.prompt.0.content",
                    "gen_ai.completion.0.content",
                ),
                set_attributes={"masking.applied": True},    # gắn cờ đánh dấu đã che
            )

    return MaskOtelSpansResult(span_patches=patches)        # trả về patch thưa; span không có trong dict thì giữ nguyên

langfuse = Langfuse(mask_otel_spans=mask_otel_spans)         # cắm hook vào client khi khởi tạo
```

**Hợp đồng của hook** (theo type contract công khai của Python SDK):

- `params.spans` là **một** lô export. Một lô **không đảm bảo** chứa trọn một trace, một request hay một cây observation. Đừng viết logic giả định đã có đủ ngữ cảnh của cả trace trong một lần gọi.
- Mỗi key là `OtelSpanIdentifier(trace_id, span_id)`. Khi trả patch phải **dùng lại đúng object identifier** lấy từ `params.spans`.
- Mỗi value là snapshot `OtelSpanData`, lấy **sau** bước lọc `should_export_span` và sau xử lý media ở khâu export. Hai mapping `attributes` và `resource_attributes` là **read-only**.
- Trả `None` để giữ nguyên cả lô.
- Trả `MaskOtelSpansResult(span_patches=...)` để xóa hoặc thay attributes trên các span đã chọn.
- Patch **thưa**: bỏ qua span nào không cần đổi.
- Trong một `OtelSpanPatch`, thứ tự là **xóa `delete_attributes` trước, rồi mới áp `set_attributes`** — nên nếu cùng một key xuất hiện ở cả hai, `set_attributes` thắng.
- Giá trị trong `set_attributes` phải là giá trị attribute OTel hợp lệ: string, bool, int, float, hoặc chuỗi (sequence) đồng nhất của các kiểu scalar đó.
- Hook **chỉ** đổi được span attributes. Không đổi được: tên span, các ID, quan hệ cha–con, resource attributes, events, links, instrumentation scope.
- Chỉ tác động span do **chính client Langfuse này** export. Nếu cùng span đó còn được gửi tới một exporter khác, exporter kia nhận **bản gốc chưa che** — phải cấu hình masking riêng cho từng non-Langfuse exporter.

### 4.1 Ràng buộc về hiệu năng và luồng thực thi

`mask_otel_spans` chạy **đồng bộ**. Thường nó chạy trên worker thread của OTel batch span processor nên không chặn thread chính của ứng dụng — nhưng khi `flush()` và lúc shutdown thì có thể chạy ngay trên caller thread.

Hệ quả thực dụng: giữ hàm **tất định (deterministic) và nhanh**. Gọi mạng được phép nhưng masking chậm sẽ làm nghẽn hàng đợi export và trễ việc gửi span. Tài liệu liệt kê những thứ cần tránh trong hàm masking: việc chạy lâu, retry vô hạn, state theo request, span đang active hiện tại, và I/O async.

### 4.2 Hành vi khi lỗi

Cách hook xử lý lỗi quyết định "mất mát" tới đâu, nên phải biết trước:

| Tình huống | Hậu quả |
|---|---|
| Hook ném exception, hoặc trả `MaskOtelSpansResult` không hợp lệ | Langfuse **bỏ nguyên lô** export |
| Một `OtelSpanPatch` riêng lẻ không hợp lệ | Langfuse chỉ **bỏ span đó** khỏi luồng export |
| Giá trị attribute trả về không hợp lệ | Chỉ **xóa đúng attribute** bị lỗi đó |

**!Note:** Đây đúng loại lỗi im lặng nguy hiểm — hook viết ẩu ném exception thì **cả lô** trace biến mất khỏi Langfuse chứ không phải chỉ một span. Không có log lỗi ở tầng nghiệp vụ, ta chỉ thấy trace "tự nhiên thiếu". Bọc phòng thủ và test kỹ hàm này.

---

## 5. `mask` (legacy) — khi nào vẫn dùng

`mask` là hook cũ của Python SDK, chạy **đồng bộ ngay khi attributes của Langfuse SDK được tạo**, và chỉ áp cho dữ liệu đặt qua API của SDK (`start_observation()`, `update()`, `set_trace_io()`). Nó **không** soi attributes OTel thô cuối cùng từ instrumentation bên thứ ba.

Chỉ dùng `mask` khi ta **cố ý** cần biến đổi dữ liệu ngay tại thời điểm tạo attribute của SDK. Ngoài trường hợp đó, setup mới nên chọn `mask_otel_spans`.

```python
from typing import Any
from langfuse import Langfuse

def masking_function(*, data: Any, **kwargs: Any) -> Any:
    if isinstance(data, str) and data.startswith("SECRET_"):
        return "REDACTED"                                   # chuỗi bắt đầu bằng SECRET_ thì che

    if isinstance(data, dict):                              # dict: đệ quy che từng value
        return {key: masking_function(data=value) for key, value in data.items()}

    if isinstance(data, list):                              # list: đệ quy che từng phần tử
        return [masking_function(data=item) for item in data]

    return data                                             # kiểu khác: trả nguyên

langfuse = Langfuse(mask=masking_function)                  # cắm hook legacy vào client
```

Khác biệt hình dạng so với `mask_otel_spans`: `mask` nhận thẳng `data` (giá trị Python gốc — str/dict/list) và trả về giá trị đã che, tự lo đệ quy vào cấu trúc lồng nhau; còn `mask_otel_spans` làm việc trên lô span và patch theo từng attribute key.

---

## 6. Áp dụng thực tế

App tư vấn khách hàng doanh nghiệp dùng LangChain, mỗi phiên chatbot ghi trace lên Langfuse để theo dõi chất lượng trả lời. Hội thoại có khách gõ số CCCD, số tài khoản, số thẻ vào ô chat. Không masking thì toàn bộ số này nằm trong input/output của trace trên Langfuse — vi phạm yêu cầu bảo mật dữ liệu cá nhân khách hàng.

Cách xử lý theo tài liệu:

- **JS/TS:** cắm một hàm `mask` vào `LangfuseSpanProcessor` (như [mục 2](#2-với-langchain--masking-nằm-ở-đâu)), quét pattern số thẻ/CCCD trên chuỗi `data`, thay bằng token che. `CallbackHandler` của LangChain giữ nguyên.
- **Python:** dùng `mask_otel_spans`, duyệt `span.attributes`, với attribute kiểu string thì `re.sub` pattern nhạy cảm, gom vào `OtelSpanPatch(set_attributes=...)`.

Ví dụ redact số thẻ (Python, nguyên từ tài liệu):

```python
import re
from langfuse.types import MaskOtelSpansResult, OtelSpanPatch

credit_card_pattern = re.compile(r"\b(?:\d[ -]*?){13,19}\b")   # bắt chuỗi 13–19 chữ số, cho phép xen space/gạch

def mask_otel_spans(*, params):
    patches = {}
    for identifier, span in params.spans.items():
        replacements = {}
        for key, value in span.attributes.items():
            if isinstance(value, str):                          # chỉ xử lý attribute kiểu chuỗi
                masked_value = credit_card_pattern.sub("[REDACTED CREDIT CARD]", value)
                if masked_value != value:                       # chỉ ghi patch khi thực sự có thay đổi
                    replacements[key] = masked_value
        if replacements:                                        # span có thay đổi mới thêm vào patch (giữ patch thưa)
            patches[identifier] = OtelSpanPatch(set_attributes=replacements)
    return MaskOtelSpansResult(span_patches=patches)
```

Tài liệu cũng cho sẵn pattern email và số điện thoại theo đúng khuôn này (`email_pattern`, `phone_pattern`), áp `.sub()` nối tiếp trên cùng một chuỗi rồi mới ghi patch — ghép thêm loại dữ liệu chỉ là thêm một dòng `re.sub`.

---

## 7. Nên dùng hook nào

Dùng **`mask_otel_spans`** khi: đang setup Python mới; cần che cả dữ liệu do instrumentation bên thứ ba (LangChain, OpenAI...) sinh ra; muốn thao tác ở mức OTel attribute cuối cùng trước export. Đây là mặc định tài liệu khuyến nghị.

Dùng **`mask`** (Python legacy) khi: cụ thể cần biến đổi tại thời điểm tạo attribute của Langfuse SDK, và chỉ quan tâm dữ liệu đặt qua API SDK.

Với **LangChain JS/TS**: cắm hàm `mask` vào `LangfuseSpanProcessor` — không có lựa chọn hook khác trong phạm vi trang này, và cũng không cần.

Điểm chung không được quên ở mọi hướng: masking chỉ áp cho **client Langfuse này**. Còn một exporter OTel khác trong hệ thống thì phải cấu hình che riêng, nếu không dữ liệu gốc vẫn thoát qua đường đó.

---

## Tham chiếu chéo

- [Chỉ mục Observability Features](./01-05-00-index.md) — vị trí của masking trong nhóm tính năng nâng cao
- Data Retention: `https://langfuse.com/docs/administration/data-retention` — tự động xóa trace/observation/score/media sau thời hạn lưu cấu hình sẵn
- Data Deletion: `https://langfuse.com/docs/administration/data-deletion` — xóa thủ công từng trace hoặc theo lô
- LangChain integration (JS/TS): `https://langfuse.com/integrations/frameworks/langchain` — nơi `CallbackHandler` được mô tả