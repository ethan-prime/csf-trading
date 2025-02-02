from config import *
import requests

def get_sales(item_name: str) -> list:
    # https://csfloat.com/api/v1/history/AWP | Dragon Lore (Factory New)/sales
    url = f'{API_URL}/history/{item_name}/sales'
    print(url)

    r = requests.get(url, headers=AUTH_HEADERS)
    return r.json()

def get_sales_prices(sales):
    return [x['price'] for x in sales]

def avg(nums):
    return sum(nums)/len(nums)

def to_usd(csf_price):
    return csf_price/100