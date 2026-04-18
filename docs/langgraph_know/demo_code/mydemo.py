from typing import TypedDict
from langgraph.graph import StateGraph, END

/** 
 * 状态（State）是一个 TypedDict，它定义了两个字段：user_message 和 response_text。
 * 节点（node_reply）是一个函数，它接收一个状态（State）作为输入，并返回一个状态（State）作为输出。
 * 状态（State）是 LangGraph 的核心概念，它是一个字典，它定义了图的输入和输出。
 * 节点（node_reply）是 LangGraph 的核心概念，它是一个函数，它接收一个状态（State）作为输入，并返回一个状态（State）作为输出。
 * 状态（State）是 LangGraph 的核心概念，它是一个字典，它定义了图的输入和输出。
 */


class State(TypedDict):
    user_message: str
    response_text: str

def node_reply(state: State) -> dict:
    return {"response_text": f"你说的是：{state['user_message']}"}

builder = StateGraph(State)
builder.add_node("reply", node_reply)
builder.set_entry_point("reply")
builder.add_edge("reply", END)