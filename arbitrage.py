from tools import *
from visual import *
from stats import *
import time

FEE = 0.025 # CSF withdrawal fee
THRESHOLD = 30 # make 30 dollars per trade at least
DELTA = 0.01 # how much we increase the max buy order
EPSILON = 10 # for finding similar sales. for example, if someone bought an item for $805 this falls in the range $800 + 10.
DELAY = 2

def ArbitrageStrategy():
    # fetch 50 sales
    listings = get_listings_by_price(250, 1000)

    for i, listing in enumerate(listings):
        try:
            print(f"{i+1}/{len(listings)}")
            # take listing ID and check avg price, compare to max buy orders
            id = listing['id']
            hash_name = listing['item']['market_hash_name']
            icon_url = "https://community.cloudflare.steamstatic.com/economy/image/" + listing['item']['icon_url']

            buy_orders = get_buy_orders(id, hash_name)
            max_buy_order = max([x['price'] for x in buy_orders])

            sales = get_sales(hash_name)
            prices = get_sales_prices(sales)
            # obviously we'll improve this lol
            prices = remove_outliers_iqr(prices)
            base_price = avg(prices)

            expected_profit = (base_price*(1-FEE)-max_buy_order-DELTA)
            n_sales = len([x for x in prices if x <= max_buy_order + EPSILON*100])

            if (expected_profit > THRESHOLD*100) and n_sales > 0:
                send_webhook(hash_name, round(base_price/100, 2), round(expected_profit/100, 2), n_sales, icon_url)
            print(f"{hash_name} | EV: {round(expected_profit/100, 2)}")
            # wait 10 seconds between requests
            time.sleep(DELAY)
        except:
            time.sleep(DELAY)
            continue