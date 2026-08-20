import akshare as ak
import os

def fetch_and_save(stock_code:str,start_date:str ="20230101",end_date:str ="20241231"):
    """从akshare获取数据并保存到本地CSV"""

    print(f"🔄 正在获取 {stock_code} 数据 ({start_date} ~ {end_date})...")

    df = ak.stock_zh_a_hist(
        symbol=stock_code,
        period="daily",
        start_date=start_date,
        end_date=end_date,
        adjust="qfq"
    )

    # 确保目录存在
    os.makedirs("./data",exist_ok=True)

    # 保存
    filepath = f"./data/{stock_code}_kline.csv"
    df.to_csv(filepath,index=False,encoding="utf-8-sig")

    print(f"✅ 已保存{len(df)}条数据到 {filepath}")
    return df

if __name__ == "__main__":
    fetch_and_save("600519") # 贵州茅台
    fetch_and_save("300750") # 宁德时代