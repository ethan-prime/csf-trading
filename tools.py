from config import *
import requests

# SALES
def get_sales(item_name: str, stickers: bool = False) -> list:
    # https://csfloat.com/api/v1/history/AWP | Dragon Lore (Factory New)/sales
    url = f'{API_URL}/history/{item_name}/sales'

    r = requests.get(url, headers=AUTH_HEADERS)
    sales = r.json()
    if not stickers:
        sales = [x for x in sales if 'stickers' not in x['item']]
    return sales

def get_sales_prices(sales):
    return [x['price'] for x in sales]

def avg(nums):
    return sum(nums)/len(nums)

def to_usd(csf_price):
    return csf_price/100

# BUY ORDERS
def get_buy_orders(listing_id: int, expect: str) -> list:
    url = f'{API_URL}/listings/{listing_id}/buy-orders?limit=20'
    
    r = requests.get(url, headers=COOKIE_HEADERS)
    buy_orders = [x for x in r.json() if x.get('market_hash_name') == expect or x.get('expression') == expect]
    
    # sort by high->low price
    buy_orders.sort(key=lambda x: x['price'], reverse=True)
    return buy_orders

def add_buy_order(max_price: int, quantity: int = 1, item_name: str = None, expression: str = None) -> None:
    payload = {}
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

    r = requests.post(API_URL + "/buy-orders", json=payload, headers=COOKIE_HEADERS)
    if r.status_code == 200:
        print(f"Submitted buy order: {payload}")
    else:
        print("Error submitting buy order...")
        print(r.text)

def remove_buy_order(id: int):
    url = f"{API_URL}/buy-orders/{id}"
    r = requests.delete(url, headers=COOKIE_HEADERS)
    if r.status_code == 200:
        print(f"Successfully removed buy order {id}")
    else:
        print("Error removing buy order")
        print(r.text)

def get_my_buy_orders():
    url = f"{API_URL}/me/buy-orders?page=0&limit=100"
    r = requests.get(url, headers=COOKIE_HEADERS)
    return r.json()

# LISTINGS
def get_listings_by_name(hash_name: str) -> list:
    url = f'{API_URL}/listings?market_hash_name={hash_name}&category=1&sort_by=most_recent' # category = 1 means normal, non-stattrak
    r = requests.get(url, headers=COOKIE_HEADERS)
    return r.json()['data']

def get_listings_by_price(min_price: int, max_price: int) -> list:
    url = f'{API_URL}/listings?min_price={min_price*100}&max_price={max_price*100}&category=1&sort_by=most_recent'
    r = requests.get(url, headers=COOKIE_HEADERS)
    return r.json()['data']