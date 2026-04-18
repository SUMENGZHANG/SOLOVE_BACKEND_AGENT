from typing import TypedDict, Literal, List, Dict
from langgraph.graph import StateGraph, END


class State(TypedDict):
    user_message: str
    response_text: str
    suggested_tasks: List[Dict]


def node_chat(state: State) -> dict:
    return {"response_text": "好的，我先理解你的需求。", "suggested_tasks": []}


def node_tasks(state: State) -> dict:
    return {
        "response_text": "我会先给你情绪支持，再给任务建议。",
        "suggested_tasks": [{"name": "今日深呼吸 3 次", "category": "自我关怀"}],
    }


def route(state: State) -> Literal["tasks", "chat"]:
    text = state["user_message"]
    if "任务" in text or "建议" in text:
        return "tasks"
                return "chat"·

# 为两个分支都设置终点
builder.add_edge("tasks", END)
builder.add_edge("chat", END)

graph = builder.compile()

print(graph.invoke({"user_message": "我想要任务建议", "response_text": "", "suggested_tasks": []}))
print(graph.invoke({"user_message": "我最近有点难过，但不需要任务", "response_text": "", "suggested_tasks": []}))