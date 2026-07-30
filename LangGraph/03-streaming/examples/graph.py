"""Graph mẫu dùng chung cho mọi ví dụ streaming: refine_topic -> generate_joke.

- refine_topic: thêm " and cats" vào topic (minh họa updates thay đổi state).
- generate_joke: gọi LLM sinh joke từ topic, lưu vào state["joke"].

get_model() là factory chọn model: có GOOGLE_API_KEY thì dùng Gemini thật,
không có thì dùng GenericFakeChatModel để mọi ví dụ chạy offline không cần key.
"""

import itertools
import os

from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import HumanMessage
from langgraph.config import get_stream_writer
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict

# vài câu joke mẫu để fake model trả lời khi không có API key
JOKES = [
    "Why did the ice cream truck break down? It had a rocky road.",
    "What do you call a cat that loves ice cream? A sundae sundae.",
    "Why don't cats ever agree on ice cream flavors? Too many purr-spectives.",
]


class State(TypedDict):
    topic: str
    joke: str


def get_model(tags=None):
    """Trả ChatGoogleGenerativeAI nếu có GOOGLE_API_KEY, ngược lại trả fake model offline."""
    if os.environ.get("GOOGLE_API_KEY"):
        from langchain_google_genai import ChatGoogleGenerativeAI  # import trễ, chỉ cần khi có key

        return ChatGoogleGenerativeAI(model="gemini-2.0-flash", tags=tags or [])
    # itertools.cycle để iterator không cạn khi một script gọi model nhiều lần
    return GenericFakeChatModel(messages=itertools.cycle(JOKES), tags=tags or [])


def refine_topic(state: State):
    return {"topic": state["topic"] + " and cats"}  # updates sẽ nhả đúng key này


def generate_joke(state: State):
    model = get_model(tags=["joke"])  # tag "joke" dùng để lọc token ở mục 4.2
    response = model.invoke([HumanMessage(content=f"Write a short joke about {state['topic']}")])
    return {"joke": response.content}


def build_graph(checkpointer=None):
    """Graph hai node dùng chung cho hầu hết ví dụ (values/updates/messages/subgraph)."""
    builder = StateGraph(State)
    builder.add_node("refine_topic", refine_topic)
    builder.add_node("generate_joke", generate_joke)
    builder.add_edge(START, "refine_topic")
    builder.add_edge("refine_topic", "generate_joke")
    builder.add_edge("generate_joke", END)
    return builder.compile(checkpointer=checkpointer)


def generate_joke_with_progress(state: State):
    """Biến thể generate_joke có phát custom event tiến trình — dùng cho mục 4.3."""
    writer = get_stream_writer()  # lấy hàm ghi custom event của lần chạy hiện tại
    writer({"status": "thinking of a joke..."})  # đẩy dict tiến trình, nhận qua stream_mode="custom"
    model = get_model(tags=["joke"])
    response = model.invoke([HumanMessage(content=f"Write a short joke about {state['topic']}")])
    return {"joke": response.content}


def build_graph_with_progress(checkpointer=None):
    """Cùng graph mẫu nhưng generate_joke phát thêm custom event — dùng cho mục 4.1 và 4.3."""
    builder = StateGraph(State)
    builder.add_node("refine_topic", refine_topic)
    builder.add_node("generate_joke", generate_joke_with_progress)
    builder.add_edge(START, "refine_topic")
    builder.add_edge("refine_topic", "generate_joke")
    builder.add_edge("generate_joke", END)
    return builder.compile(checkpointer=checkpointer)


def build_parent_graph_with_subgraph():
    """Graph cha bọc graph mẫu làm một node con — dùng cho mục 4.4 để trường `ns` có giá trị."""
    subgraph = build_graph()  # graph compiled dùng thẳng làm node của graph cha

    parent_builder = StateGraph(State)
    parent_builder.add_node("joke_subgraph", subgraph)
    parent_builder.add_edge(START, "joke_subgraph")
    parent_builder.add_edge("joke_subgraph", END)
    return parent_builder.compile()
