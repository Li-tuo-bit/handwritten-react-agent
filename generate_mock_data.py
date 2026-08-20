"""生成模拟股票数据，用于回测"""

import pandas as pd
import numpy as np
import os

def generate_stock_data(stock_code: str, days: int = 500):
    """
    生成模拟股票数据
    包含：上涨→震荡→下跌→反弹，确保 MA5 和 MA20 有多次交叉
    """
    np.random.seed(42 if stock_code == "600519" else 24)
    
    # 生成 500 个交易日（约 2 年）
    dates = pd.date_range(start="2023-01-01", periods=days, freq="B")
    
    # 构造有趋势的价格（确保产生金叉/死叉）
    # 阶段 1: 缓慢上涨
    t1 = np.linspace(1000, 1200, 100)
    # 阶段 2: 快速上涨
    t2 = np.linspace(1200, 1600, 80)
    # 阶段 3: 下跌
    t3 = np.linspace(1600, 1300, 100)
    # 阶段 4: 震荡
    t4 = 1400 + np.sin(np.linspace(0, 8*np.pi, 120)) * 100
    # 阶段 5: 反弹
    t5 = np.linspace(1350, 1700, 100)
    
    trend = np.concatenate([t1, t2, t3, t4, t5])
    
    # 添加随机波动
    noise = np.cumsum(np.random.randn(days) * 15)
    close = trend + noise
    
    # 确保价格为正
    close = np.maximum(close, 50)
    
    # 生成 OHLCV
    df = pd.DataFrame({
        "日期": dates,
        "开盘": np.round(close * (1 + np.random.randn(days) * 0.005), 2),
        "收盘": np.round(close, 2),
        "最高": np.round(close * (1 + np.abs(np.random.randn(days)) * 0.015), 2),
        "最低": np.round(close * (1 - np.abs(np.random.randn(days)) * 0.015), 2),
        "成交量": np.random.randint(50000, 500000, days),
        "成交额": np.round(np.random.uniform(500000000, 5000000000, days), 2),
        "振幅": np.round(np.random.rand(days) * 5, 2),
        "涨跌幅": np.round(np.random.randn(days) * 2, 2),
        "涨跌额": np.round(np.random.randn(days) * 10, 2),
        "换手率": np.round(np.random.rand(days) * 2, 2),
    })
    
    # 确保最高 >= 收盘 >= 最低
    df["最高"] = np.maximum(df["最高"], df["收盘"])
    df["最低"] = np.minimum(df["最低"], df["收盘"])
    df["开盘"] = np.clip(df["开盘"], df["最低"], df["最高"])
    
    # 保存
    os.makedirs("./data", exist_ok=True)
    filepath = f"./data/{stock_code}_kline.csv"
    df.to_csv(filepath, index=False, encoding="utf-8-sig")
    
    print(f"✅ 已生成 {stock_code} 模拟数据: {len(df)} 条，保存到 {filepath}")
    print(f"   价格区间: {df['收盘'].min():.2f} ~ {df['收盘'].max():.2f}")
    return df

if __name__ == "__main__":
    generate_stock_data("600519")
    generate_stock_data("300750")