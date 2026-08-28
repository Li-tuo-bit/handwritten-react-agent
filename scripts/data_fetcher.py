import akshare as ak
import os
import pandas as pd
from datetime import datetime, timedelta
import time


def get_stock_kline(stock_code: str,period:str="daily",start_date:str=None,end_date:str=None) -> pd.DataFrame:
    """
    获取股票历史 K 线数据

    Args:
        stock_code: 股票代码，如 "600519"（自动补全 .SH/.SZ）
        period: 周期，daily/weekly/monthly
        start_date: 开始日期，格式 YYYYMMDD，默认一年前
        end_date: 结束日期，默认今天

    Returns:
        DataFrame，列：日期, 开盘, 收盘, 最高, 最低, 成交量
    """
    # 自动补全市场后缀
    if stock_code.startswith("6"):
            stock_code += ".SH"
    elif  stock_code.startswith("0") or stock_code.startswith("3"):
            stock_code += ".SZ"

    # 设置默认日期范围
    if end_date is None:
            end_date = datetime.now().strftime("%Y%m%d")
    if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")

        # ===== 本地缓存优先 =====
    csv_path = f"./data/{stock_code.split('.')[0]}_kline.csv"
    
    if os.path.exists(csv_path):
        print(f"📂 从本地读取: {csv_path}")
        df = pd.read_csv(csv_path)
        df["日期"] = pd.to_datetime(df["日期"])
        return df
    
    # ✅ 本地没有，用 akshare 获取
    print(f"🌐 从 akshare 获取: {stock_code}")
    df = ak.stock_zh_a_hist(
        symbol=stock_code.split(".")[0],
        period=period,
        start_date=start_date,
        end_date=end_date,
        adjust="qfq"
    )
    
    # 标准化列名
    df.columns = ["日期", "开盘", "收盘", "最高", "最低", "成交量", "成交额", 
                  "振幅", "涨跌幅", "涨跌额", "换手率"]
    
    # 保存到本地（下次直接用缓存）
    save_stock_data(df, stock_code.split('.')[0])
    
    return df

def save_stock_data(df:pd.DataFrame,stock_code:str,filepath:str=None):
    """
    保存股票数据到CSV文件
    """
    if filepath is None:
        filepath = f"./data/{stock_code}_kline.csv"

    import os
    os.makedirs(os.path.dirname(filepath),exist_ok=True)

    df.to_csv(filepath,index=False,encoding="utf-8-sig")
    print(f"✅ 数据已保存: {filepath}")
    return filepath

def load_stock_data(filepath :str )-> pd.DataFrame:
    """从CSV加载股票数据"""
    df = pd.read_csv(filepath)
    df["日期"] = pd.to_datetime(df["日期"])
    return df

# ========== 测试 ==========
if __name__ == "__main__":
    df =get_stock_kline("600519",start_date="20240101")
    print(f"获取到{len(df)}条数据")
    print(df.head())

     # 保存测试
    save_stock_data(df,"600519")
    


