# LangGraph 学习路线（入门到可落地）

适用场景：你对 LangGraph 一无所知，但希望能在现有 FastAPI 项目中把 `"/api/chat"` 接上“状态化、多步骤”的 Agent。

---

## 学习路线（建议 1-3 天）
1. 概念扫盲（半天）
   - 理解：LangGraph 的核心是“图（graph）+ 状态（state）”，它管理多步骤推理，而不是写一条长链。
2. 最小可运行图（半天）
   - 学会：`State`、`StateGraph`、节点（node）、边（edge）、`compile()`、`invoke/ainvoke()`。
3. 条件分支（1 天）
   - 学会：`add_conditional_edges`，根据 state 决定下一步节点。
4. 引入 LLM 节点（1 天）
   - 把 LLM 调用封装成 node（先假实现，后替换成真实模型）。
5. （可选）断点续跑/持久化（0.5-1 天）
   - 学会：checkpointer + `thread_id`，支持多轮对话记忆可恢复。
6. 落到 FastAPI（半天）
   - 在你的 `app/api/chat.py` 里：`await graph.ainvoke(...)`，再把结果写回 `Conversation`。

---

## 核心学习点（最该掌握的 8 件事）
1. `State`：运行时承载数据的结构（通常用 `TypedDict` 或 dataclass）。
2. `Node`：图里的“步骤函数”（输入 state，输出 state 的更新）。
3. `Edge`：节点之间的连线（线性流程）。
4. 条件边（Conditional edges）：根据 state 路由到不同分支。
5. `compile()`：把声明的图“编译”为可执行对象。
6. `invoke/ainvoke()`：同步/异步执行图。
7. `thread_id / checkpointer`（可选）：多轮对话可恢复。
8. `stream`（可选）：流式输出，适合前端边生成边展示。

官方文档建议收藏：
- https://langchain-ai.github.io/langgraph/

---

## 安装（先跑 demo 用）
```bash
pip install langgraph
```

如果你之后要接 LLM（例如 OpenAI 兼容接口、Qwen 等），还需要额外的 LLM wrapper 包或自定义 HTTP 封装（后续再按你的实际模型方式补）。

---

## Demo 1：Hello World（线性两步）
目标：先理解“图怎么跑起来”，不依赖真实 LLM。

文件名建议：`demo1_linear.py`
```python
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
```

---

## Demo 2：条件分支（根据输入决定走哪个节点）
目标：学会 `add_conditional_edges`。

文件名建议：`demo2_conditional.py`
```python
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
    return "chat"


builder = StateGraph(State)
builder.add_node("chat", node_chat)
builder.add_node("tasks", node_tasks)
builder.set_entry_point("chat")

builder.add_conditional_edges(
    "chat",
    route,
    {
        "chat": "chat",
        "tasks": "tasks",
    },
)

# 为两个分支都设置终点
builder.add_edge("tasks", END)
builder.add_edge("chat", END)

graph = builder.compile()

print(graph.invoke({"user_message": "我想要任务建议", "response_text": "", "suggested_tasks": []}))
print(graph.invoke({"user_message": "我最近有点难过，但不需要任务", "response_text": "", "suggested_tasks": []}))
```

你会学到：`add_conditional_edges` 像“路由逻辑”一样工作。

---

## Demo 3：聊天 Agent 骨架（替换成真实 LLM 即可）
目标：模拟未来你在 `/api/chat` 做的事：输入 -> 生成回复 -> 可选生成结构化任务。

文件名建议：`demo3_agent_skeleton.py`
```python
from typing import TypedDict, Optional, List, Dict
from langgraph.graph import StateGraph, END


class State(TypedDict):
    openid: str
    user_message: str
    response_text: str
    suggested_tasks: Optional[List[Dict]]


def node_generate(state: State) -> dict:
    # 这里先用假逻辑：后续换成真实模型调用
    msg = state["user_message"]
    response_text = f"陪你一起：收到 '{msg}'。"
    suggested_tasks = None
    if "任务" in msg:
        suggested_tasks = [{"name": "写下3个感受", "category": "自我关怀"}]
    return {"response_text": response_text, "suggested_tasks": suggested_tasks}


builder = StateGraph(State)
builder.add_node("generate", node_generate)
builder.set_entry_point("generate")
builder.add_edge("generate", END)

graph = builder.compile()

out = graph.invoke({
    "openid": "user123",
    "user_message": "我今天有点焦虑，能给我任务吗？",
    "response_text": "",
    "suggested_tasks": None,
})

print(out["response_text"])
print(out["suggested_tasks"])
```

---

## 把 Demo 变成你项目里的 `/api/chat`（落地提示）
当你开始写真实接入时，通常按下面顺序改造：
1. 新建一个 graph 文件（例如：`app/agent/chat_graph.py`）
2. 图的 state 里放你需要的字段：`openid`、`message`、`response_text`、`suggested_tasks` 等
3. 在 FastAPI 的 `chat_with_agent()` 里：
   - 从数据库读取最近聊天历史（可选）
   - `await graph.ainvoke(input_state)`
   - 把 `Conversation` 写回数据库

---

## 下一步我需要你确认（用于把 demo 接到真实模型）
你打算用哪种方式调用 Qwen/大模型？
1. `AI_API_BASE` 是 OpenAI 兼容接口（base_url + api_key + model），可用现成 wrapper
2. 需要走 Qwen 专用 SDK/自定义 HTTP（我就写一个最小 LLM node 封装）

你回复 `1` 或 `2` 后，我就可以按你的选择给你：
- LangGraph 图的 state 定义
- LLM node 的实现方式
- 接入你当前 `app/api/chat.py` 的具体改动

