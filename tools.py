"""工具层：Agent 可调用的外部能力"""

# ========== 工具 1：计算器 ==========
def calculator(expression: str) -> str:
    """安全计算器：只支持数字和基本运算符"""
    try:
        allowed = set('0123456789+-*/.() ')
        if not all(c in allowed for c in expression):
            return "Error: 非法字符，只允许数字和 +-*/.()"
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"


# ========== 工具 2：搜索（模拟） ==========
def search(query: str) -> str:
    """模拟搜索：从本地知识库中查找信息"""
    knowledge = {
        "贵州茅台": "贵州茅台是中国高端白酒龙头企业，股票代码 600519.SH",
        "MA": "MA（Moving Average，移动平均线）是最基础的技术指标",
        "backtrader": "Backtrader 是 Python 量化回测框架",
    }
    for key, value in knowledge.items():
        if key in query:
            return value
    return f"未找到关于 '{query}' 的信息"


# ========== 工具注册表 ==========
TOOL_REGISTRY = {
    "calculator": calculator,
    "search": search,
}


def get_tool_description() -> str:
    """返回工具描述，供 Agent 的 Prompt 使用"""
    return """可用工具：
1. calculator[expression] - 计算表达式，如 calculator[2+3*4]
2. search[query] - 搜索信息，如 search[贵州茅台]
"""


# ========== 自检：运行此文件可直接测试工具 ==========
if __name__ == "__main__":
    print("=== 工具自检 ===")
    print(f"calculator[2+3*4] = {calculator('2+3*4')}")
    print(f"calculator[100/4+5] = {calculator('100/4+5')}")
    print(f"search[贵州茅台] = {search('贵州茅台')}")
    print(f"search[比特币] = {search('比特币')}")
    print("\n工具描述：")
    print(get_tool_description())
