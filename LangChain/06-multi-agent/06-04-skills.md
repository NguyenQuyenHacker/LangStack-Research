---
title: Skills
doc_source: https://docs.langchain.com/oss/python/langchain/multi-agent/skills
accessed: 2026-07-25
lc_version: unknown
status: draft
lab:
related:
  - ./04-01-multi-agent-overview.md
  - ./04-02-subagents.md
---

# Skills (`@tool` nạp prompt chuyên biệt)

> Pattern trong đó các năng lực chuyên biệt được đóng gói thành "skill" gọi được, làm giàu hành vi cho một agent. Skill chủ yếu là chuyên biệt hóa bằng prompt, agent gọi khi cần.
> Một agent duy nhất giữ quyền điều khiển; đây là điểm khác Subagents (nhiều agent con) và Router (bước phân loại tách rời).

---

## 1. Tổng quan

Skill là chuyên biệt hóa chủ yếu bằng prompt: mỗi skill là một prompt (và ngữ cảnh) riêng cho một mảng việc, agent nạp lúc cần thay vì nạp hết từ đầu. Cơ chế lõi là một tool `load_skill` trả về nội dung prompt của skill:

```python
@tool
def load_skill(skill_name: str) -> str:                    # tool nạp một skill theo tên
    """Load a specialized skill prompt.
    Available skills:
    - write_sql: SQL query writing expert
    - review_legal_doc: Legal document reviewer
    Returns the skill's prompt and context.
    """                                                    # docstring liệt kê skill để model biết có gì mà gọi
    # Load skill content from file/database                # nội dung skill lấy từ file hoặc CSDL — nạp lúc cần
    ...

agent = create_agent(
    model="gpt-5.4",
    tools=[load_skill],                                    # agent chỉ cầm một tool nạp skill
    system_prompt=("You are a helpful assistant. "
                   "You have access to two skills: "
                   "write_sql and review_legal_doc. "
                   "Use load_skill to access them."),
)
```

**Kết quả in ra** (dựng lại):

```
[user]        "Viết câu SQL lấy 10 khách hàng chi tiêu cao nhất"
[AIMessage]   tool_calls=[load_skill(skill_name="write_sql")]   ← agent nhận ra việc là SQL, nạp skill tương ứng
[ToolMessage] "Bạn là chuyên gia SQL. Quy ước: ... Lược đồ bảng: ..."  ← prompt chuyên biệt được đưa vào ngữ cảnh
[AIMessage]   "SELECT customer_id, SUM(amount) ... LIMIT 10"    ← giờ agent trả lời với ngữ cảnh SQL đã nạp
```

**Vai trò của "hé lộ dần".** Prompt của mọi skill nếu nhồi hết từ đầu sẽ làm phình ngữ cảnh và tốn token mỗi lần gọi. Nạp khi cần (progressive disclosure — hé lộ dần) giữ cửa sổ ngữ cảnh gọn: chỉ mảng đang dùng mới có mặt.

**!Note:** Đừng nhầm "Skills" ở đây (một pattern trong LangChain) với file skill của kho research này. Cùng chữ, khác thứ.

---

## 2. Đặc điểm và khi nào dùng

**Khái niệm.** Chuyên biệt bằng prompt (skill định nghĩa chủ yếu bằng prompt). Hé lộ dần (skill khả dụng theo ngữ cảnh hoặc nhu cầu). Nhiều nhóm phát triển skill độc lập. Nhẹ hơn agent con đầy đủ. Skill có thể trỏ tới script, mẫu, tài nguyên khác.

**Vai trò.** Dùng khi muốn **một** agent có nhiều chuyên môn, không cần ép ràng buộc giữa các skill, hoặc các nhóm cần dựng năng lực độc lập.

**Áp dụng thực tế.** Trợ lý lập trình: một agent, mỗi ngôn ngữ (SQL, Python, Go) là một skill. Người dùng hỏi câu SQL → agent nạp skill `write_sql` với quy ước và lược đồ bảng; hỏi tiếp về Python → nạp skill Python. Agent không phải mang cả ba bộ quy ước cùng lúc trong ngữ cảnh.

---

## 3. Ba hướng mở rộng pattern

Để rõ hướng dẫn thực hành hãy truy cập [Skills](https://docs.langchain.com/oss/python/langchain/multi-agent/skills-sql-assistant)

Khi tự viết cài đặt riêng, có ba cách mở rộng pattern cơ bản.

### 3.1 Đăng ký tool động khi nạp skill

**Khái niệm.** Ghép hé lộ dần với quản lý trạng thái để **đăng ký thêm tool** khi skill được nạp.

**Vai trò.** Một skill không chỉ mang thêm ngữ cảnh mà còn mở ra tool riêng của mảng đó.

**Áp dụng thực tế.** Nạp skill `database_admin` vừa thêm ngữ cảnh quản trị CSDL, vừa đăng ký các tool riêng: `backup`, `restore`, `migrate`. Trước khi nạp skill, agent không thấy — do đó không lỡ tay gọi — các tool nguy hiểm này. Cơ chế vẫn là tool cập nhật trạng thái để đổi năng lực agent, giống các pattern multi-agent khác.

### 3.2 Skill phân cấp

**Khái niệm.** Skill định nghĩa skill khác theo cây, tạo chuyên biệt lồng nhau.

**Vai trò.** Quản lý kho kiến thức lớn bằng cách gom năng lực thành nhóm logic, khám phá và nạp theo nhu cầu.

**Áp dụng thực tế.** Nạp skill `data_science` mở ra các skill con `pandas_expert`, `visualization`, `statistical_analysis`. Mỗi skill con nạp độc lập khi cần — hé lộ dần ở mức mịn hơn, không kéo cả cây kiến thức vào ngữ cảnh một lúc.

### 3.3 Nhận biết tài nguyên tham chiếu

**Khái niệm.** Mỗi skill chỉ có một prompt, nhưng prompt đó trỏ được tới vị trí các tài nguyên khác (script, mẫu, file) và nêu khi nào agent nên dùng chúng.

**Vai trò.** Khi tài nguyên trở nên cần thiết, agent biết các file đó tồn tại và tự đọc vào bộ nhớ để làm việc — cũng theo lối hé lộ dần, giữ ngữ cảnh gọn.

---

## Tham chiếu chéo

- [04-01 Tổng quan](./04-01-multi-agent-overview.md) — Skills đối chiếu bốn pattern còn lại (chú ý: ít lần gọi model nhưng token cao do ngữ cảnh tích tụ)
- [04-02 Subagents](./04-02-subagents.md) — mục "tìm agent qua tool" cũng dùng hé lộ dần, cùng ý tưởng
- Tool: [03-02](../03-agent-harness/03-02-tools.md)
- Deep Agents (built-in skill): `docs.langchain.com/oss/python/deepagents/skills`
- LangChain Skills (kho skill sẵn dùng): `github.com/langchain-ai/langchain-skills`