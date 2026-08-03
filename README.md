# LangStack-Research

Ba stack nghiên cứu song song về hệ sinh thái LangChain, viết bằng tiếng Việt cho kỹ sư đã biết Python và đã dùng LangChain ở mức cơ bản.

## Ba stack

| Stack | Trọng tâm | Trạng thái |
|---|---|---|
| [`LangChain/`](LangChain/) | Xây agent với `create_agent` + middleware, core components, retrieval, multi-agent, production | Đang viết |
| [`LangGraph/`](LangGraph/) | State machine, checkpointer, durable execution, orchestration bậc thấp | Chưa bắt đầu |
| [`Langfuse/`](Langfuse/) | Observability: dashboard, dataset, scoring, tracing | Đang viết |

## Thứ tự đọc đề xuất

1. **LangChain** trước — nắm mô hình agent và các thành phần cốt lõi.
2. **LangGraph** sau — hiểu lớp orchestration bên dưới mà LangChain gọi tới.
3. **Langfuse** cuối — gắn quan sát và đánh giá vào hệ đã dựng.

## Đọc dạng website (VitePress)

Bản online: **https://nguyenquyenhacker.github.io/LangStack-Research/** — mỗi lần push lên `main`, GitHub Actions tự build và deploy lại ([.github/workflows/deploy.yml](.github/workflows/deploy.yml)).

Chạy tại máy: toàn bộ file `.md` giữ nguyên vị trí, VitePress lấy chính repo làm nguồn.

```bash
npm install        # chỉ chạy lần đầu
npm run docs:dev   # http://localhost:5173
```

- `npm run docs:build` — build tĩnh ra `.vitepress/dist/`
- `npm run docs:preview` — xem thử bản build

Sidebar sinh tự động từ cây thư mục và `title` trong frontmatter — thêm file note mới là nó tự xuất hiện, không phải sửa config. Cấu hình ở [`.vitepress/config.mts`](.vitepress/config.mts), bộ sinh sidebar ở [`.vitepress/sidebar.mts`](.vitepress/sidebar.mts), style ở [`.vitepress/theme/custom.css`](.vitepress/theme/custom.css).

## Ranh giới giữa ba stack

Mỗi khái niệm chỉ có một stack là nguồn chính. Cơ chế state machine, checkpointer, durable execution thuộc `LangGraph/`. Dashboard, dataset, scoring thuộc `Langfuse/`. `LangChain/` chỉ mô tả tới mức API và link sang khi chạm ranh giới.
