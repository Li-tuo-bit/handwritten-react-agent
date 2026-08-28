def calculate_ma(df:pd.DataFrame,window: int =20) -> pd.DataFrame:
    df =df.copy()
    #前 (window-1) 天为 NaN 是正常的：滚动窗口需要足够数据才能计算均值
    df[f"MA{window}"]=df["收盘"].rolling(window=window).mean()
    return df

def calculate_rsi(df:pd.DataFrame,window: int =14) -> pd.DataFrame:
    df =df.copy()

    delta = df["收盘"].diff() # 每天涨跌（今天收盘 - 昨天收盘）
    gain =delta.where(delta>0,0) # 涨的部分，跌的变0
    loss =(-delta).where(delta<0,0) # 跌的部分(取正数)，涨的变0

    #前window 天RSI为NAN是正常的，需要window天的平均涨跌数据才能开始计算
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()

    rs = avg_gain / avg_loss
    df[f"RSI{window}"]=100 - (100 / (1 + rs))

    return df

def calculate_macd(df:pd.DataFrame,fast: int =12,slow: int =26,signal: int =9) -> pd.DataFrame:
    df =df.copy()

    ema_fast = df["收盘"].ewm(span=fast,adjust=False).mean()
    ema_slow = df["收盘"].ewm(span=slow,adjust=False).mean()

    # MACD 前 (slow + signal - 2) 天为 NaN 是正常的：需要足够数据计算 EMA 慢线和信号线
    df["DIF"] = ema_fast - ema_slow
    df["DEA"] =df["DIF"].ewm(span=signal,adjust=False).mean()
    df["MACD"] =2*(df["DIF"]-df["DEA"])

    return df

def add_all_indicators(df:pd.DataFrame) -> pd.DataFrame:
    df =calculate_ma(df,window=5)
    df =calculate_ma(df,window=20)
    df =calculate_ma(df,window=60)
    df =calculate_rsi(df,window=14)
    df =calculate_macd(df)
    return df

if __name__ == "__main__":
    from data_fetcher import get_stock_kline

    df = get_stock_kline("600519",start_date="20240101")
    df = add_all_indicators(df)

    print(df[["日期","收盘","MA5","MA20","MA60","RSI14","DIF","DEA","MACD"]].tail(10))

