from buff.price_scraping import scrape_skins
from screener import *

s = Screener("data/skins.txt", None)
s.read_list()

OUTPUT_FILE = "output/all_skins.csv"

scrape_skins(s.scan_list, OUTPUT_FILE)