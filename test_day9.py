"""Day 9 测试：Memory + RAG 智能路由"""

from langgraph_agent import run_agent

# 测试 1：需要查研报
print("=" * 60)
print("测试 1：行业分析 → 应该调研报")
print("=" * 60)
result1 = run_agent("新能源行业最近怎么样？研报里怎么说？", thread_id="________")  # 填 test_memory_1
print(f"结果: {result1}\n")

# 测试 2：不需要查研报（数学）
print("=" * 60)
print("测试 2：数学计算 → 不调研报")
print("=" * 60)
result2 = run_agent("计算 100 除以 4", thread_id="________")  # 填 test_memory_2
print(f"结果: {result2}\n")

# 测试 3：不需要查研报（回测）
print("=" * 60)
print("测试 3：回测请求 → 不调研报，直接获取数据")
print("=" * 60)
result3 = run_agent("回测贵州茅台的双均线策略", thread_id="________")  # 填 test_memory_3
print(f"结果: {result3}\n")

# 测试 4：记忆测试（同 thread_id）
print("=" * 60)
print("测试 4：记忆测试 → 同 thread_id 应该记住")
print("=" * 60)
run_agent("计算 50 + 80", thread_id="________")  # 填 test_memory_4
result4 = run_agent("刚才算的是多少？", thread_id="________")  # 填同一个 test_memory_4
print(f"结果: {result4}\n")

# 测试 5：研报 + 数据结合
print("=" * 60)
print("测试 5：研报 + 回测 → 先查研报，再回测")
print("=" * 60)
result5 = run_agent("白酒行业怎么样？用双均线策略回测一下五粮液", thread_id="________")  # 填 test_memory_5
print(f"结果: {result5}")