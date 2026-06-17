import sys
from pathlib import Path

import pandas as pd

# Add the main project folder to Python's import path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.calibration import create_probability_buckets, summarize_by_segment
from src.metrics import calculate_brier_score, calculate_log_loss


input_path = "data/processed/sample_cbb_odds_clean.csv"

calibration_output_path = "data/processed/sample_calibration.csv"
segment_output_path = "data/processed/sample_segment_summary.csv"
metrics_output_path = "data/processed/sample_metrics.csv"

df = pd.read_csv(input_path)

# 1. Calibration by probability bucket
calibration_df = create_probability_buckets(
    df=df,
    prob_col="team_a_no_vig_prob",
    outcome_col="team_a_win",
    bucket_size=0.10
)

calibration_df.to_csv(calibration_output_path, index=False)

# 2. Favorite vs. underdog segment summary
segment_df = summarize_by_segment(
    df=df,
    segment_col="team_a_market_role",
    prob_col="team_a_no_vig_prob",
    outcome_col="team_a_win"
)

segment_df.to_csv(segment_output_path, index=False)

# 3. Overall probability accuracy metrics
brier = calculate_brier_score(
    outcomes=df["team_a_win"],
    probabilities=df["team_a_no_vig_prob"]
)

logloss = calculate_log_loss(
    outcomes=df["team_a_win"],
    probabilities=df["team_a_no_vig_prob"]
)

metrics_df = pd.DataFrame(
    [
        {"metric": "brier_score", "value": brier},
        {"metric": "log_loss", "value": logloss},
    ]
)

metrics_df.to_csv(metrics_output_path, index=False)

print("Market efficiency analysis complete.")
print("Calibration saved to:", calibration_output_path)
print("Segment summary saved to:", segment_output_path)
print("Metrics saved to:", metrics_output_path)
print()
print("Metrics:")
print(metrics_df)