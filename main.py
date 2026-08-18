"""入口脚本：测试手写 ReAct Agent"""

import os
from agent import ReActAgent


def main():
    """
    运行两个测试用例验证 Agent 是否正常工作
    """
    # ========== 配置检查 ==========
    api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ 错误：没有找到 API Key！")
        print("\n请设置环境变量，有以下两种方式：")
        print("\n方式 1 - 临时设置（当前终端有效）：")
        print("  $env:DEEPSEEK_API_KEY=\"sk-your-key-here\"")
        print("\n方式 2 - 永久设置（推荐）：")
        print("  在系统环境变量中添加 DEEPSEEK_API_KEY=sk-your-key-here")
        print("\n申请地址：https://platform.deepseek.com/")
        return
    
    print(f"✅ API Key 已配置: {api_key[:8]}...")
    print(f"🤖 使用模型: deepseek-chat\n")
    
    # ========== 测试用例 1：数学计算 ==========
    print("\n" + "=" * 50)
    print("【测试 1】数学计算")
    print("=" * 50)
    
    agent1 = ReActAgent()
    result1 = agent1.run("计算 100 除以 4 再加 5")
    print(f"\n📌 最终结果: {result1}")
    
    # ========== 测试用例 2：需要搜索 ==========
    print("\n" + "=" * 50)
    print("【测试 2】搜索问题")
    print("=" * 50)
    
    agent2 = ReActAgent()
    result2 = agent2.run("贵州茅台是做什么的？")
    print(f"\n📌 最终结果: {result2}")
    
    # ========== 完成 ==========
    print("\n" + "=" * 50)
    print("🎉 所有测试完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()
