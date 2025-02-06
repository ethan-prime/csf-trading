from tools import *
from visual import *
import time

FEE = 0.025

def AbritrageStrategy(items: list, threshold=30, delta=0.01, epsilon=10, delay=2, write_to_output=None):
    """
    a strategy which looks for discrepancies in buy order and market value.
    items: list of strings of items to check against strategys
    threshold: minimum $ EV
    delta: step increase for buy order price once placed
    epsilon: we search for all sales x where buy_order <= x <= buy_order + epsilon to find if a sale is feasible
    delay: how long we wait between checking listings
    """

    if write_to_output is not None:
        with open(write_to_output, 'w', encoding='utf-8') as f:
            f.write("Item_Name, Max_Buy_Order, Market_Value, EV, N_Sales\n")

    for i, item in enumerate(items):
        print(f"{i+1}/{len(items)} [~{delay*(len(items)-i-1)}s remaining...]")
        print(f"Searching {item}")
        try:
            base_price, _, id, icon_url = get_info_by_hash_name(item)
            url = f"https://csfloat.com/item/{id}"
            icon_url = f"https://community.cloudflare.steamstatic.com/economy/image/{icon_url}"

            buy_orders = get_buy_orders(id, item)
            max_buy_order = max([x['price'] for x in buy_orders])
            sales = get_sales(item)
            past_prices = get_sales_prices(sales)

            expected_profit = (base_price*(1-FEE)-max_buy_order-(delta*100))
            n_sales = len([x for x in past_prices if x <= max_buy_order + epsilon*100])

            if (expected_profit > threshold*100) and n_sales > 0 and was_recent(sales[0]['sold_at'], 3):
                send_webhook(item, round(max_buy_order/100, 2), round(base_price/100, 2), round(expected_profit/100, 2), n_sales, url, icon_url)
                if write_to_output is not None:
                    with open(write_to_output, 'a', encoding='utf-8') as f:
                        f.write(f"{item}, {max_buy_order}, {base_price}, {expected_profit}, {n_sales}\n")

            print(f"{item} | EV: {round(expected_profit/100, 2)} | #: {n_sales}")
            time.sleep(delay)
        except Exception as e:
            print(e)
            time.sleep(delay)
            continue