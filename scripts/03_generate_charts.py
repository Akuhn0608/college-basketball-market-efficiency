import sys
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

# Add the main project folder to Python's import path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))


calibration_input_path = "data/processed/sample_calibration.csv"
segment_input_path = "data/processed/sample_segment_summary.csv"

calibration_chart_path = "reports/charts/sample_calibration_chart.png"
segment_chart_path = "reports/charts/sample_segment_chart.png"

calibration_df = pd.read_csv(calibration_input_path)
segment_df = pd.read_csv(segment_input_path)

# 1. Calibration chart
plt.figure(figsize=(8, 6))

plt.plot(
    calibration_df["avg_market_prob"],
    calibration_df["actual_win_rate"],
    marker="o",
    label="Sample calibration"
)

plt.plot(
    [0, 1],
    [0, 1],
    linestyle="--",
    label="Perfect calibration"
)

plt.xlabel("Average Market-Implied Probability")
plt.ylabel("Actual Win Rate")
plt.title("Sample College Basketball Market Calibration")
plt.legend()
plt.grid(True)

plt.savefig(calibration_chart_path, bbox_inches="tight")
plt.close()

# 2. Segment chart: favorite vs. underdog pricing error
plt.figure(figsize=(8, 6))

plt.bar(
    segment_df["team_a_market_role"],
    segment_df["avg_pricing_error"]
)

plt.axhline(0, linestyle="--")

plt.xlabel("Market Role")
plt.ylabel("Average Pricing Error")
plt.title("Sample Pricing Error by Market Role")

plt.savefig(segment_chart_path, bbox_inches="tight")
plt.close()

print("Charts generated.")
print("Calibration chart saved to:", calibration_chart_path)
print("Segment chart saved to:", segment_chart_path)