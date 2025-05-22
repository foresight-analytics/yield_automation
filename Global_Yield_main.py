import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

# --- CONFIGURATION ---

FUND_IDS  = [
    "41388","42085","41986","44639","43898","43377",
    "0000","40573","40572","41432","16334","15003","42208",
    "16750","16749","44206","14651","19109","19316",
    "19319","15838","19480","46939","46511","46062",
    "13457","40374","13287","40378","41544","15700",
    "43992","41700","40949","47111","44284","44682",
    "46587","46642","18408","44123","16241","16242"
]

URL_FUND   = "https://www.morningstar.com.au/investments/security/fund/{}/portfolio"

OUTPUT_XLSX   = "dividend_yields.xlsx"
DELAY_SECONDS = 1
TIMEOUT       = 15

def setup_driver():
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no‑sandbox")
    opts.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/113.0.0.0 Safari/537.36"
    )
    service = ChromeService(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=opts)

def fetch_fund_info(driver, url):
    driver.get(url)
    # Wait for the measures table
    try:
        WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.sal-measures__value-table table"))
        )
    except Exception:
        return None, None, "Timeout loading page"

    soup = BeautifulSoup(driver.page_source, "html.parser")

    # 1) Parse the page title to get the fund name
    title_tag = soup.find("title")
    if title_tag:
        full_title = title_tag.get_text(strip=True)
        # Remove suffix "Overview | Morningstar"
        name_part = full_title.split("Overview")[0].strip()
        # Take first 4 words for a short name
        short_name = " ".join(name_part.split()[:4])
    else:
        short_name = None

    # 2) Scrape Dividend Yield
    table = soup.select_one("div.sal-measures__value-table table")
    if not table:
        return short_name, None, "Table not found"

    raw_yield = None
    for tr in table.select("tbody tr"):
        th_txt = tr.find("th").get_text(strip=True)
        if "Dividend Yield" in th_txt:
            cell = tr.find("td")
            if cell:
                raw_yield = cell.get_text(strip=True)
            break

    if raw_yield is None:
        return short_name, None, "Dividend Yield row missing"
    return short_name, raw_yield, None

def parse_yield(raw_text):
    try:
        return float(raw_text.strip().replace("%", ""))
    except:
        return None

def main():
    driver = setup_driver()
    records = []

    # Scrape tickers
    

    # Scrape fund IDs
    for fid in FUND_IDS:
        url = URL_FUND.format(fid)
        name, raw, err = fetch_fund_info(driver, url)
        val = parse_yield(raw) if raw else None
        records.append({
            "fund_name":   name or fid,
            "FUNDID":    fid,
            "raw_yield":   raw,
            "yield_%":     val,
            "error":       err or ""
        })
        print(f"[FUNDID] {name or fid} → {val or 'ERROR'}")

    driver.quit()

    # Save to Excel
    df = pd.DataFrame(records)
    df["yield_%"] = pd.to_numeric(df["yield_%"], errors="coerce")
    df.to_excel(OUTPUT_XLSX, index=False)
    print(f"\nSaved results to {OUTPUT_XLSX}")

if __name__ == "__main__":
    main()