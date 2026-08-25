# Handwritten ReAct Agent × 量化交易 × RAG

> 从零手写 ReAct Agent，逐步演进为基于 LangGraph 的多能力智能体：支持股票数据分析、技术指标计算、策略回测、研报检索增强生成（RAG）和记忆持久化。

## ✨ 功能特性

### 第一阶段：手写 Agent（Day 1-5）
- [x] **手写 ReAct Agent**：不依赖 LangChain，200 行代码实现 Thought → Action → Observation 循环
- [x] **JSON 结构化输出**：LLM 输出标准化 JSON，解析更可靠
- [x] **持久化记忆**：`agent_memory.json` 记录历史对话
- [x] **工具扩展**：计算器、文件读写、股票数据获取、回测执行
- [x] **真实数据接入**：akshare 获取 A 股历史 K 线数据
- [x] **技术指标计算**：MA / RSI / MACD 三指标
- [x] **backtrader 回测**：双均线策略（金叉买入/死叉卖出）
- [x] **端到端自动化**：一句话完成"数据获取 → 指标分析 → 策略回测 → 报告生成"
- [x] **指标可视化**：matplotlib 绘制 K 线 + 技术指标图表

### 第二阶段：LangGraph 框架化（Day 6）
- [x] **LangGraph 迁移**：State / Node / Edge 架构重写 Agent
- [x] **图结构可视化**：工作流可图形化展示
- [x] **手写版 vs 框架版对比**：同一功能两种实现，理解框架价值

### 第三阶段：RAG 知识库（Day 7-8）
- [x] **文本分块**：`RecursiveCharacterTextSplitter` 处理中文研报
- [x] **Embedding 向量化**：本地 `bge-small-zh` + OpenAI Embedding 双方案
- [x] **ChromaDB 向量数据库**：持久化存储研报向量，支持语义检索
- [x] **研报知识库**：3 篇模拟研报（新能源/白酒/半导体）入库
- [x] **RAG 问答**：检索相关文本块 + LLM 生成回答

### 第四阶段：记忆 + 智能路由（Day 9）
- [x] **LangGraph MemorySaver**：支持断点续跑，同 `thread_id` 共享记忆
- [x] **智能路由**：`decision_node` 自动判断何时查研报、何时直接执行工具
- [x] **研报辅助决策**：行业/板块问题自动查研报，技术问题直接执行

---

## 🚀 快速开始

### 环境准备

```bash
# 克隆仓库
git clone https://github.com/Li-tuo-bit/handwritten-react-agent.git
cd handwritten-react-agent

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# 安装依赖
pip install openai akshare pandas backtrader matplotlib langgraph langchain langchain-openai chromadb sentence-transformers
```

### 配置 API Key

```bash
# Windows
set OPENAI_API_KEY=your_key_here
set DEEPSEEK_API_KEY=your_key_here

# 或使用 .env 文件
echo DEEPSEEK_API_KEY=your_key_here > .env
```

### 运行测试

```bash
# 测试 LangGraph Agent（带 Memory + RAG）
python test_day9.py

# 或运行单个功能
python langgraph_agent.py        # LangGraph 版 Agent
python data_fetcher.py           # 获取股票数据
python indicators.py             # 计算技术指标
python backtest_dual_ma.py       # 双均线回测
python report_qa.py              # 研报问答
```

---

## 📁 项目结构

```
.
├── agent.py                    # 手写 ReAct Agent 核心（Day 1-5）
├── tools.py                    # 工具注册表
├── langgraph_agent.py          # LangGraph 版 Agent（Day 6-9）⭐
├── shared_tools.py             # 共用工具层
├── test_day9.py                # Day 9 完整测试
│
├── data_fetcher.py             # akshare 数据获取
├── indicators.py               # 技术指标计算（MA/RSI/MACD）
├── backtest_dual_ma.py         # backtrader 双均线回测策略
├── backtest_tools.py           # 回测工具封装（供 Agent 调用）
├── visualize.py                # 技术指标可视化
├── report_generator.py         # 综合分析报告生成
│
├── text_splitter.py            # 文本分块（Day 7）
├── embedding_local.py          # 本地 bge-small-zh Embedding
├── embedding_openai.py         # OpenAI Embedding（备选）
├── chroma_manager.py           # ChromaDB 向量数据库管理器
├── report_ingest.py            # 研报入库（分块→向量化→存储）
├── report_qa.py                # 研报问答系统（检索+LLM生成）
├── rag_tool.py                 # RAG 工具封装（供 Agent 调用）
│
├── main.py                     # 手写版入口测试
├── compare_versions.py         # 手写版 vs LangGraph 版对比
│
├── reports/                    # 研报原文（3 篇模拟研报）
│   ├── 新能源_2024Q2.txt
│   ├── 白酒_2024Q2.txt
│   └── 半导体_2024Q2.txt
├── data/                       # 股票数据 CSV
│   ├── 600519_kline.csv
│   └── 000858_kline.csv
├── chroma_db/                  # ChromaDB 向量数据库
│
└── README.md                   # 本文件
```

---

## 💡 使用示例

### 示例 1：行业分析（自动查研报）

```python
from langgraph_agent import run_agent

result = run_agent("新能源行业最近怎么样？研报里怎么说？", thread_id="user_001")
print(result)
```

**Agent 行为**：
1. `decision_node` 检测到"新能源"关键词
2. 自动查询 `query_research_report`
3. 返回基于研报的行业分析

### 示例 2：数学计算（不调研报）

```python
result = run_agent("计算 100 除以 4", thread_id="user_002")
# 直接调用 calculator，不查研报
```

### 示例 3：回测请求（直接执行）

```python
result = run_agent("回测贵州茅台的双均线策略", thread_id="user_003")
# 直接调用 get_stock_data → run_backtest
```

### 示例 4：多轮对话（记忆）

```python
run_agent("计算 50 + 80", thread_id="memory_test")
result = run_agent("刚才算的是多少？", thread_id="memory_test")
# 返回：刚才计算的是 50 + 80，结果是 130。
```

### 示例 5：研报 + 回测组合

```python
result = run_agent("白酒行业怎么样？用双均线策略回测一下五粮液", thread_id="combo_test")
# 1. 先查白酒研报 → 2. 再回测 000858
```

---

## 🏗️ 架构演进

| 阶段 | 文件 | 特点 |
|------|------|------|
| **手写版** | `agent.py` | 纯 Python 实现 ReAct 循环，理解底层原理 |
| **框架版** | `langgraph_agent.py` | LangGraph State/Node/Edge，支持断点续跑和记忆 |

### LangGraph 工作流

```
        ┌─────────────┐
        │  __start__  │
        └──────┬──────┘
               │
               ▼
        ┌─────────────┐
        │  decision   │ ──→ 检测行业关键词？是→查研报
        └──────┬──────┘
               │
               ▼
        ┌─────────────┐
        │   thought   │ ──→ LLM 思考：决定调用哪个工具
        └──────┬──────┘
               │
               ▼
        ┌─────────────┐
        │   action    │ ──→ 执行工具调用
        └──────┬──────┘
               │
               ▼
        ┌─────────────┐
        │   observe   │ ──→ 打印日志 + 检查是否完成
        └──────┬──────┘
           │          │
      continue      end
           │          │
           ▼          ▼
        thought     __end__
```

---

## 🛠️ 技术栈

| 模块 | 技术 |
|------|------|
| LLM | DeepSeek API（兼容 OpenAI 格式）|
| Agent 框架 | LangGraph |
| 数据源 | akshare（A 股真实数据）|
| 数据处理 | pandas, numpy |
| 技术指标 | pandas（rolling/ewm）|
| 回测引擎 | backtrader |
| 可视化 | matplotlib |
| 向量数据库 | ChromaDB |
| Embedding | BAAI/bge-small-zh-v1.5（本地）|
| 文本分块 | langchain RecursiveCharacterTextSplitter |

---

## 📊 回测策略说明

**双均线策略（DualMAStrategy）**

| 参数 | 默认值 | 说明 |
|------|--------|------|
| short_window | 5 | 短期均线（MA5）|
| long_window | 20 | 长期均线（MA20）|

**交易规则**：
- **金叉**（MA5 上穿 MA20）→ 买入
- **死叉**（MA5 下穿 MA20）→ 卖出
- 手续费：万 2.5（0.00025）
- 初始资金：10 万元

---

## 📝 完成清单（Day 1-9）

- [x] Day 1：手写 ReAct Agent（Thought → Action → Observation）
- [x] Day 2：扩展工具 + 持久化记忆 + JSON 结构化输出
- [x] Day 3：接入 akshare 真实数据 + MA/RSI/MACD 指标
- [x] Day 4：backtrader 双均线策略回测
- [x] Day 5：端到端整合（数据→分析→回测→报告）
- [x] Day 6：迁移到 LangGraph（State/Node/Edge）
- [x] Day 7：RAG 基础（文本分块 + Embedding）
- [x] Day 8：ChromaDB 向量数据库 + 研报知识库
- [x] Day 9：LangGraph Memory + RAG 智能路由

---

## ⚠️ 常见问题

| 问题 | 解决 |
|------|------|
| akshare 获取数据失败 | 检查网络；项目已支持本地 CSV 缓存模式 |
| LLM 陷入循环 | `should_continue` 已增加防循环检测 |
| ChromaDB 启动报错 | `pip install pysqlite3-binary` 或升级 Python 到 3.9+ |
| 研报回答有编造 | Prompt 已约束："如果研报中没有相关信息，明确说明" |
| 同 thread_id 记不住 | 检查 `config = {"configurable": {"thread_id": ...}}` 是否传入 |

---

## 🎯 明日预告（Day 10）

**多 Agent 架构设计**：把数据获取、技术分析、研报检索、策略生成、回测验证拆成独立 Agent，用 Orchestrator 调度。

---

## 📄 License

MIT
