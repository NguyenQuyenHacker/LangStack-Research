"""Mục 4.5 — checkpoints, tasks, debug: cần checkpointer (MemorySaver) mới dùng được.

Compile graph mẫu với MemorySaver, chạy lần lượt ba mode, in mỗi mode ra riêng.
"""

from langgraph.checkpoint.memory import MemorySaver

from graph import build_graph

checkpointer = MemorySaver()
graph = build_graph(checkpointer=checkpointer)
config = {"configurable": {"thread_id": "demo"}}

print("=== stream_mode='checkpoints' ===")
for chunk in graph.stream(
    {"topic": "ice cream"}, config, stream_mode="checkpoints", version="v2"
):
    print(chunk["data"])

print()
print("=== stream_mode='tasks' ===")
config["configurable"]["thread_id"] = "demo-tasks"  # thread mới để chạy lại từ đầu
for chunk in graph.stream({"topic": "ice cream"}, config, stream_mode="tasks", version="v2"):
    print(chunk["data"])

print()
print("=== stream_mode='debug' ===")
config["configurable"]["thread_id"] = "demo-debug"
for chunk in graph.stream({"topic": "ice cream"}, config, stream_mode="debug", version="v2"):
    print(chunk["data"])

# ---- OUTPUT THẬT (đã chạy 2026-07-29, langgraph 1.2.10) ----
# Lưu ý: checkpoint_id và timestamp đổi mỗi lần chạy (UUID theo thời gian) — chỉ phần
# cấu trúc (values/metadata/next/tasks, hoặc step/type/payload) là ổn định để đối chiếu.
#
# === stream_mode='checkpoints' ===
# {'config': {...'checkpoint_id': '<uuid>'}, 'parent_config': None, 'values': {}, 'metadata': {'source': 'input', 'step': -1, 'parents': {}}, 'next': ['__start__'], 'tasks': [{'id': '<uuid>', 'name': '__start__', 'interrupts': (), 'state': None}]}
# {'config': {...}, 'parent_config': {...}, 'values': {'topic': 'ice cream'}, 'metadata': {'source': 'loop', 'step': 0, ...}, 'next': ['refine_topic'], 'tasks': [{'name': 'refine_topic', ...}]}
# {'config': {...}, 'parent_config': {...}, 'values': {'topic': 'ice cream and cats'}, 'metadata': {'source': 'loop', 'step': 1, ...}, 'next': ['generate_joke'], 'tasks': [{'name': 'generate_joke', ...}]}
# {'config': {...}, 'parent_config': {...}, 'values': {'topic': 'ice cream and cats', 'joke': 'Why did the ice cream truck break down? It had a rocky road.'}, 'metadata': {'source': 'loop', 'step': 2, ...}, 'next': [], 'tasks': []}
#
# === stream_mode='tasks' ===
# {'id': '<uuid>', 'name': 'refine_topic', 'input': {'topic': 'ice cream'}, 'triggers': ('branch:to:refine_topic',)}
# {'id': '<uuid>', 'name': 'refine_topic', 'error': None, 'result': {'topic': 'ice cream and cats'}, 'interrupts': []}
# {'id': '<uuid>', 'name': 'generate_joke', 'input': {'topic': 'ice cream and cats'}, 'triggers': ('branch:to:generate_joke',)}
# {'id': '<uuid>', 'name': 'generate_joke', 'error': None, 'result': {'joke': 'Why did the ice cream truck break down? It had a rocky road.'}, 'interrupts': []}
#
# === stream_mode='debug' ===
# {'step': -1, 'timestamp': '<iso>', 'type': 'checkpoint', 'payload': {...}}
# {'step': 0, 'timestamp': '<iso>', 'type': 'checkpoint', 'payload': {'values': {'topic': 'ice cream'}, 'next': ['refine_topic'], ...}}
# {'step': 1, 'timestamp': '<iso>', 'type': 'task', 'payload': {'name': 'refine_topic', 'input': {'topic': 'ice cream'}, ...}}
# {'step': 1, 'timestamp': '<iso>', 'type': 'task_result', 'payload': {'name': 'refine_topic', 'result': {'topic': 'ice cream and cats'}, ...}}
# {'step': 1, 'timestamp': '<iso>', 'type': 'checkpoint', 'payload': {'values': {'topic': 'ice cream and cats'}, 'next': ['generate_joke'], ...}}
# {'step': 2, 'timestamp': '<iso>', 'type': 'task', 'payload': {'name': 'generate_joke', ...}}
# {'step': 2, 'timestamp': '<iso>', 'type': 'task_result', 'payload': {'name': 'generate_joke', 'result': {'joke': '...'}, ...}}
# {'step': 2, 'timestamp': '<iso>', 'type': 'checkpoint', 'payload': {'values': {'topic': 'ice cream and cats', 'joke': '...'}, 'next': [], ...}}
#
# Xác nhận: 'debug' đúng là gộp các sự kiện 'checkpoint' + 'task'/'task_result', thêm 'step' và 'timestamp'.
