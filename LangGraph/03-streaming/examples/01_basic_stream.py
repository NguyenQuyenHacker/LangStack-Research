"""Mục 1 — Tổng quan: stream() cơ bản, gộp updates + custom trong version="v2".

Chứng minh: chunk luôn có dạng {"type", "ns", "data"}; custom event (do node tự
phát qua get_stream_writer) hiện ra trước dòng updates của node đó, vì node
gọi writer trước khi return.
"""

from graph import build_graph_with_progress

graph = build_graph_with_progress()  # generate_joke ở graph này có phát custom event tiến trình

for chunk in graph.stream(
    {"topic": "ice cream"},  # input khởi tạo state
    stream_mode=["updates", "custom"],  # chọn loại dữ liệu muốn nhận
    version="v2",  # bật định dạng StreamPart thống nhất (mục 2)
):
    if chunk["type"] == "updates":  # phân nhánh theo loại chunk nhận về
        for node_name, state in chunk["data"].items():
            print(f"Node {node_name} updated: {state}")
    elif chunk["type"] == "custom":
        print(f"Status: {chunk['data']['status']}")

# ---- OUTPUT THẬT (đã chạy 2026-07-29, langgraph 1.2.10) ----
# Node refine_topic updated: {'topic': 'ice cream and cats'}
# Status: thinking of a joke...
# Node generate_joke updated: {'joke': 'Why did the ice cream truck break down? It had a rocky road.'}
