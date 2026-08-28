class Strategy_300750(bt.Strategy):
    params = (
        ('short_period', 5),
        ('long_period', 20),
    )

    def __init__(self):
        self.short_ma = bt.indicators.SMA(period=self.p.short_period)
        self.long_ma = bt.indicators.SMA(period=self.p.long_period)
        self.crossover = bt.indicators.CrossOver(self.short_ma, self.long_ma)

    def next(self):
        if not self.position:
            if self.crossover > 0:
                self.buy()
        else:
            if self.crossover < 0:
                self.sell()