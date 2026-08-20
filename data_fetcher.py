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

    # ===== 本地数据模式（网络恢复后切回下面的 akshare）=====
    csv_path = f"./data/{stock_code.split('.')[0]}_kline.csv"
    
    if os.path.exists(csv_path):
        print(f"📂 从本地读取: {csv_path}")
        df = pd.read_csv(csv_path)
        df["日期"] = pd.to_datetime(df["日期"])

        # ===== 按日期范围过滤=====
        if start_date:
             start_dt = pd.to_datetime(start_date,format="%Y%m%d")
             df = df[df["日期"] >= start_dt]
        if end_date:
             end_dt = pd.to_datetime(end_date,format="%Y%m%d")
             df = df[df["日期"] <= end_dt]
        # 过滤后如果还有数据，直接返回
        if len(df) > 0:
            return df
        else:
            print("⚠️ 本地缓存无该日期范围数据，尝试重新获取...")
             
    else:
        raise FileNotFoundError(
            f"本地文件不存在: {csv_path}\n"
            f"请先用 akshare 获取数据保存，或手动创建模拟数据文件。"
        )

    #调用 akshare
    #df = ak.stock_zh_a_hist(
        #symbol=stock_code.split(".")[0],
        #period=period,
        #start_date=start_date,
        #end_date=end_date,
        #adjust="qfq"
    #)



    print("原始列名：",df.columns.tolist())
    print("列数：",len(df.columns))

    # 安全做法：只重命名需要的列，多余的不管
    column_map = {
        "日期": "日期",
        "开盘": "开盘",
        "收盘": "收盘",
        "最高": "最高",
        "最低": "最低",
        "成交量": "成交量",
        "成交额": "成交额",
        "振幅": "振幅",
        "涨跌幅": "涨跌幅",
        "涨跌额": "涨跌额",
        "换手率": "换手率"
    }
    #df = df.rename(columns=column_map)
    #return df

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
    


