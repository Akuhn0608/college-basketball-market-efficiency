from pathlib import Path

import pandas as pd


DATA_DIR = Path("data/raw/kaggle_2026")

teams_path = DATA_DIR / "MTeams.csv"
regular_season_path = DATA_DIR / "MRegularSeasonCompactResults.csv"
tournament_path = DATA_DIR / "MNCAATourneyCompactResults.csv"

teams_df = pd.read_csv(teams_path)
regular_season_df = pd.read_csv(regular_season_path)
tournament_df = pd.read_csv(tournament_path)

louisville_df = teams_df[
    teams_df["TeamName"].str.contains(
        "Louisville",
        case=False,
        na=False
    )
]

print("Men's teams:", len(teams_df))
print("Regular-season games:", len(regular_season_df))
print("NCAA Tournament games:", len(tournament_df))

print()
print("Team columns:")
print(teams_df.columns.tolist())

print()
print("Regular-season columns:")
print(regular_season_df.columns.tolist())

print()
print("Louisville team match:")
print(louisville_df)

print()
print("Most recent regular-season rows:")
print(
    regular_season_df
    .sort_values(["Season", "DayNum"])
    .tail()
)