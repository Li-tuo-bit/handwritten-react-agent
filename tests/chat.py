from agent import ReActAgent

print("=" * 50)
print("🤖 量化 Agent 已启动")
print("输入你的问题，或输入 'quit' 退出")
print("=" * 50)

while True:
    question = input("\n你: ").strip()
    if question.lower() in ["quit", "exit", "q"]:
        print("再见！")
        break
    
    if not question:
        continue
    
    agent = ReActAgent()
    answer = agent.run(question)
    print(f"\n🤖 Agent: {answer}")
