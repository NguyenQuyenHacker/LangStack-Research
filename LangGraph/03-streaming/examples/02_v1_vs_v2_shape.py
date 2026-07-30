"""Mục 2 — Version="v2": in cạnh nhau ba trường hợp để thấy vỏ chunk đổi/không đổi.

Case A: v1, một mode -> chunk là dict thô.
Case B: v1, nhiều mode -> chunk là tuple (mode, data).
Case C: v2, nhiều mode -> chunk luôn là dict {"type", "ns", "data"}.
"""

from graph import build_graph

graph = build_graph()

print("=== Case A: v1, một mode (stream_mode='updates') ===")
for chunk in graph.stream({"topic": "ice cream"}, stream_mode="updates"):
    print(chunk)  # dict thô, không có chỗ nào ghi đây là mode 'updates'

print()
print("=== Case B: v1, nhiều mode (stream_mode=['updates', 'values']) ===")
for chunk in graph.stream({"topic": "ice cream"}, stream_mode=["updates", "values"]):
    print(chunk)  # tuple (mode, data) — cấu trúc đổi hẳn so với case A

print()
print("=== Case C: v2, nhiều mode (stream_mode=['updates', 'values'], version='v2') ===")
for chunk in graph.stream(
    {"topic": "ice cream"}, stream_mode=["updates", "values"], version="v2"
):
    print(chunk)  # luôn {"type", "ns", "data"} dù mode nào

# ---- OUTPUT THẬT (đã chạy 2026-07-29, langgraph 1.2.10) ----
# === Case A: v1, một mode (stream_mode='updates') ===
# {'refine_topic': {'topic': 'ice cream and cats'}}
# {'generate_joke': {'joke': 'Why did the ice cream truck break down? It had a rocky road.'}}
#
# === Case B: v1, nhiều mode (stream_mode=['updates', 'values']) ===
# ('values', {'topic': 'ice cream'})
# ('updates', {'refine_topic': {'topic': 'ice cream and cats'}})
# ('values', {'topic': 'ice cream and cats'})
# ('updates', {'generate_joke': {'joke': 'Why did the ice cream truck break down? It had a rocky road.'}})
# ('values', {'topic': 'ice cream and cats', 'joke': 'Why did the ice cream truck break down? It had a rocky road.'})
#
# === Case C: v2, nhiều mode (stream_mode=['updates', 'values'], version='v2') ===
# {'type': 'values', 'ns': (), 'data': {'topic': 'ice cream'}, 'interrupts': ()}
# {'type': 'updates', 'ns': (), 'data': {'refine_topic': {'topic': 'ice cream and cats'}}}
# {'type': 'values', 'ns': (), 'data': {'topic': 'ice cream and cats'}, 'interrupts': ()}
# {'type': 'updates', 'ns': (), 'data': {'generate_joke': {'joke': 'Why did the ice cream truck break down? It had a rocky road.'}}}
# {'type': 'values', 'ns': (), 'data': {'topic': 'ice cream and cats', 'joke': '...'}, 'interrupts': ()}
#
# LỆCH SO VỚI DOC: chunk type='values' thực tế có thêm khóa 'interrupts' (tuple rỗng ở đây),
# ngoài ba khóa type/ns/data mà trang gốc mô tả. Chunk type='updates' thì không có khóa này.
# Doc không nhắc chi tiết này — cần đối chiếu thêm khi triển khai dựa vào interrupt trên chunk values.
