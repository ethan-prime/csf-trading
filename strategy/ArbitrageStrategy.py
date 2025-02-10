from tools import *
from visual import *
from stats import *
from heuristics.harvey import harvey
import time

FEE = 0.025

def ArbitrageStrategy(items: list, min_price: int = 0, max_price: int = 1000000, threshold: float = 0.03, delta=0.01, epsilon=10, delay=2, min_similar_sales: int = 1, min_vol: int = 3, heuristic=harvey, write_to_output: str = None, send_alert: bool = True):
    """
    a strategy which looks for discrepancies in buy order and market value.
    items: list of strings of items to check against strategys
    threshold: minimum profit margin % (float 0 - 1)
    delta: step increase for buy order price once placed
    epsilon: we search for all sales x where buy_order <= x <= buy_order + epsilon to find if a sale is feasible
    delay: how long we wait between checking listings
    """

    if write_to_output is not None:
        with open(write_to_output, 'w', encoding='utf-8') as f:
            f.write("Item_Name, Max_Buy_Order, Market_Value, EV, Eq_Value, N_Sales, Volume_7_Days, Heuristic\n")

    for i, item in enumerate(items):
        print(f"{i+1}/{len(items)} [~{delay*(len(items)-i-1)}s remaining...]")
        print(f"Searching {item}")
        try:
            base_price, _, id, icon_url = get_info_by_hash_name(item)
            url = f"https://csfloat.com/item/{id}"
            icon_url = f"https://community.cloudflare.steamstatic.com/economy/image/{icon_url}"

            max_buy_order = get_max_buy_order(id, item)
            sales = get_sales(item)
            past_prices = get_sales_prices(sales)
            past_prices = remove_outliers_iqr(past_prices)

            expected_profit = (base_price*(1-FEE)-max_buy_order-(delta*100))
            n_sales = len([x for x in past_prices if x <= max_buy_order + epsilon*100])
            vol = volume(sales, 7)

            ev_percent = expected_profit/max_buy_order
            h_val = heuristic(ev_percent, n_sales, vol)

            eq = base_price*(1-FEE)-base_price*threshold  
            print(f"eq: {eq}")

            if (ev_percent >= threshold) and n_sales >= min_similar_sales and price_accurate(base_price, past_prices, percent=0.05) and vol >= min_vol and min_price <= max_buy_order + delta <= max_price:
                if send_alert:
                    send_webhook(item, round(max_buy_order/100, 2), round(base_price/100, 2), round(expected_profit/100, 2), round(eq/100, 2), n_sales, vol, h_val, url, icon_url)
                
                if write_to_output is not None:
                    with open(write_to_output, 'a', encoding='utf-8') as f:
                        f.write(f"{item}, {max_buy_order}, {base_price}, {expected_profit}, {eq}, {n_sales}, {vol}, {h_val}\n")

            print(f"{item} | EV: {round(expected_profit/100, 2)} | #: {n_sales}")
            time.sleep(delay)
        except Exception as e:
            print(e)
            time.sleep(delay)
            continue

    if len(items) == 1:
        return eq