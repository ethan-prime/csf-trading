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

# LISTINGS
def get_listings_by_name(hash_name: str) -> list:
    url = f'{API_URL}/listings?market_hash_name={hash_name}&category=1' # category = 1 means normal, non-stattrak
    r = requests.get(url, headers=COOKIE_HEADERS)
    return r.json()

def get_listings_by_price(min_price: int, max_price: int) -> list:
    url = f'{API_URL}/listings?min_price={min_price}&max_price={max_price}&category=1'
    r = requests.get(url, headers=COOKIE_HEADERS)
    return r.json()