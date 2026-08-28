"""QuantAgent 入口"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from quant_agent.core.graph_builder import build_quant_agent_graph
from quant_agent.core.state import QuantAgentState

def run_quant_agent(user_input: str,thread_id: str="default"):
    """运行 QuantAgent"""
    graph = build_quant_agent_graph()
    initial_state = {
        "user_input": user_input,
        "intent": "",
        "stock_node": "",
        "stock_data": None,
        "technical_analysis": None,
        "research_summary": None,
        "strategy_code": None,
        "backtest_results": None,
        "current_agent":"",
        "execution_plan": [],
        "plan_step": 0,
        "errors": [],
        "final_report": None,
        "finish": False,
    }

    config = {"configurable":{"thread_id":thread_id}}

    print(f"🚀 QuantAgent 启动: {user_input}")
    print("=" * 60)

    final_state = graph.invoke(initial_state,config)

    # 打印结果
    print("\n" + "=" * 60)
    print("执行完成！")
    print(f"意图识别: {final_state['intent']}")
    print(f"执行计划: {' → '.join(final_state['execution_plan'])}")

    # 各 Agent 输出摘要
    if final_state.get("research_summary"):
        print(f"\n📄 研报摘要（前200字）:")
        print(final_state['research_summary'][:200] + "...")
    
    if final_state.get("stock_data"):
        print(f"\n📊 数据获取:")
        print(f"  股票: {final_state['stock_data']['code']}")
        print(f"  收盘价: {final_state['stock_data']['latest_close']}")
    
    if final_state.get("technical_analysis"):
        print(f"\n📈 技术分析:")
        print(final_state['technical_analysis'])
    
    if final_state.get("errors"):
        print(f"\n⚠️ 错误: {final_state['errors']}")
    
    return final_state

if __name__ == "__main__":
    print("🤖 QuantAgent 多 Agent 量化研究系统")
    print("支持: 研究分析 / 策略回测 / 数据查询")
    print("示例: '研究贵州茅台' / '回测宁德时代双均线策略' / '分析一下五粮液'")
    print("-" * 60)
    
    user_input = input("\n🚀 请输入你的问题: ")
    run_quant_agent(user_input)