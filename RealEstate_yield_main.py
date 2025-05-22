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
    "ADV0094AU", "42087", "43724", "41082", "44292", "46228",
    "14291", "43855", "11787", "42209", "44653", "APN0023AU",
    "14258", "43954", "15778", "43805", "44763", "43468",
    "16754", "12113", "12114", "BLK9379AU", "40661", "40375",
    "40377", "12993", "44283", "13148", "15287", "42004",
    "18531", "42082", "12549", "15436", "43102", "14848",
    "40742", "41686", "44598", "44596", "12166", "43028",
    "40518", "11241", "43995", "41565", "41389", "43897",
    "13426", "13427"
]

URL_FUND   = "https://www.morningstar.com.au/investments/security/fund/{}/portfolio"

OUTPUT_XLSX   = "dividend_yields_Realestate.xlsx"
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