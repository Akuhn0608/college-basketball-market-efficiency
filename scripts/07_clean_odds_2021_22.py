from pathlib import Path

import pandas as pd


INPUT_PATH = Path("data/raw/odds/ncaab_odds_2021_22.csv")
OUTPUT_DIR = Path("data/processed")
OUTPUT_PATH = OUTPUT_DIR / "ncaab_odds_games_2021_22.csv"

column_names = [
    "date_code",
    "rotation",
    "location",
    "team",
    "first_half_score",
    "second_half_score",
    "final_score",
    "opening_line",
    "closing_line",
    "moneyline",
    "second_half_line",
]

df = pd.read_csv(INPUT_PATH)

# The webpage table stored its real column names as the first data row.
df.columns = column_names
df = df.iloc[1:].copy()
df = df.reset_index(drop=True)

# Convert useful numeric fields.
numeric_columns = [
    "rotation",
    "first_half_score",
    "second_half_score",
    "final_score",
    "opening_line",
    "closing_line",
    "moneyline",
    "second_half_line",
]

for column in numeric_columns:
    df[column] = pd.to_numeric(df[column], errors="coerce")

# Make date codes four characters, such as 1109 or 0305.
df["date_code"] = (
    df["date_code"]
    .astype(str)
    .str.replace(".0", "", regex=False)
    .str.zfill(4)
)

df["month"] = df["date_code"].str[:2].astype(int)
df["day"] = df["date_code"].str[2:].astype(int)

# The 2021–22 season begins in late 2021 and ends in spring 2022.
df["year"] = df["month"].apply(
    lambda month: 2021 if month >= 8 else 2022
)

df["game_date"] = pd.to_datetime(
    {
        "year": df["year"],
        "month": df["month"],
        "day": df["day"],
    },
    errors="coerce",
)

# Every two consecutive rows represent one game.
df["game_number"] = df.index // 2

visitor_df = (
    df.groupby("game_number")
    .nth(0)
    .reset_index()
)

home_df = (
    df.groupby("game_number")
    .nth(1)
    .reset_index()
)

games_df = pd.DataFrame(
    {
        "game_number": visitor_df["game_number"],
        "game_date": visitor_df["game_date"],
        "visitor_team": visitor_df["team"],
        "home_team": home_df["team"],
        "visitor_score": visitor_df["final_score"],
        "home_score": home_df["final_score"],
        "visitor_moneyline": visitor_df["moneyline"],
        "home_moneyline": home_df["moneyline"],
        "visitor_rotation": visitor_df["rotation"],
        "home_rotation": home_df["rotation"],
        "visitor_location_code": visitor_df["location"],
        "home_location_code": home_df["location"],
    }
)

games_df["visitor_win"] = (
    games_df["visitor_score"] > games_df["home_score"]
).astype(int)

games_df["home_win"] = (
    games_df["home_score"] > games_df["visitor_score"]
).astype(int)

games_df["moneylines_available"] = (
    games_df["visitor_moneyline"].notna()
    & games_df["home_moneyline"].notna()
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
games_df.to_csv(OUTPUT_PATH, index=False)

print("Clean odds game data saved to:", OUTPUT_PATH)
print()
print("Team rows:", len(df))
print("Games created:", len(games_df))
print("Games with both moneylines:", games_df["moneylines_available"].sum())
print("Games missing at least one moneyline:", (~games_df["moneylines_available"]).sum())

print()
print("Date range:")
print(games_df["game_date"].min(), "to", games_df["game_date"].max())

print()
print("First five games:")
print(
    games_df[
        [
            "game_date",
            "visitor_team",
            "home_team",
            "visitor_score",
            "home_score",
            "visitor_moneyline",
            "home_moneyline",
            "visitor_win",
        ]
    ].head()
)