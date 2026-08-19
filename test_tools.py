"""直接测试工具函数"""

from tools import get_stock_data, analyze_stock

# 测试 1：获取股票数据
print("=== 测试 1：get_stock_data ===")
result = get_stock_data("600519|20240101")
print(result)
print()

# 测试 2：技术分析
print("=== 测试 2：analyze_stock ===")
result2 = analyze_stock("600519")
print(result2)
print()

# 测试 3：写入文件
print("=== 测试 3：write_file ===")
from tools import write_file
result3 = write_file("./analysis_300750.txt|这是一份测试分析报告")
print(result3)
