"""构建多 Agent 的 LangGraph"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from langgraph.graph import StateGraph,END
from langgraph.checkpoint.memory import MemorySaver

from quant_agent.core.state import QuantAgentState
from quant_agent.core.orchestrator import classify_intent,should_continue
from quant_agent.agents.data_agent import data_agent_node
from quant_agent.agents.tech_agent import tech_agent_node
from quant_agent.agents.rag_agent import rag_agent_node
from quant_agent.agents.strategy_agent import strategy_agent_node
from quant_agent.agents.backtest_agent import backtest_agent_node

def build_quant_agent_graph():
    """构建 QuantAgent 多 Agent 协作图"""
    builder = StateGraph(QuantAgentState)

    # === 添加所有节点 ===
    builder.add_node("orchestrator",classify_intent)
    builder.add_node("data_agent",data_agent_node)
    builder.add_node("tech_agent",tech_agent_node)
    builder.add_node("rag_agent",rag_agent_node)
    builder.add_node("strategy_agent",strategy_agent_node)
    builder.add_node("backtest_agent",backtest_agent_node)

    # === 设置入口 ===
    builder.set_entry_point("orchestrator")

    # === Orchestrator → 条件路由 ===
    builder.add_conditional_edges(
        "orchestrator",
        should_continue,
        {
            "rag_agent": "rag_agent",
            "data_agent": "data_agent",
            "tech_agent": "tech_agent",
            "strategy_agent": "strategy_agent",
            "backtest_agent": "backtest_agent",
            "finish": END,
        },
    )

    # === 各 Agent → 回到 Orchestrator（让总指挥决定下一步）===
    for agent in ["rag_agent","data_agent","tech_agent","strategy_agent","backtest_agent"]:
        builder.add_conditional_edges(
            agent,
            should_continue,
            {
                "rag_agent": "rag_agent",
                "data_agent": "data_agent",
                "tech_agent": "tech_agent",
                "strategy_agent": "strategy_agent",
                "backtest_agent": "backtest_agent",
                "finish": END,
            }
        )

    # === 编译 ===
    memory = MemorySaver()
    return builder.compile(checkpointer=memory)

def generate_final_report(state: dict) -> str:
    """生成最终报告"""
    
    lines = []
    lines.append("=" * 60)
    lines.append("QuantAgent 研究报告")
    lines.append("=" * 60)
    lines.append(f"用户问题: {state['user_input']}")
    lines.append(f"执行计划: {' → '.join(state.get('execution_plan', []))}")
    lines.append("")
    
    if state.get("research_summary"):
        lines.append("【研报摘要】")
        lines.append(state["research_summary"][:500])
        lines.append("")
    
    if state.get("stock_data"):
        lines.append("【数据摘要】")
        sd = state["stock_data"]
        lines.append(f"股票代码: {sd['code']}")
        lines.append(f"最新收盘价: {sd.get('latest_close', 'N/A')}")
        lines.append(f"数据条数: {sd.get('row_count', 'N/A')}")
        lines.append("")
    
    if state.get("technical_analysis"):
        lines.append("【技术分析】")
        lines.append(state["technical_analysis"])
        lines.append("")
    
    if state.get("backtest_result"):
        lines.append("【回测结果】")
        br = state["backtest_result"]
        lines.append(f"总收益率: {br['total_return']}%")
        lines.append(f"夏普比率: {br['sharpe_ratio']}")
        lines.append(f"最大回撤: {br['max_drawdown']}%")
        lines.append("")
    
    if state.get("errors"):
        lines.append("【执行错误】")
        for err in state["errors"]:
            lines.append(f"- {err}")
        lines.append("")
    
    lines.append("=" * 60)
    
    return "\n".join(lines)
