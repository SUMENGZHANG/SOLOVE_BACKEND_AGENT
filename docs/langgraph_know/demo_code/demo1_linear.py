from typing import TypedDict
from langgraph.graph import StateGraph, END


class State(TypedDict):
    user_message: str
    response_text: str


def node_reply(state: State) -> dict:
    # 假 LLM：用字符串拼接代替
    return {"response_text": f"你说的是：{state['user_message']}"}


builder = StateGraph(State)
builder.add_node("reply", node_reply)
builder.set_entry_point("reply")
builder.add_edge("reply", END)

graph = builder.compile()

result = graph.invoke({"user_message": "你好！"})
print(result["response_text"])