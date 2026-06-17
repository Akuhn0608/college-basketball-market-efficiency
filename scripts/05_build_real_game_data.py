from pathlib import Path

import pandas as pd


DATA_DIR = Path("data/raw/kaggle_2026")
OUTPUT_DIR = Path("data/processed")

teams_path = DATA_DIR / "MTeams.csv"
regular_season_path = DATA_DIR / "MRegularSeasonCompactResults.csv"
tournament_path = DATA_DIR / "MNCAATourneyCompactResults.csv"

output_path = OUTPUT_DIR / "mens_cbb_games_1985_2026.csv"
louisville_output_path = OUTPUT_DIR / "louisville_games_1985_2026.csv"

teams_df = pd.read_csv(teams_path)
regular_season_df = pd.read_csv(regular_season_path)
tournament_df = pd.read_csv(tournament_path)

# Label the type of game before combining the files.
regular_season_df["game_type"] = "regular_season"
tournament_df["game_type"] = "ncaa_tournament"

games_df = pd.concat(
    [regular_season_df, tournament_df],
    ignore_index=True
)

# Create a TeamID-to-TeamName lookup table.
team_name_map = teams_df.set_index("TeamID")["TeamName"]

games_df["winner_name"] = games_df["WTeamID"].map(team_name_map)
games_df["loser_name"] = games_df["LTeamID"].map(team_name_map)

# Add easy-to-analyze game-level features.
games_df["score_margin"] = games_df["WScore"] - games_df["LScore"]
games_df["total_points"] = games_df["WScore"] + games_df["LScore"]
games_df["went_to_overtime"] = games_df["NumOT"] > 0

# Reorder the columns so the output is easier to read.
games_df = games_df[
    [
        "Season",
        "DayNum",
        "game_type",
        "WTeamID",
        "winner_name",
        "WScore",
        "LTeamID",
        "loser_name",
        "LScore",
        "WLoc",
        "NumOT",
        "score_margin",
        "total_points",
        "went_to_overtime",
    ]
]

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
games_df.to_csv(output_path, index=False)

# Louisville's official Kaggle TeamID.
LOUISVILLE_TEAM_ID = 1257

louisville_df = games_df[
    (games_df["WTeamID"] == LOUISVILLE_TEAM_ID)
    | (games_df["LTeamID"] == LOUISVILLE_TEAM_ID)
].copy()

# Rewrite every game from Louisville's point of view.
louisville_df["louisville_win"] = (
    louisville_df["WTeamID"] == LOUISVILLE_TEAM_ID
).astype(int)

louisville_df["opponent"] = louisville_df.apply(
    lambda row: (
        row["loser_name"]
        if row["WTeamID"] == LOUISVILLE_TEAM_ID
        else row["winner_name"]
    ),
    axis=1,
)

louisville_df["louisville_score"] = louisville_df.apply(
    lambda row: (
        row["WScore"]
        if row["WTeamID"] == LOUISVILLE_TEAM_ID
        else row["LScore"]
    ),
    axis=1,
)

louisville_df["opponent_score"] = louisville_df.apply(
    lambda row: (
        row["LScore"]
        if row["WTeamID"] == LOUISVILLE_TEAM_ID
        else row["WScore"]
    ),
    axis=1,
)

louisville_df["louisville_margin"] = (
    louisville_df["louisville_score"]
    - louisville_df["opponent_score"]
)

louisville_df.to_csv(louisville_output_path, index=False)

print("Real men's game dataset saved to:", output_path)
print("Louisville game dataset saved to:", louisville_output_path)
print()
print("Total games:", len(games_df))
print("Louisville games:", len(louisville_df))
print("Louisville wins:", louisville_df["louisville_win"].sum())
print(
    "Louisville win rate:",
    round(louisville_df["louisville_win"].mean(), 3)
)
print()
print("Most recent Louisville games:")
print(
    louisville_df[
        [
            "Season",
            "DayNum",
            "game_type",
            "opponent",
            "louisville_score",
            "opponent_score",
            "louisville_win",
            "louisville_margin",
        ]
    ]
    .sort_values(["Season", "DayNum"])
    .tail(10)
)