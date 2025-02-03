from tools import *

item = "AK-47 | Bloodsport (Field-Tested)"
sales = get_sales(item, stickers=False)
print(sales)
prices = get_sales_prices(sales)
print(prices)
print(f"Average Price: ${to_usd(avg(prices))}")
print(get_buy_orders(805905729717406597, item))