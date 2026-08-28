"""导出 LangGraph 的图结构"""

from langgraph_agent import create_agent

graph = create_agent()

# 文本方式打印（不需要安装任何额外依赖）
print(graph.get_graph().draw_ascii())