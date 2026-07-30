"""Mục 4.1 — so sánh values vs updates trên cùng graph.

updates: chỉ phần state node vừa ghi, kèm tên node.
values: toàn bộ state (ảnh chụp đầy đủ) sau mỗi bước.
"""

from graph import build_graph

graph = build_graph()

print("=== stream_mode='updates' ===")
for chunk in graph.stream({"topic": "ice cream"}, stream_mode="updates", version="v2"):
    for node_name, state in chunk["data"].items():
        print(f"Node `{node_name}` updated: {state}")  # chỉ key vừa đổi

print()
print("=== stream_mode='values' ===")
for chunk in graph.stream({"topic": "ice cream"}, stream_mode="values", version="v2"):
    print(f"State hiện tại: {chunk['data']}")  # toàn bộ state, lớn dần qua từng bước

# ---- OUTPUT THẬT (đã chạy 2026-07-29, langgraph 1.2.10) ----
# === stream_mode='updates' ===
# Node `refine_topic` updated: {'topic': 'ice cream and cats'}
# Node `generate_joke` updated: {'joke': 'Why did the ice cream truck break down? It had a rocky road.'}
#
# === stream_mode='values' ===
# State hiện tại: {'topic': 'ice cream'}
# State hiện tại: {'topic': 'ice cream and cats'}
# State hiện tại: {'topic': 'ice cream and cats', 'joke': 'Why did the ice cream truck break down? It had a rocky road.'}
