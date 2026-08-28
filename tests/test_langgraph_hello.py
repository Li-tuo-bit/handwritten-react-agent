"""LangGraph 最小示例：理解 State 流转"""

from typing import TypedDict
from langgraph.graph import StateGraph

# ========== 1. 定义 State ==========
class AgentState(TypedDict):
    count: int
    message: str

# ========== 2. 定义节点 ==========
def node_a(state: AgentState) -> AgentState:
    """第一个节点：给count +1. 追加消息"""
    print(f"📍 进入 Node A | 当前 State: {state}")
    return{
        "count": state["count"] + 1,
        "message": state["message"] + " → A",
    }

def node_b(state: AgentState) -> AgentState:
    """第二个节点：再给count +1. 追加消息"""
    print(f"📍 进入 Node B | 当前 State: {state}")
    return{
        "count": state["count"] + 1,
        "message": state["message"] + " → B",
    }

def should_continue(state: AgentState) -> str:
    """条件判断 ： count < 3 就继续循环"""
    if state["count"] < 3:
        print(f"🔁 count={state['count']}，继续循环")
        return "continue"
    else:
        print(f"✅ count={state['count']}，结束")
        return "end"

# ========== 3. 构建图 ==========
builder = StateGraph(AgentState)

builder.add_node("node_a", node_a)
builder.add_node("node_b", node_b)

builder.set_entry_point("node_a")
builder.add_edge("node_a", "node_b")

# 条件边：node_b 之后，根据 should_continue 决定去向
builder.add_conditional_edges(
    "node_b",
    should_continue,
    {
        "continue": "node_a", # 回去继续
        "end": "__end__",  # ✅ 直接用字符串，不用 import END
    },
)

graph = builder.compile()

# ========== 4. 运行 ==========
if __name__ == "__main__":
    print("🚀 启动最小 LangGraph 示例\n")

    initial_state = {
        "count": 0, 
        "message": "Start",
    }

    final_state = graph.invoke(initial_state)

    print(f"\n📊  最终 State: {final_state}")