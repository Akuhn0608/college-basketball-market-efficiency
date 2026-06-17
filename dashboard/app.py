import sys
from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))


st.set_page_config(
    page_title="College Basketball Market Efficiency",
    layout="wide",
)

st.title("College Basketball Market Efficiency Research Platform")

st.caption(
    "Analysis of 2021–22 NCAA men's basketball closing moneylines, "
    "no-vig probabilities, market calibration, and Louisville pricing."
)

DATA_DIR = PROJECT_ROOT / "data" / "processed"
CHART_DIR = PROJECT_ROOT / "reports" / "charts"

market_path = DATA_DIR / "ncaab_market_probabilities_2021_22.csv"
calibration_path = DATA_DIR / "real_calibration_2021_22.csv"
segment_path = DATA_DIR / "real_segment_summary_2021_22.csv"
metrics_path = DATA_DIR / "real_metrics_2021_22.csv"
louisville_path = DATA_DIR / "louisville_market_analysis_2021_22.csv"

calibration_chart_path = CHART_DIR / "real_calibration_2021_22.png"
segment_chart_path = CHART_DIR / "real_segment_pricing_error_2021_22.png"
louisville_chart_path = CHART_DIR / "louisville_expected_vs_actual_2021_22.png"

market_df = pd.read_csv(
    market_path,
    parse_dates=["game_date"],
)

calibration_df = pd.read_csv(calibration_path)
segment_df = pd.read_csv(segment_path)
metrics_df = pd.read_csv(metrics_path)

louisville_df = pd.read_csv(
    louisville_path,
    parse_dates=["game_date"],
)

brier_score = metrics_df.loc[
    metrics_df["metric"] == "brier_score",
    "value",
].iloc[0]

log_loss = metrics_df.loc[
    metrics_df["metric"] == "log_loss",
    "value",
].iloc[0]


st.header("Market Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Games analyzed",
        f"{len(market_df):,}",
    )

with col2:
    st.metric(
        "Average sportsbook vig",
        f"{market_df['market_vig'].mean() * 100:.2f}%",
    )

with col3:
    st.metric(
        "Visitor win rate",
        f"{market_df['visitor_win'].mean() * 100:.1f}%",
    )

with col4:
    st.metric(
        "Home win rate",
        f"{market_df['home_win'].mean() * 100:.1f}%",
    )


st.header("Probability Accuracy")

metric_col1, metric_col2 = st.columns(2)

with metric_col1:
    st.metric(
        "Brier score",
        f"{brier_score:.4f}",
    )

with metric_col2:
    st.metric(
        "Log loss",
        f"{log_loss:.4f}",
    )

st.write(
    "Lower values indicate more accurate probability forecasts. "
    "These metrics evaluate whether no-vig market probabilities "
    "were consistent with actual game outcomes."
)


st.header("Market Calibration")

st.write(
    "Calibration compares average market-implied probability with "
    "the actual win rate for teams in each probability bucket. "
    "Points near the diagonal indicate stronger calibration."
)

st.image(str(calibration_chart_path))

st.dataframe(
    calibration_df,
    use_container_width=True,
)


st.header("Favorite and Underdog Segments")

st.write(
    "Pricing error is actual outcome minus market probability. "
    "Positive values indicate that a segment won more frequently "
    "than its average market probability predicted."
)

st.image(str(segment_chart_path))

st.dataframe(
    segment_df,
    use_container_width=True,
)


st.header("Louisville Basketball Pricing Case Study")

louisville_expected_wins = (
    louisville_df["louisville_no_vig_prob"].sum()
)

louisville_actual_wins = (
    louisville_df["louisville_win"].sum()
)

lou_col1, lou_col2, lou_col3, lou_col4 = st.columns(4)

with lou_col1:
    st.metric(
        "Louisville games",
        len(louisville_df),
    )

with lou_col2:
    st.metric(
        "Actual wins",
        int(louisville_actual_wins),
    )

with lou_col3:
    st.metric(
        "Market-expected wins",
        f"{louisville_expected_wins:.1f}",
    )

with lou_col4:
    st.metric(
        "Win shortfall",
        f"{louisville_actual_wins - louisville_expected_wins:.1f}",
    )

st.write(
    "Across the 2021–22 season, Louisville won fewer games than its "
    "closing no-vig moneyline probabilities implied. This reflects "
    "one season of performance and should not by itself be interpreted "
    "as evidence of a persistent market bias."
)

st.image(str(louisville_chart_path))

louisville_display_df = louisville_df[
    [
        "game_date",
        "opponent",
        "louisville_win",
        "louisville_moneyline",
        "louisville_no_vig_prob",
        "louisville_market_role",
        "louisville_pricing_error",
    ]
].copy()

louisville_display_df["louisville_no_vig_prob"] = (
    louisville_display_df["louisville_no_vig_prob"] * 100
).round(1)

louisville_display_df["louisville_pricing_error"] = (
    louisville_display_df["louisville_pricing_error"] * 100
).round(1)

louisville_display_df = louisville_display_df.rename(
    columns={
        "game_date": "Date",
        "opponent": "Opponent",
        "louisville_win": "Win",
        "louisville_moneyline": "Moneyline",
        "louisville_no_vig_prob": "No-vig probability (%)",
        "louisville_market_role": "Market role",
        "louisville_pricing_error": "Pricing error (pp)",
    }
)

st.dataframe(
    louisville_display_df,
    use_container_width=True,
)


st.header("Real Game-Level Market Data")

display_columns = [
    "game_date",
    "visitor_official_name",
    "home_official_name",
    "visitor_score",
    "home_score",
    "visitor_moneyline",
    "home_moneyline",
    "visitor_no_vig_prob",
    "home_no_vig_prob",
    "market_vig",
]

st.dataframe(
    market_df[display_columns],
    use_container_width=True,
)