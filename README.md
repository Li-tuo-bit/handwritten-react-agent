# Handwritten ReAct Agent × 量化交易

手写 ReAct Agent，从零实现一个能获取股票数据、计算技术指标、执行回测的智能体。

## 功能

- [x] 手写 ReAct Agent（不依赖 LangChain）
- [x] JSON 结构化输出 + 持久化记忆
- [x] 接入 akshare 获取 A 股真实数据
- [x] MA / RSI / MACD 技术指标计算
- [x] backtrader 双均线策略回测
- [x] 端到端自动化：一句话完成数据→分析→回测

## 快速开始

```bash
pip install openai akshare pandas backtrader matplotlib
python main.py
```

## 项目结构

```
.
├── agent.py              # ReAct Agent 核心
├── tools.py              # 工具注册表
├── data_fetcher.py       # akshare 数据获取
├── indicators.py         # 技术指标计算
├── backtest_dual_ma.py   # 双均线回测策略
├── backtest_tools.py     # 回测工具封装
├── report_generator.py   # 报告生成
├── visualize.py          # 指标可视化
└── main.py               # 入口测试
```

## 示例

输入：
```
帮我回测贵州茅台过去一年的双均线策略
```

Agent 自动执行：
1. 获取 600519 一年 K 线数据
2. 计算 MA/RSI/MACD 指标
3. 执行双均线策略回测
4. 生成综合分析报告
