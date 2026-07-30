"""Mục 4.2 — lấy token LLM qua stream_mode="messages", và ba cách lọc token.

Graph ba node gọi LLM: generate_joke (tag "joke"), generate_title (tag "title"),
internal_summary (tag "nostream" — chạy nhưng không lộ token ra ngoài).
"""

from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict

from graph import get_model


class State(TypedDict):
    topic: str
    joke: str
    title: str


def generate_joke(state: State):
    model = get_model(tags=["joke"])  # tag "joke" để lọc theo lần gọi
    resp = model.invoke([HumanMessage(content=f"Write a short joke about {state['topic']}")])
    return {"joke": resp.content}


def generate_title(state: State):
    model = get_model(tags=["title"])  # node khác, tag khác, để lọc theo node/tag
    resp = model.invoke([HumanMessage(content=f"Write a title for a joke about {state['topic']}")])
    return {"title": resp.content}


def internal_summary(state: State):
    model = get_model(tags=["nostream"])  # tag đặc biệt: model chạy nhưng không lộ token qua messages
    model.invoke([HumanMessage(content=f"Summarize internally: {state['joke']}")])
    return {}


def build_multi_llm_graph():
    builder = StateGraph(State)
    builder.add_node("generate_joke", generate_joke)
    builder.add_node("generate_title", generate_title)
    builder.add_node("internal_summary", internal_summary)
    builder.add_edge(START, "generate_joke")
    builder.add_edge("generate_joke", "generate_title")
    builder.add_edge("generate_title", "internal_summary")
    builder.add_edge("internal_summary", END)
    return builder.compile()


def stream_all_tokens():
    """In mọi token, không lọc gì — thấy token của joke, title, nhưng KHÔNG có nostream."""
    graph = build_multi_llm_graph()
    tokens = []
    for chunk in graph.stream({"topic": "ice cream"}, stream_mode="messages", version="v2"):
        message_chunk, metadata = chunk["data"]
        tokens.append(message_chunk.content)
    print("Tất cả token (không lọc):", "|".join(t for t in tokens if t))


def stream_filtered_by_tag(tag: str):
    """Chỉ giữ token có tag chỉ định trong metadata."""
    graph = build_multi_llm_graph()
    tokens = []
    for chunk in graph.stream({"topic": "ice cream"}, stream_mode="messages", version="v2"):
        message_chunk, metadata = chunk["data"]
        if tag in metadata.get("tags", []):
            tokens.append(message_chunk.content)
    print(f"Token lọc theo tag='{tag}':", "|".join(t for t in tokens if t))


def stream_filtered_by_node(node_name: str):
    """Chỉ giữ token có metadata['langgraph_node'] bằng node chỉ định."""
    graph = build_multi_llm_graph()
    tokens = []
    for chunk in graph.stream({"topic": "ice cream"}, stream_mode="messages", version="v2"):
        message_chunk, metadata = chunk["data"]
        if metadata.get("langgraph_node") == node_name:
            tokens.append(message_chunk.content)
    print(f"Token lọc theo node='{node_name}':", "|".join(t for t in tokens if t))


if __name__ == "__main__":
    stream_all_tokens()
    stream_filtered_by_tag("joke")
    stream_filtered_by_node("generate_title")

# ---- OUTPUT THẬT (đã chạy 2026-07-29, langgraph 1.2.10) ----
# Tất cả token (không lọc): Why| |did| |the| |ice| |cream| |truck| |break| |down?| |It| |had| |a| |rocky| |road.|Why| |did| |the| |ice| |cream| |truck| |break| |down?| |It| |had| |a| |rocky| |road.
# Token lọc theo tag='joke': Why| |did| |the| |ice| |cream| |truck| |break| |down?| |It| |had| |a| |rocky| |road.
# Token lọc theo node='generate_title': Why| |did| |the| |ice| |cream| |truck| |break| |down?| |It| |had| |a| |rocky| |road.
#
# Ghi chú: "Tất cả token (không lọc)" chỉ có 2 câu joke (từ generate_joke và generate_title),
# không có câu thứ 3 từ internal_summary — xác nhận tag "nostream" thật sự loại token khỏi
# stream_mode="messages" như doc mô tả (grep thấy TAG_NOSTREAM = "nostream" trong langgraph/constants.py).
# Vì dùng chung fake model lặp cùng danh sách JOKES, hai node joke/title trả cùng nội dung —
# không ảnh hưởng tới việc minh họa cơ chế lọc theo tag/node.
