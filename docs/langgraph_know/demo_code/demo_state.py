from typing import TypedDict,Literal,List,Dict
from langgraph.graph import StateGraph, END


# 定义个state
class State(TypedDict):
    input: str
    output: str
    suggested_tasks: List[Dict]


def node_chat(state: State) -> dict:
    return {"output": f"你说的是：{state['input']}"}


def node_tasks(state: State) -> dict:
    return {"output": f"我会先给你情绪支持，再给任务建议。"}


def route(state: State) -> Literal["chat", "tasks"]:
    return "chat"



# 构建一个状态图
builder  = StateGraph(State)
builder.add_node("chat", node_chat)
builder.add_node("tasks", node_tasks)
builder.set_entry_point("chat")
builder.add_conditional_edges("chat", route, {
    "chat": "chat",
    "tasks": "tasks",
})
builder.add_edge("tasks", END)
builder.add_edge("chat", END)

graph = builder.compile()

result = graph.invoke({"input": "你好", "output": "", "suggested_tasks": []})
print(result)
