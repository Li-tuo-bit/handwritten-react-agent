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

def read_file(filepath:str)->str:
    """读取本地内容文件"""
    try:
        with open(filepath,'r',encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error: 无法读取文件 -{e}"

def write_file(args:str)-> str:
    """写入文件，参数格式：filepath|content"""
    try:
        parts =args.split('|',1)
        if len(parts)!=2:
            return "Error:格式应为 filepath|content"
        filepath,content = parts
        with open(filepath,'w',encoding='utf-8') as f:
            f.write(content)
        return f"文件已写入:{filepath}"
    except Exception as e:
        return f"Error: 写入失败 - {e}"

def get_stock_price(args:str)->str:
    """模拟获取股票价格(Day 3 会替换为真实akshare数据)"""
    import random
    parts = args.split('|')
    stock_code = parts[0]

    base_price= {
        "600519":1700.0,
        "000858":150.0,
        "000333":55.0,
    }.get(stock_code,100.0)

    price=base_price*(1+random.uniform(-0.05,+0.05))
    return f"股票{stock_code} 当前价格:{price:.2f}元"

# ========== 工具注册表 ==========
TOOL_REGISTRY = {
    "calculator": calculator,
    "search": search,
    "read_file":read_file,
    "write_file":write_file,
    "get_stock_price":get_stock_price,
}


def get_tool_description() -> str:
    """返回工具描述，供 Agent 的 Prompt 使用"""
    return """可用工具：
1. calculator[expression] - 计算表达式，如 calculator[2+3*4]
2. search[query] - 搜索信息，如 search[贵州茅台]
3. read_file[filepath] - 读取文件内容，如 read_file[./data.txt]
4. write_file[filepath|content] - 写入文件，如 write_file[./output.txt|Hello]
5. get_stock_price[stock_code|date] - 获取股票价格，如 get_stock_price[600519]
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
