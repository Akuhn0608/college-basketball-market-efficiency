import sys
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.backtest import calculate_bet_return


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


RANDOM_SEED = 42
BOOTSTRAP_SAMPLES = 5000
MINIMUM_SAMPLE_SIZE = 100


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


def bootstrap_roi(
    returns: pd.Series,
    bootstrap_samples: int = BOOTSTRAP_SAMPLES,
    random_seed: int = RANDOM_SEED,
) -> dict:
    """
    Estimate ROI uncertainty using bootstrap resampling.
    """

    clean_returns = (
        returns
        .dropna()
        .astype(float)
        .to_numpy()
    )

    sample_size = len(clean_returns)

    if sample_size == 0:
        return {
            "roi": np.nan,
            "roi_ci_lower": np.nan,
            "roi_ci_upper": np.nan,
            "probability_positive_roi": np.nan,
        }

    rng = np.random.default_rng(random_seed)

    bootstrap_rois = np.empty(
        bootstrap_samples
    )

    for sample_number in range(
        bootstrap_samples
    ):
        sampled_returns = rng.choice(
            clean_returns,
            size=sample_size,
            replace=True,
        )

        bootstrap_rois[sample_number] = (
            sampled_returns.mean()
        )

    observed_roi = clean_returns.mean()

    roi_ci_lower = np.percentile(
        bootstrap_rois,
        2.5,
    )

    roi_ci_upper = np.percentile(
        bootstrap_rois,
        97.5,
    )

    probability_positive_roi = (
        bootstrap_rois > 0
    ).mean()

    return {
        "roi": float(observed_roi),
        "roi_ci_lower": float(
            roi_ci_lower
        ),
        "roi_ci_upper": float(
            roi_ci_upper
        ),
        "probability_positive_roi": float(
            probability_positive_roi
        ),
    }


strategy_masks = {
    "All favorites": (
        observations_df["market_role"]
        == "favorite"
    ),

    "All underdogs": (
        observations_df["market_role"]
        == "underdog"
    ),

    "Home favorites": (
        (
            observations_df["location"]
            == "Home"
        )
        & (
            observations_df["market_role"]
            == "favorite"
        )
    ),

    "Home underdogs": (
        (
            observations_df["location"]
            == "Home"
        )
        & (
            observations_df["market_role"]
            == "underdog"
        )
    ),

    "Visitor favorites": (
        (
            observations_df["location"]
            == "Visitor"
        )
        & (
            observations_df["market_role"]
            == "favorite"
        )
    ),

    "Visitor underdogs": (
        (
            observations_df["location"]
            == "Visitor"
        )
        & (
            observations_df["market_role"]
            == "underdog"
        )
    ),
}


strategy_uncertainty_results = []

for strategy_name, strategy_mask in (
    strategy_masks.items()
):
    strategy_df = observations_df[
        strategy_mask
    ].copy()

    uncertainty = bootstrap_roi(
        strategy_df["net_return"]
    )

    uncertainty["strategy"] = strategy_name
    uncertainty["bets"] = len(strategy_df)

    uncertainty["sample_flag"] = (
        "Sufficient sample"
        if len(strategy_df)
        >= MINIMUM_SAMPLE_SIZE
        else "Small sample"
    )

    uncertainty["interpretation"] = (
        "Evidence of positive ROI"
        if uncertainty["roi_ci_lower"] > 0
        else (
            "Evidence of negative ROI"
            if uncertainty["roi_ci_upper"] < 0
            else "Inconclusive"
        )
    )

    strategy_uncertainty_results.append(
        uncertainty
    )


strategy_uncertainty_df = pd.DataFrame(
    strategy_uncertainty_results
)

strategy_uncertainty_df = (
    strategy_uncertainty_df[
        [
            "strategy",
            "bets",
            "roi",
            "roi_ci_lower",
            "roi_ci_upper",
            "probability_positive_roi",
            "sample_flag",
            "interpretation",
        ]
    ]
)


bucket_uncertainty_results = []

for probability_bucket, bucket_df in (
    observations_df.groupby(
        "probability_bucket",
        observed=True,
    )
):
    uncertainty = bootstrap_roi(
        bucket_df["net_return"]
    )

    uncertainty["probability_bucket"] = (
        str(probability_bucket)
    )

    uncertainty["bets"] = len(bucket_df)

    uncertainty[
        "average_market_probability"
    ] = bucket_df[
        "market_probability"
    ].mean()

    uncertainty["sample_flag"] = (
        "Sufficient sample"
        if len(bucket_df)
        >= MINIMUM_SAMPLE_SIZE
        else "Small sample"
    )

    uncertainty["interpretation"] = (
        "Evidence of positive ROI"
        if uncertainty["roi_ci_lower"] > 0
        else (
            "Evidence of negative ROI"
            if uncertainty["roi_ci_upper"] < 0
            else "Inconclusive"
        )
    )

    bucket_uncertainty_results.append(
        uncertainty
    )


bucket_uncertainty_df = pd.DataFrame(
    bucket_uncertainty_results
)

bucket_uncertainty_df = (
    bucket_uncertainty_df[
        [
            "probability_bucket",
            "bets",
            "average_market_probability",
            "roi",
            "roi_ci_lower",
            "roi_ci_upper",
            "probability_positive_roi",
            "sample_flag",
            "interpretation",
        ]
    ]
)


strategy_output_path = (
    OUTPUT_DIR
    / "strategy_bootstrap_uncertainty_2021_22.csv"
)

bucket_output_path = (
    OUTPUT_DIR
    / "bucket_bootstrap_uncertainty_2021_22.csv"
)


strategy_uncertainty_df.to_csv(
    strategy_output_path,
    index=False,
)

bucket_uncertainty_df.to_csv(
    bucket_output_path,
    index=False,
)


display_columns = [
    "strategy",
    "bets",
    "roi",
    "roi_ci_lower",
    "roi_ci_upper",
    "probability_positive_roi",
    "interpretation",
]

print("Bootstrap uncertainty analysis complete.")
print()
print("Strategy uncertainty:")
print(
    strategy_uncertainty_df[
        display_columns
    ].to_string(index=False)
)

print()
print("Probability-bucket uncertainty:")
print(
    bucket_uncertainty_df[
        [
            "probability_bucket",
            "bets",
            "roi",
            "roi_ci_lower",
            "roi_ci_upper",
            "probability_positive_roi",
            "interpretation",
        ]
    ].to_string(index=False)
)

print()
print("Outputs saved to:")
print(strategy_output_path)
print(bucket_output_path)