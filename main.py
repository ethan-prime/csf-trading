from screener import *
from autobid.bidtools import *
from strategy.ArbitrageStrategy import *

# test
#s = Screener("data/test.txt", ArbitrageStrategy, max_price=100000, threshold=10, delay=5, write_to_output="output/3.csv")
#s.execute()

#print(add_buy_order(500, 1, item_name="AK-47 | Aquamarine Revenge (Battle-Scarred)"))

#remove_buy_order(807403228542140855)
#print(get_my_buy_orders())
#808267621169498782

#print(get_buy_order_by_id(808267621169498782))
#try_update_buy_order(808274546749736666, 2000)

autobid(0)