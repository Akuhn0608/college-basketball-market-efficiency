from pathlib import Path

import pandas as pd


DATA_DIR = Path("data/raw/kaggle_2026")

teams_path = DATA_DIR / "MTeams.csv"
spellings_path = DATA_DIR / "MTeamSpellings.csv"

teams_df = pd.read_csv(teams_path)
spellings_df = pd.read_csv(
    spellings_path,
    encoding="cp1252"
)

print("Teams:", len(teams_df))
print("Team spellings:", len(spellings_df))

print()
print("Spelling columns:")
print(spellings_df.columns.tolist())

print()
print("First 10 spelling rows:")
print(spellings_df.head(10))

print()
print("Louisville-related spellings:")
print(
    spellings_df[
        spellings_df["TeamNameSpelling"]
        .str.contains("louis", case=False, na=False)
    ]
)

print()
print("UC San Diego-related spellings:")
print(
    spellings_df[
        spellings_df["TeamNameSpelling"]
        .str.contains("san diego", case=False, na=False)
    ]
)