# QuantAgent —— 多 Agent 量化研究系统

> 基于 LangGraph 的多 Agent 协作系统，支持自然语言驱动的一站式量化分析：数据获取 → 技术分析 → 研报检索 → 策略生成 → 自动回测。

## 🚀 核心亮点

| 能力 | 说明 |
|------|------|
| **🔮 LLM 策略生成** | 输入一句话（如"双均线策略"），系统自动生成可执行的 Backtrader 策略代码 |
| **🤖 多 Agent 协作** | 6 个 Agent 由 Orchestrator 统一调度，按意图自动编排执行链路 |
| **📊 自动回测** | 策略代码动态加载（exec），Cerebro 引擎自动执行，输出收益率/夏普比率/最大回撤 |
| **📚 研报 RAG** | 基于 ChromaDB + 本地嵌入模型，检索研报并生成投资摘要 |
| **🎯 意图识别** | 自动识别用户意图，匹配最佳 Agent 组合（研究/回测/分析） |

## 🏗️ 系统架构

```
用户输入
   ↓
Orchestrator（意图识别 + 执行计划编排）
   ↓
┌─────────┬─────────┬─────────┬─────────┬─────────┐
│RAGAgent │DataAgent│TechAgent│Strategy │Backtest │
│研报检索  │数据获取  │技术分析  │策略生成  │回测验证  │
└─────────┴─────────┴─────────┴─────────┴─────────┘
   ↓                    ↓
综合报告              回测报告
```

### Agent 职责

| Agent | 输入 | 输出 | 依赖 |
|-------|------|------|------|
| **Orchestrator** | 用户自然语言 | 意图 + 执行计划 | - |
| **DataAgent** | 股票代码 | CSV 数据文件 + 指标 | - |
| **TechAgent** | 数据路径 | 技术分析报告（MA/RSI/MACD） | DataAgent |
| **RAGAgent** | 用户问题 | 研报摘要 | - |
| **StrategyAgent** | 用户需求 + 技术分析 | 可执行 Python 策略代码 | DataAgent(可选Tech) |
| **BacktestAgent** | 策略代码 + 数据 | 回测结果（收益率/夏普/回撤） | StrategyAgent + DataAgent |

## 🛠️ 技术栈

- **Agent 框架**：LangGraph（状态机 + 条件路由）
- **LLM**：DeepSeek API（兼容 OpenAI 格式）
- **回测引擎**：Backtrader
- **数据获取**：AKShare / 本地 CSV
- **向量数据库**：ChromaDB + BGE 中文嵌入模型
- **数据处理**：Pandas + NumPy

## 📁 项目结构

```
quant_agent/
├── core/
│   ├── state.py           # 全局 State 定义（TypedDict）
│   ├── orchestrator.py    # 意图识别 + 执行计划编排
│   └── graph_builder.py   # LangGraph 图构建
├── agents/
│   ├── data_agent.py      # 股票数据获取 + 指标计算
│   ├── tech_agent.py      # 技术分析（MA/RSI/MACD 信号）
│   ├── rag_agent.py       # 研报检索（ChromaDB RAG）
│   ├── strategy_agent.py  # LLM 生成 Backtrader 策略代码
│   └── backtest_agent.py  # 动态加载策略 + Cerebro 回测
└── main.py                # 主入口

strategies/                # 生成的策略代码
├── 600519_strategy.py     # 贵州茅台-双均线策略
└── 300750_strategy.py     # 宁德时代-双均线策略

data/                      # 股票数据 CSV
report_*.txt               # 生成的研究报告
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
# 核心依赖：langgraph, langchain-openai, backtrader, pandas, chromadb, akshare
```

### 2. 配置 API Key

```bash
# .env
DEEPSEEK_API_KEY=your_key_here
```

### 3. 运行单个案例

```bash
# 案例 A：综合研究
python -c "
from quant_agent.main import run
run('研究一下贵州茅台的投资价值')
"

# 案例 B：策略回测
python -c "
from quant_agent.main import run
run('用双均线策略回测宁德时代')
"
```

### 4. 运行完整测试

```bash
python test_day13.py
# 输出：3 个端到端案例执行报告
```

## 📈 功能演示

### 案例 A：综合研究

```
输入："研究一下贵州茅台的投资价值"
输出：
  → 研报摘要：2024年Q2营收369.7亿元，同比+17.3%...
  → 最新收盘价：1444.42
  → MA5: 1447.57 | MA20: 1439.52
  → 信号：MA5在MA20上方，短期趋势向上；RSI=45.3，中性区间
```

### 案例 B：策略回测

```
输入："用双均线策略回测宁德时代"
输出：
  → 生成策略：Strategy_300750（双均线交叉）
  → 回测结果：
      总收益率: 0.0%
      夏普比率: -25.97
      最大回撤: 0.07%
```

## 🐛 踩坑记录 & 经验

| 问题 | 根因 | 解法 |
|------|------|------|
| LLM 生成非法类名 `600519Strategy` | Python 标识符不能以数字开头 | Prompt 约束 + 强制 `str.replace()` 兜底 |
| `exec()` 后找不到策略类 | 类名不固定 | `namespace` 遍历 + `issubclass(obj, bt.Strategy)` 兜底 |
| LLM 输出 markdown 代码块 | 模型习惯 | `strip()` + 去除 ` ```python ` 前缀 |
| 回测数据列名不匹配 | CSV 中文列名 | `df.rename(columns={"日期": "datetime", ...})` |

## 📌 项目状态

- ✅ Day 1-11：DataAgent / TechAgent / RAGAgent / Orchestrator
- ✅ Day 12：StrategyAgent（LLM 策略生成）+ BacktestAgent（自动回测）
- ✅ Day 13：3 个端到端案例联调通过，Bug 清零
- 🔄 Day 14+：工程化（日志、异常处理、README、代码清理）

## 📄 License

MIT

---

> 本项目为个人学习项目，用于实践 LangGraph 多 Agent 架构和量化策略自动化。回测结果仅供学习参考，不构成投资建议。
