from tools import *
from visual import *
from strategy.ArbitrageStrategy import ArbitrageStrategy
from math import ceil
from db.database import Database
from datetime import datetime

bids = Database("db/bids")

def get_time_str() -> str:
    now = datetime.now()
    return now.strftime("%m/%d %I:%M %p")

def get_buy_order_by_id(buy_order_id: int):
    orders = get_my_buy_orders()
    for order in orders['orders']:
        if order['id'] == buy_order_id:
            return order

# if we have the highest buy order, do nothing
# else, update by delta.
# buy_order_id: int
# buy_order_id: cents increase
# threshold: max you will bid up to, else an outbid will remove your order...
def try_update_buy_order(buy_order_id: int, threshold: int, delta: int=1):
    print(f"Attempting to update buy order {buy_order_id}...")
    buy_order = get_buy_order_by_id(buy_order_id)
    if buy_order is None:
        print(f"Buy order {buy_order_id} no longer exists...")
        return
    my_price = buy_order['price']
    item = buy_order['market_hash_name']
    base_price, predicted_price, id, icon_url = get_info_by_hash_name(item)
    max_buy_order = get_max_buy_order(id, item)
    print(max_buy_order)

    print(my_price, threshold)

    if my_price > threshold:
        remove_buy_order(buy_order_id, item)
        print(msg := f"Removed order on {item} as threshold was exceeded.")
        send_webhook_msg(msg)
        return

    if max_buy_order > my_price:
        if max_buy_order + delta <= threshold:
            remove_buy_order(buy_order_id, item)
            add_buy_order(bid := max_buy_order + delta, 1, item_name=item)
            print(msg := f"Updated order on {item} from ${round(my_price/100, 2)} to ${round(bid/100, 2)}.")
            send_webhook_msg(msg)
        else:
            remove_buy_order(buy_order_id, item)
            print(msg := f"Removed order on {item} as threshold was exceeded.")
            send_webhook_msg(msg)

def autobid(threshold: float, delay: int = 20):
    while True:
            buy_orders = get_my_buy_orders()['orders']
            for buy_order in buy_orders:
                try:
                    id = buy_order['id']
                    name = buy_order['market_hash_name']
                    if name in cache.data:
                        eq = cache.get(name)
                        print("bid data was cached")
                    else:
                        item, base_price, eq, icon_url = ArbitrageStrategy([name], threshold=threshold, send_alert=False)
                        cache.add(name, eq)
                    print(eq)
                    try_update_buy_order(id, eq)
                    time.sleep(delay)
                except Exception as e:
                    print(e)
                    continue