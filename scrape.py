from buff.price_scraping import scrape_skins
from screener import *

s = Screener("data/skins.txt", None)
s.read_list()

OUTPUT_FILE = "output/all_skins.csv"
STEP = 100

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write("Item, Buff_Price\n")

i = 0
while (i+1)*STEP < len(s.scan_list):
    skins = s.scan_list[i*STEP:(i+1)*STEP]
    prices = scrape_skins(skins)
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        for price in prices:
            f.write(f"{price[0]}, {price[1]}\n")
    i += 1

prices = scrape_skins(s.scan_list[i*STEP:])
with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
    for price in prices:
        f.write(f"{price[0]}, {price[1]}\n")