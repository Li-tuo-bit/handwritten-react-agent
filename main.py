"""Day 5 端到端测试：一句话完成数据→分析→回测→报告"""

from agent import ReActAgent

# ========== 测试 1：完整链路 ==========
print("=" * 60)
print("测试 1：完整链路 —— 数据 → 分析 → 回测 → 报告")
print("=" * 60)

agent = ReActAgent()
result = agent.run("帮我回测贵州茅台(600519)从2024年1月到2024年12月的双均线策略，并生成一份完整的分析报告")
print(f"\n最终结果:\n{result}")

# ========== 测试 2：多股票对比 ==========
print("\n" + "=" * 60)
print("测试 2：对比两只股票的策略表现")
print("=" * 60)

for stock in ["600519", "300750"]:
    print(f"\n--- {stock} ---")
    agent = ReActAgent()
    r = agent.run(f"回测{stock}从2024年1月到2024年6月的双均线策略")
    print(r[:500])  # 只打印前 500 字

# ========== 测试 3：复杂查询 ==========
print("\n" + "=" * 60)
print("测试 3：复杂查询 —— 获取数据并分析技术面")
print("=" * 60)

agent = ReActAgent()
result3 = agent.run("获取宁德时代(300750)最近半年的数据，分析一下技术面，告诉我该不该买入")
print(result3)