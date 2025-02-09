from tools import *
from visual import *
from strategy.ArbitrageStrategy import ArbitrageStrategy
from math import ceil

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
    _, _, id, _ = get_info_by_hash_name(item)
    max_buy_order = get_max_buy_order(id, item)
    print(max_buy_order)

    if max_buy_order > my_price:
        if max_buy_order + delta <= threshold:
            remove_buy_order(buy_order_id)
            add_buy_order(bid := max_buy_order + delta, 1, item_name=item)
            print(msg := f"[CSF TRADER] Updated order on {item} from ${round(my_price/100, 2)} to ${round(bid/100, 2)}.")
            send_webhook_msg(msg)
        else:
            remove_buy_order(buy_order_id)
            print(msg := f"[CSF TRADER] Removed order on {item} as threshold was exceeded.")
            send_webhook_msg(msg)

def autobid(threshold: int, delay: int = 20):
    while True:
        buy_orders = get_my_buy_orders()['orders']
        for buy_order in buy_orders:
            id = buy_order['id']
            name = buy_order['market_hash_name']
            eq = ceil(ArbitrageStrategy([name], threshold=threshold, send_alert=False))
            print(eq)
            try_update_buy_order(id, eq)
            time.sleep(0.5)
        time.sleep(delay)