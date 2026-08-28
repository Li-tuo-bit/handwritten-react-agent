"""StrategyAgent：利用 LLM 生成 Backtrader 策略代码"""

import sys
import os

# ========== 填空 1：路径设置 ==========
# 当前文件在 quant_agent/agents/ 下，要回到项目根目录需要上几层？
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

# ========== 填空 2：导入 ==========
# 从 langchain_openai 导入 LLM 类；从 core.state 导入 State 类型
from langchain_openai import ChatOpenAI
from quant_agent.core.state import QuantAgentState
from dotenv import load_dotenv
load_dotenv()

def strategy_agent_node(state: QuantAgentState) -> QuantAgentState:
    """
    策略生成节点

    输入：state["user_input"] + state["technical_analysis"]
    输出：state["strategy_code"]（Python 代码字符串）
    """

    user_input = state["user_input"]
    tech_analysis = state.get("technical_analysis", "")
    stock_code = state.get("stock_code", "")

    print(f"🧠 StrategyAgent: 正在生成策略代码...")

    try:
        # ========== 填空 3：构建 Few-shot Prompt ==========
        # 这里已经写好了完整的 Prompt，你不需要改
        # 它的作用是给 LLM 两个示例（双均线、MACD），让它学会写 Backtrader 策略

        prompt = f"""你是一个量化策略工程师，精通 Backtrader 框架。
请根据用户需求和技术分析，生成一个完整的 Backtrader 策略类。

要求：
1. 必须是一个完整的 Python 类，继承 bt.Strategy
2. 类名格式：Strategy_{stock_code}（如 Strategy_600519）
3. 包含 __init__ 和 next 方法
4. 代码必须可以直接执行，不要省略任何部分
5. 不要输出任何解释文字，只输出代码
6. 不要输出 markdown 标记（如 ```python）

=== 示例 1：双均线策略 ===
class DualMAStrategy(bt.Strategy):
    params = (
        ('short_period', 5),
        ('long_period', 20),
    )

    def __init__(self):
        self.short_ma = bt.indicators.SMA(period=self.p.short_period)
        self.long_ma = bt.indicators.SMA(period=self.p.long_period)
        self.crossover = bt.indicators.CrossOver(self.short_ma, self.long_ma)

    def next(self):
        if self.crossover > 0:
            self.buy()
        elif self.crossover < 0:
            self.sell()

=== 示例 2：MACD 策略 ===
class MACDStrategy(bt.Strategy):
    params = (
        ('fast', 12),
        ('slow', 26),
        ('signal', 9),
    )

    def __init__(self):
        self.macd = bt.indicators.MACD(
            period1=self.p.fast,
            period2=self.p.slow,
            period3=self.p.signal
        )

    def next(self):
        if self.macd.macd > self.macd.signal:
            self.buy()
        elif self.macd.macd < self.macd.signal:
            self.sell()

=== 用户需求 ===
股票代码: {stock_code}
用户输入: {user_input}
技术分析: {tech_analysis[:200] if tech_analysis else '无'}

=== 输出要求 ===
只输出 Python 代码，不要解释，不要 markdown 标记。
"""

        # ========== 填空 4：调用 LLM ==========
        llm = ChatOpenAI(
            model="deepseek-chat",        
            temperature=0.1,    
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com",  # 关键：指向 DeepSeek 的 API 地址
        )

        response = llm.invoke(prompt)
        strategy_code = response.content.strip()

        # ========== 填空 5：清理代码 ==========
        # LLM 可能会输出 markdown 代码块标记，我们需要去掉它们
        # 比如：```python 开头、``` 结尾
        # 请补全下面的清理逻辑
        if strategy_code.startswith("```python"):
            strategy_code = strategy_code[9:]   # 去掉前面的 ```python（共9个字符）
        if strategy_code.startswith("```"):
            strategy_code = strategy_code[3:]   # 去掉前面的 ```（共3个字符）
        if strategy_code.endswith("```"):
            strategy_code = strategy_code[:-3]   # 去掉后面的 ```（共3个字符）
        strategy_code = strategy_code.strip()

        # ===== 强制修复：类名不能以数字开头 =====
        # LLM 可能不遵守 Prompt 的命名格式，兜底处理
        illegal_class_name = f"class {stock_code}Strategy(bt.Strategy):"
        legal_class_name = f"class Strategy_{stock_code}(bt.Strategy):"
        if illegal_class_name in strategy_code:
            strategy_code = strategy_code.replace(illegal_class_name, legal_class_name)
            print(f"⚠️ 自动修复类名: {stock_code}Strategy -> Strategy_{stock_code}")

        # ========== 填空 6：保存代码到文件 ==========
        # 保存路径：项目根目录下的 strategies/{stock_code}_strategy.py
        # 当前文件在 quant_agent/agents/ 下，怎么回到项目根目录？
        project_root = os.path.join(os.path.dirname(__file__), "../..")
        strategy_dir = os.path.join(project_root, "strategies")
        os.makedirs(strategy_dir, exist_ok=True)

        strategy_path = os.path.join(strategy_dir, f"{stock_code}_strategy.py")  # 文件名格式：{stock_code}_strategy.py

        with open(strategy_path, 'w', encoding='utf-8') as f:
            f.write(strategy_code)

        print(f"✅ StrategyAgent: 策略代码已生成，保存至 {strategy_path}")

        return {
            **state,
            "strategy_code": strategy_code,
            "plan_step": state["plan_step"] + 1,
            "current_agent": "strategy_agent",
        }

    except Exception as e:
        print(f"❌ StrategyAgent 错误: {e}")
        import traceback
        traceback.print_exc()
        return {
            **state,
            "errors": state.get("errors", []) + [f"StrategyAgent: {str(e)}"],
            "plan_step": state["plan_step"] + 1,
            "current_agent": "strategy_agent",
        }

# ========== 独立测试 ==========
if __name__ == "__main__":
    test_state = {
        "user_input": "生成一个双均线策略",
        "stock_code": "600519",
        "technical_analysis": "MA5在MA20上方，趋势向上",
        "strategy_code": None,
        "technical_analysis": None,
        "research_summary": None,
        "backtest_result": None,
        "current_agent": "orchestrator",
        "execution_plan": ["strategy_agent"],
        "plan_step": 0,
        "errors": [],
        "finish": False,
    }

    result = strategy_agent_node(test_state)
    code = result.get("strategy_code", "")
    print(f"\n生成的代码前500字符:\n{code[:500]}...")

    # 简单验证：代码里有没有 class 和 bt.Strategy
    if "class" in code and "bt.Strategy" in code:
        print("\n✅ 基本结构检查通过")
    else:
        print("\n❌ 代码结构异常")