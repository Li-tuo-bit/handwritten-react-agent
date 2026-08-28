"""Day 12 联调测试：StrategyAgent → BacktestAgent"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from quant_agent.agents.data_agent import data_agent_node
from quant_agent.agents.strategy_agent import strategy_agent_node
from quant_agent.agents.backtest_agent import backtest_agent_node

def test_strategy_pipeline():
    """测试完整链路：数据 → 策略生成 → 回测"""

    # Step 1: 获取数据
    print("=" * 60)
    print(">>> Step 1: 获取数据")
    state = {
        "user_input": "用双均线策略回测贵州茅台",
        "stock_code": "600519",
        "stock_data": None,
        "technical_analysis": None,
        "strategy_code": None,
        "backtest_result": None,
        "current_agent": "orchestrator",
        "execution_plan": ["data_agent", "strategy_agent", "backtest_agent"],
        "plan_step": 0,
        "errors": [],
        "finish": False,
    }
    state = data_agent_node(state)
    print(f"✅ 数据获取完成: {state['stock_data']['row_count']} 条")

    # Step 2: 生成策略
    print("\n" + "=" * 60)
    print(">>> Step 2: 生成策略")
    state = strategy_agent_node(state)
    print(f"✅ 策略代码长度: {len(state['strategy_code'])} 字符")
    print(f"策略代码前 300 字:\n{state['strategy_code'][:300]}...")

    # Step 3: 回测
    print("\n" + "=" * 60)
    print(">>> Step 3: 执行回测")
    state = backtest_agent_node(state)

    # 汇总
    print("\n" + "=" * 60)
    print("🎉 联调完成！")
    if state.get("errors"):
        print(f"❌ 错误: {state['errors']}")
    else:
        result = state["backtest_result"]
        print(f"📊 回测结果:")
        print(f"  初始资金: {result['initial_cash']}")
        print(f"  最终资金: {result['final_value']}")
        print(f"  总收益率: {result['total_return']}%")
        print(f"  夏普比率: {result['sharpe_ratio']}")
        print(f"  最大回撤: {result['max_drawdown']}%")
    print("=" * 60)

if __name__ == "__main__":
    test_strategy_pipeline()