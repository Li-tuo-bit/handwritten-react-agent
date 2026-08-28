"""BacktestAgent：加载策略代码并执行回测"""

import sys
import os

# ========== 填空 1：路径设置 ==========
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import backtrader as bt
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

from quant_agent.core.state import QuantAgentState

def backtest_agent_node(state: QuantAgentState) -> QuantAgentState:
    """
    回测验证节点

    输入：state["strategy_code"] + state["stock_data"]
    输出：state["backtest_result"] = {
        "initial_cash": 100000.0,
        "final_value": ...,
        "total_return": ...,
        "sharpe_ratio": ...,
        "max_drawdown": ...,
    }
    """

    strategy_code = state.get("strategy_code", "")
    stock_data = state.get("stock_data")

    if not strategy_code or not stock_data:
        return {
            **state,
            "errors": state.get("errors", []) + ["BacktestAgent: 缺少策略代码或数据"],
            "plan_step": state["plan_step"] + 1,
            "current_agent": "backtest_agent",
        }

    stock_code = stock_data.get("code", "unknown")
    print(f"📊 BacktestAgent: 正在回测 {stock_code}...")

    try:
        # ========== 填空 2：动态加载策略类 ==========
        # 用 exec() 在局部命名空间执行代码，然后提取策略类
        namespace = {}
        exec(strategy_code, {"bt": bt, "__name__": "__main__"}, namespace)

        # 类名格式是 Strategy_{stock_code}，比如 Strategy_600519
        strategy_class_name = f"Strategy_{stock_code}"
        strategy_cls = namespace.get(strategy_class_name)

        # 如果按名字找不到，兜底：找 namespace 里任何继承 bt.Strategy 的类
        if not strategy_cls:
            for name, obj in namespace.items():
                if isinstance(obj, type) and issubclass(obj, bt.Strategy):
                    strategy_cls = obj
                    print(f"⚠️ 按名字找不到策略类，兜底使用: {name}")
                    break

        if not strategy_cls:
            raise ValueError(f"未找到策略类，代码内容前200字: {strategy_code[:200]}")

        print(f"✅ 加载策略类: {strategy_cls.__name__}")

        # ========== 填空 3：准备数据 ==========
        # 从 stock_data["path"] 读取 CSV
        df = pd.read_csv(stock_data["path"])

        # 重命名列为 backtrader 需要的英文格式
        # 你的 CSV 列名可能是中文（日期、开盘、收盘...）或英文（date、open、close...）
        # 这里假设是中文，请根据你的实际 CSV 调整
        df = df.rename(columns={
            "日期": "datetime",   # 日期列的原始名字
            "开盘": "open",         # 开盘列的原始名字
            "收盘": "close",        # 收盘列的原始名字
            "最高": "high",         # 最高列的原始名字
            "最低": "low",          # 最低列的原始名字
            "成交量": "volume",     # 成交量列的原始名字
        })
        print("rename后列名:", df.columns.tolist())
        df["datetime"] = pd.to_datetime(df["datetime"])
        df["openinterest"] = 0  # backtrader 需要这个列，设为0

        # ========== 填空 4：创建 Cerebro 引擎 ==========
        cerebro = bt.Cerebro()
        cerebro.addstrategy(strategy_cls)

        # 添加数据
        data = bt.feeds.PandasData(
            dataname=df,
            datetime="datetime",
            open="open",
            high="high",
            low="low",
            close="close",
            volume="volume",
            openinterest="openinterest",
        )
        cerebro.adddata(data)

        # 设置初始资金和手续费
        cerebro.broker.setcash(100000.0)
        cerebro.broker.setcommission(commission=0.00025)  # 万2.5手续费

        # 添加分析器
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe")
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
        cerebro.addanalyzer(bt.analyzers.Returns, _name="returns")

        # ========== 填空 5：运行回测 ==========
        print(f"初始资金: {cerebro.broker.getvalue()}")
        results = cerebro.run()
        strat = results[0]
        final_value = cerebro.broker.getvalue()

        # ========== 填空 6：提取结果 ==========
        sharpe = strat.analyzers.sharpe.get_analysis()
        drawdown = strat.analyzers.drawdown.get_analysis()
        returns = strat.analyzers.returns.get_analysis()

        backtest_result = {
            "initial_cash": 100000.0,
            "final_value": round(final_value, 2),
            "total_return": round((final_value / 100000.0 - 1) * 100, 2),
            "sharpe_ratio": sharpe.get("sharperatio", "N/A"),
            "max_drawdown": round(drawdown.max.drawdown, 2) if hasattr(drawdown, "max") else "N/A",
            "annual_return": returns.get("rnorm100", "N/A"),
        }

        print(f"✅ BacktestAgent: 回测完成")
        print(f"  总收益率: {backtest_result['total_return']}%")
        print(f"  夏普比率: {backtest_result['sharpe_ratio']}")
        print(f"  最大回撤: {backtest_result['max_drawdown']}%")

        return {
            **state,
            "backtest_result": backtest_result,
            "plan_step": state["plan_step"] + 1,
            "current_agent": "backtest_agent",
        }

    except Exception as e:
        print(f"❌ BacktestAgent 错误: {e}")
        import traceback
        traceback.print_exc()
        return {
            **state,
            "errors": state.get("errors", []) + [f"BacktestAgent: {str(e)}"],
            "plan_step": state["plan_step"] + 1,
            "current_agent": "backtest_agent",
        }

# ========== 独立测试 ==========
if __name__ == "__main__":
    # 先准备一个测试用的策略代码
    test_strategy = """
class Strategy_600519(bt.Strategy):
    def __init__(self):
        self.ma5 = bt.indicators.SMA(period=5)
        self.ma20 = bt.indicators.SMA(period=20)

    def next(self):
        if self.ma5 > self.ma20:
            self.buy()
        elif self.ma5 < self.ma20:
            self.sell()
"""

    test_state = {
        "user_input": "回测",
        "stock_code": "600519",
        "stock_data": {
            "code": "600519",
            "path": "./data/600519_full_analysis.csv",  # 你的数据文件路径
        },
        "strategy_code": test_strategy,
        "backtest_result": None,
        "current_agent": "orchestrator",
        "execution_plan": ["backtest_agent"],
        "plan_step": 0,
        "errors": [],
        "finish": False,
    }

    result = backtest_agent_node(test_state)
    print(f"\n回测结果: {result.get('backtest_result')}")