"""TechAgent：技术分析"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pandas as pd
from quant_agent.core.state import QuantAgentState

def tech_agent_node(state: QuantAgentState) -> QuantAgentState:
    """技术分析节点"""
    stock_data = state.get("stock_data")

    if not stock_data:
        return {
            **state,
            "errors":state.get("errors", []) + ["TechAgent: 无数据"],
            "plan_step": state["plan_step"]+1,
            "current_agent": "tech_agent",
        }

    print(f"📈 TechAgent: 正在分析 {stock_data['code']}...")

    try:
        df = pd.read_csv(stock_data["path"])
        latest = df.iloc[-1]

        # 取最近两天数据做对比
        latest = df.iloc[-1]
        prev = df.iloc[-2]

        signals = []
        
        # MA 金叉/死叉判断（需要对比 today 和 yesterday）
        if latest["MA5"] > latest["MA20"] and prev["MA5"] <= prev["MA20"]:
            signals.append("🟢 MA5 上穿 MA20，出现金叉信号")
        elif latest["MA5"] < latest["MA20"] and prev["MA5"] >= prev["MA20"]:
            signals.append("🔴 MA5 下穿 MA20，出现死叉信号")
        elif latest["MA5"] > latest["MA20"]:
            signals.append("🟡 MA5 在 MA20 上方，短期趋势向上")
        else:
            signals.append("🟡 MA5 在 MA20 下方，短期趋势向下")

        # RSI 判断
        rsi = latest["RSI14"]
        if rsi > 70:
            signals.append(f"🔴 RSI={rsi:.1f} > 70，超买区间")
        elif rsi < 30:
            signals.append(f"🟢 RSI={rsi:.1f} < 30，超卖区间")
        else:
            signals.append(f"⚪ RSI={rsi:.1f}，中性区间")

        # MACD 判断（对比 today 和 yesterday 的 MACD 柱）
        # 提示：add_all_indicators 返回的 df 里有 "MACD" 列
        if latest["MACD"] > 0 and prev["MACD"] <= 0:
            signals.append("🟢 MACD 柱由负转正，多头信号")
        elif latest["MACD"] < 0 and prev["MACD"] >= 0:
            signals.append("🔴 MACD 柱由正转负，空头信号")

        # ========== 填空 4：汇总成分析文字 ==========
        analysis = f"""
        【{stock_data['code']} 技术分析】
        最新收盘价: {stock_data['latest_close']}
        MA5: {stock_data.get('latest_ma5', 'N/A')} | MA20: {stock_data.get('latest_ma20', 'N/A')}

        信号:
        {chr(10).join(signals)}
            """.strip()
        
        print(f"✅ TechAgent: 分析完成")
        
        return {
            **state,
            "technical_analysis": analysis,
            "plan_step": state["plan_step"]+1,
            "current_agent": "tech_agent",
        }

    except Exception as e:
        error_msg = f"TechAgent: {type(e).__name__}: {str(e)}"
        print(f"❌ {error_msg}")
        import traceback
        traceback.print_exc()
        return {
            **state,
            "errors":state.get("errors", []) + [f"TechAgent: {str(e)}"],
            "plan_step": state["plan_step"]+1,
            "current_agent": "tech_agent",
        }

# ========== 填空 6：独立测试块 ==========
if __name__ == "__main__":
    test_state = {
        "user_input": "分析贵州茅台",
        "stock_code": "600519",
        "stock_data": {
            "code": "600519",
            # ↓↓↓ 填空：这个 path 必须指向 DataAgent 刚才生成的 CSV ↓↓↓
            "path": "./data/600519_full_analysis.csv",
            "latest_close": 1444.42,
            "latest_ma5": 1447.57,
            "latest_ma20": 1439.52,
        },
        "technical_analysis": None,
        "current_agent": "",
        "execution_plan": ["data_agent", "tech_agent"],
        "plan_step": 1,
        "errors": [],
        "finish": False,
    }
    
    result = tech_agent_node(test_state)
    print(f"\n测试结果:\n{result.get('analysis', 'N/A')[:300]}...")
