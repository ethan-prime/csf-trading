from screener import *
from autobid.bidtools import *
from strategy.ArbitrageStrategy import *
from heuristics.harvey import harvey, hamilton

# test
s = Screener("data/test.txt", ArbitrageStrategy, max_price=85000, threshold=0.05, min_price=0, delay=30, min_similar_sales=3, min_vol=7, heuristic=hamilton, write_to_output="output/all_rifles.csv")
s.execute()

#print(add_buy_order(500, 1, item_name="AK-47 | Aquamarine Revenge (Battle-Scarred)"))

#remove_buy_order(807403228542140855)
#print(get_my_buy_orders())
#808267621169498782

#print(get_buy_order_by_id(808267621169498782))
#try_update_buy_order(808274546749736666, 2000)

#autobid()