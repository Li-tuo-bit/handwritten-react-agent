"""LangGraph 版 ReAct Agent —— 与手写版功能完全一致"""

import os
import json
import re
from typing import TypedDict, List

from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from shared_tools import TOOL_REGISTRY, get_tool_description


# ========== 1. 定义 State ==========
class AgentState(TypedDict):
    question: str
    history: List[dict]      # {thought, action, action_input, observation}
    current_step: int
    max_steps: int
    final_answer: str
    finish: bool


# ========== 2. 初始化 LLM（DeepSeek 配置） ==========
llm = ChatOpenAI(
    model="deepseek-chat",
    temperature=0.3,
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
)


# ========== 3. 定义节点 ==========

def thought_node(state: AgentState) -> AgentState:
    """
    思考节点：调用 LLM，生成 Thought + Action
    """

    # 构建 Prompt（同手写版逻辑）
    prompt = _build_prompt(state)
    
    # 调用 LLM
    messages = [
        SystemMessage(content="你是遵循 ReAct 范式的智能助手，必须输出 JSON 格式。"),
        HumanMessage(content=prompt),
    ]
    response = llm.invoke(messages)
    
    # 解析 JSON
    try:
        parsed = json.loads(response.content)
    except json.JSONDecodeError:
        # 降级处理
        parsed = _fallback_parse(response.content)
    
    # 更新 State
    new_history = state["history"] + [{
        "thought": parsed.get("thought", ""),
        "action": parsed.get("action", ""),
        "action_input": parsed.get("action_input", ""),
        "observation": "",  # observation 节点填充
    }]
    
    return {
        **state,  # 保留原有所有字段
        "history": new_history,
        "finish": parsed.get("finish", False),
        "final_answer": parsed.get("answer", ""),
    }


def action_node(state: AgentState) -> AgentState:
    """
    行动节点：执行工具调用
    """
    last_step = state["history"][-1]
    action_name = last_step["action"]
    action_input = last_step["action_input"]
    
    if not action_name:
        # 没有行动，直接返回
        return state
    
    # 执行工具
    if action_name in TOOL_REGISTRY:
        try:
            observation = TOOL_REGISTRY[action_name](action_input)
        except Exception as e:
            observation = f"Error: {e}"
    else:
        observation = f"Error: 未知工具 '{action_name}'"
    
    # ✅ 修复：创建全新的字典，不修改原始 State
    new_history = state["history"][:-1] + [{
        **last_step,
        "observation": observation,
    }]
    
    return {
        **state,
        "history": new_history,
    }


def observation_node(state: AgentState) -> AgentState:
    """
    观察节点：打印日志，检查是否完成
    （这个节点主要是给框架一个检查点，也可以合并到 action_node）
    """
    last_step = state["history"][-1]
    print(f"\n[Step {state['current_step'] + 1}]")
    print(f"🤔 Thought: {last_step['thought'][:80]}...")
    if last_step["action"]:
        print(f"🔧 Action: {last_step['action']}[{last_step['action_input']}]")
    print(f"📊 Observation: {last_step['observation'][:80]}...")
    
    return {
        **state,
        "current_step": state["current_step"] + 1,
    }


# ========== 4. 条件判断函数 ==========

def should_continue(state: AgentState) -> str:
    """
    决定是继续循环还是结束
    返回 "continue" 或 "end"
    """
    if state["finish"]:
        print(f"\n✅ Answer: {state['final_answer']}")
        return "end"
    
    if state["current_step"] >= state["max_steps"]:
        print(f"\n⚠️ 达到最大步数限制")
        return "end"
    
    return "continue"


# ========== 5. Prompt 构建（与手写版逻辑一致）==========

def _build_prompt(state: AgentState) -> str:
    question = state["question"]
    
    prompt = f"""你是一个智能量化助手。

{get_tool_description()}

规则：
1. 输出 JSON 格式：{{"thought": "...", "action": "工具名", "action_input": "...", "finish": false}}
2. 完成时：{{"thought": "...", "action": "", "action_input": "", "finish": true, "answer": "..."}}
3. 如需多步任务，按顺序调用工具

历史记录：
"""
    # 追加历史
    for step in state["history"]:
        prompt += f"\nThought: {step['thought']}"
        if step["action"]:
            prompt += f"\nAction: {step['action']}[{step['action_input']}]"
        if step["observation"]:
            prompt += f"\nObservation: {step['observation']}"
    
    prompt += f"\n\nQuestion: {question}\n"
    return prompt


# ========== 6. 降级解析（同手写版）==========

def _fallback_parse(response: str) -> dict:
    """当 JSON 解析失败时，用正则提取信息"""
    thought = re.search(r'Thought:\s*(.+?)(?=Action:|Answer:|$)', response, re.DOTALL)
    action = re.search(r'Action:\s*(\w+)\[(.*?)\]', response)
    answer = re.search(r'Answer:\s*(.+)', response)
    
    if answer:
        return {"thought": "", "action": "", "action_input": "", "finish": True, "answer": answer.group(1)}
    elif action:
        return {"thought": thought.group(1) if thought else "", "action": action.group(1), "action_input": action.group(2), "finish": False, "answer": ""}
    else:
        return {"thought": "", "action": "", "action_input": "", "finish": False, "answer": ""}

# ========== 7. 构建图 ==========
def create_agent():
    """创建并编译 LangGraph Agent"""
    builder = StateGraph(AgentState)

    # 添加节点
    builder.add_node("thought", thought_node)
    builder.add_node("action", action_node)
    builder.add_node("observe", observation_node)

    # 设置入口点
    builder.set_entry_point("thought")
    
    # 添加边
    builder.add_edge("thought", "action")
    builder.add_edge("action", "observe")

    # 条件边：observe 之后，要么继续循环，要么结束
    builder.add_conditional_edges(
        "observe",           # 从 "observe" 节点出发
        should_continue,     # 用这个函数判断走哪条路
        {
            "continue": "thought",  # 返回 "continue" → 回 thought 继续循环
            "end": "__end__",        # 返回 "end" → 结束运行
        }
    )

    return builder.compile()

# ========== 8. 运行入口 ==========
def run_agent(question: str,max_steps: int = 100):
    """运行 LangGraph Agent"""
    graph = create_agent()

    # 初始状态
    initial_state = {
        "question": question,
        "history": [],
        "current_step": 0,
        "max_steps": max_steps,
        "final_answer": "",
        "finish": False,
    }

    print(f"🚀 LangGraph Agent 启动：{question}")
    print("="*50)

    # 运行图
    final_state = graph.invoke(initial_state)

    return final_state["final_answer"]

if __name__ == "__main__":
    # 测试 1：简单计算
    result = run_agent("计算 100 除以 4 再加 5")
    print(f"\n结果: {result}")
    
    print("\n" + "=" * 50 + "\n")
    
    # 测试 2：回测
    result2 = run_agent("回测贵州茅台(600519)2024年的双均线策略")
    print(f"\n结果: {result2}")