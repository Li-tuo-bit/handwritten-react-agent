"""DataAgent：获取股票数据"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../scripts'))

import pandas as pd
from data_fetcher import get_stock_kline
from indicators import add_all_indicators
from quant_agent.core.state import QuantAgentState

def data_agent_node(state: QuantAgentState) -> QuantAgentState:
    """数据获取节点
    输入：state["stock_code"]
    输出：state["stock_data"] = {
        "code": ...,
        "path": ...,
        "latest_close": ...,
        "latest_ma5": ...,
        "latest_ma20": ...,
        "rsi14": ...,
        "row_count": ...
    }
    """

    # ========== 【已有，检查】从 state 中获取股票代码 ==========
    stock_code = state.get("stock_code", "")

    # 如果没有股票代码，尝试从 user_input 提取（备用）
    if not stock_code:
        import re
        match = re.search(r'\b(\d{6})\b', state["user_input"])
        stock_code = match.group(1) if match else ""

    if not stock_code:
        return {
            **state,
            "errors":state.get("errors", []) + ["DataAgent: 未提供股票代码"],
            "plan_step": state["plan_step"]+1,
            "current_agent": "data_agent"
        }

    print(f"📊 DataAgent: 正在获取 {stock_code} 的数据...")

    try:
        # ========== 【已有，检查】获取 K 线数据 ==========
        df = get_stock_kline(stock_code=stock_code,start_date="20240101")
        # ========== 【已有，检查】计算技术指标 ==========
        df = add_all_indicators(df)

        # ========== 【修改这里】保存路径改为 _full_analysis.csv ==========
        output_path = f"./data/{stock_code}_full_analysis.csv"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False,encoding="utf-8-sig")

        # ========== 【已有】提取最新数据 ==========
        latest = df.iloc[-1]

        # ========== 【补充这里】构造完整的 stock_data 字典 ==========
        stock_data = {
            "code": stock_code,
            "path": output_path,
            "latest_close": round(float(latest["收盘"]), 2),
            # ↓↓↓ 填空：补充 latest_ma5 字段，注意用 round(, 2) 和 pd.isna() 保护 ↓↓↓
            "latest_ma5": round(float(latest["MA5"]), 2) if not pd.isna(latest["MA5"]) else None,
            "latest_ma20": round(float(latest["MA20"]), 2) if not pd.isna(latest["MA20"]) else None,
            # ↓↓↓ 填空：补充 rsi14 字段，和上面格式一致 ↓↓↓
            "rsi14": round(float(latest["RSI14"]), 2) if not pd.isna(latest["RSI14"]) else None,
            "row_count": len(df),
        }
        
        print(f"✅ DataAgent: 获取成功，{len(df)} 条数据")
        
        return {
            **state,
            "stock_data": stock_data,
            "plan_step": state["plan_step"] + 1,
            "current_agent": "data_agent",
        }
    
    except Exception as e:
        error_msg = f"DataAgent: {type(e).__name__}: {str(e)}"
        print(f"❌ {error_msg}")
        import traceback
        traceback.print_exc()
        return {
            **state,
            "errors":state.get("errors", []) + [f"DataAgent: {str(e)}"],
            "plan_step": state["plan_step"]+1,
            "current_agent": "data_agent"
        }

# ========== 【补充这里】独立测试块 ==========
if __name__ == "__main__":
    test_state = {
        "user_input": "分析贵州茅台",
        "intent": "数据分析",
        "stock_code": "600519",
        "stock_data": None,
        "technical_analysis": None,
        "research_summary": None,
        "current_agent": "",
        "execution_plan": ["data_agent"],
        "plan_step": 0,
        "errors": [],
        "final_report": None,
        "finish": False,
    }
    
    result = data_agent_node(test_state)
    print(f"\n测试结果:")
    print(f"stock_data: {result.get('stock_data')}")
    print(f"errors: {result.get('errors')}")