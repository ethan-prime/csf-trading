from screener import *
from strategy.ArbitrageStrategy import *

# test
s = Screener("data/golds.txt", AbritrageStrategy, threshold=0, delay=5, write_to_output="1.csv")
s.execute()