"""
双均线策略回测
规则：
- MA5 上穿 MA20（金叉）→ 买入
- MA5 下穿 MA20（死叉）→ 卖出
"""
import backtrader as bt
import pandas as pd
from datetime import datetime

# ========== 1. 定义策略 ==========
class DualMaStrategy(bt.Strategy):
    """双均线策略"""
    
    # 策略参数（可外部传入）
    params = (
        ('short_window',5), #短期均线
        ('long_window',20), #长期均线
    )

    def __init__(self):
        # 初始化指标
        # 收盘价的引用
        self.dataclose =self.datas[0].close

        # 计算两条移动平均线
        self.ma_short = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.short_window
        )
        self.ma_long = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.long_window
        )

        # 金叉/死叉信号（crossover > 0 表示金叉，< 0 表示死叉）
        self.crossover = bt.indicators.CrossOver(
            self.ma_short, self.ma_long
        )

        #记录订单，防止重复下单
        self.order = None

        #记录交易日志
        self.trade_log = []

    def log(self,txt,dt=None):
        """打印日志"""
        dt = dt or self.datas[0].datetime.datetime(0)
        print(f'{dt.isoformat()} {txt}')

    def notify_order(self,order):
        """订单状态回调"""
        if order.status in [order.Submitted,order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f"【买入执行】价格: {order.executed.price:.2f}, 数量: {order.executed.size}")
            else:
                self.log(f"【卖出执行】价格: {order.executed.price:.2f}, 数量: {order.executed.size}")
            
        self.order = None

    def next(self):
        """每个交易日调用一次，核心交易逻辑"""

        #如果有未完成的订单，等待
        if self.order:
            return

        #当前持仓量
        current_position = self.position.size

        if self.crossover > 0 and current_position == 0:
            self.log(f'【金叉信号】MA{self.params.short_window}({self.ma_short[0]:.2f}) 上穿 MA{self.params.long_window}({self.ma_long[0]:.2f})')
            # 全仓买入（留 5% 现金）
            size = int(self.broker.getcash()/self.dataclose[0]*0.95)
            if size > 0:
                self.order = self.buy(size=size)
                self.trade_log.append({
                    'date': self.datas[0].datetime.datetime(0).isoformat(),
                    'action': 'buy',
                    'price': self.dataclose[0],
                    'size': size,
                })

            # 死叉信号：MA5 下穿 MA20，且有持仓 → 卖出
        elif self.crossover < 0 and current_position > 0:
            self.log(f'【死叉信号】MA{self.params.short_window}({self.ma_short[0]:.2f}) 下穿 MA{self.params.long_window}({self.ma_long[0]:.2f})')
            # 清仓卖出
            self.order = self.sell(size=current_position)
            self.trade_log.append({
                'date': self.datas[0].datetime.datetime(0).isoformat(),
                'action': 'sell',
                'price': self.dataclose[0],
                'size': current_position,
            })

# ========== 2. 准备数据 ==========
def prepare_data(stock_code:str,start_date:str,end_date:str)->pd.DataFrame:
    """从本地 CSV 获取数据并转换为 backtrader 格式"""
    from data_fetcher import get_stock_kline

    df = get_stock_kline(stock_code,start_date=start_date,end_date=end_date)

    # backtrader 需要的列名：datetime, open, high, low, close, volume, openinterest
    df = df.rename(columns={
        "开盘": "open",
        "收盘": "close",
        "最高": "high",
        "最低": "low",
        "成交量": "volume",
    })

    #添加 openinterest 列（A股没有，填 0）
    df["openinterest"] = 0

    # 确保日期是索引
    if "日期" in df.columns:
        df['日期'] = pd.to_datetime(df['日期'])
        df.set_index('日期',inplace=True)

    return df

# ========== 3. 运行回测 ==========
def run_backtest(stock_code: str ="600519",
                 start_date: str ="20230101",
                 end_date: str ="20241231",
                 initial_cash: float =100000.0,
                 commission: float = 0.00025):
    """
    运行回测
    
    Args:
        stock_code: 股票代码
        start_date: 回测开始日期
        end_date: 回测结束日期
        initial_cash: 初始资金
        commission: 手续费（默认万 2.5）
    """

    # 创建 Cerebro 引擎
    cerebro = bt.Cerebro()
 
    # 添加策略
    cerebro.addstrategy(DualMaStrategy)

    # 获取数据
    df = prepare_data(stock_code,start_date,end_date)

    # 创建 Data Feed
    data = bt.feeds.PandasData(
        dataname=df,
        datetime=None,
        open="open",
        high="high",
        low="low",
        close="close",
        volume="volume",
        openinterest="openinterest",
    )
    cerebro.adddata(data)

    # 设置初始资金
    cerebro.broker.setcash(initial_cash)

    # 设置手续费
    cerebro.broker.setcommission(commission=commission)

    # 添加分析指标
    cerebro.addanalyzer(bt.analyzers.SharpeRatio,_name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown,_name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns,_name='returns')

    # 打印回测前信息
    print(f"\n{'='*50}")
    print(f"回测标的：{stock_code}")
    print(f"回测区间：{start_date} ~ {end_date}")
    print(f"初始资金：{initial_cash:,.2f}")
    print(f"手续费：{commission*100:,.3f}")
    print(f"{'='*50}\n")

    # 运行回测
    results = cerebro.run()
    strat = results[0]  

    # 打印回测结果
    print(f"\n{'='*50}")
    print(f"最终资金:{cerebro.broker.getvalue():.2f}")
    print(f"总收益率：{(cerebro.broker.getvalue()/initial_cash-1)*100:.2f}%")

    # 分析指标
    sharpe = strat.analyzers.sharpe.get_analysis()
    drawdown = strat.analyzers.drawdown.get_analysis()
    returns = strat.analyzers.returns.get_analysis()

    print(f"夏普比率：{sharpe.get('sharperatio','N/A')}")
    print(f"最大回撤：{drawdown.max.drawdown:.2f}%")
    print(f"年化收益率：{returns.get('rnorm100','N/A')}")
    print(f"{'='*50}\n")

    # 保存交易日志
    import json
    with open(f"./trade_log_{stock_code}.json","w",encoding="utf-8") as f:
        json.dump(strat.trade_log,f,ensure_ascii=False,indent=2)
    print(f"✅ 交易日志已保存: ./trade_log_{stock_code}.json")

    # 绘制图表
    cerebro.plot(style="candlestick",barup='red',bardown='green')

    return {
        "final_value": cerebro.broker.getvalue(),
        "total_return": (cerebro.broker.getvalue()/initial_cash-1)*100,
        "sharpe_ratio": sharpe.get('sharperatio'),
        "max_drawdown": drawdown.max.drawdown,
        "trade_count": len(strat.trade_log),
    }

# ========== 入口 ==========
if __name__ == "__main__":
    result = run_backtest("600519","20230101","20241231")
    print(f"\n回测摘要:{result}")
