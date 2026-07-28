---
title: LangSmith Studio
doc_source: https://docs.langchain.com/oss/python/langchain/studio
accessed: 2026-07-25
lc_version: unknown
status: draft
lab:
related:
  - ./deploy.md          # chưa có file — xem Tham chiếu chéo
  - ../03-agent-harness/  # file agent (create_agent) — chỉnh lại tên chính xác khi đặt vào cây thư mục
---

# LangSmith Studio (`langgraph dev`)

> Giao diện trực quan chạy trên trình duyệt để phát triển và gỡ lỗi agent LangChain ngay trên máy local. Miễn phí, không cần deploy.
> Dựng lên bằng LangGraph CLI qua một lệnh `langgraph dev`; agent bên trong thường tạo bằng `create_agent` (xem file agent).

---

## 1. Tổng quan

Khi chạy agent bằng script thuần, mọi thứ bên trong đều ẩn: prompt nào được gửi tới model, tool nào được gọi với tham số gì, model trả về ra sao. Muốn thấy, phải tự nhét `print` khắp nơi hoặc dựng log. Studio phơi bày toàn bộ chuỗi đó trong một giao diện web, không cần thêm dòng code nào.

Điểm khác biệt cốt lõi so với công cụ debug quen thuộc nằm ở kiến trúc **hai nửa**: giao diện chạy trên cloud (`smith.langchain.com`), còn agent chạy trên máy local. Studio chỉ *kết nối tới* server local qua trình duyệt để đọc từng chặng — bản thân code và (nếu tắt tracing) dữ liệu không rời máy.

Sau khi cấu hình xong, một lệnh duy nhất dựng cả server lẫn điểm kết nối:

```shell
langgraph dev                                        # dựng server dev local, mở sẵn kết nối cho Studio
```

**Kết quả** — server local chạy lên và có thể truy cập theo hai đường:

```
API:       http://127.0.0.1:2024                                              ← gọi agent trực tiếp qua API
Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024  ← mở giao diện, trỏ về server local ở trên
```

Studio UI nằm trên tên miền cloud nhưng tham số `baseUrl` trỏ ngược về `127.0.0.1:2024` — đó chính là chỗ nối hai nửa: giao diện cloud đọc dữ liệu từ server đang chạy trên máy bạn.

---

## 2. Studio dùng để làm gì

**Khái niệm.** Một môi trường phát triển trực quan cho agent: chạy thử input, xem toàn bộ vết thực thi (execution trace), chỉnh code rồi chạy lại — tất cả trong trình duyệt.

**Vai trò.** Nó thay cho vòng lặp "sửa code → thêm print → chạy lại terminal → đọc log rối". Với agent nhiều chặng (model gọi tool, tool trả kết quả, model gọi tiếp), log terminal phẳng rất khó lần theo thứ tự. Studio dựng lại chuỗi đó thành từng bước tách bạch, kèm số liệu token và độ trễ (latency) mỗi bước.

**Áp dụng thực tế.** Một agent gửi email có tool `send_email(to, subject, body)`. Khi test, email cứ gửi nhầm người nhận. Chạy trong Studio, mở đúng bước tool call, thấy model điền `to="sếp"` thay vì địa chỉ thật — lỗi nằm ở system prompt chứ không phải ở hàm gửi. Không có Studio thì phải đoán mò giữa prompt, model và tool xem chỗ nào sai.

Doc còn nêu: khi có lỗi (exception), Studio bắt luôn ngoại lệ cùng trạng thái xung quanh tại thời điểm đó, nên đọc được ngữ cảnh đã dẫn tới lỗi thay vì chỉ thấy dòng traceback.

---

## 3. Điều kiện cần trước khi bắt đầu

Ba thứ phải có sẵn:

| Điều kiện | Chi tiết |
|---|---|
| Tài khoản LangSmith | Đăng ký miễn phí tại `smith.langchain.com` |
| LangSmith API key | Studio dùng khóa này để kết nối server local — không có khóa thì không nối được |
| (Tùy chọn) Tắt tracing | Đặt `LANGSMITH_TRACING=false` trong `.env` nếu không muốn dữ liệu bị gửi (traced) lên LangSmith |

> **!Note (quan trọng với dữ liệu nhạy cảm):** Mặc định tracing **bật**. Nghĩa là nếu không chủ động đặt `LANGSMITH_TRACING=false`, mọi input/output của agent sẽ được đẩy lên LangSmith cloud. Doc khẳng định: chỉ khi tắt tracing thì "không dữ liệu nào rời khỏi server local". Đây là lỗi im lặng điển hình — code chạy trơn tru, không cảnh báo, nhưng dữ liệu đã ra ngoài.

---

## 4. Sáu bước dựng server local và mở Studio

Cấu trúc thư mục đích sau khi làm xong:

```
my-app/
├── src
│   └── agent.py            ← file định nghĩa agent
├── .env                    ← khóa API + biến môi trường
└── langgraph.json          ← file cấu hình cho LangGraph CLI
```

### 4.1 Cài LangGraph CLI

CLI này cung cấp server dev local (doc gọi là Agent Server) — chính là thứ nối agent với Studio.

```shell
# Python >= 3.11 là bắt buộc
pip install --upgrade "langgraph-cli[inmem]"        # [inmem] = bản server chạy trong bộ nhớ, dùng cho dev local
```

**!Note:** Python dưới 3.11 sẽ không cài được. Đây là ngưỡng doc nêu rõ.

### 4.2 Chuẩn bị agent

Nếu đã có sẵn agent LangChain thì dùng thẳng. Ví dụ của doc là một agent gửi email tối giản:

```python
from langchain.agents import create_agent

def send_email(to: str, subject: str, body: str):
    """Send an email"""
    # ... phần logic gửi email thật
    return f"Email sent to {to}"                     # tool phải trả về chuỗi để model đọc kết quả

agent = create_agent(
    "gpt-5.5",                                       # tên model — xem !Note bên dưới
    tools=[send_email],                              # danh sách tool agent được phép gọi
    system_prompt="You are an email assistant. Always use the send_email tool.",  # chỉ thị cố định
)
```

`create_agent` tự trả về một LangGraph graph đã dựng sẵn (compiled) — đây là lý do ở bước 4.4 có thể trỏ thẳng vào biến `agent` mà không cần bước dựng graph riêng.

> **!Note:** `"gpt-5.5"` là tên model xuất hiện nguyên văn trong doc. Chưa xác minh được đây là model có thật hay chỉ placeholder trong ví dụ; khi chạy thử phải thay bằng tên model thật mà nhà cung cấp đang hỗ trợ, nếu không lệnh sẽ báo lỗi model không tồn tại.

### 4.3 Khai báo biến môi trường

Tạo file `.env` ở gốc project, dán API key lấy từ trang settings của LangSmith:

```bash
LANGSMITH_API_KEY=lsv2...                            # khóa lấy từ smith.langchain.com/settings, tiền tố lsv2
```

> **!Note:** `.env` **không được** commit lên version control (Git). File này chứa khóa API — lộ khóa là lộ quyền truy cập tài khoản LangSmith. Đây là cảnh báo doc nêu trực tiếp.

### 4.4 File cấu hình langgraph.json

CLI dùng file này để biết agent nằm ở đâu và cần cài phụ thuộc gì. Tạo `langgraph.json` trong thư mục app:

```json
{
  "dependencies": ["."],
  "graphs": {
    "agent": "./src/agent.py:agent"
  },
  "env": ".env"
}
```

JSON không cho phép chú thích, nên ý nghĩa từng khóa để ở đây:

| Khóa | Giá trị mẫu | Nghĩa |
|---|---|---|
| `dependencies` | `["."]` | Cài chính thư mục hiện tại như một package |
| `graphs` | `{"agent": "./src/agent.py:agent"}` | Định dạng `tên_hiển_thị: đường_dẫn_file:tên_biến`. Ở đây trỏ tới biến `agent` trong `src/agent.py` |
| `env` | `.env` | File chứa biến môi trường (đã tạo ở 4.3) |

> **!Note:** Đường dẫn trong `graphs` phải khớp đúng vị trí thật của file. Doc đặt file ở `src/agent.py` nên đường dẫn là `./src/agent.py:agent`. Nếu để file chỗ khác mà không sửa đường dẫn, server sẽ không tìm thấy agent. (Nhắc thêm: tiêu đề khối code agent ở 4.2 ghi `agent.py` chỉ là nhãn tên file, vị trí thật vẫn là `src/agent.py` theo cây thư mục.)

Giải thích chi tiết từng khóa của file cấu hình nằm ở trang tham chiếu LangGraph CLI (xem Tham chiếu chéo) — không lặp lại ở đây.

### 4.5 Cài dependencies

Từ thư mục gốc, cài phụ thuộc của project. Doc cho hai cách:

```shell
pip install langchain langchain-openai              # cách 1: pip
```

```shell
uv add langchain langchain-openai                   # cách 2: uv (trình quản lý package nhanh hơn)
```

### 4.6 Chạy server và mở Studio

```shell
langgraph dev                                        # dựng server dev, giữ nó chạy để Studio kết nối
```

Server lên xong, truy cập theo hai đường đã nêu ở mục 1: API tại `http://127.0.0.1:2024` và Studio UI tại `https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024`.

---

## 5. Studio làm được gì sau khi kết nối

Bốn năng lực doc nêu, tất cả không cần viết thêm code:

- **Xem trọn vẹn vết thực thi.** Chạy một input, đọc toàn bộ trace: prompt gửi tới model, tham số tool, giá trị trả về, cùng số liệu token và độ trễ mỗi bước.

- **Bắt lỗi kèm ngữ cảnh.** Khi có ngoại lệ, Studio giữ lại trạng thái xung quanh thời điểm lỗi để lần được nguyên nhân, thay vì chỉ đưa dòng traceback trơ trọi.

- **Hot-reload.** Sửa prompt hoặc chữ ký tool (tool signature) trong code, Studio cập nhật ngay, không phải khởi động lại server.

- **Chạy lại thread từ bất kỳ bước nào.** Chạy lại một luồng hội thoại từ một chặng giữa chừng để test thay đổi mà không phải làm lại từ đầu.

---

## Tham chiếu chéo

- File agent (`create_agent`) — định nghĩa agent mà Studio nạp vào. Chỉnh lại đường dẫn tương đối chính xác khi đặt file này vào cây thư mục project.
- `deploy.md` — trang doc *Deployment* (`/oss/python/langchain/deploy`) nói về agent đã deploy, khác với Studio (chạy local). File này **chưa được nghiên cứu**.
- Các hướng dẫn vận hành Studio chi tiết (Run application, Manage assistants, Manage threads, Iterate on prompts, Debug traces, Add node to dataset) nằm ở **cây doc LangSmith** (`/langsmith/...`), không thuộc cây `langchain` — khi làm file cho những trang đó cần ghi rõ nguồn LangSmith.
- Tham chiếu cấu hình `langgraph.json` từng khóa: trang **LangGraph CLI** (`/langsmith/cli#configuration-file`).
- Khái niệm tracing/traces: trang **LangSmith observability** (`/langsmith/observability-concepts#traces`).