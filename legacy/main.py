"""Day 8 端到端测试：Agent 研报查询能力"""

from agent import ReActAgent

# 场景 1：需要查研报
print("="*60)
print("测试 1：Agent 自动查研报")
print("="*60)
agent = ReActAgent()
result = agent.run("新能源行业最近怎么样？研报里怎么说？")
print(f"结果:\n{result}\n")

# 场景 2：不需要查研报（测试 Agent 的判断）
print("="*60)
print("测试 2：数学问题不走研报查询")
print("="*60)
agent2 = ReActAgent()
result2 = agent2.run("计算 100 除以 4")
print(f"结果:\n{result2}")