import matplotlib.pyplot as plt
import pandas as pd
from data_fetcher import get_stock_kline
from indicators import add_all_indicators

def plot_stock_analysis(stock_code:str ,start_date: str ="20240101") :
    """
    绘制股票 K 线图+技术指标，用于验证计算正确性
    """

    #获取数据
    df = get_stock_kline(stock_code,start_date=start_date)
    df = add_all_indicators(df)

    #取最近60天展示
    df = df.tail(60).reset_index(drop=True)

    fig,axes = plt.subplots(3,1,figsize=(12,10),sharex=True)

    # 子图 1：K 线 + MA
    ax1 = axes[0]
    ax1.plot(df.index,df["收盘"],label="收盘",color="black",linewidth=1)
    ax1.plot(df.index,df["MA5"],label="MA5",color="orange",alpha=0.7)
    ax1.plot(df.index,df["MA20"],label="MA20",color="blue",alpha=0.7)
    ax1.plot(df.index,df["MA60"],label="MA60",color="red",alpha=0.7)
    ax1.set_title(f"{stock_code}K线 + 移动平均线")
    ax1.legend()
    ax1.grid(True,alpha=0.3)

    #子图 2 ：RSI
    ax2 = axes[1]
    ax2.plot(df.index,df["RSI14"],label="RSI14",color="purple")
    ax2.axhline(y=70,color="red",linestyle="--",alpha=0.5,label="超买（70）")
    ax2.axhline(y=30,color="green",linestyle="--",alpha=0.5,label="超卖（30）")
    ax2.set_title("RSI指标")
    ax2.legend()
    ax2.grid(True,alpha=0.3)

    #子图 3 ：MACD
    ax3 = axes[2]
    ax3.plot(df.index,df["DIF"],label="DIF",color="blue")
    ax3.plot(df.index,df["DEA"],label="DEA",color="orange")
    colors = ["red" if v >= 0 else "green" for v in df["MACD"]]
    ax3.bar(df.index,df["MACD"],label="MACD",color=colors,alpha=0.5)
    ax3.set_title("MACD指标")
    ax3.legend()
    ax3.grid(True,alpha=0.3)

    plt.tight_layout()
    plt.savefig(f"./analysis_{stock_code}.png",dpi=150)
    print(f"✅ 图表已保存：./analysis_{stock_code}.png")
    plt.close()

if __name__ == "__main__":
    plot_stock_analysis("600519")
    plot_stock_analysis("300750")



