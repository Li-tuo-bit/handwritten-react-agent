"""对比手写版 vs LangGraph 版"""

from agent import ReActAgent as HandwrittenAgent
from langgraph_agent import run_agent as LangGraphAgent

TEST_QUESTION = [
    "计算 100 除以 4 再加 5",    
]

print("="*50)
print("对比测试：手写版 vs LangGraph 版")
print("=" * 70)

for q in TEST_QUESTION:
    print(f"\n{'='*50}")
    print(f"问题: {q}")
    print(f"\n{'='*50}")

    print("\n【手写版】")
    hw_agent = HandwrittenAgent()
    hw_result = hw_agent.run(q)

    print("\n【LangGraph 版】")
    lg_result = LangGraphAgent(q)

    print(f"\n结果一致：{hw_result == lg_result}")
