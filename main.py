from tools import *

sales = get_sales("AK-47 | Bloodsport (Field-Tested)")
prices = get_sales_prices(sales)
print(prices)
print(f"Average Price: ${to_usd(avg(prices))}")