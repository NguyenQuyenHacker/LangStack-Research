---
title: Multi-agent — tổng quan
doc_source: https://docs.langchain.com/oss/python/langchain/multi-agent/index
accessed: 2026-07-25
lc_version: unknown
status: draft
lab:
related:
  - ./04-02-subagents.md
  - ./04-03-handoffs.md
  - ./04-04-skills.md
  - ./04-05-router.md
  - ./04-06-custom-workflow.md
---

# Multi-agent — tổng quan


## 1. Tổng quan

Hệ multi-agent là hệ ghép nhiều thành phần chuyên biệt để xử lý một luồng công việc phức tạp. 

Không phải việc phức tạp nào cũng cần đến nó — một agent đơn với đúng bộ tool và đúng prompt (kể cả tool/prompt đổi động theo tình huống) thường cho kết quả tương đương.

**Ba nhu cầu đẩy cần sang multi-agent.** :

- **Quản lý ngữ cảnh** — nạp kiến thức chuyên biệt mà không làm tràn cửa sổ ngữ cảnh của model. Nếu ngữ cảnh vô hạn và độ trễ bằng không thì cứ nhồi hết mọi kiến thức vào một prompt; nhưng thực tế không vậy, nên cần cách chọn lọc chỉ đưa ra phần liên quan.
- **Phát triển phân tán** — nhiều nhóm tự dựng và bảo trì từng năng lực độc lập, rồi ghép lại thành hệ lớn với ranh giới rõ ràng.
- **Chạy song song** — sinh ra nhiều worker chuyên biệt cho các việc con và chạy đồng thời cho nhanh.

Multi-agent đáng dùng nhất khi: một agent đơn có quá nhiều [tool](../03-agent-harness/03-02-tools.md) và chọn sai tool; hoặc việc cần kiến thức chuyên biệt với ngữ cảnh dày (prompt dài, tool riêng ngành); hoặc cần ép ràng buộc tuần tự — chỉ mở khóa năng lực sau khi thỏa điều kiện nào đó.

Trung tâm của mọi thiết kế multi-agent là **context engineering** — quyết định mỗi agent được thấy thông tin gì. Chất lượng cả hệ phụ thuộc vào việc từng agent có đúng dữ liệu cho việc của nó hay không.

---

## 2. Năm pattern cơ bản

Đây là năm cách dựng, mỗi cách phù hợp một kiểu bài toán khác nhau. Chi tiết cơ chế ở file riêng — bảng dưới chỉ định vị.

| Pattern | Cách vận hành | File |
|---|---|---|
| **Subagents** | Một agent chính điều phối các agent con bằng cách gọi chúng như tool. Mọi định tuyến đi qua agent chính; nó quyết khi nào và gọi agent con nào. | [04-02](./04-02-subagents.md) |
| **Handoffs** | Hành vi đổi động theo trạng thái. Lệnh gọi tool cập nhật một biến trạng thái, biến đó kích hoạt định tuyến hoặc đổi cấu hình — chuyển sang agent khác hoặc chỉnh tool/prompt của agent hiện tại. | [04-03](./04-03-handoffs.md) |
| **Skills** | Prompt và kiến thức chuyên biệt được nạp khi cần. Một agent duy nhất giữ quyền điều khiển, nạp thêm ngữ cảnh từ các skill lúc cần. | [04-04](./04-04-skills.md) |
| **Router** | Một bước phân loại đầu vào rồi hướng nó tới một hoặc nhiều agent chuyên biệt. Kết quả được tổng hợp lại thành một câu trả lời. | [04-05](./04-05-router.md) |
| **Custom workflow** | Tự dựng luồng chạy riêng bằng LangGraph, trộn logic tất định với hành vi agentic. Nhúng các pattern khác vào làm chặng trong luồng của mình. | [04-06](./04-06-custom-workflow.md) |

Các pattern trộn được với nhau: một kiến trúc **subagents** có thể gọi tool là một **custom workflow** hoặc một **router**; agent con lại có thể dùng **skills** để nạp ngữ cảnh khi cần.

---

## 3. Chọn pattern theo năng lực cần có

Bốn tiêu chí để đối chiếu yêu cầu với pattern. Số sao là mức đáp ứng, theo tài liệu.

| Pattern | Phát triển phân tán | Chạy song song | Nhiều chặng (multi-hop) | Nói trực tiếp với người dùng |
|---|:---:|:---:|:---:|:---:|
| **Subagents** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ |
| **Handoffs** | – | – | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Skills** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Router** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | – | ⭐⭐⭐ |

Nghĩa của bốn tiêu chí:

- **Phát triển phân tán** — nhiều nhóm có bảo trì từng phần độc lập được không.
- **Chạy song song** — nhiều agent có chạy đồng thời được không.
- **Nhiều chặng (multi-hop)** — pattern có gọi nhiều agent con nối tiếp nhau được không.
- **Nói trực tiếp với người dùng** — agent con có trò chuyện thẳng với người dùng được không.

---

## 4. So sánh số lần gọi model qua ba tình huống

Mỗi pattern có đặc tính hiệu năng khác nhau. Hai chỉ số đo:

- **Số lần gọi model** — số lần gọi LLM. Càng nhiều lần thì độ trễ càng cao (nhất là khi gọi tuần tự) và chi phí API mỗi yêu cầu càng lớn.
- **Số token xử lý** — tổng lượng ngữ cảnh dùng qua tất cả các lần gọi. Càng nhiều token thì chi phí xử lý càng cao và càng dễ chạm giới hạn cửa sổ ngữ cảnh.

### 4.1 Yêu cầu một lần (One-shot request)

> Người dùng: "Mua cà phê"

Một agent (hoặc skill) chuyên cà phê gọi tool `buy_coffee`.

| Pattern | Số lần gọi model | Tốt nhất |
|---|:---:|:---:|
| **Subagents** | 4 | |
| **Handoffs** | 3 | ✅ |
| **Skills** | 3 | ✅ |
| **Router** | 3 | ✅ |

Handoffs, Skills và Router hiệu quả nhất cho việc đơn (3 lần gọi). Subagents thêm một lần vì kết quả phải chảy ngược về agent chính — chi phí phát sinh này đổi lấy quyền điều khiển tập trung.

Kết quả bạn có thể xem trên [one-shot-request](https://docs.langchain.com/oss/python/langchain/multi-agent#one-shot-request)

### 4.2 Yêu cầu lặp lại (Repeat request)

> Lượt 1: "Mua cà phê" → Lượt 2: "Mua cà phê nữa"

Người dùng lặp lại đúng yêu cầu trong cùng cuộc trò chuyện.

| Pattern | Lượt 2 | Tổng hai lượt | Tốt nhất |
|---|:---:|:---:|:---:|
| **Subagents** | 4 | 8 | |
| **Handoffs** | 2 | 5 | ✅ |
| **Skills** | 2 | 5 | ✅ |
| **Router** | 3 | 6 | |

Chênh lệch đến từ chỗ có giữ trạng thái hay không:

- **Subagents** không giữ trạng thái theo thiết kế — mỗi lần gọi lặp lại y nguyên luồng, nên lại 4 lần. Đổi lại là cô lập ngữ cảnh mạnh.
- **Handoffs** — agent cà phê vẫn đang hoạt động từ lượt 1 (trạng thái còn đó), khỏi handoff lại; tiết kiệm 1 lần gọi.
- **Skills** — ngữ cảnh skill đã nạp sẵn trong lịch sử, khỏi nạp lại; tiết kiệm 1 lần gọi.
- **Router** không giữ trạng thái — mỗi yêu cầu lại tốn một lần gọi LLM để phân loại.

Các pattern giữ trạng thái (Handoffs, Skills) tiết kiệm 40–50% số lần gọi khi yêu cầu lặp lại.

Kết quả bạn có thể xem trên [repeat-request](https://docs.langchain.com/oss/python/langchain/multi-agent#repeat-request)


### 4.3 Nhiều mảng cùng lúc (multi-domain)

> Người dùng: "So sánh Python, JavaScript và Rust cho web"

Mỗi agent/skill ngôn ngữ chứa ~2000 token tài liệu.

| Pattern | Số lần gọi | Tổng token | Tốt nhất |
|---|:---:|:---:|:---:|
| **Subagents** | 5 | ~9K | ✅ |
| **Handoffs** | 7+ | ~14K+ | |
| **Skills** | 3 | ~15K | |
| **Router** | 5 | ~9K | ✅ |

- **Subagents / Router** chạy song song được, mỗi agent con làm trong ngữ cảnh cô lập chỉ chứa phần liên quan → 9K token.
- **Skills** ít lần gọi nhất nhưng token cao: sau khi nạp, mọi lần gọi tiếp theo đều phải xử lý lại toàn bộ tài liệu skill đã tích tụ.
- **Handoffs** kém nhất ở đây — buộc chạy tuần tự, không tận dụng được việc gọi tool song song để hỏi nhiều mảng cùng lúc.

### 4.4 Bảng tổng hợp

| Pattern | One-shot | Repeat | Multi-domain |
|---|:---:|:---:|:---:|
| **Subagents** | 4 | 8 (4+4) | 5 lần, 9K token |
| **Handoffs** | 3 | 5 (3+2) | 7+ lần, 14K+ token |
| **Skills** | 3 | 5 (3+2) | 3 lần, 15K token |
| **Router** | 3 | 6 (3+3) | 5 lần, 9K token |

---

## 5. Nên chọn pattern nào

| Tối ưu cho | Subagents | Handoffs | Skills | Router |
|---|:---:|:---:|:---:|:---:|
| Yêu cầu đơn lẻ | | ✅ | ✅ | ✅ |
| Yêu cầu lặp lại | | ✅ | ✅ | |
| Chạy song song | ✅ | | | ✅ |
| Mảng ngữ cảnh lớn | ✅ | | | ✅ |
| Việc đơn giản, gọn phạm vi | | | ✅ | |

Diễn giải ngắn:

- Cần **song song** hoặc **mảng ngữ cảnh lớn** → Subagents hoặc Router.
- Cần **nói trực tiếp với người dùng qua nhiều bước, ép thứ tự** → Handoffs.
- Cần **một agent gọn, nhiều chuyên môn nạp khi cần** → Skills.
- Cần **luồng riêng trộn tất định với agentic** → Custom workflow (xem [04-06](./04-06-custom-workflow.md)).

> Muốn built-in đầy đủ (agent con, skill, lập kế hoạch, hệ thống file ảo, quản lý ngữ cảnh) mà không tự dựng thì tài liệu trỏ sang [**Deep Agents**](https://docs.langchain.com/oss/python/deepagents/overview) — một harness cấp cao hơn dựng trên LangChain. Deep Agents không nằm trong phạm vi mục này.

---

## Tham chiếu chéo

- [04-02 Subagents](./04-02-subagents.md) — agent chính điều phối agent con qua tool
- [04-03 Handoffs](./04-03-handoffs.md) — đổi hành vi theo biến trạng thái
- [04-04 Skills](./04-04-skills.md) — nạp prompt/kiến thức chuyên biệt khi cần
- [04-05 Router](./04-05-router.md) — phân loại rồi hướng tới agent chuyên biệt
- [04-06 Custom workflow](./04-06-custom-workflow.md) — tự dựng luồng bằng LangGraph
- Tool: [03-02](../03-agent-harness/03-02-tools.md)
- Deep Agents (ngoài phạm vi): `docs.langchain.com/oss/python/deepagents/overview`
- Context engineering: `docs.langchain.com/oss/python/langchain/context-engineering`