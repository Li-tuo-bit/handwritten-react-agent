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
| **📝 手写 ReAct 实现** | Day 1 从零手写 200 行 ReAct Agent（见 `legacy/agent.py`），理解原理后再上框架 |

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
day01_handwritten_agent/
├── quant_agent/           ← 核心多 Agent 系统
│   ├── core/              # 状态定义、Orchestrator、图构建
│   ├── agents/            # 5 个子 Agent 实现
│   └── main.py            # 主入口
├── scripts/               ← 独立工具脚本（数据获取、指标、回测、可视化）
├── legacy/                ← 手写 Agent 历史代码（Day1 ReAct 实现，见 agent.py）
├── tests/                 ← 测试与实验代码
├── data/                  ← 股票数据 CSV
├── reports/               ← 研报文本
├── strategies/            ← 生成的策略代码
└── docs/                  ← 文档与架构图
```

## 🚀 快速开始

```bash
# 克隆项目
git clone <你的仓库地址>
cd day01_handwritten_agent
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

## 📌 开发日志

- Day 1-2：手写 ReAct Agent + 工具扩展
- Day 3-4：akshare 数据获取 + backtrader 回测
- Day 5：端到端整合
- Day 6：LangGraph 迁移
- Day 7-9：RAG 基础 + ChromaDB + Memory
- Day 10：多 Agent 架构设计
- Day 11-13：5 个子 Agent 实现 + 联调测试
- Day 14-15：工程化整理（代码结构、异常处理、README、Demo）

## 📄 License

MIT

---

> 本项目为个人学习项目，用于实践 LangGraph 多 Agent 架构和量化策略自动化。回测结果仅供学习参考，不构成投资建议。
