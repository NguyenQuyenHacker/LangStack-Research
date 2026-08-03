---
title: Prompt Management — Features — Automation & Integrations
doc_source:
  - https://langfuse.com/docs/prompt-management/features/agentic-access
  - https://langfuse.com/docs/prompt-management/features/mcp-server
  - https://langfuse.com/docs/prompt-management/features/webhooks-slack-integrations
  - https://langfuse.com/docs/prompt-management/features/github-integration
  - https://langfuse.com/docs/prompt-management/features/n8n-node
accessed: 2026-08-03
version: v4
status: draft
related:
  - ./02-03-00-index.md
---

# Automation & Integrations

Năm tính năng cho phép tác nhân bên ngoài đọc/sửa thư viện prompt và cho phép mỗi thay đổi prompt kích hoạt hệ thống khác, thay vì chỉ fetch prompt trong ứng dụng.

## Tổng quan

Nhóm này gồm hai mạch. Mạch thứ nhất — Agent Access và MCP Server — cho AI agent làm việc trực tiếp với prompt (tạo, sửa, gán nhãn) trong lúc code, chứ không chỉ đọc. Mạch thứ hai — Webhooks, GitHub Integration, n8n Node — biến sự kiện đổi prompt thành đầu vào cho hệ thống ngoài: bắn thông báo, chạy CI/CD, đồng bộ repo, hay nạp prompt vào workflow tự động. MCP Server là một phương thức con của Agent Access; GitHub Integration xây thẳng trên Webhooks.

## 1. Agent Access

**Khái niệm.** Agent Access không phải một cơ chế đơn lẻ mà là bộ ba đường cho AI agent thao tác trên prompt library, chọn theo năng lực agent. Agent tự cài được tool và chạy shell thì dùng Langfuse Agent Skill (chạy trên Langfuse CLI). Agent không cài được tool thì nối Langfuse MCP server để phơi thao tác Langfuse thành tool. Agent chạy trong script hay CI/CD thì gọi thẳng Langfuse CLI hoặc Public API. Cả ba đều cho phép cùng một lớp thao tác: lấy prompt, tạo version text/chat mới, so version, promote bằng cách đổi deployment label.

**Vai trò.** Để agent quản lý prompt ngay trong lúc sửa code ứng dụng, thay vì người phải thao tác tay trên UI.

**Ví dụ.** Một coding agent được giao migrate các prompt hardcode trong codebase agent ngân hàng sang Langfuse: nó tạo từng version, rồi promote version đã kiểm thử bằng cách gán nhãn `production` — toàn bộ qua một trong ba đường trên, không rời editor.

Chi tiết cấu hình: https://langfuse.com/docs/prompt-management/features/agentic-access

## 2. MCP Server

**Khái niệm.** MCP Server là máy chủ Model Context Protocol dựng sẵn trong Langfuse để AI assistant/agent thao tác với Prompt Management như gọi tool. Nó nằm ngay tại endpoint `/api/public/mcp` (streamableHttp), không cần dựng hạ tầng ngoài hay bước build. Các thao tác phơi ra dưới dạng tool gồm `getPrompt` (lấy prompt), `createTextPrompt` / `createChatPrompt` (tạo version mới), `updatePromptLabels` (đổi nhãn deploy). MCP Reference là nguồn chuẩn cho danh sách tool, input schema, và ví dụ request hiện hành.

**Vai trò.** Cấp đường cho agent không chạy được shell vẫn quản lý prompt, bằng cách biến thao tác Langfuse thành tool MCP mà client AI gọi được trực tiếp.

**Ví dụ.** Một agent không có quyền cài tool nối vào MCP server rồi nhận lệnh "chuyển nhãn production từ version 2 sang version 3 của prompt customer-email"; agent gọi `updatePromptLabels` để thực hiện, không cần viết code gọi API.

Chi tiết cấu hình: https://langfuse.com/docs/prompt-management/features/mcp-server

## 3. Webhooks & Slack

**Khái niệm.** Webhooks là cơ chế Langfuse gửi thông báo thời gian thực mỗi khi một prompt version bị tạo, sửa, hay xóa — để kích hoạt CI/CD, đồng bộ danh mục prompt, hay ghi log thay đổi mà không phải poll API. Cấu hình ở `Prompts > Automations > Create Automation`, chọn sự kiện cần theo dõi, tùy chọn lọc theo prompt cụ thể. Ba loại sự kiện: **Created** khi thêm version mới; **Updated** khi label hoặc tag đổi; **Deleted** khi xóa version. Mỗi lần bắn, endpoint nhận một POST kèm header mặc định (`Content-Type: application/json`, `User-Agent: Langfuse/1.0`, `x-langfuse-signature`) và body JSON mô tả `action` cùng toàn bộ prompt object (name, version, labels, prompt, config, tags...). Chữ ký `x-langfuse-signature` là HMAC SHA-256 để xác thực nguồn; secret lấy lúc tạo webhook, tái tạo được. Ngoài webhook thô, Langfuse còn nối Slack qua OAuth để bắn thông báo thẳng vào channel chọn sẵn.

**Vai trò.** Đẩy thay đổi prompt ra ngoài theo mô hình sự kiện, để hệ thống khác phản ứng ngay thay vì phải hỏi Langfuse định kỳ.

**Ví dụ.** Đội vận hành chuyển nhãn `production` từ version 2 sang version 3 của một prompt; webhook bắn để một handler chạy bộ regression trên version mới, đồng thời đăng thông báo vào channel Slack của team.

> **!Note:** Một thao tác đổi nhãn sinh **hai** sự kiện Updated — một cho version được gán nhãn, một cho version bị mất nhãn. Handler nào mặc định "mỗi thay đổi một sự kiện" sẽ xử lý dư hoặc nhầm version nào đang là production. Thêm nữa, Langfuse retry theo exponential backoff cho tới khi nhận 2xx, nên handler không idempotent sẽ xử lý trùng cùng một sự kiện mà không báo lỗi.

Chi tiết cấu hình: https://langfuse.com/docs/prompt-management/features/webhooks-slack-integrations

## 4. GitHub Integration

**Khái niệm.** GitHub Integration là hai cách nối prompt Langfuse với GitHub, cả hai đứng trên cơ chế Webhooks. Cách một, **Repository Dispatch**: mỗi thay đổi prompt bắn một sự kiện `repository_dispatch` kích hoạt GitHub Actions workflow, không cần dựng thêm hạ tầng; cấu hình trong Langfuse với Dispatch URL `https://api.github.com/repos/{owner}/{repo}/dispatches`, Event Type khớp với workflow (ví dụ `langfuse-prompt-update`), và một GitHub token; dữ liệu prompt đọc trong workflow qua `github.event.client_payload.*`. Cách hai, **Sync to repository**: một webhook server (docs ví dụ bằng FastAPI) nghe sự kiện version rồi commit prompt vào một file trong repo — mặc định `langfuse_prompt.json` trên nhánh `main`; nếu đặt biến `REQUIRED_LABEL` thì chỉ prompt mang nhãn đó mới được đồng bộ, còn lại bị bỏ qua âm thầm.

**Vai trò.** Đưa prompt vào quy trình version control và CI/CD của repo, để prompt được kiểm thử và triển khai cùng luồng với code.

**Ví dụ.** Lưu một version prompt mới trong Langfuse; webhook server nhận sự kiện và commit `langfuse_prompt.json` vào repo với commit message mô tả action và version — prompt giờ có lịch sử git song song với ứng dụng.

Chi tiết cấu hình: https://langfuse.com/docs/prompt-management/features/github-integration

## 5. n8n Node

**Khái niệm.** n8n Node là node do cộng đồng bảo trì, cho phép fetch và dùng prompt Langfuse ngay trong workflow n8n (nền tảng tự động hóa dạng node mã nguồn mở). Cài trên n8n self-hosted qua `Settings > Community Nodes` với package `@langfuse/n8n-nodes-langfuse`; trên n8n Cloud thì tìm node "Langfuse" trực tiếp.

Chi tiết cấu hình: https://langfuse.com/docs/prompt-management/features/n8n-node

## Tham chiếu chéo

- MCP Server là một trong ba phương thức mà Agent Access liệt kê. Hai phương thức còn lại — Agent Skill + CLI, và Public API — được tài liệu ở nhánh API & Data Platform, ngoài phạm vi note này.
- GitHub Integration (nhánh Sync) và mọi tự động hóa theo sự kiện đều tiêu thụ Webhooks; sự kiện Updated tương ứng đúng thao tác đổi label/tag của Version Control — xem note Versioning & Deployment cho ngữ nghĩa nhãn.
- n8n Node fetch prompt như đường `get_prompt` của SDK, nên chịu cùng cơ chế phiên bản/cache; xem Versioning & Deployment và Runtime Reliability.
- Index nhóm feature: [./02-03-00-index.md](./02-03-00-index.md)