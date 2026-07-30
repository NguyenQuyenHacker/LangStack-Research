"""Mục 6 — tắt streaming cho model cụ thể; invoke() ở version="v2" trả GraphOutput.

Phần 1: model khởi tạo disable_streaming=True vẫn invoke được, nhưng không sinh
token qua stream_mode="messages" — kiểm bằng cách so với model bình thường.
Phần 2: graph.invoke(inputs, version="v2") trả GraphOutput có .value và .interrupts,
thay vì dict thô như v1.
"""

import itertools

from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict

from graph import JOKES, build_graph


class State(TypedDict):
    topic: str
    joke: str


def generate_joke_no_stream(state: State):
    # disable_streaming=True: model vẫn invoke được, nhưng không lộ token qua stream_mode="messages"
    model = GenericFakeChatModel(messages=itertools.cycle(JOKES), disable_streaming=True)
    resp = model.invoke([HumanMessage(content=f"Write a short joke about {state['topic']}")])
    return {"joke": resp.content}


def build_no_stream_graph():
    builder = StateGraph(State)
    builder.add_node("generate_joke", generate_joke_no_stream)
    builder.add_edge(START, "generate_joke")
    builder.add_edge("generate_joke", END)
    return builder.compile()


def demo_disable_streaming():
    no_stream_graph = build_no_stream_graph()
    normal_graph = build_graph()
    no_stream_tokens = list(
        no_stream_graph.stream({"topic": "ice cream"}, stream_mode="messages", version="v2")
    )
    normal_tokens = list(
        normal_graph.stream({"topic": "ice cream"}, stream_mode="messages", version="v2")
    )
    # disable_streaming=True: model rơi về invoke() nội bộ, nhả đúng 1 chunk (cả câu),
    # trong khi model bình thường nhả nhiều chunk (từng từ) — không phải "không có token nào",
    # mà là "không còn nhả theo từng phần nhỏ" như doc mô tả.
    print(f"Số chunk từ model disable_streaming=True: {len(no_stream_tokens)}")
    print(f"Số chunk từ model streaming bình thường: {len(normal_tokens)}")


def demo_invoke_v2():
    graph = build_graph()
    result = graph.invoke({"topic": "ice cream"}, version="v2")  # trả GraphOutput, không phải dict
    print("type(result):", type(result).__name__)
    print("result.value:", result.value)  # output thật, tương đương dict state v1
    print("result.interrupts:", result.interrupts)  # tuple rỗng vì graph không có interrupt


if __name__ == "__main__":
    demo_disable_streaming()
    print()
    demo_invoke_v2()

# ---- OUTPUT THẬT (đã chạy 2026-07-29, langgraph 1.2.10) ----
# Số chunk từ model disable_streaming=True: 1
# Số chunk từ model streaming bình thường: 25
#
# type(result): GraphOutput
# result.value: {'topic': 'ice cream and cats', 'joke': 'Why did the ice cream truck break down? It had a rocky road.'}
# result.interrupts: ()
