from pathlib import Path
import sqlite3

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data" / "processed"
DATABASE_DIR = PROJECT_ROOT / "data" / "database"
DATABASE_PATH = DATABASE_DIR / "cbb_market_efficiency.db"

TEAMS_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "kaggle_2026"
    / "MTeams.csv"
)

MARKET_PATH = (
    DATA_DIR
    / "ncaab_market_probabilities_2021_22.csv"
)

LOUISVILLE_PATH = (
    DATA_DIR
    / "louisville_market_analysis_2021_22.csv"
)


DATABASE_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

teams_df = pd.read_csv(TEAMS_PATH)

market_df = pd.read_csv(
    MARKET_PATH,
    parse_dates=["game_date"],
)

louisville_df = pd.read_csv(
    LOUISVILLE_PATH,
    parse_dates=["game_date"],
)

# SQLite stores dates most reliably as ISO-formatted text.
market_df["game_date"] = (
    market_df["game_date"]
    .dt.strftime("%Y-%m-%d")
)

louisville_df["game_date"] = (
    louisville_df["game_date"]
    .dt.strftime("%Y-%m-%d")
)

# Keep the core team fields and use clearer SQL-style names.
teams_sql_df = teams_df.rename(
    columns={
        "TeamID": "team_id",
        "TeamName": "team_name",
        "FirstD1Season": "first_d1_season",
        "LastD1Season": "last_d1_season",
    }
)

# Create a game-level table.
games_sql_df = market_df[
    [
        "game_number",
        "game_date",
        "visitor_team_id",
        "home_team_id",
        "visitor_score",
        "home_score",
        "visitor_win",
        "home_win",
    ]
].copy()

games_sql_df = games_sql_df.rename(
    columns={
        "game_number": "game_id",
    }
)

# Create a separate market-pricing table.
market_sql_df = market_df[
    [
        "game_number",
        "visitor_moneyline",
        "home_moneyline",
        "visitor_implied_prob",
        "home_implied_prob",
        "market_vig",
        "visitor_no_vig_prob",
        "home_no_vig_prob",
        "visitor_market_role",
        "home_market_role",
        "visitor_pricing_error",
        "home_pricing_error",
    ]
].copy()

market_sql_df = market_sql_df.rename(
    columns={
        "game_number": "game_id",
    }
)

with sqlite3.connect(DATABASE_PATH) as connection:
    teams_sql_df.to_sql(
        "teams",
        connection,
        if_exists="replace",
        index=False,
    )

    games_sql_df.to_sql(
        "games",
        connection,
        if_exists="replace",
        index=False,
    )

    market_sql_df.to_sql(
        "market_prices",
        connection,
        if_exists="replace",
        index=False,
    )

    louisville_df.to_sql(
        "louisville_case_study",
        connection,
        if_exists="replace",
        index=False,
    )

    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_games_date
        ON games(game_date)
        """
    )

    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_games_visitor_team
        ON games(visitor_team_id)
        """
    )

    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_games_home_team
        ON games(home_team_id)
        """
    )

    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_market_game
        ON market_prices(game_id)
        """
    )

print("SQLite database created:", DATABASE_PATH)
print()
print("Rows loaded:")
print("teams:", len(teams_sql_df))
print("games:", len(games_sql_df))
print("market_prices:", len(market_sql_df))
print("louisville_case_study:", len(louisville_df))