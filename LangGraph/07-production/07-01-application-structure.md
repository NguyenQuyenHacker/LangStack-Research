---
title: Cấu trúc ứng dụng
doc_source: https://docs.langchain.com/oss/python/langgraph/application-structure
accessed: 2026-07-30
lc_version: unknown
status: draft
lab:
related:
  - ./07-03-backward-compatibility.md
---

# Cấu trúc ứng dụng LangGraph (`langgraph.json`)

> Bộ quy ước về cây thư mục + một file khai báo để nền tảng quản lý (LangSmith Deployment) biết cách nạp và chạy đồ thị của ta.
> Trang này nói về *đóng gói để deploy*, không nói về cách viết logic bên trong đồ thị.

---

## 1. Tổng quan

Một ứng dụng LangGraph không phải là một script Python chạy thẳng bằng `python agent.py`. Nó là bốn thứ đứng cạnh nhau: một hoặc nhiều **đồ thị** (graph) chứa logic, một file **`langgraph.json`** khai báo cấu hình, một file khai **phụ thuộc** (`requirements.txt` hoặc `pyproject.toml`), và một file **`.env`** tùy chọn cho biến môi trường.

Điểm khác với một dự án Python thường: khi deploy lên nền tảng quản lý, không ai chạy khối `if __name__ == "__main__"` của ta cả. Nền tảng cần một *bản khai* cho biết đồ thị nằm ở đâu, cần cài thư viện gì, đọc biến môi trường ở đâu. `langgraph.json` chính là bản khai đó — thiếu nó thì có code cũng không deploy được.

Đơn vị nhỏ nhất chạy được là một `langgraph.json` ba khóa:

```json
{
  "dependencies": ["langchain_openai", "./your_package"],
  "graphs": {
    "my_agent": "./your_package/your_file.py:agent"
  },
  "env": "./.env"
}
```

Trang tài liệu này là trang cấu hình/cấu trúc, không có đoạn code in ra stdout để minh họa. "Kết quả" ở đây là chính cây thư mục và file JSON — nên phần dưới không có khối output nào, và cũng không dựng lại output giả.

**Quan hệ với deploy.** Cả trang phục vụ đúng một việc: deploy bằng LangSmith Deployment — nền tảng hosting có quản lý, lo hạ tầng và scale để ta chạy agent stateful, chạy dài. Nếu chỉ chạy đồ thị trong tiến trình Python của mình, không đụng tới nền tảng, thì phần lớn trang này có thể bỏ qua.

---

## 2. Cấu trúc thư mục — quy ước, không phải luật

Cây thư mục chuẩn tách phần logic đồ thị khỏi phần tiện ích, để file dựng đồ thị (`agent.py`) gọn và dễ đọc. Đây là **nỗi đau** nó lo: khi dự án lớn, nếu tools, node và định nghĩa state trộn chung một file thì rất khó lần. Quy ước dưới đây gom mỗi loại vào một chỗ.

```plaintext
my-app/
├── my_agent                  # toàn bộ code dự án nằm trong đây
│   ├── utils                 # nhóm tiện ích cho đồ thị
│   │   ├── __init__.py
│   │   ├── tools.py          # các tool đồ thị gọi
│   │   ├── nodes.py          # hàm xử lý cho từng node
│   │   └── state.py          # định nghĩa state của đồ thị
│   ├── __init__.py
│   └── agent.py              # code dựng đồ thị — đây là nơi biến đồ thị được tạo
├── .env                      # biến môi trường
├── requirements.txt          # phụ thuộc gói (bản dùng requirements)
└── langgraph.json            # file cấu hình cho LangGraph
```

Bản dùng `pyproject.toml` giống hệt, chỉ thay hai dòng cuối: bỏ `requirements.txt`, thêm `pyproject.toml` để khai phụ thuộc.

**!Note:** Cây thư mục này *không bắt buộc*. Tài liệu nói rõ cấu trúc thư mục có thể khác nhau tùy ngôn ngữ và trình quản lý gói. Cái nền tảng thật sự cần không phải là các tên thư mục `my_agent/`, `utils/` — mà là đường dẫn ta khai trong `langgraph.json` trỏ đúng tới file chứa đồ thị. Đổi tên thư mục thoải mái, miễn là sửa đường dẫn trong `langgraph.json` cho khớp. Bám cứng đúng tên trong ví dụ mà quên điểm này là hiểu ngược bản chất.

---

## 3. `langgraph.json` — bản khai báo với nền tảng

File này trả lời cho nền tảng ba câu: cài gì, đồ thị ở đâu, đọc biến môi trường ở đâu. Nó là file JSON đặt ở thư mục gốc dự án.

Ví von cho dễ hình dung: coi nó như **tờ khai giao nhận** dán ngoài một kiện hàng. Bên nhận không mở kiện ra đọc từng món — họ đọc tờ khai để biết trong kiện có gì, món chính nằm ở ngăn nào, cần dụng cụ gì để mở. Nền tảng cũng vậy: nó không quét cả codebase để đoán đâu là đồ thị, nó đọc `langgraph.json`.

Ba khóa lõi trong ví dụ ở Mục 1:

| Khóa | Kiểu | Chứa gì |
|---|---|---|
| `dependencies` | mảng chuỗi | Danh sách phụ thuộc: tên gói trên PyPI (`"langchain_openai"`) và/hoặc gói cục bộ trỏ bằng đường dẫn (`"./your_package"`). Xem Mục 5. |
| `graphs` | object | Ánh xạ *tên đồ thị* → *đường dẫn tới đồ thị*. Xem Mục 4. |
| `env` | chuỗi | Đường dẫn file `.env` để nạp biến môi trường (dùng khi chạy cục bộ). Xem Mục 6. |

Đọc ví dụ Mục 1 theo tờ khai: cài `langchain_openai` cùng gói cục bộ `./your_package`; nạp một đồ thị tên `my_agent` lấy từ biến `agent` trong `./your_package/your_file.py`; đọc biến môi trường từ `./.env`.

**Khoảng trống của trang này.** Ngoài ba khóa trên, `langgraph.json` còn nhận thêm khóa khác — trang này chỉ nhắc thêm `dockerfile_lines` (Mục 5) và gọi chung phần còn lại là "các thiết lập khác". Danh sách khóa đầy đủ (ví dụ `auth`, `store`, `http`, `node_version`, `pip_installer`...) không nằm trong phạm vi trang này; tài liệu trỏ sang trang tham chiếu LangGraph CLI để tra. Khi cần khóa ngoài ba cái lõi, phải mở trang CLI reference, đừng suy từ trang này.

**!Note:** LangGraph CLI mặc định tìm file tên đúng `langgraph.json` ở thư mục hiện hành. Đặt tên khác hoặc để sai thư mục thì CLI không thấy — phải chỉ đường bằng cờ `-c/--config`.

---

## 4. `graphs` — chỉ đường tới đồ thị

Khóa `graphs` cho nền tảng biết ứng dụng cung cấp những đồ thị nào và mỗi cái nằm đâu. Không có nó, nền tảng có code nhưng không biết điểm vào.

Mỗi đồ thị gồm hai phần: một **tên** (phải là duy nhất trong ứng dụng) và một **đường dẫn**. Đường dẫn trỏ tới một trong hai thứ: (1) một đồ thị đã compile, hoặc (2) một hàm dựng ra đồ thị.

Cú pháp đường dẫn là điểm dễ sai nhất của cả trang:

```json
"graphs": {
  "my_agent": "./your_package/your_file.py:agent"
}
```

Đọc phần bên phải: `đường-dẫn-file` + dấu `:` + `tên-biến`. Ở đây là file `./your_package/your_file.py`, lấy biến tên `agent` bên trong file đó. Biến `agent` này chính là đồ thị đã compile hoặc hàm dựng đồ thị.

Được khai nhiều đồ thị: thêm nhiều cặp tên→đường dẫn trong cùng object `graphs`.

**!Note:** Phần trước dấu `:` là *đường dẫn file* (`./your_package/your_file.py`), **không phải** đường dẫn module kiểu chấm (`your_package.your_file`). Theo thói quen viết `import` mà gõ thành `"your_package.your_file:agent"` là một lỗi rất dễ mắc — và nó không lộ ra lúc viết, chỉ lộ khi nền tảng nạp đồ thị và không tìm thấy.

---

## 5. `dependencies` — khai phụ thuộc thư viện

Ứng dụng LangGraph thường phụ thuộc các gói Python khác, và khai đúng chúng là điều kiện để môi trường deploy dựng lên chạy được. Việc khai gồm ba lớp, mỗi lớp lo một phần:

Lớp thứ nhất là **file khai phụ thuộc** trong thư mục — `requirements.txt`, `pyproject.toml`, hoặc `package.json` (với JS). Đây là danh sách gói theo chuẩn của trình quản lý gói.

Lớp thứ hai là **khóa `dependencies` trong `langgraph.json`**. Nó cho nền tảng biết những phụ thuộc nào cần có để chạy ứng dụng. Giá trị là mảng, trộn được hai loại: tên gói (`"langchain_openai"`) và đường dẫn gói cục bộ (`"./your_package"`).

Lớp thứ ba, khi cần **binary hoặc thư viện hệ thống** ngoài gói Python, khai qua khóa `dockerfile_lines` trong `langgraph.json` — mỗi dòng là một lệnh thêm vào Dockerfile lúc dựng ảnh.

**!Note:** Hai chỗ khai phụ thuộc (file `requirements.txt` và khóa `dependencies`) phục vụ mục đích khác nhau, đừng nhầm là một. Trang này không nói rõ quan hệ chính xác giữa hai chỗ khi chúng lệch nhau — điểm này còn để ngỏ, phải đối chiếu trang CLI reference khi dựng thực tế.

---

## 6. Biến môi trường — `.env` và khóa `env`

Biến môi trường (khóa API, chuỗi kết nối...) được nạp khác nhau giữa chạy cục bộ và chạy production, và trộn hai cách này là nguồn lỗi cấu hình phổ biến.

Khi làm việc **cục bộ** với ứng dụng đã deploy, khai biến qua khóa `env` trong `langgraph.json` — trỏ tới file `.env` như ví dụ Mục 1.

Khi lên **production**, thông thường ta không dùng file `.env` nữa mà cấu hình biến trực tiếp trong môi trường deploy. Nghĩa là file `.env` cục bộ chủ yếu để chạy thử, còn giá trị thật trên production đặt ở nơi khác.

**!Note:** Vì hai đường nạp khác nhau, một biến chạy đúng ở máy mình (nhờ `.env`) vẫn có thể rỗng trên production nếu quên đặt lại trong môi trường deploy. Đây là lỗi im lặng điển hình: code không báo lỗi cấu hình, chỉ hành xử sai vì biến rỗng.

---

## 7. Bảng tổng hợp — bốn thành phần bắt buộc

| Thành phần | File / khóa | Vai trò | Bỏ được không |
|---|---|---|---|
| Đồ thị (graphs) | file `.py` + khóa `graphs` | Chứa logic ứng dụng, là điểm vào | Không |
| File cấu hình | `langgraph.json` | Bản khai: cài gì, đồ thị ở đâu, env ở đâu | Không |
| File phụ thuộc | `requirements.txt` / `pyproject.toml` | Danh sách gói theo chuẩn trình quản lý gói | Không |
| Biến môi trường | `.env` + khóa `env` | Cấu hình khóa API, chuỗi kết nối | Có — `.env` là tùy chọn |

Chốt lại: đồ thị là phần ta viết; ba thứ còn lại là phần *khai báo* để nền tảng biết cách nạp và chạy phần ta viết. Nắm được ranh giới "code" và "bản khai" này là đủ để không lạc khi mở một dự án LangGraph lần đầu.

---

## Tham chiếu chéo

- [07-03 Tương thích ngược](./07-03-backward-compatibility.md) — quan hệ giữa cấu trúc/cấu hình và các thay đổi phá vỡ tương thích qua các phiên bản.
- Trang gốc: `https://docs.langchain.com/oss/python/langgraph/application-structure`
- Danh sách khóa đầy đủ của `langgraph.json`: trang tham chiếu LangGraph CLI (chưa fetch trong lần soạn này — cần bổ sung khi tra).