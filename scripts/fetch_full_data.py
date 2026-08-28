"""获取完整的股票历史数据并保存到本地"""

import os
# 强制禁用代理
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
os.environ["http_proxy"] = ""
os.environ["https_proxy"] = ""

import akshare as ak
import time

def fetch_and_save(stock_code: str, start_date: str = "20230101", end_date: str = "20241231"):
    print(f"🔄 正在获取 {stock_code} 数据 ({start_date} ~ {end_date})...")
    
    for retry in range(3):
        try:
            df = ak.stock_zh_a_hist(
                symbol=stock_code,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust="qfq",
                timeout=30  # 延长超时
            )
            break
        except Exception as e:
            print(f"⚠️ 第 {retry+1} 次尝试失败: {e}")
            if retry < 2:
                time.sleep(2)
            else:
                raise
    
    os.makedirs("./data", exist_ok=True)
    filepath = f"./data/{stock_code}_kline.csv"
    df.to_csv(filepath, index=False, encoding="utf-8-sig")
    print(f"✅ 已保存 {len(df)} 条数据到 {filepath}")
    return df

if __name__ == "__main__":
    fetch_and_save("600519")
    fetch_and_save("300750")