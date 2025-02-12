from scraper.price_scraping import scrape_skins
from screener import *

s = Screener("data/relevant_skins.txt", None)
s.read_list()

OUTPUT_FILE = "output/relevant_skins.csv"

scrape_skins(s.scan_list, OUTPUT_FILE)