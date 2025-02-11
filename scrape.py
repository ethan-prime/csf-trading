from buff.price_scraping import scrape_skins
from screener import *

s = Screener("data/skins.txt", None)
s.read_list()

OUTPUT_FILE = "output/all_skins.csv"
STEP = 1000

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write("Item, Buff_Price\n")

i = 0
while (i+1)*STEP < len(s.scan_list):
    skins = s.scan_list[i*STEP:(i+1)*STEP]
    scrape_skins(skins, OUTPUT_FILE)
    i += 1

scrape_skins(s.scan_list[i*STEP:])