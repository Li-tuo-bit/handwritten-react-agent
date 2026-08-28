"""报告生成工具：汇总数据、分析、回测结果为一份报告"""

import json
from datetime import datetime
import os
import glob

def generate_report(args: str) -> str:
    """
    生成综合分析报告
    参数: stock_code（如 600519）
    """ 
    try:
        stock_code = args.strip()

        report_lines = []
        report_lines.append("="*50)
        report_lines.append(f"量化分析报告: {stock_code}")
        report_lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report_lines.append("="*50)

        # 1.数据摘要 （从analysis CSV 读取）
        data_files = glob.glob(f"./data/{stock_code}_analysis*.csv")
        if data_files:
            import pandas as pd
            df = pd.read_csv(data_files[0])
            latest = df.iloc[-1]
            report_lines.append("\n【数据摘要】")
            report_lines.append(f"  最新日期: {latest.get('日期', 'N/A')}")
            report_lines.append(f"  最新收盘价: {latest.get('收盘', 'N/A')}")
            report_lines.append(f"  MA5: {latest.get('MA5', 'N/A')}")
            report_lines.append(f"  MA20: {latest.get('MA20', 'N/A')}")
            report_lines.append(f"  RSI14: {latest.get('RSI14', 'N/A')}")
        else:
            report_lines.append("\n【数据摘要】未找到数据文件")

        # 2. 交易记录（从 trade_log JSON 读取）
        trade_files = glob.glob(f"./trade_log_{stock_code}.json")
        if trade_files:
            with open(trade_files[0], "r", encoding="utf-8") as f:
                trades = json.load(f)
            report_lines.append(f"\n【交易记录】共 {len(trades)} 笔")
            for t in trades[:5]:
                report_lines.append(f"  {t['date']} {t['action']} 价格:{t['price']:.2f} 数量:{t['size']}")
            if len(trades) > 5:
                report_lines.append(f"  ... 共 {len(trades)} 笔交易")
        else:
            report_lines.append("\n【交易记录】未找到交易日志")

        # 3. 回测结果（从 backtest result JSON 读取）
        result_files = glob.glob(f"./backtest_result_{stock_code}*.json")
        if result_files:
            with open(result_files[0], "r", encoding="utf-8") as f:
                result = json.load(f)
            for key, value in result.items():
                report_lines.append(f"  {key}: {value}")
        else:
            report_lines.append("\n【回测结果】详见 Agent 对话输出")

        report_lines.append("\n" + "=" * 50)

        # 保存报告
        report_text = "\n".join(report_lines)
        report_path = f"./report_{stock_code}_{datetime.now().strftime('%m%d')}.txt"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_text)

        return f"报告已生成: {report_path}\n\n{report_text}"
    except Exception as e:
        return f"Error: 报告生成失败 - {str(e)}"
