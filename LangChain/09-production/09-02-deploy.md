---
title: Deploy
doc_source: https://docs.langchain.com/oss/python/langchain/deploy
accessed: 2026-07-28
lc_version: unknown
status: draft
lab:
related:
  - ./09-03-observability-hooks.md
---

# Deploy — đưa agent lên production

> Trang này trả lời một việc: khi agent đã chạy được ở máy local, làm sao đưa nó lên production. Con đường chính mà trang mô tả là **LangSmith Cloud** — hạ tầng được quản lý sẵn (managed) cho agent có trạng thái, chạy dài, cần lưu trạng thái bền và chạy nền.
> Bản thân cơ chế deploy (hạ tầng, scaling, vận hành) thuộc cây tài liệu `/langsmith/...` — **nguồn khác**. Trang này chỉ là bản quickstart trỏ vào đó.

---

## 1. Tổng quan

Khi sẵn sàng lên production, chọn một mô hình hosting hợp với stack của mình. Trang nêu bốn lựa chọn, nhưng chỉ hướng dẫn chi tiết một:

| Lựa chọn | Trang này có gì | Ghi chú |
|---|---|---|
| **LangSmith Cloud** | Hướng dẫn đầy đủ (mục 3–5) | Hạ tầng quản lý sẵn cho agent có trạng thái, chạy dài, lưu trạng thái bền, chạy nền |
| Hybrid | Chỉ nêu tên + link | Chi tiết ở `/langsmith/hybrid` |
| Standalone server | Chỉ nêu tên + link | Chi tiết ở `/langsmith/deploy-standalone-server` |
| Self-hosted với control plane | Chỉ nêu tên + link | Chi tiết ở `/langsmith/deploy-with-control-plane` |

Ba lựa chọn cuối trang chỉ đặt link, không mô tả. Nội dung của chúng thuộc trang khác — không viết vào file này.

**!Note:** Con đường deploy này gắn chặt với LangSmith và với **runtime LangGraph**. Ứng dụng phải "LangGraph-compatible" thì mới deploy được (xem mục 3, bước 1). Đây không phải kiểu deploy một script Python thuần — nó là deploy một đồ thị LangGraph.

---

## 2. Vì sao dùng LangSmith Cloud

### Khái niệm

LangSmith Cloud là hạ tầng do LangSmith quản lý toàn bộ. Bạn đẩy code lên, nó lo hạ tầng, scaling và các mối lo vận hành.

### Vai trò

Agent thật khác một hàm gọi một phát rồi xong: nó **có trạng thái** (state), **chạy dài** (long-running), cần **lưu trạng thái bền** (persistent state) qua nhiều lượt, và có thể **chạy nền** (background execution). Tự dựng hạ tầng cho mấy tính chất này rất tốn công. Cloud gánh phần đó để bạn chỉ lo code agent.

### Áp dụng thực tế

Một agent thẩm định hồ sơ chạy nhiều bước, mỗi bước chờ người duyệt rồi mới đi tiếp (kiểu dừng chờ người duyệt — xem `03-08`). Giữa các lần chờ, trạng thái hồ sơ phải được giữ nguyên chứ không mất khi tiến trình rảnh. LangSmith Cloud giữ trạng thái đó, thay vì mình phải tự dựng database + hàng đợi + tiến trình nền.

Chi tiết Cloud lo những gì, giới hạn ra sao — thuộc trang `/langsmith/deploy-to-cloud`, nguồn khác.

---

## 3. Các bước deploy lên LangSmith Cloud

### Điều kiện cần

- Một tài khoản GitHub (repo công khai hoặc riêng tư đều được).
- Một tài khoản LangSmith (miễn phí).

### Năm bước

**Bước 1 — Đưa code lên repo GitHub.** Code ứng dụng phải nằm trong một repo GitHub thì LangSmith mới deploy được. Trước khi đẩy, làm cho app "LangGraph-compatible" theo hướng dẫn dựng server local (trang `studio`), rồi push code lên repo.

**Bước 2 — Deploy trên LangSmith.** Đăng nhập LangSmith → sidebar trái chọn **Deployments** → nút **+ New Deployment** → nếu lần đầu (hoặc thêm repo riêng tư chưa nối) thì bấm **Add new account** để nối tài khoản GitHub → chọn repo → **Submit**. Quá trình này mất khoảng **15 phút**; theo dõi ở mục **Deployment details**.

**Bước 3 — Thử app trong Studio.** Khi deploy xong, chọn deployment vừa tạo → bấm nút **Studio** ở góc trên bên phải để mở đồ thị của agent.

**Bước 4 — Lấy API URL.** Trong **Deployment details**, bấm vào **API URL** để copy vào clipboard.

**Bước 5 — Thử gọi API.** Xem mục 4.

Chi tiết từng màn hình LangSmith (Deployments, Studio) thuộc giao diện LangSmith, không nằm trong trang này.

---

## 4. Gọi thử API sau khi deploy

### Vai trò

Sau bước 4, agent đã sống ở một URL. Cần kiểm tra nó nhận request và trả kết quả. Trang cho hai cách gọi: Python SDK và REST thô (curl).

> **Về khối kết quả in ra.** Trang gốc **không in output** cho ví dụ nào. Khối kết quả dưới đây tôi tự dựng lại từ cấu trúc code (mỗi vòng lặp in một dòng loại sự kiện rồi in dữ liệu). Tên loại sự kiện cụ thể chưa đọc được từ tài liệu — cần đối chiếu khi chạy thử.

### Cách 1 — Python, dùng `langgraph-sdk`

Lưu ý: đây là gói `langgraph-sdk`, **không phải** `langchain`. Deploy đi qua runtime LangGraph nên client cũng là client của LangGraph.

```bash
pip install langgraph-sdk        # gói client để gọi deployment, khác với langchain
```

```python
from langgraph_sdk import get_sync_client   # get_client nếu muốn bản bất đồng bộ (async)

client = get_sync_client(url="your-deployment-url", api_key="your-langsmith-api-key")

for chunk in client.runs.stream(       # gọi agent, nhận kết quả chảy dần theo từng mẩu
    None,                              # threadless run — không gắn vào luồng hội thoại có sẵn
    "agent",                           # tên agent, khai báo trong langgraph.json
    input={
        "messages": [{
            "role": "human",
            "content": "What is LangGraph?",
        }],
    },
    stream_mode="updates",             # "updates" = mỗi mẩu là phần state vừa đổi ở một chặng
):
    print(f"Receiving new event of type: {chunk.event}...")   # loại sự kiện của mẩu này
    print(chunk.data)                                         # dữ liệu kèm theo mẩu
    print("\n\n")
```

**Kết quả in ra** (dựng lại):

```
Receiving new event of type: metadata...        ← mẩu đầu, thường là thông tin lần chạy (run id...)
{'run_id': '...'}                               ← nội dung metadata — hình dạng chưa xác minh
                                                ← (print("\n\n") tạo dòng trống ngăn cách)

Receiving new event of type: updates...         ← mẩu cập nhật state; "updates" đúng như stream_mode
{'agent': {'messages': [...]}}                  ← phần state vừa đổi ở chặng "agent" — dựng lại, chưa chắc đúng khóa

...                                             ← còn nhiều mẩu updates cho tới khi chạy xong
```

Khối trên chỉ minh họa **hình dạng chung** mà hai lệnh `print` sinh ra: một dòng "Receiving new event of type: ..." rồi một dòng dữ liệu. **Giá trị thật của `chunk.event`** (ví dụ có đúng là `metadata`/`updates` không) và **khóa trong `chunk.data`** chưa đọc được từ trang này — phải chạy thử mới xác nhận.

### Cách 2 — REST thô (curl)

```bash
curl -s --request POST \
    --url <DEPLOYMENT_URL>/runs/stream \
    --header 'Content-Type: application/json' \
    --header "X-Api-Key: <LANGSMITH API KEY> \
    --data "{
        \"assistant_id\": \"agent\",       # tên agent, khai báo trong langgraph.json
        \"input\": {
            \"messages\": [
                {
                    \"role\": \"human\",
                    \"content\": \"What is LangGraph?\"
                }
            ]
        },
        \"stream_mode\": \"updates\"
    }"
```

**!Note:** Trong bản doc, dòng header của lệnh curl **thiếu dấu nháy đóng**: `--header "X-Api-Key: <LANGSMITH API KEY> \` (đúng phải là `...KEY>" \`). Chép nguyên si sẽ lỗi cú pháp shell — code chạy không nổi chứ không phải lỗi im lặng. Khi dùng phải tự thêm dấu `"` đóng sau `<LANGSMITH API KEY>`.

---

## Phạm vi trang này dừng ở đâu

Trang này chỉ là quickstart deploy qua LangSmith Cloud. Ba mô hình hosting còn lại (hybrid, standalone server, self-hosted với control plane), toàn bộ chi tiết vận hành, scaling, giới hạn, cấu hình `langgraph.json` — đều thuộc cây tài liệu LangSmith/LangGraph, là **nguồn khác**. Khi đưa những phần đó vào vault, ghi rõ nguồn LangSmith chứ không gán cho trang LangChain OSS này.

---

## Tham chiếu chéo

- [09-03 Observability hooks](./09-03-observability-hooks.md) — sau khi deploy, dùng tracing để theo dõi agent trên production.
- LangSmith Deployment overview (nguồn khác): `docs.langchain.com/langsmith/deployment` — hybrid, standalone, self-hosted.
- LangSmith Deploy to Cloud (nguồn khác): `docs.langchain.com/langsmith/deploy-to-cloud` — chi tiết Cloud.
- LangChain Studio / server local (cùng cây OSS): `docs.langchain.com/oss/python/langchain/studio` — bước làm app "LangGraph-compatible".