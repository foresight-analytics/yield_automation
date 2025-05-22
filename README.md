# Morningstar Fund Dividend Yield Scraper

This Python project scrapes **Dividend Yield** data for managed funds from [Morningstar Australia](https://www.morningstar.com.au) using Selenium and BeautifulSoup, and exports the results to an Excel spreadsheet.
 
---

## 🧾 Requirements

- Python 3.7+  
- Google Chrome (installed)  
- ChromeDriver (managed automatically via `webdriver-manager`)  

### 📦 Install dependencies

```bash
pip install -r requirements.txt

## Main Scripts

This project contains two primary scripts:

- **global_yield_main.py** — scrapes global funds.
- **realestate_yield_main.py** — scrapes real estate funds.

# List of Morningstar FUND IDs to scrape
FUND_IDS = [
    "41388", "42085", "41986", …  # etc.
]

# URL template for each fund
URL_FUND = "https://www.morningstar.com.au/investments/security/fund/{}/portfolio"

# Output filename
OUTPUT_XLSX = "dividend_yields.xlsx"

# Delay between requests (seconds)
DELAY_SECONDS = 1

# Maximum wait time for page load (seconds)
TIMEOUT = 15

