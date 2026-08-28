"""全局 State 定义——所有 Agent 共享的数据结构"""

from typing import TypedDict,Optional

class QuantAgentState(TypedDict):
    """QuantAgent 全局状态"""
    
    # === 用户输入层 ===
    user_input: str           # 原始用户输入
    intent: str               # Orchestrator 识别的意图
    stock_code: Optional[str] # 提取的股票代码

    # === Agent 输出层 ===
    stock_data :Optional[dict]
    technical_analysis :Optional[str]
    research_summary :Optional[str]
    strategy_code :Optional[str]
    backtest_result :Optional[dict]

    # === 控制层 ===
    current_agent: str        # 当前执行的 Agent 名称
    execution_plan: list      # Orchestrator 制定的执行计划
    plan_step: int            # 当前执行到第几步
    errors: list              # 错误记录  

    # === 输出层 ===
    final_report: Optional[str]  # 最终综合报告
    finish: bool                 # 是否结束

# ========== 测试 ==========
if __name__ == "__main__":
    # 创建一个测试用的 State
    state = QuantAgentState(
        user_input="分析一下贵州茅台",
        intent="",
        stock_code="600519",
        stock_data=None,
        technical_analysis=None,
        research_summary=None,
        strategy_code=None,
        backtest_result=None,
        current_agent="orchestrator",
        execution_plan=[],
        plan_step=0,
        errors=[],
        final_report=None,
        finish=False,
    )

    print(f"✅ State 创建成功: {state['user_input']}")
    print(f"股票代码: {state['stock_code']}")
