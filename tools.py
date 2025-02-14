from config import *
import requests
from datetime import datetime, timedelta, timezone
from db.database import Database
import time
from tqdm import tqdm

auth_header = {"Authorization": API_KEY_CSF}
cookie_header = {"cookie": COOKIE}
bids = Database("db/bids")
cache = Database("db/cache")
proxies = None

def cooldown():
    ##print("We're being rate limited... switching auth keys...")
    #global i
    #i += 1
    #auth_header["Authorization"] = CYCLE_KEYS[i % len(CYCLE_KEYS)]
    #cookie_header["cookie"] = CYCLE_COOKIES[i % len(CYCLE_COOKIES)]
    #print(auth_header)
    #print(cookie_header)
    print("Sleeping 15m...")
    for i in tqdm(range(15*60)):
        time.sleep(1)

def sum_stickers(stickers: list) -> int:
    s = 0
    for sticker in stickers:
        s += sticker['reference']['price']
    return s

# SALES
def get_sales(item_name: str, sticker_price_threshold: int = 0) -> list:
    # https://csfloat.com/api/v1/history/AWP | Dragon Lore (Factory New)/sales
    url = f'{API_URL}/history/{item_name}/sales'

    r = requests.get(url, headers=auth_header, proxies=proxies)
    # being rate-limited...
    if r.status_code == 429:
        cooldown()
        return get_sales(item_name, sticker_price_threshold)

    sales = r.json()
    sales_refined = []
    for sale in sales:
        if "stickers" not in sale:
            sales_refined.append(sale)
        else:
            if sum_stickers(sale['stickers']) <= sticker_price_threshold:
                sales_refined.append(sale)

    return sales_refined

def get_sales_prices(sales):
    return [x['price'] for x in sales]

def get_base_price(listing_id):
    url = f'{API_URL}/listings/{listing_id}'
    r = requests.get(url, headers=cookie_header, proxies=proxies).json()
    if r.status_code == 429:
        cooldown()
        return get_base_price(listing_id)
    base_price = r['reference']['base_price']
    predicted_price = r['reference']['predicted_price']
    return base_price, predicted_price

def get_info_by_hash_name(hash_name: str):
    url = f'{API_URL}/listings?market_hash_name={hash_name}'
    r = requests.get(url, headers=cookie_header, proxies=proxies)
    if r.status_code == 429:
        cooldown()
        return get_info_by_hash_name(hash_name)
    r = r.json()['data']
    base_price = r[0]['reference']['base_price']
    predicted_price = r[0]['reference']['predicted_price']
    id = r[0]['id']
    icon_url = r[0]['item']['icon_url']
    return base_price, predicted_price, id, icon_url

def avg(nums):
    return sum(nums)/len(nums)

def to_usd(csf_price):
    return csf_price/100

# BUY ORDERS
def get_buy_orders(listing_id: int, expect: str) -> list:
    url = f'{API_URL}/listings/{listing_id}/buy-orders?limit=20'
    
    r = requests.get(url, headers=cookie_header, proxies=proxies)
    if r.status_code == 429:
        cooldown()
        return get_buy_orders(listing_id, expect)
    buy_orders = [x for x in r.json() if x.get('market_hash_name') == expect or x.get('expression') == expect]
    
    # sort by high->low price
    buy_orders.sort(key=lambda x: x['price'], reverse=True)
    return buy_orders

def get_max_buy_order(id: int, item: str):
    return max([x['price'] for x in get_buy_orders(id, item)])

def add_buy_order(max_price: int, quantity: int = 1, item_name: str = None, expression: str = None) -> None:
    payload = {}
    if item_name not in bids.data:
        if expression is not None:
            payload = {
                "expression": expression,
                "max_price": max_price,
                "quantity": quantity,
            }
        elif item_name is not None:
            payload = {
                "market_hash_name": item_name,
                "max_price": max_price,
                "quantity": quantity,
            }
        else:
            print("no item name or expression specified for buy order...")

        r = requests.post(API_URL + "/buy-orders", json=payload, headers=cookie_header)
        if r.status_code == 429:
            cooldown()
            return add_buy_order(max_price, quantity, item_name, expression)
        if r.status_code == 200:
            print(f"Submitted buy order: {payload}")
            bids.add(item_name, {"item": item_name, "bid_price": max_price})
        else:
            print("Error submitting buy order...")
            print(r.text)
    else:
        print(f"Buy order unsuccessful: already bidding on {item_name}.")

def remove_buy_order(id: int, item_name: str):
    url = f"{API_URL}/buy-orders/{id}"
    r = requests.delete(url, headers=cookie_header)
    if r.status_code == 429:
        cooldown()
        return remove_buy_order(id, item_name)
    if r.status_code == 200:
        print(f"Successfully removed buy order {id}")
        bids.clear_section(item_name)
    else:
        print("Error removing buy order")
        print(r.text)

def get_my_buy_orders():
    url = f"{API_URL}/me/buy-orders?page=0&limit=100"
    r = requests.get(url, headers=cookie_header)
    if r.status_code == 429:
        cooldown()
        return get_my_buy_orders()
    return r.json()

# LISTINGS
def get_listings_by_name(hash_name: str) -> list:
    url = f'{API_URL}/listings?market_hash_name={hash_name}&category=1&sort_by=most_recent' # category = 1 means normal, non-stattrak
    r = requests.get(url, headers=cookie_header, proxies=proxies)
    if r.status_code == 429:
        cooldown()
        return get_listings_by_name(hash_name)
    return r.json()['data']

def get_listings_by_price(min_price: int, max_price: int) -> list:
    url = f'{API_URL}/listings?min_price={min_price*100}&max_price={max_price*100}&category=1&sort_by=most_recent'
    r = requests.get(url, headers=cookie_header, proxies=proxies)
    if r.status_code == 429:
        cooldown()
        return get_listings_by_price(min_price, max_price)
    return r.json()['data']

def was_recent(date_str, n_days):
    # Define the format of the input date
    date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    
    # Convert the string to a datetime object
    date_obj = datetime.strptime(date_str, date_format)
    date_obj = date_obj.replace(tzinfo=timezone.utc)
    
    # Get the current time
    current_time = datetime.now(timezone.utc)
    
    # Calculate the time difference
    time_difference = current_time - date_obj
    
    # Return True if the time difference is less than or equal to 24 hours, else False
    return time_difference <= timedelta(days=n_days)

# how many sales were made in the past n_days
def volume(sales, n_days):
    return len(list(filter(lambda x: was_recent(x['sold_at'], n_days=n_days), sales)))

# returns whether we have sold >= n_sales in the past n_days
def has_volume(sales, n_sales, n_days):
    return volume(sales, n_days) >= n_sales

# calculates whether or not the predicted price is within a percentage of the average sale price.
def price_accurate(price, sale_prices, percent=0.03, verbose=False):
    average = avg(sale_prices)
    if average - price >= 0:
        return True
    if verbose:
        print(f"avg: {average} | csf price: {price} | eq: {percent*price}")
    return (price-average) <= percent*price

def parse_args(s: str) -> dict:
    args = s.split(" ")
    parsed = {}
    for arg in args:
        a = arg.split("=")
        parsed[a[0]] = a[1]
    return parsed