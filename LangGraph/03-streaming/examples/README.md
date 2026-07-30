# Ví dụ chạy được — 03-01-streaming.md

Script Python minh họa từng mode streaming của LangGraph, khớp với các mục trong
[`../03-01-streaming.md`](../03-01-streaming.md). File `.md` chỉ trình bày khái niệm;
folder này giữ code chạy được và output thật.

## Cài đặt

```bash
pip install -r requirements.txt
```

Mặc định mọi ví dụ chạy **offline, không cần API key** — dùng `GenericFakeChatModel`
lặp qua vài câu joke mẫu (xem `graph.py`). Muốn chạy với model thật (Gemini), đặt biến
môi trường `GOOGLE_API_KEY` trước khi chạy; `graph.get_model()` sẽ tự chuyển sang
`ChatGoogleGenerativeAI(model="gemini-2.0-flash")`.

## Chạy

```bash
python 01_basic_stream.py          # một ví dụ
for f in 0*.py; do python "$f"; done   # tất cả, lần lượt (bash)
```

Trên Windows PowerShell, nếu gặp lỗi `UnicodeEncodeError` khi in tiếng Việt ra
console, đặt `PYTHONIOENCODING=utf-8` trước khi chạy.

## File ↔ mục trong 03-01-streaming.md

| File | Mục trong doc |
|---|---|
| `graph.py` | Graph mẫu dùng chung (không phải một mục riêng) |
| `01_basic_stream.py` | Mục 1 — Tổng quan |
| `02_v1_vs_v2_shape.py` | Mục 2 — `version="v2"` |
| `03_values_updates.py` | Mục 4.1 — `values` và `updates` |
| `04_messages_tokens.py` | Mục 4.2 — `messages`, lọc theo tag/node/`nostream` |
| `05_custom_data.py` | Mục 4.3 — `custom` qua `get_stream_writer` |
| `06_subgraphs.py` | Mục 4.4 — `subgraphs=True` |
| `07_checkpoints_tasks_debug.py` | Mục 4.5 — `checkpoints`, `tasks`, `debug` |
| `08_multiple_modes.py` | Mục 5 — nhiều mode cùng lúc |
| `09_advanced.py` | Mục 6 — tắt streaming, `invoke()` v2 trả `GraphOutput` |

## Output là thật

Mỗi file có khối `# ---- OUTPUT THẬT ----` ở cuối, dán từ lần chạy thực tế
(2026-07-29, `langgraph==1.2.10`, `langchain-core==1.5.2`, Python 3.14.6), không phải
dựng lại. `checkpoint_id`/`timestamp` trong ví dụ `07_...` đổi mỗi lần chạy (UUID theo
thời gian) nên được ghi dưới dạng rút gọn `<uuid>`/`<iso>`.

## Chỗ lệch giữa doc và hành vi thực tế quan sát được

- `02_v1_vs_v2_shape.py`: chunk `type="values"` ở `version="v2"` thực tế có thêm khóa
  `interrupts` ngoài ba khóa `type`/`ns`/`data` mà trang gốc mô tả. Chunk `type="updates"`
  thì không có khóa này. Trang gốc không nhắc chi tiết này.

## Ví dụ chưa chạy được

Không có — cả 9 file đều chạy thành công với fake model offline, dùng `langgraph==1.2.10`.
