"""Day 4 测试入口"""

from agent import ReActAgent

# 测试 1：单股回测
print("=== 测试 1：双均线回测 ===")
agent = ReActAgent()
result = agent.run("用双均线策略回测贵州茅台(600519)从2023年到2024年的表现")
print(result)

# 测试 2：对比不同参数
print("\n=== 测试 2：参数对比 ===")
agent2 = ReActAgent()
result2 = agent2.run("对比贵州茅台用MA5/MA20和MA10/MA60两种参数的回测结果")
print(result2)