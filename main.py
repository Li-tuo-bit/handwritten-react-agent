"""Day 3 测试入口"""

from agent import ReActAgent

# 测试 1：获取股票数据
print("=== 测试 1：获取股票数据 ===")
agent = ReActAgent()
result = agent.run("获取贵州茅台(600519)从2024年1月1日至今的股价数据")
print(f"结果:\n{result}\n")

# 测试 2：技术分析
print("=== 测试 2：技术分析 ===")
agent2 = ReActAgent()
result2 = agent2.run("分析一下贵州茅台(600519)的技术面")
print(f"结果:\n{result2}\n")

# 测试 3：多工具组合
print("=== 测试 3：多工具组合 ===")
agent3 = ReActAgent()
result3 = agent3.run("获取宁德时代(300750)的数据，把分析结果写入 ./analysis_300750.txt")
print(f"结果:\n{result3}\n")