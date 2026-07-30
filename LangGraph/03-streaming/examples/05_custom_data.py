"""Mục 4.3 — gửi dữ liệu tự định nghĩa qua get_stream_writer(), nhận bằng stream_mode="custom".

generate_joke_with_progress (trong graph.py) gọi get_stream_writer() rồi đẩy dict
tiến trình trước khi gọi LLM — mô phỏng báo tiến trình của việc không phải LLM.
"""

from graph import build_graph_with_progress

graph = build_graph_with_progress()

for chunk in graph.stream({"topic": "ice cream"}, stream_mode="custom", version="v2"):
    print(f"Custom event: {chunk['data']}")  # chunk['data'] chính là dict truyền vào writer(...)

# ---- OUTPUT THẬT (đã chạy 2026-07-29, langgraph 1.2.10) ----
# Custom event: {'status': 'thinking of a joke...'}
