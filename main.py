from screener import *
from strategy.ArbitrageStrategy import *

s = Screener("data/golds.txt", AbritrageStrategy, delay=5)
s.execute()