from screener import *
from strategy.ArbitrageStrategy import *

# test
s = Screener("data/golds_refined_sorted.txt", AbritrageStrategy, threshold=30, delay=5, write_to_output="output/feb5golds.csv")
s.execute()

#remove_buy_order(807403228542140855)
#print(get_my_buy_orders())