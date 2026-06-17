import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.calibration import create_probability_buckets
from src.metrics import calculate_brier_score, calculate_log_loss


INPUT_PATH = Path(
    "data/processed/ncaab_market_probabilities_2021_22.csv"
)

CALIBRATION_OUTPUT_PATH = Path(
    "data/processed/real_calibration_2021_22.csv"
)

SEGMENT_OUTPUT_PATH = Path(
    "data/processed/real_segment_summary_2021_22.csv"
)

METRICS_OUTPUT_PATH = Path(
    "data/processed/real_metrics_2021_22.csv"
)

LOUISVILLE_OUTPUT_PATH = Path(
    "data/processed/louisville_market_analysis_2021_22.csv"
)


df = pd.read_csv(
    INPUT_PATH,
    parse_dates=["game_date"],
)

# Analyze every game from the visitor team's perspective.
calibration_df = create_probability_buckets(
    df=df,
    prob_col="visitor_no_vig_prob",
    outcome_col="visitor_win",
    bucket_size=0.10,
)

calibration_df.to_csv(
    CALIBRATION_OUTPUT_PATH,
    index=False,
)

# Overall probability-scoring metrics.
brier_score = calculate_brier_score(
    outcomes=df["visitor_win"],
    probabilities=df["visitor_no_vig_prob"],
)

logloss = calculate_log_loss(
    outcomes=df["visitor_win"],
    probabilities=df["visitor_no_vig_prob"],
)

metrics_df = pd.DataFrame(
    [
        {
            "metric": "brier_score",
            "value": brier_score,
        },
        {
            "metric": "log_loss",
            "value": logloss,
        },
    ]
)

metrics_df.to_csv(
    METRICS_OUTPUT_PATH,
    index=False,
)

# Favorite and underdog analysis.
visitor_segment_df = (
    df.groupby("visitor_market_role")
    .agg(
        games=("visitor_win", "size"),
        avg_market_prob=("visitor_no_vig_prob", "mean"),
        actual_win_rate=("visitor_win", "mean"),
        avg_pricing_error=("visitor_pricing_error", "mean"),
    )
    .reset_index()
    .rename(
        columns={
            "visitor_market_role": "market_role"
        }
    )
)

home_segment_df = (
    df.groupby("home_market_role")
    .agg(
        games=("home_win", "size"),
        avg_market_prob=("home_no_vig_prob", "mean"),
        actual_win_rate=("home_win", "mean"),
        avg_pricing_error=("home_pricing_error", "mean"),
    )
    .reset_index()
    .rename(
        columns={
            "home_market_role": "market_role"
        }
    )
)

# Combine visitor and home observations so each team-game is one observation.
combined_segments_df = pd.concat(
    [
        visitor_segment_df.assign(team_location="visitor"),
        home_segment_df.assign(team_location="home"),
    ],
    ignore_index=True,
)

combined_segments_df.to_csv(
    SEGMENT_OUTPUT_PATH,
    index=False,
)

# Create Louisville analysis from Louisville's perspective.
LOUISVILLE_TEAM_ID = 1257

louisville_df = df[
    (df["visitor_team_id"] == LOUISVILLE_TEAM_ID)
    | (df["home_team_id"] == LOUISVILLE_TEAM_ID)
].copy()

louisville_df["louisville_is_visitor"] = (
    louisville_df["visitor_team_id"] == LOUISVILLE_TEAM_ID
)

louisville_df["opponent"] = louisville_df.apply(
    lambda row: (
        row["home_official_name"]
        if row["louisville_is_visitor"]
        else row["visitor_official_name"]
    ),
    axis=1,
)

louisville_df["louisville_win"] = louisville_df.apply(
    lambda row: (
        row["visitor_win"]
        if row["louisville_is_visitor"]
        else row["home_win"]
    ),
    axis=1,
)

louisville_df["louisville_moneyline"] = louisville_df.apply(
    lambda row: (
        row["visitor_moneyline"]
        if row["louisville_is_visitor"]
        else row["home_moneyline"]
    ),
    axis=1,
)

louisville_df["louisville_no_vig_prob"] = louisville_df.apply(
    lambda row: (
        row["visitor_no_vig_prob"]
        if row["louisville_is_visitor"]
        else row["home_no_vig_prob"]
    ),
    axis=1,
)

louisville_df["louisville_market_role"] = louisville_df.apply(
    lambda row: (
        row["visitor_market_role"]
        if row["louisville_is_visitor"]
        else row["home_market_role"]
    ),
    axis=1,
)

louisville_df["louisville_pricing_error"] = (
    louisville_df["louisville_win"]
    - louisville_df["louisville_no_vig_prob"]
)

louisville_df.to_csv(
    LOUISVILLE_OUTPUT_PATH,
    index=False,
)

print("Real market analysis complete.")
print("Calibration saved to:", CALIBRATION_OUTPUT_PATH)
print("Segment summary saved to:", SEGMENT_OUTPUT_PATH)
print("Metrics saved to:", METRICS_OUTPUT_PATH)
print("Louisville analysis saved to:", LOUISVILLE_OUTPUT_PATH)

print()
print("Overall metrics:")
print(metrics_df)

print()
print("Calibration:")
print(calibration_df)

print()
print("Segment summary:")
print(combined_segments_df)

print()
print("Louisville summary:")
print("Games:", len(louisville_df))
print(
    "Win rate:",
    round(louisville_df["louisville_win"].mean(), 4),
)
print(
    "Average market probability:",
    round(louisville_df["louisville_no_vig_prob"].mean(), 4),
)
print(
    "Average pricing error:",
    round(louisville_df["louisville_pricing_error"].mean(), 4),
)