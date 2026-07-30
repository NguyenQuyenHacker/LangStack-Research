"""Mục 5 — nhiều mode cùng lúc, rẽ nhánh theo chunk["type"] (v2 luôn cùng vỏ StreamPart)."""

from graph import build_graph_with_progress

graph = build_graph_with_progress()
inputs = {"topic": "ice cream"}

for chunk in graph.stream(inputs, stream_mode=["updates", "custom"], version="v2"):
    if chunk["type"] == "updates":
        for node_name, state in chunk["data"].items():
            print(f"Node `{node_name}` updated: {state}")
    elif chunk["type"] == "custom":
        print(f"Custom event: {chunk['data']}")

# ---- OUTPUT THẬT (đã chạy 2026-07-29, langgraph 1.2.10) ----
# Node `refine_topic` updated: {'topic': 'ice cream and cats'}
# Custom event: {'status': 'thinking of a joke...'}
# Node `generate_joke` updated: {'joke': 'Why did the ice cream truck break down? It had a rocky road.'}
