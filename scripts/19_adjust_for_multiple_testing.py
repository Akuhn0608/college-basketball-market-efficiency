from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "backtests"
    / "team_market_observations_2021_22.csv"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "backtests"
    / "bucket_multiple_testing_adjustment_2021_22.csv"
)


RANDOM_SEED = 42
BOOTSTRAP_SAMPLES = 5000
NUMBER_OF_BUCKETS = 10


def calculate_net_return(
    american_odds: float,
    actual_win: int,
) -> float:
    """
    Calculate flat-stake net return for one observation.
    """

    if actual_win == 0:
        return -1.0

    if american_odds > 0:
        return american_odds / 100.0

    return 100.0 / abs(american_odds)


observations_df = pd.read_csv(
    INPUT_PATH,
    parse_dates=["game_date"],
)

observations_df["net_return"] = observations_df.apply(
    lambda row: calculate_net_return(
        american_odds=row["american_odds"],
        actual_win=int(row["actual_win"]),
    ),
    axis=1,
)

bucket_edges = np.arange(
    0.0,
    1.1,
    0.1,
)

bucket_labels = [
    "0%–10%",
    "10%–20%",
    "20%–30%",
    "30%–40%",
    "40%–50%",
    "50%–60%",
    "60%–70%",
    "70%–80%",
    "80%–90%",
    "90%–100%",
]

observations_df["bucket"] = pd.cut(
    observations_df["market_probability"],
    bins=bucket_edges,
    labels=bucket_labels,
    include_lowest=True,
    right=True,
)


# Aggregate each game's return and bet count by bucket.
# This allows the bootstrap to resample entire games rather than
# treating every team observation as fully independent.
game_bucket_returns = (
    observations_df
    .pivot_table(
        index="game_number",
        columns="bucket",
        values="net_return",
        aggfunc="sum",
        fill_value=0.0,
        observed=False,
    )
    .reindex(
        columns=bucket_labels,
        fill_value=0.0,
    )
)

game_bucket_counts = (
    observations_df
    .assign(bet_count=1)
    .pivot_table(
        index="game_number",
        columns="bucket",
        values="bet_count",
        aggfunc="sum",
        fill_value=0,
        observed=False,
    )
    .reindex(
        columns=bucket_labels,
        fill_value=0,
    )
)


return_matrix = game_bucket_returns.to_numpy(
    dtype=float
)

count_matrix = game_bucket_counts.to_numpy(
    dtype=float
)

number_of_games = len(return_matrix)

observed_returns = return_matrix.sum(axis=0)
observed_counts = count_matrix.sum(axis=0)

observed_roi = (
    observed_returns
    / observed_counts
)


rng = np.random.default_rng(
    RANDOM_SEED
)

bootstrap_rois = np.empty(
    (
        BOOTSTRAP_SAMPLES,
        NUMBER_OF_BUCKETS,
    )
)


for sample_number in range(
    BOOTSTRAP_SAMPLES
):
    sampled_game_indices = rng.integers(
        low=0,
        high=number_of_games,
        size=number_of_games,
    )

    sampled_returns = return_matrix[
        sampled_game_indices
    ].sum(axis=0)

    sampled_counts = count_matrix[
        sampled_game_indices
    ].sum(axis=0)

    bootstrap_rois[
        sample_number
    ] = np.divide(
        sampled_returns,
        sampled_counts,
        out=np.full(
            NUMBER_OF_BUCKETS,
            np.nan,
        ),
        where=sampled_counts > 0,
    )


results = []

# Standard 95% confidence interval.
standard_lower_percentile = 2.5
standard_upper_percentile = 97.5

# Bonferroni-adjusted familywise 95% interval:
# alpha / 10 = 0.005, so use 0.25% and 99.75%.
adjusted_lower_percentile = (
    100
    * (
        0.05
        / NUMBER_OF_BUCKETS
        / 2
    )
)

adjusted_upper_percentile = (
    100
    - adjusted_lower_percentile
)


for bucket_number, bucket_name in enumerate(
    bucket_labels
):
    bucket_bootstrap_rois = bootstrap_rois[
        :,
        bucket_number,
    ]

    ci_95_lower = np.nanpercentile(
        bucket_bootstrap_rois,
        standard_lower_percentile,
    )

    ci_95_upper = np.nanpercentile(
        bucket_bootstrap_rois,
        standard_upper_percentile,
    )

    bonferroni_lower = np.nanpercentile(
        bucket_bootstrap_rois,
        adjusted_lower_percentile,
    )

    bonferroni_upper = np.nanpercentile(
        bucket_bootstrap_rois,
        adjusted_upper_percentile,
    )

    probability_positive_roi = np.nanmean(
        bucket_bootstrap_rois > 0
    )

    if bonferroni_lower > 0:
        adjusted_interpretation = (
            "Positive after multiple-testing adjustment"
        )
    elif bonferroni_upper < 0:
        adjusted_interpretation = (
            "Negative after multiple-testing adjustment"
        )
    else:
        adjusted_interpretation = (
            "Inconclusive after adjustment"
        )

    results.append(
        {
            "probability_bucket": bucket_name,
            "bets": int(
                observed_counts[bucket_number]
            ),
            "observed_roi": float(
                observed_roi[bucket_number]
            ),
            "clustered_ci_95_lower": float(
                ci_95_lower
            ),
            "clustered_ci_95_upper": float(
                ci_95_upper
            ),
            "bonferroni_ci_lower": float(
                bonferroni_lower
            ),
            "bonferroni_ci_upper": float(
                bonferroni_upper
            ),
            "probability_positive_roi": float(
                probability_positive_roi
            ),
            "adjusted_interpretation": (
                adjusted_interpretation
            ),
        }
    )


results_df = pd.DataFrame(
    results
)

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)

results_df.to_csv(
    OUTPUT_PATH,
    index=False,
)


print(
    "Clustered bootstrap and multiple-testing "
    "adjustment complete."
)

print()
print(
    results_df.to_string(
        index=False
    )
)

print()
print("Output saved to:")
print(OUTPUT_PATH)