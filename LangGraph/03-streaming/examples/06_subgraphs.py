"""Mục 4.4 — subgraphs=True: nhận cả sự kiện bên trong subgraph, phân biệt qua chunk["ns"].

build_parent_graph_with_subgraph() (trong graph.py) bọc graph mẫu làm node
"joke_subgraph" của một graph cha, để chunk từ bên trong subgraph có ns khác rỗng.
"""

from graph import build_parent_graph_with_subgraph

graph = build_parent_graph_with_subgraph()

for chunk in graph.stream(
    {"topic": "ice cream"},
    stream_mode="updates",
    subgraphs=True,  # bật để nhận cả sự kiện từ bên trong subgraph
    version="v2",
):
    origin = "graph gốc" if chunk["ns"] == () else f"subgraph ns={chunk['ns']}"
    print(f"[{origin}] {chunk['data']}")

# ---- OUTPUT THẬT (đã chạy 2026-07-29, langgraph 1.2.10) ----
# [subgraph ns=('joke_subgraph:ed5e13eb-b15c-a377-6283-4ed6e6eb2e1f',)] {'refine_topic': {'topic': 'ice cream and cats'}}
# [subgraph ns=('joke_subgraph:ed5e13eb-b15c-a377-6283-4ed6e6eb2e1f',)] {'generate_joke': {'joke': 'Why did the ice cream truck break down? It had a rocky road.'}}
# [graph gốc] {'joke_subgraph': {'topic': 'ice cream and cats', 'joke': 'Why did the ice cream truck break down? It had a rocky road.'}}
#
# ns thật khớp mô tả doc: dạng ("tên_node:<task_id>",) — ở đây node cha tên "joke_subgraph".
# Chunk của graph gốc chỉ xuất hiện sau khi cả subgraph chạy xong (updates của node joke_subgraph).
