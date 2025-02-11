import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import logging
import re
from tqdm import tqdm

def scrape_skins(skins: list, output_file: str) -> list:
    logging.getLogger("selenium").setLevel(logging.CRITICAL)
    driver = webdriver.Chrome()
    driver.get("https://buff.163.com/")
    input("Please login. Hit enter when done ...")
    
    res = set()
    skins_consolidated = [re.sub(r"\s\([^)]+\)", "", skin) for skin in skins]
    skins_consolidated = list(set(skins_consolidated))

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Item_Name, Buff_Price\n")

        for skin in tqdm(skins_consolidated):
            driver.get(f"https://buff.163.com/market/csgo#game=csgo&page_num=1&search={skin}&tab=selling")
            time.sleep(3)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "market-card")))
            try:
                # Get all cards
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "card_csgo")))
                cards = driver.find_elements(By.CLASS_NAME, "card_csgo")      
                
                for card in cards:  # Iterate through each card
                    listings = card.find_elements(By.TAG_NAME, "li")  # Find listings inside each card
                    for listing in listings:
                        if len(listings) > 20:
                            break
                        try:
                            listing_header = listing.find_element(By.TAG_NAME, "h3")
                            item = listing_header.text
                            price_elem = listing.find_elements(By.TAG_NAME, "p")
                            if price_elem is not None and len(price_elem) == 1:
                                price_elem = price_elem[0]
                                price = price_elem.find_element(By.CLASS_NAME, "f_Strong")  # Get price directly
                                price = float(price.text.replace("$ ", ""))
                                if (item, price) not in res:
                                    f.write(f"{item}, {price}\n")
                                    res.add((item, price))
                            else:
                                if (item, 0) not in res:
                                    f.write(f"{item}, 0\n")
                                    res.add((item, 0))
                        except Exception as e:
                            print("Error extracting listing:", e)
            except:
                print("error doing everything")