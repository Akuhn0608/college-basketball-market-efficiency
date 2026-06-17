import sys
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.backtest import (
    calculate_bet_return,
    summarize_backtest,
)


INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "backtests"
    / "team_market_observations_2021_22.csv"
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


BOOTSTRAP_SAMPLES = 5000
RANDOM_SEED = 42


observations_df = pd.read_csv(
    INPUT_PATH,
    parse_dates=["game_date"],
)

observations_df["net_return"] = observations_df.apply(
    lambda row: calculate_bet_return(
        american_odds=row["american_odds"],
        won=int(row["actual_win"]),
        stake=1.0,
    ),
    axis=1,
)


candidate_df = observations_df[
    (
        observations_df["market_probability"]
        >= 0.70
    )
    & (
        observations_df["market_probability"]
        < 0.80
    )
].copy()

candidate_df = candidate_df.sort_values(
    "game_date"
).reset_index(drop=True)


split_index = len(candidate_df) // 2

first_half_df = candidate_df.iloc[
    :split_index
].copy()

second_half_df = candidate_df.iloc[
    split_index:
].copy()


def bootstrap_roi(
    returns: pd.Series,
    random_seed: int,
) -> dict:
    """
    Estimate a 95% confidence interval for flat-stake ROI.
    """

    clean_returns = (
        returns
        .dropna()
        .astype(float)
        .to_numpy()
    )

    sample_size = len(clean_returns)

    rng = np.random.default_rng(
        random_seed
    )

    bootstrap_rois = np.empty(
        BOOTSTRAP_SAMPLES
    )

    for sample_number in range(
        BOOTSTRAP_SAMPLES
    ):
        sampled_returns = rng.choice(
            clean_returns,
            size=sample_size,
            replace=True,
        )

        bootstrap_rois[sample_number] = (
            sampled_returns.mean()
        )

    return {
        "roi_ci_lower": float(
            np.percentile(
                bootstrap_rois,
                2.5,
            )
        ),
        "roi_ci_upper": float(
            np.percentile(
                bootstrap_rois,
                97.5,
            )
        ),
        "probability_positive_roi": float(
            (
                bootstrap_rois > 0
            ).mean()
        ),
    }


period_definitions = {
    "Full season": candidate_df,
    "First half": first_half_df,
    "Second half": second_half_df,
}


period_results = []

for period_number, (
    period_name,
    period_df,
) in enumerate(
    period_definitions.items()
):
    summary = summarize_backtest(
        observations_df=period_df,
        stake=1.0,
    )

    uncertainty = bootstrap_roi(
        returns=period_df["net_return"],
        random_seed=(
            RANDOM_SEED
            + period_number
        ),
    )

    period_results.append(
        {
            "segment": period_name,
            "start_date": (
                period_df["game_date"].min()
            ),
            "end_date": (
                period_df["game_date"].max()
            ),
            "bets": summary["bets"],
            "wins": summary["wins"],
            "hit_rate": summary["hit_rate"],
            "net_profit": summary["net_profit"],
            "roi": summary["roi"],
            "roi_ci_lower": (
                uncertainty["roi_ci_lower"]
            ),
            "roi_ci_upper": (
                uncertainty["roi_ci_upper"]
            ),
            "probability_positive_roi": (
                uncertainty[
                    "probability_positive_roi"
                ]
            ),
            "maximum_drawdown": (
                summary["maximum_drawdown"]
            ),
        }
    )


period_results_df = pd.DataFrame(
    period_results
)


location_results = []

for location, location_df in (
    candidate_df.groupby("location")
):
    summary = summarize_backtest(
        observations_df=location_df,
        stake=1.0,
    )

    uncertainty = bootstrap_roi(
        returns=location_df["net_return"],
        random_seed=(
            RANDOM_SEED
            + len(location_results)
            + 10
        ),
    )

    location_results.append(
        {
            "location": location,
            "bets": summary["bets"],
            "wins": summary["wins"],
            "hit_rate": summary["hit_rate"],
            "net_profit": summary["net_profit"],
            "roi": summary["roi"],
            "roi_ci_lower": (
                uncertainty["roi_ci_lower"]
            ),
            "roi_ci_upper": (
                uncertainty["roi_ci_upper"]
            ),
            "probability_positive_roi": (
                uncertainty[
                    "probability_positive_roi"
                ]
            ),
            "maximum_drawdown": (
                summary["maximum_drawdown"]
            ),
        }
    )


location_results_df = pd.DataFrame(
    location_results
)


candidate_df["month"] = (
    candidate_df["game_date"]
    .dt.to_period("M")
    .astype(str)
)

monthly_results = []

for month, month_df in (
    candidate_df.groupby("month")
):
    summary = summarize_backtest(
        observations_df=month_df,
        stake=1.0,
    )

    monthly_results.append(
        {
            "month": month,
            "bets": summary["bets"],
            "wins": summary["wins"],
            "hit_rate": summary["hit_rate"],
            "net_profit": summary["net_profit"],
            "roi": summary["roi"],
            "maximum_drawdown": (
                summary["maximum_drawdown"]
            ),
        }
    )


monthly_results_df = pd.DataFrame(
    monthly_results
)


period_output_path = (
    OUTPUT_DIR
    / "candidate_edge_time_validation_2021_22.csv"
)

location_output_path = (
    OUTPUT_DIR
    / "candidate_edge_location_validation_2021_22.csv"
)

monthly_output_path = (
    OUTPUT_DIR
    / "candidate_edge_monthly_validation_2021_22.csv"
)


period_results_df.to_csv(
    period_output_path,
    index=False,
)

location_results_df.to_csv(
    location_output_path,
    index=False,
)

monthly_results_df.to_csv(
    monthly_output_path,
    index=False,
)


print(
    "Candidate-edge robustness analysis complete."
)

print()
print("Chronological validation:")
print(
    period_results_df.to_string(
        index=False
    )
)

print()
print("Home and visitor validation:")
print(
    location_results_df.to_string(
        index=False
    )
)

print()
print("Monthly stability:")
print(
    monthly_results_df.to_string(
        index=False
    )
)

print()
print("Outputs saved to:")
print(period_output_path)
print(location_output_path)
print(monthly_output_path)