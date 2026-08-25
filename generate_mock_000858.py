import pandas as pd
import numpy as np
import os

# 生成 2024年 240 个交易日的模拟数据
dates = pd.date_range('2024-01-02', '2024-12-31', freq='B')[:240]
np.random.seed(858)

base = 150.0
prices = [base]
for i in range(1, 240):
    prices.append(prices[-1] * (1 + np.random.normal(0, 0.015)))

df = pd.DataFrame({
    '日期': dates,
    '开盘': [p * (1 + np.random.normal(0, 0.005)) for p in prices],
    '收盘': prices,
    '最高': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
    '最低': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
    '成交量': np.random.randint(50000, 200000, 240),
    '成交额': np.random.randint(5000000, 20000000, 240),
    '振幅': np.random.uniform(1, 5, 240),
    '涨跌幅': np.random.uniform(-3, 3, 240),
    '涨跌额': np.random.uniform(-5, 5, 240),
    '换手率': np.random.uniform(0.5, 3, 240),
})

os.makedirs('./data', exist_ok=True)
df.to_csv('./data/000858_kline.csv', index=False, encoding='utf-8-sig')
print('✅ 000858 模拟数据已生成: ./data/000858_kline.csv')