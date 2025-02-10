from buff.price_scraping import scrape_skins
from screener import *

s = Screener("data/kg.txt", None)
s.read_list()

prices = scrape_skins(s.scan_list)
with open("output/kg.csv", 'w', encoding='utf-8') as f:
    f.write("Item, Buff_Price\n")
    for price in prices:
        f.write(f"{price[0]}, {price[1]}\n")