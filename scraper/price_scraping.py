import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import logging
import re
from tqdm import tqdm

def format_skin_name(skin_name: str) -> str:
    # Remove special characters and extra spaces, replace '|' with a space
    cleaned = re.sub(r'[^a-zA-Z0-9|]+', ' ', skin_name).strip()
    # Replace '|' with a space
    cleaned = cleaned.replace('|', ' ')
    # Convert to lowercase and replace spaces with hyphens
    return '-'.join(cleaned.lower().split())

def scrape_skins(skins: list, output_file: str) -> list:
    logging.getLogger("selenium").setLevel(logging.CRITICAL)
    chrome_options = Options()
    #chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)

    skins_consolidated = [re.sub(r"\s\([^)]+\)", "", skin) for skin in skins]
    skins_consolidated = list(set(skins_consolidated))
    skins_consolidated = [skin for skin in skins_consolidated if "StatTrak" not in skin]
    skins_consolidated = [format_skin_name(x) for x in skins_consolidated]

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Item_Name, Price\n")

    for skin in tqdm(skins_consolidated):
        try:
            driver.get(f"https://csgoskins.gg/items/{skin}")
            time.sleep(2)
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "/html/body/main/div[2]/div[1]/div[1]/div")))
            item_name = driver.find_element(By.XPATH, "/html/body/main/div[1]/h1").text
            parent = driver.find_element(By.XPATH, "/html/body/main/div[2]/div[1]/div[1]/div")
            elems = parent.find_elements(By.CLASS_NAME, "version-link")
            elems = [x.text for x in elems]
            for elem in elems:
                wear = elem.split("\n")[0]
                price = elem.split("\n")[1]
                if not price[0] == "$":
                    price = 0
                else:
                    price = price[1:]
                item = ""
                if "StatTrak" in wear:
                    wear = wear.replace("StatTrak ", "")
                    if item_name[0] == "★":
                        item = f"★ StatTrak™ {item_name.replace('★ ', '')} ({wear})"
                    else:
                        item = f"StatTrak™ {item_name} ({wear})"
                else:
                    item = f"{item_name} ({wear})"
                with open(output_file, 'a', encoding='utf-8') as f:
                    f.write(f"{item}, {price}\n")
        except:
            print("error doing everything")