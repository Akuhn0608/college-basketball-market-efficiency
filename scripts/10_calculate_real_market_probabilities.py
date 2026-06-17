import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.vig import remove_vig_two_way


INPUT_PATH = Path(
    "data/processed/ncaab_odds_games_2021_22_mapped.csv"
)

OUTPUT_PATH = Path(
    "data/processed/ncaab_market_probabilities_2021_22.csv"
)


df = pd.read_csv(
    INPUT_PATH,
    parse_dates=["game_date"],
)

# Keep games where:
# 1. Both teams were mapped to Kaggle IDs.
# 2. Both moneylines are available.
market_df = df[
    df["both_teams_mapped"]
    & df["moneylines_available"]
].copy()

probability_rows = []

for _, row in market_df.iterrows():
    probabilities = remove_vig_two_way(
        row["visitor_moneyline"],
        row["home_moneyline"],
    )

    probability_rows.append(
        {
            "visitor_implied_prob": probabilities[
                "team_a_implied_prob"
            ],
            "home_implied_prob": probabilities[
                "team_b_implied_prob"
            ],
            "market_vig": probabilities[
                "market_vig"
            ],
            "visitor_no_vig_prob": probabilities[
                "team_a_no_vig_prob"
            ],
            "home_no_vig_prob": probabilities[
                "team_b_no_vig_prob"
            ],
        }
    )

probabilities_df = pd.DataFrame(
    probability_rows,
    index=market_df.index,
)

market_df = pd.concat(
    [market_df, probabilities_df],
    axis=1,
)

market_df["visitor_pricing_error"] = (
    market_df["visitor_win"]
    - market_df["visitor_no_vig_prob"]
)

market_df["home_pricing_error"] = (
    market_df["home_win"]
    - market_df["home_no_vig_prob"]
)

market_df["visitor_market_role"] = market_df.apply(
    lambda row: (
        "favorite"
        if row["visitor_no_vig_prob"] > row["home_no_vig_prob"]
        else "underdog"
    ),
    axis=1,
)

market_df["home_market_role"] = market_df.apply(
    lambda row: (
        "favorite"
        if row["home_no_vig_prob"] > row["visitor_no_vig_prob"]
        else "underdog"
    ),
    axis=1,
)

market_df.to_csv(
    OUTPUT_PATH,
    index=False,
)

print("Real market probability data saved to:", OUTPUT_PATH)
print()
print("Games analyzed:", len(market_df))
print(
    "Average vig:",
    round(market_df["market_vig"].mean(), 4),
)
print(
    "Average visitor no-vig probability:",
    round(market_df["visitor_no_vig_prob"].mean(), 4),
)
print(
    "Average home no-vig probability:",
    round(market_df["home_no_vig_prob"].mean(), 4),
)

print()
print("Louisville games with probabilities:")

louisville_df = market_df[
    (market_df["visitor_team_id"] == 1257)
    | (market_df["home_team_id"] == 1257)
]

print("Louisville games:", len(louisville_df))

print(
    louisville_df[
        [
            "game_date",
            "visitor_official_name",
            "home_official_name",
            "visitor_moneyline",
            "home_moneyline",
            "visitor_no_vig_prob",
            "home_no_vig_prob",
            "visitor_win",
            "home_win",
        ]
    ].head(10)
)