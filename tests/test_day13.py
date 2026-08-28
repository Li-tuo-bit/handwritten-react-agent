"""Day 13 联调测试：3 个完整案例"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from quant_agent.core.graph_builder import build_quant_agent_graph


def run_case(user_input: str, thread_id: str) -> dict:
    """运行单个测试案例"""
    print(f"\n{'='*70}")
    print(f"案例: {user_input}")
    print(f"{'='*70}")
    
    graph = build_quant_agent_graph()
    
    initial_state = {
        "user_input": user_input,
        "intent": "",
        "stock_code": "",
        "stock_data": None,
        "technical_analysis": None,
        "research_summary": None,
        "strategy_code": None,
        "backtest_result": None,
        "current_agent": "",
        "execution_plan": [],
        "plan_step": 0,
        "errors": [],
        "final_report": None,
        "finish": False,
    }
    
    config = {"configurable": {"thread_id": thread_id}}

    # 在 run_case 函数最后，return 之前加：
    report = generate_final_report(final_state)
    with open(f"./report_{thread_id}.txt", "w", encoding="utf-8") as f:
        f.write(report)
    print(f"📄 报告已保存: report_{thread_id}.txt")
    
    try:
        final_state = graph.invoke(initial_state, config)
        
        # 打印结果摘要
        print(f"\n📋 执行结果:")
        print(f"  意图: {final_state.get('intent', 'N/A')}")
        print(f"  计划: {' → '.join(final_state.get('execution_plan', []))}")
        print(f"  研报摘要: {str(final_state.get('research_summary', 'N/A'))[:100]}...")
        print(f"  数据获取: {final_state.get('stock_data') is not None}")
        print(f"  技术分析: {str(final_state.get('technical_analysis', 'N/A'))[:100]}...")
        print(f"  策略代码: {str(final_state.get('strategy_code', 'N/A'))[:100]}...")
        print(f"  回测结果: {final_state.get('backtest_result', 'N/A')}")
        print(f"  错误数: {len(final_state.get('errors', []))}")
        
        if final_state.get('errors'):
            print(f"  ⚠️ 错误: {final_state['errors']}")
        
        return final_state
    
    except Exception as e:
        print(f"❌ 案例执行失败: {e}")
        import traceback
        traceback.print_exc()
        return {"errors": [str(e)]}


if __name__ == "__main__":
    # ========== 案例 A：综合研究 ==========
    print("\n" + "🧪" * 20)
    print("开始测试案例 A：综合研究")
    print("🧪" * 20)
    case_a = run_case("研究一下贵州茅台的投资价值", "case_a")
    
    # ========== 案例 B：策略回测 ==========
    print("\n" + "🧪" * 20)
    print("开始测试案例 B：策略回测")
    print("🧪" * 20)
    case_b = run_case("用双均线策略回测宁德时代", "case_b")
    
    # ========== 案例 C：技术面分析 ==========
    print("\n" + "🧪" * 20)
    print("开始测试案例 C：技术面分析")
    print("🧪" * 20)
    case_c = run_case("分析一下五粮液的技术面", "case_c")
    
    # ========== 汇总 ==========
    print("\n" + "="*70)
    print("测试汇总")
    print("="*70)
    
    cases = [
        ("A: 综合研究", case_a),
        ("B: 策略回测", case_b),
        ("C: 技术面分析", case_c),
    ]
    
    for name, result in cases:
        status = "✅ 通过" if not result.get("errors") else "❌ 失败"
        print(f"{name}: {status}")
        if result.get("errors"):
            print(f"  错误: {result['errors']}")
