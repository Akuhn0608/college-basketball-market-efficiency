import sys
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.backtest import summarize_backtest


DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "ncaab_market_probabilities_2021_22.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "backtests"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


market_df = pd.read_csv(
    DATA_PATH,
    parse_dates=["game_date"],
)


visitor_df = market_df[
    [
        "game_number",
        "game_date",
        "visitor_official_name",
        "visitor_moneyline",
        "visitor_no_vig_prob",
        "visitor_market_role",
        "visitor_win",
    ]
].copy()

visitor_df = visitor_df.rename(
    columns={
        "visitor_official_name": "team_name",
        "visitor_moneyline": "american_odds",
        "visitor_no_vig_prob": "market_probability",
        "visitor_market_role": "market_role",
        "visitor_win": "actual_win",
    }
)

visitor_df["location"] = "Visitor"


home_df = market_df[
    [
        "game_number",
        "game_date",
        "home_official_name",
        "home_moneyline",
        "home_no_vig_prob",
        "home_market_role",
        "home_win",
    ]
].copy()

home_df = home_df.rename(
    columns={
        "home_official_name": "team_name",
        "home_moneyline": "american_odds",
        "home_no_vig_prob": "market_probability",
        "home_market_role": "market_role",
        "home_win": "actual_win",
    }
)

home_df["location"] = "Home"


team_observations_df = pd.concat(
    [
        visitor_df,
        home_df,
    ],
    ignore_index=True,
)

team_observations_df["probability_bucket"] = pd.cut(
    team_observations_df["market_probability"],
    bins=np.arange(0, 1.1, 0.1),
    include_lowest=True,
)


strategy_definitions = {
    "All favorites": (
        team_observations_df["market_role"]
        == "favorite"
    ),

    "All underdogs": (
        team_observations_df["market_role"]
        == "underdog"
    ),

    "Home favorites": (
        (
            team_observations_df["location"]
            == "Home"
        )
        & (
            team_observations_df["market_role"]
            == "favorite"
        )
    ),

    "Home underdogs": (
        (
            team_observations_df["location"]
            == "Home"
        )
        & (
            team_observations_df["market_role"]
            == "underdog"
        )
    ),

    "Visitor favorites": (
        (
            team_observations_df["location"]
            == "Visitor"
        )
        & (
            team_observations_df["market_role"]
            == "favorite"
        )
    ),

    "Visitor underdogs": (
        (
            team_observations_df["location"]
            == "Visitor"
        )
        & (
            team_observations_df["market_role"]
            == "underdog"
        )
    ),
}


strategy_results = []

for strategy_name, strategy_mask in (
    strategy_definitions.items()
):
    strategy_df = team_observations_df[
        strategy_mask
    ].copy()

    summary = summarize_backtest(
        observations_df=strategy_df,
        stake=1.0,
    )

    summary["strategy"] = strategy_name
    strategy_results.append(summary)


strategy_results_df = pd.DataFrame(
    strategy_results
)

strategy_results_df = strategy_results_df[
    [
        "strategy",
        "bets",
        "wins",
        "losses",
        "hit_rate",
        "total_staked",
        "net_profit",
        "roi",
        "average_return",
        "return_volatility",
        "sharpe_like_ratio",
        "maximum_drawdown",
    ]
]


bucket_results = []

for probability_bucket, bucket_df in (
    team_observations_df.groupby(
        "probability_bucket",
        observed=True,
    )
):
    summary = summarize_backtest(
        observations_df=bucket_df,
        stake=1.0,
    )

    summary["probability_bucket"] = str(
        probability_bucket
    )

    summary["average_market_probability"] = (
        bucket_df["market_probability"].mean()
    )

    bucket_results.append(summary)


bucket_results_df = pd.DataFrame(
    bucket_results
)

bucket_results_df = bucket_results_df[
    [
        "probability_bucket",
        "bets",
        "wins",
        "hit_rate",
        "average_market_probability",
        "net_profit",
        "roi",
        "return_volatility",
        "sharpe_like_ratio",
        "maximum_drawdown",
    ]
]


minimum_sample_size = 100

strategy_results_df["sample_flag"] = np.where(
    strategy_results_df["bets"]
    >= minimum_sample_size,
    "Sufficient sample",
    "Small sample",
)

bucket_results_df["sample_flag"] = np.where(
    bucket_results_df["bets"]
    >= minimum_sample_size,
    "Sufficient sample",
    "Small sample",
)


strategy_output_path = (
    OUTPUT_DIR
    / "market_strategy_summary_2021_22.csv"
)

bucket_output_path = (
    OUTPUT_DIR
    / "probability_bucket_backtest_2021_22.csv"
)

observations_output_path = (
    OUTPUT_DIR
    / "team_market_observations_2021_22.csv"
)


strategy_results_df.to_csv(
    strategy_output_path,
    index=False,
)

bucket_results_df.to_csv(
    bucket_output_path,
    index=False,
)

team_observations_df.to_csv(
    observations_output_path,
    index=False,
)


print("Market backtesting complete.")
print()
print("Strategy results:")
print(
    strategy_results_df[
        [
            "strategy",
            "bets",
            "hit_rate",
            "net_profit",
            "roi",
            "maximum_drawdown",
        ]
    ].to_string(index=False)
)

print()
print("Probability-bucket results:")
print(
    bucket_results_df[
        [
            "probability_bucket",
            "bets",
            "hit_rate",
            "average_market_probability",
            "net_profit",
            "roi",
            "maximum_drawdown",
        ]
    ].to_string(index=False)
)

print()
print("Outputs saved to:")
print(strategy_output_path)
print(bucket_output_path)
print(observations_output_path)