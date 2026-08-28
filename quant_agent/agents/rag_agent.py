"""RAGAgent：研报检索"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../tests'))

from rag_tool import query_research_report
from quant_agent.core.state import QuantAgentState

def rag_agent_node(state: QuantAgentState) -> QuantAgentState:
    """研报检索节点
    
    输入：state["user_input"]
    输出：state["research_summary"]（研报摘要）
    """
    user_input = state["user_input"]
    print(f"📚 RAGAgent: 正在查询研报...")
    try:
        # 直接调用已有的 RAG 工具
        result = query_research_report(user_input)
        print(f"✅ RAGAgent: 查询完成")
        return {
            **state,
            "research_summary": result,
            "plan_step": state["plan_step"] + 1,
            "current_agent": "rag_agent",
        }
    
    except Exception as e:
        error_msg = f"RAGAgent: {type(e).__name__}: {str(e)}"
        print(f"❌ {error_msg}")
        import traceback
        traceback.print_exc()
        return {
            **state,
            "errors": state.get("errors", []) + [f"RAGAgent: {str(e)}"],
            "plan_step": state["plan_step"] + 1,
            "current_agent": "rag_agent",
        }

# ========== 填空 3：补充独立测试块 ==========
if __name__ == "__main__":
    test_state = {
        # ↓↓↓ 填空：写一个和新能源/白酒/科技相关的问题 ↓↓↓
        "user_input": "分析一下贵州茅台的投资价值",
        "execution_plan": ["rag_agent"],
        "plan_step": 0,
        "errors": [],
        "finish": False,
    }
    
    result = rag_agent_node(test_state)
    print(f"\n测试结果:\n{result.get('research_summary', 'N/A')[:300]}...")