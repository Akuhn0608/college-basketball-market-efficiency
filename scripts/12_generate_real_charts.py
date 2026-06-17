from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


CALIBRATION_PATH = Path(
    "data/processed/real_calibration_2021_22.csv"
)

SEGMENT_PATH = Path(
    "data/processed/real_segment_summary_2021_22.csv"
)

LOUISVILLE_PATH = Path(
    "data/processed/louisville_market_analysis_2021_22.csv"
)

CHART_DIR = Path("reports/charts")
CHART_DIR.mkdir(parents=True, exist_ok=True)


calibration_df = pd.read_csv(CALIBRATION_PATH)
segment_df = pd.read_csv(SEGMENT_PATH)
louisville_df = pd.read_csv(
    LOUISVILLE_PATH,
    parse_dates=["game_date"],
)


# 1. Real market calibration chart
plt.figure(figsize=(8, 6))

plt.plot(
    calibration_df["avg_market_prob"],
    calibration_df["actual_win_rate"],
    marker="o",
    label="2021–22 market calibration",
)

plt.plot(
    [0, 1],
    [0, 1],
    linestyle="--",
    label="Perfect calibration",
)

plt.xlabel("Average No-Vig Market Probability")
plt.ylabel("Actual Win Rate")
plt.title("NCAA Basketball Moneyline Calibration, 2021–22")
plt.legend()
plt.grid(True)

calibration_chart_path = (
    CHART_DIR / "real_calibration_2021_22.png"
)

plt.savefig(
    calibration_chart_path,
    bbox_inches="tight",
)
plt.close()


# 2. Favorite and underdog pricing error
segment_df["segment_label"] = (
    segment_df["team_location"].str.title()
    + " "
    + segment_df["market_role"].str.title()
)

plt.figure(figsize=(9, 6))

plt.bar(
    segment_df["segment_label"],
    segment_df["avg_pricing_error"] * 100,
)

plt.axhline(
    0,
    linestyle="--",
)

plt.xlabel("Team Segment")
plt.ylabel("Average Pricing Error, Percentage Points")
plt.title("Pricing Error by Location and Market Role, 2021–22")
plt.xticks(rotation=20)

segment_chart_path = (
    CHART_DIR / "real_segment_pricing_error_2021_22.png"
)

plt.savefig(
    segment_chart_path,
    bbox_inches="tight",
)
plt.close()


# 3. Louisville expected versus actual cumulative wins
louisville_df = louisville_df.sort_values(
    "game_date"
).reset_index(drop=True)

louisville_df["cumulative_actual_wins"] = (
    louisville_df["louisville_win"].cumsum()
)

louisville_df["cumulative_expected_wins"] = (
    louisville_df["louisville_no_vig_prob"].cumsum()
)

plt.figure(figsize=(10, 6))

plt.plot(
    louisville_df["game_date"],
    louisville_df["cumulative_actual_wins"],
    marker="o",
    label="Actual cumulative wins",
)

plt.plot(
    louisville_df["game_date"],
    louisville_df["cumulative_expected_wins"],
    marker="o",
    label="Market-expected cumulative wins",
)

plt.xlabel("Game Date")
plt.ylabel("Cumulative Wins")
plt.title("Louisville Actual vs. Market-Expected Wins, 2021–22")
plt.legend()
plt.grid(True)
plt.xticks(rotation=30)

louisville_chart_path = (
    CHART_DIR / "louisville_expected_vs_actual_2021_22.png"
)

plt.savefig(
    louisville_chart_path,
    bbox_inches="tight",
)
plt.close()


print("Real charts generated.")
print("Calibration chart:", calibration_chart_path)
print("Segment chart:", segment_chart_path)
print("Louisville chart:", louisville_chart_path)