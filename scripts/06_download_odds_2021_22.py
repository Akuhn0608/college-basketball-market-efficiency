from pathlib import Path

import pandas as pd
import requests


URL = (
    "https://www.sportsbookreviewsonline.com/"
    "scoresoddsarchives/ncaa-basketball-2021-22/"
)

OUTPUT_DIR = Path("data/raw/odds")
OUTPUT_PATH = OUTPUT_DIR / "ncaab_odds_2021_22.csv"

# Some websites reject requests that do not look like they came from a browser.
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Chrome/148.0 Safari/537.36"
    )
}

response = requests.get(
    URL,
    headers=headers,
    timeout=30
)

response.raise_for_status()

# Find every HTML table on the page.
tables = pd.read_html(response.text)

print("Tables found:", len(tables))

# The odds dataset should be the largest table on the page.
odds_df = max(
    tables,
    key=lambda table: len(table)
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
odds_df.to_csv(OUTPUT_PATH, index=False)

print("Odds data saved to:", OUTPUT_PATH)
print("Rows:", len(odds_df))
print("Columns:", len(odds_df.columns))

print()
print("Column names:")
print(odds_df.columns.tolist())

print()
print("First 10 rows:")
print(odds_df.head(10))