---
title: Integrations — Overview
doc_source:
  - https://langfuse.com/integrations
accessed: 2026-08-03
version: unknown
status: draft
related:
  - ./01-05-00-index.md
---

# Integrations

Integrations là danh mục mọi cách để một nguồn bên ngoài nối vào Langfuse và gửi trace lên, xếp theo bản chất của nguồn gửi.

## Tổng quan

Langfuse dựng trên OpenTelemetry và bản thân nó là điểm nhận, không tự sinh ra trace — mọi trace đều do một nguồn bên ngoài log lên, qua Python SDK, JS/TS SDK, hoặc gửi thẳng vào OpenTelemetry endpoint từ bất kỳ ngôn ngữ nào. Integrations phân các nguồn đó thành tám nhóm: **Native** (đường vào gốc do Langfuse cung cấp), **Frameworks** (framework điều phối agent/LLM), **Model Providers** (SDK model gọi thẳng), **Gateways** (lớp proxy/gateway trước provider), **No-Code** (nền tảng dựng agent không viết code), **Analytics** (chiều ngược — công cụ đọc lại dữ liệu Langfuse để trực quan hóa), **Developer Tools** (trợ lý code, editor, CLI), và **Other** (phần còn lại).

## 1. Native

Đây là các đường vào do chính Langfuse cung cấp, không qua thư viện bên thứ ba: hai SDK chính thức cho Python và JS/TS, REST API gọi trực tiếp, một CLI, một MCP Server, và OpenTelemetry endpoint nhận trace từ bất kỳ ngôn ngữ nào. Đây là phần ta chọn khi tự viết instrument mà không dựa vào một framework hay provider đã có integration sẵn — hoặc khi stack chạy ở ngôn ngữ chưa được nhóm nào phủ, lúc đó gửi thẳng qua OTel endpoint là con đường còn lại. Tiêu biểu: Python SDK, JS/TS SDK, OpenTelemetry, MCP Server, API.

Chi tiết: https://langfuse.com/integrations#native

## 2. Frameworks

Nhóm này gom instrument cho các framework điều phối agent/LLM — nơi luồng gọi model, gọi tool và các bước trung gian đều do framework quản; integration bắt vào lớp framework để trace tự sinh khi ứng dụng chạy. Ta dùng nhóm này khi xây ứng dụng trên một framework có sẵn thay vì gọi model trần, và chọn nó thay cho Model Providers khi phần điều phối nằm ở framework chứ không ở từng lời gọi provider đơn lẻ. Tiêu biểu: LangChain & LangGraph, LlamaIndex, CrewAI, Vercel AI SDK, Pydantic AI.

Chi tiết: https://langfuse.com/integrations#frameworks

## 3. Model Providers

Nhóm này bọc SDK của nhà cung cấp model để bắt từng lời gọi model trực tiếp, không đi qua một lớp framework điều phối. Đây là phần hỗ trợ ta khi ứng dụng gọi thẳng SDK của một provider: chọn nó thay cho Frameworks khi không có lớp orchestration ở giữa, và thay cho Gateways khi lời gọi đi thẳng tới provider chứ không qua một proxy. Tiêu biểu: OpenAI, Anthropic, Google Gemini, Amazon Bedrock, Ollama.

Chi tiết: https://langfuse.com/integrations#model-providers

## 4. Gateways

Nhóm này đặt điểm bắt trace ở lớp gateway/proxy — chỗ định tuyến lời gọi tới nhiều provider phía sau một endpoint chung. Ta dùng nó khi lưu lượng model đã đi qua một gateway rồi mới tới provider: bật integration ở tầng gateway thì mọi lời gọi qua đó vào trace mà không phải chạm vào SDK của từng provider riêng. Tiêu biểu: LiteLLM Proxy, OpenRouter, Portkey, Helicone, Kong Gateway.

Chi tiết: https://langfuse.com/integrations#gateways

## 5. No-Code

Nhóm này gom các nền tảng dựng agent và workflow bằng giao diện, không viết code ứng dụng — nên việc bật Langfuse nằm trong cấu hình của chính nền tảng chứ không phải trong codebase. Đây là phần hỗ trợ ta khi agent được dựng bên trong một công cụ no-code, không có mã nguồn để gắn SDK. Tiêu biểu: Dify, Flowise, Langflow, n8n, OpenWebUI.

Chi tiết: https://langfuse.com/integrations#no-code

## 6. Analytics

Nhóm này đi ngược chiều so với bảy nhóm còn lại: không phải nguồn gửi trace lên Langfuse, mà là công cụ đọc lại trace và metric đã có trong Langfuse để trực quan hóa. Ta dùng nó khi muốn xem dữ liệu Langfuse trong một công cụ phân tích quen thuộc thay vì chỉ trong giao diện Langfuse. Tiêu biểu: PostHog, Mixpanel, Coval, Trubrics.

Chi tiết: https://langfuse.com/integrations#analytics

## 7. Developer Tools

Nhóm này phục vụ hai hướng dùng — trace các trợ lý code AI, editor và CLI; hoặc dùng Langfuse ngay từ trong editor. Ta dùng nó khi đối tượng cần quan sát là bản thân công cụ lập trình AI (prompt, phản hồi, phiên làm việc của trợ lý), không phải một ứng dụng ta tự viết. Tiêu biểu: Cursor, Claude Code, GitHub Copilot, VS Code, Codex.

Chi tiết: https://langfuse.com/integrations#developer-tools

## 8. Other

Nhóm này gom các integration không rơi vào bảy nhóm trên — nhiều loại công cụ khác nhau đứng cạnh một agent hay ứng dụng: cơ sở dữ liệu vector, công cụ tìm kiếm và crawl, giao diện demo, nền tảng tự động hóa, công cụ eval, kênh thông báo. Ta tra ở đây khi công cụ cần nối không thuộc loại SDK model, framework, gateway hay nền tảng no-code — trước khi kết luận Langfuse chưa hỗ trợ. Tiêu biểu: Milvus, Firecrawl, Exa, Zapier, Promptfoo, LibreChat.

Chi tiết: https://langfuse.com/integrations#other

## Ghi chú nguồn

Sidebar của trang liệt kê thêm một nhóm **Data Platform**, nhưng trang overview vừa đọc không có section tương ứng — nội dung của nó không nằm trong phạm vi trang này. Cần đối chiếu URL riêng trước khi bổ sung, không viết dựa trên phỏng đoán.

## Tham chiếu chéo

Nhóm Native chồng lấn trực tiếp với phần SDK và OpenTelemetry của bộ note: cách log trace cụ thể giảng ở đó, note này chỉ định vị Native trong toàn cảnh Integrations. Trỏ sang [`./01-05-00-index.md`](./01-05-00-index.md), và tới file SDK/OpenTelemetry riêng nếu bộ note đã tách file đó (chưa xác nhận có trong bộ hiện tại).