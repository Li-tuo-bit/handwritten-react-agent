"""回测工具：封装 backtrader，供 Agent 调用"""

import json
from backtest_dual_ma import run_backtest

def run_strategy_backtest(args: str) -> str:
    """
    运行双均线策略回测
    参数格式: stock_code|start_date|end_date（后两个可选）
    示例: 600519|20230101|20241231
    """
    try:
        parts = args.split("|")
        stock_code = parts[0]
        start_date = parts[1] if len(parts) > 1 else "20230101"
        end_date = parts[2] if len(parts) > 2 else "20241231"

        result = run_backtest(stock_code,start_date,end_date)

        # 返回精简版结果
        summary = {
            "股票代码": stock_code,
            "回测区间": f"{start_date} ~ {end_date}",
            "最终资金": f"{result['final_value']:,.2f}",
            "总收益率": f"{result['total_return']:.2f}%",
            "夏普比率": result['sharpe_ratio'],
            "最大回撤": f"{result['max_drawdown']:.2f}%",
            "交易次数": result['trade_count'],
        }

        # 保存回测结果到文件，供报告生成器读取
        result_path = f"./backtest_result_{stock_code}.json"
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        return json.dumps(summary,ensure_ascii=False,indent=2)

    except Exception as e:
        return f"Error: 回测执行失败 - {str(e)}"

def compare_strategies(args: str) -> str:
    """
    对比不同参数的双均线策略
    参数格式: stock_code|short1,long1|short2,long2
    示例: 600519|5,20|10,60
    """
    try:
        parts = args.split("|")
        stock_code = parts[0]

        results = []
        for param_str in parts[1:]:
            short,long = map(int,param_str.split(","))
            # 这里需要修改 run_backtest 支持传入参数，作为扩展任务
            result = run_backtest(stock_code,"20230101","20241231",short_window=short, long_window=long)
            results.append({
                "参数": f"MA{short}/MA{long}",
                "收益率": f"{result['total_return']:.2f}%",
                "夏普": result['sharpe_ratio'],
                "回撤": f"{result['max_drawdown']:.2f}%",
            })

        return json.dumps(results,ensure_ascii=False,indent=2)

    except Exception as e:
        return f"Error: 对比执行失败 - {str(e)}"
