"""Orchestrator：总指挥，负责理解用户意图并制定执行计划"""

import sys
import os

# 把项目根目录（quant_agent 的父目录）加入 sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import re
from typing import List
from quant_agent.core.state import QuantAgentState

# 常见股票名称 → 代码映射
_STOCK_NAME_MAP = {
    "贵州茅台": "600519",
    "宁德时代": "300750",
    "五粮液": "000858",
    "比亚迪": "002594",
    "中芯国际": "688981",
}

def extract_stock_code(text: str) -> str:
    """从文本中提取股票代码（6位数字 或 中文名称）"""
    # 1. 先尝试匹配 6 位数字
    match = re.search(r'\b(\d{6})\b', text)
    if match:
        return match.group(1)
    
    # 2. 再尝试匹配中文名称
    for name, code in _STOCK_NAME_MAP.items():
        if name in text:
            return code
    
    return ""

def classify_intent(state: QuantAgentState) -> QuantAgentState:
    """
    意图识别：根据用户输入，判断要执行哪些 Agent
    
    返回更新后的 State，包含 execution_plan 和 intent
    """
    user_input = state["user_input"]
    stock_code = extract_stock_code(user_input)

    # 意图关键词匹配
    needs_data = any(kw in user_input for kw in ["股价","行情","数据","回测","策略","分析","投资"])
    needs_tech = any(kw in user_input for kw in ["技术指标","MA","RSI","MACD","分析","投资"])
    needs_research = any(kw in user_input for kw in ["研报","行业","板块","机会","怎么样","投资"])
    needs_strategy = any(kw in user_input for kw in ["策略","回测","均线","MACD"])
    needs_backtest = any(kw in user_input for kw in ["回测","策略表现","收益率"])

    # 制定执行计划
    plan = []
    intent_parts = []

    if needs_research:
        plan.append("rag_agent")
        intent_parts.append("研报分析")

    if needs_data:
        plan.append("data_agent")
        intent_parts.append("数据获取")

    if needs_tech:
        plan.append("tech_agent")
        intent_parts.append("技术分析")

    if needs_strategy:
        plan.append("strategy_agent")
        intent_parts.append("策略生成")

    if needs_backtest:
        plan.append("backtest_agent")
        intent_parts.append("回测验证")

    # 如果什么都没匹配到，默认走研报查询
    if not plan:
        plan = ["rag_agent"]
        intent_parts = ["general_query"]

    return {
        **state,
        "intent":"+".join(intent_parts),
        "stock_code":stock_code,
        "execution_plan":plan,
        "plan_step":0,
        "current_agent":"orchestrator",
    }

def get_next_agent(state: QuantAgentState) -> str:
    """
    根据执行计划，决定下一步调用哪个 Agent
    
    返回: Agent 名称 或 "FINISH"
    """
    plan = state.get("execution_plan",[])
    step = state.get("plan_step",0)

    if step < len(plan):
        return plan[step]
    else:
        return "FINISH"

def should_continue(state: QuantAgentState) -> str:
    """
    条件边判断：是否继续执行下一个 Agent
    """
    next_agent = get_next_agent(state)

    if next_agent == "FINISH":
        return "finish"

    # 检查是否有严重错误（超过3个错误强制结束）
    if state.get("errors") and len(state["errors"]) >= 3:
        return "finish"

    return next_agent

# ========== 测试 ==========
if __name__ == "__main__":
    # 测试 1：综合分析
    state1: QuantAgentState = {
        "user_input": "分析一下贵州茅台的投资价值",
        "intent": "", "stock_code": "", "stock_data": None,
        "technical_analysis": None, "research_summary": None,
        "strategy_code": None, "backtest_result": None,
        "current_agent": "", "execution_plan": [], "plan_step": 0,
        "errors": [], "final_report": None, "finish": False,
    }
    result1 = classify_intent(state1)
    print(f"测试 1: {result1['user_input']}")
    print(f"  意图: {result1['intent']}")
    print(f"  股票代码: {result1['stock_code']}")
    print(f"  执行计划: {' → '.join(result1['execution_plan'])}")
    print(f"  下一步: {get_next_agent(result1)}")
    print()
    
    # 测试 2：纯数据查询
    state2: QuantAgentState = {
        "user_input": "获取宁德时代的数据",
        "intent": "", "stock_code": "", "stock_data": None,
        "technical_analysis": None, "research_summary": None,
        "strategy_code": None, "backtest_result": None,
        "current_agent": "", "execution_plan": [], "plan_step": 0,
        "errors": [], "final_report": None, "finish": False,
    }
    result2 = classify_intent(state2)
    print(f"测试 2: {result2['user_input']}")
    print(f"  意图: {result2['intent']}")
    print(f"  股票代码: {result2['stock_code']}")
    print(f"  执行计划: {' → '.join(result2['execution_plan'])}")
    print(f"  下一步: {get_next_agent(result2)}")
