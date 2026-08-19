"""工具层：Agent 可调用的外部能力"""
from data_fetcher import get_stock_kline,save_stock_data
from indicators import add_all_indicators
import json
import pandas as pd



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

def get_stock_data(args:str)->str:
    """
    获取股票历史数据并计算技术指标
    参数格式：stock_code|start_date|end_date(后两个可选)
    示例:600519|20240101|20241231
    """
    try:
        parts = args.split('|')
        stock_code = parts[0]
        start_date = parts[1] if len(parts)> 1 else None
        end_date = parts[2] if len(parts)> 2 else None

        #获取数据
        df = get_stock_kline(stock_code,start_date=start_date,end_date=end_date)
        #计算指标
        df = add_all_indicators(df)
        #保存到文件
        filepath = save_stock_data(df,f"{stock_code}_analysis")
        #返回摘要信息
        latest = df.iloc[-1]
        summary ={
            "股票代码": stock_code,
            "数据条数": len(df),
            "最新日期": str(latest["日期"]),
            "最新收盘价": round(latest["收盘"], 2),
            "MA5": round(latest["MA5"], 2) if not pd.isna(latest["MA5"]) else None,
            "MA20": round(latest["MA20"], 2) if not pd.isna(latest["MA20"]) else None,
            "RSI14": round(latest["RSI14"], 2) if not pd.isna(latest["RSI14"]) else None,
            "MACD": round(latest["MACD"], 4) if not pd.isna(latest["MACD"]) else None,
            "数据文件": filepath,
        }
        return json.dumps(summary,ensure_ascii=False,indent=2)
    except Exception as e:
        return f"Error: 获取股票数据失败 - {str(e)}"

def analyze_stock(args: str)->str:
    """
    简单的股票技术分析
    参数:stock_code
    返回:基于MA和RSI的简单判断
    """
    try:
        df=get_stock_kline(args)
        df = add_all_indicators(df)

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        signals =[]

        # MA 金叉/死叉判断
        if latest["MA5"]>latest["MA20"] and prev["MA5"]<=prev["MA20"]:
            signals.append("MA5 上穿 MA20，出现金叉信号")
        elif latest["MA5"]<latest["MA20"] and prev["MA5"]>=prev["MA20"]:
            signals.append("MA5 下穿 MA20，出现死叉信号")
        elif latest["MA5"]>latest["MA20"]:
            signals.append("MA5 在 MA20 上方，短期趋势向上")
        else:
            signals.append("MA5 在 MA20 下方，短期趋势向下")

        # RSI判断
        rsi = latest["RSI14"]
        if rsi>70:
            signals.append(f"RSI={rsi:.1f} > 70，可能超买")
        elif rsi<30:
            signals.append(f"RSI={rsi:.1f} < 30，可能超卖")
        else:
            signals.append(f"RSI={rsi:.1f}，处于中性区间")

        # MACD判断
        if latest["MACD"]>0 and prev["MACD"]<=0:
            signals.append("MACD 柱由负转正，可能出现买入信号")
        elif latest["MACD"]<0 and prev["MACD"]>=0:
            signals.append("MACD 柱由正转负，可能出现卖出信号")

        return "\n".join(signals)
    except Exception as e:
        return f"Error: 分析股票失败 - {str(e)}"

# ========== 工具注册表 ==========
TOOL_REGISTRY = {
    "calculator": calculator,
    "search": search,
    "read_file":read_file,
    "write_file":write_file,
    "get_stock_data":get_stock_data,
    "analyze_stock":analyze_stock,
}

def get_tool_description() -> str:
    """返回工具描述，供 Agent 的 Prompt 使用"""
    return """可用工具：
1. calculator[expression] - 计算表达式，如 calculator[2+3*4]
2. search[query] - 搜索信息，如 search[贵州茅台]
3. read_file[filepath] - 读取文件内容，如 read_file[./data.txt]
4. write_file[filepath|content] - 写入文件，如 write_file[./output.txt|Hello]
5. get_stock_data[stock_code|start_date|end_date] - 获取股票数据+技术指标
6. analyze_stock[stock_code] - 股票技术分析
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
