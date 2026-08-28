"""Day 11 联调测试：DataAgent → TechAgent → RAGAgent"""

import sys
sys.path.insert(0, '.')

from quant_agent.core.state import QuantAgentState
from quant_agent.agents.data_agent import data_agent_node
from quant_agent.agents.tech_agent import tech_agent_node
from quant_agent.agents.rag_agent import rag_agent_node

def test_pipeline():
    """手动模拟 Orchestrator 调度，测试数据传递"""
    
    # 初始状态
    state = {
        "user_input": "分析贵州茅台的投资价值",
        "intent": "数据分析 + 研报分析",
        "stock_code": "600519",
        "stock_data": None,
        "technical_analysis": None,
        "research_summary": None,
        "current_agent": "",
        # ========== 填空 1：执行计划，按什么顺序执行三个 Agent？ ==========
        "execution_plan": [data_agent_node, tech_agent_node, rag_agent_node],
        "plan_step": 0,
        "errors": [],
        "final_report": None,
        "finish": False,
    }

    print("=" * 60)
    print("开始联调测试：三个 Agent 串行执行")
    print("=" * 60)

    # Step 1: RAGAgent
    print("\n>>> Step 1: RAGAgent")
    state = rag_agent_node(state)
    print(f"研报摘要: {state['research_summary'][:200]}..." if state['research_summary'] else "无")
    print(f"plan_step: {state['plan_step']}")
    
    # Step 2: DataAgent
    print("\n>>> Step 2: DataAgent")
    state = data_agent_node(state)
    print(f"数据获取: {state['stock_data']}")
    print(f"plan_step: {state['plan_step']}")
    
    # Step 3: TechAgent
    print("\n>>> Step 3: TechAgent")
    state = tech_agent_node(state)
    print(f"技术分析: {state['technical_analysis'][:200]}..." if state['technical_analysis'] else "无")
    print(f"plan_step: {state['plan_step']}")
    
    # 汇总
    print("\n" + "=" * 60)
    print("测试完成！")
    print(f"错误数: {len(state['errors'])}")
    if state['errors']:
        print(f"错误详情: {state['errors']}")
    print("=" * 60)

if __name__ == "__main__":
    test_pipeline()