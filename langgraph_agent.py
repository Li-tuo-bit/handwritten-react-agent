"""LangGraph 版 ReAct Agent —— 与手写版功能完全一致"""

import os
import json
import re
from typing import TypedDict, List

from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver # 内存版（开发用）
# 生产环境用：from langgraph.checkpoint.sqlite import SqliteSaver

from shared_tools import TOOL_REGISTRY, get_tool_description

from typing import Annotated
import operator

# ========== 1. 定义 State ==========
class AgentState(TypedDict):
    question: str
    history: List[dict]      # {thought, action, action_input, observation}
    current_step: int
    max_steps: int
    final_answer: str
    finish: bool
    report_summary: str 


# ========== 2. 初始化 LLM（DeepSeek 配置） ==========
llm = ChatOpenAI(
    model="deepseek-chat",
    temperature=0.3,
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
)


# ========== 3. 定义节点 ==========
def decision_node(state: AgentState) -> AgentState:
    """
    决策节点：根据用户问题判断是否需要查研报
    """
    question = state["question"]

    # 简单关键词判断
    industry_keywords = ["新能源","白酒","半导体","消费","医药","行业","板块"]
    need_report = any(kw in question for kw in industry_keywords)

    if need_report:
        print("🔍 决策节点：检测到行业关键词，查询研报...")
        from rag_tool import query_research_report
        report_summary = query_research_report(question)

        return {
            **state,
            "report_summary": report_summary,
        }

    return state

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
    new_history = state["history"].copy()
    new_history[-1]["observation"] = observation
    
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
    # ✅ 修复：如果已经 finish，直接结束
    if state["finish"]:
        print(f"\n✅ Answer: {state['final_answer']}")
        return "end"
    
    # ✅ 修复：防循环检测——最近 3 步都是同一个 action，强制结束
    history = state["history"]
    if len(history) >= 3:
        last_3_actions = [h["action"] for h in history[-3:]]
        last_3_obs = [h["observation"] for h in history[-3:]]
        # 如果最近 3 步调了同一个工具，且结果都一样，说明卡住了
        if len(set(last_3_actions)) == 1 and last_3_actions[0] != "":
            if len(set(last_3_obs)) == 1:
                print(f"\n⚠️ 检测到循环，强制结束")
                # 把最后一条 observation 当作答案
                return "end"
    
    # ✅ 原有逻辑：达到最大步数结束
    if state["current_step"] >= state["max_steps"]:
        print(f"\n⚠️ 达到最大步数限制")
        return "end"
    
    return "continue"


# ========== 5. Prompt 构建（与手写版逻辑一致）==========

def _build_prompt(state: AgentState) -> str:
    question = state["question"]
    
    prompt = f"""你是一个智能量化助手，擅长数据分析、行业研究和策略回测。

{get_tool_description()}

【重要规则】
1. 输出 JSON 格式：{{"thought": "...", "action": "工具名", "action_input": "...", "finish": false}}
2. 完成时：{{"thought": "...", "action": "", "action_input": "", "finish": true, "answer": "..."}}
3. 如果需要多步任务，按顺序调用Agent节点，每个节点完成一个任务
4. ⚠️ 重要：如果上一步已经得到了 Observation 且问题已解决，必须输出 finish: true 和 answer，不要重复调用工具
5. ⚠️ 绝对禁止：同一个问题已经得到正确结果后，再次调用同一工具。必须立即输出 finish: true。
6. ⚠️ 绝对禁止：Action 的格式必须是 工具名[参数]，禁止出现 工具名[参数][参数] 或 工具名[参数][] 这种嵌套格式。

【何时查询研报】
- 用户问行业趋势、板块机会、公司基本面 → 调用 query_research_report 工具          
- 用户问具体股票价格、技术指标、回测 → 调对应工具，不查研报    
- 用户问数学计算 → 直接 calculator 工具，不调研报                        

【示例】
Question: 新能源行业最近怎么样？
{{"thought": "用户问行业情况，应该查询研报知识库", "action": "query_research_report", "action_input": "新能源行业最近的趋势和投资机会", "finish": false}}

Question: 计算 100 / 4
{{"thought": "简单数学计算", "action": "calculator", "action_input": "100 / 4", "finish": false}}

Question: 回测贵州茅台的双均线策略
{{"thought": "用户要求回测，直接获取数据并回测", "action": "get_stock_data", "action_input": "600519|20240101", "finish": false}}

历史记录：
"""
    # 追加历史
    for step in state["history"]:
        prompt += f"\nThought: {step['thought']}"
        if step["action"]:
            prompt += f"\nAction: {step['action']}[{step['action_input']}]"
        if step["observation"]:
            prompt += f"\nObservation: {step['observation']}"

    if state.get("report_summary"):
        prompt += f"\n\n【研报参考信息】\n{state['report_summary']}\n"
    
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
    """创建并编译 LangGraph Agent（带 decision + Memory）"""
    builder = StateGraph(AgentState)

    # 添加节点
    builder.add_node("decision", decision_node)
    builder.add_node("thought", thought_node)
    builder.add_node("action", action_node)
    builder.add_node("observe", observation_node)

    # 设置入口点
    builder.set_entry_point("decision")

    # 无论是否查研报，都进入思考
    builder.add_edge("decision", "thought")
    
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

    # 添加 Memory
    memory = MemorySaver()
    
    return builder.compile(checkpointer=memory)

# ========== 8. 运行入口 ==========
def run_agent(question: str, thread_id: str = "default", max_steps: int = 10):
    """
    运行 LangGraph Agent（支持断点续跑）
    
    Args:
        question: 用户问题
        thread_id: 会话 ID，相同 ID 共享记忆
        max_steps: 最大步数
    """
    graph = get_graph()
    config = {"configurable": {"thread_id": thread_id}}

    # 关键修复：从 checkpoint 读取历史
    previous_history = []
    try:
        checkpoint = graph.get_state(config)
        if checkpoint and hasattr(checkpoint, 'values'):
            previous_history = checkpoint.values.get("history", [])
            if previous_history:
                print(f"📚 加载历史: {len(previous_history)} 条")
    except Exception as e:
        print(f"⚠️ 读取 checkpoint 失败: {e}")

    # 初始状态
    initial_state = {
        "question": question,
        "history": previous_history,  # 手动注入 checkpoint 历史
        "current_step": 0,
        "max_steps": max_steps,
        "final_answer": "",
        "finish": False,
        "report_summary": "",
    }

    print(f"🚀 LangGraph Agent 启动 [thread_id={thread_id}]:{question}")
    print("="*50)

    # 运行图
    final_state = graph.invoke(initial_state,config)

    return final_state["final_answer"]

def continue_agent(thread_id: str):
    """
    断点续跑：从上次中断的地方继续
    """
    graph = get_graph()
    config = {"configurable": {"thread_id": thread_id}}  # 填 thread_id 和 thread_id
    
    # 传入 None，从 checkpoint 恢复
    final_state = graph.invoke(None, config)  # 填 None
    return final_state["final_answer"]

# ========== 全局单例 ==========
_graph = None  # 全局缓存，避免重复创建 MemorySaver

def get_graph():
    """获取或创建 LangGraph（复用 MemorySaver）"""
    global _graph
    if _graph is None:
        _graph = create_agent()
    return _graph

if __name__ == "__main__":
    # 测试 1：需要查研报（行业问题）
    print("=" * 60)
    print("测试 1：行业分析 → 应该调研报")
    print("=" * 60)
    result1 = run_agent("新能源行业最近怎么样？研报里怎么说？", thread_id="test_rag_1")
    print(f"\n结果: {result1}\n")
    
    # 测试 2：不需要查研报（数学）
    print("=" * 60)
    print("测试 2：数学计算 → 不调研报")
    print("=" * 60)
    result2 = run_agent("计算 100 除以 4", thread_id="test_rag_2")
    print(f"\n结果: {result2}\n")
    
    # 测试 3：不需要查研报（回测）
    print("=" * 60)
    print("测试 3：回测请求 → 不调研报，直接获取数据")
    print("=" * 60)
    result3 = run_agent("回测贵州茅台的双均线策略", thread_id="test_rag_3")
    print(f"\n结果: {result3}")  
