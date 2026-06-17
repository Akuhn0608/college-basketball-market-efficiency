from typing import List, Optional, Tuple
import sqlite3
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

DATA_DIR = PROJECT_ROOT / "data" / "processed"
SQL_OUTPUT_DIR = DATA_DIR / "sql_outputs"
DATABASE_PATH = (
    PROJECT_ROOT
    / "data"
    / "database"
    / "cbb_market_efficiency.db"
)
CHART_DIR = PROJECT_ROOT / "reports" / "charts"


st.set_page_config(
    page_title="College Basketball Market Efficiency",
    page_icon="🏀",
    layout="wide",
)

st.title("College Basketball Market Efficiency Research Platform")

st.caption(
    "SQL-powered analysis of 2021–22 NCAA men's basketball closing "
    "moneylines, no-vig probabilities, market calibration, team "
    "performance, and Louisville pricing."
)


if not DATABASE_PATH.exists():
    st.error(
        "The SQLite database was not found. Run "
        "`python scripts/13_build_sql_database.py` before launching "
        "the dashboard."
    )
    st.stop()


@st.cache_data
def run_sql_query(
    query: str,
    params: Optional[Tuple] = None,
) -> pd.DataFrame:
    """Run a SQL query against the project SQLite database."""

    with sqlite3.connect(DATABASE_PATH) as connection:
        return pd.read_sql_query(
            query,
            connection,
            params=params,
        )


@st.cache_data
def load_csv(
    path: Path,
    parse_dates: Optional[List[str]] = None,
) -> pd.DataFrame:
    """Load a project CSV file."""

    return pd.read_csv(
        path,
        parse_dates=parse_dates,
    )


market_overview_query = """
SELECT
    COUNT(*) AS games_analyzed,
    AVG(mp.market_vig) AS average_vig,
    AVG(g.visitor_win) AS visitor_win_rate,
    AVG(g.home_win) AS home_win_rate
FROM games AS g
JOIN market_prices AS mp
    ON g.game_id = mp.game_id;
"""


team_rankings_query = """
WITH team_observations AS (
    SELECT
        g.game_id,
        g.game_date,
        g.visitor_team_id AS team_id,
        g.visitor_win AS actual_win,
        mp.visitor_no_vig_prob AS market_probability
    FROM games AS g
    JOIN market_prices AS mp
        ON g.game_id = mp.game_id

    UNION ALL

    SELECT
        g.game_id,
        g.game_date,
        g.home_team_id AS team_id,
        g.home_win AS actual_win,
        mp.home_no_vig_prob AS market_probability
    FROM games AS g
    JOIN market_prices AS mp
        ON g.game_id = mp.game_id
)

SELECT
    t.team_name,
    COUNT(*) AS games,
    SUM(o.actual_win) AS actual_wins,
    SUM(o.market_probability) AS expected_wins,
    SUM(o.actual_win) - SUM(o.market_probability)
        AS wins_above_expectation
FROM team_observations AS o
JOIN teams AS t
    ON o.team_id = t.team_id
GROUP BY
    t.team_id,
    t.team_name
HAVING COUNT(*) >= 20
ORDER BY
    wins_above_expectation DESC;
"""


segment_query = """
WITH team_market_observations AS (
    SELECT
        'Visitor' AS team_location,
        mp.visitor_market_role AS market_role,
        mp.visitor_no_vig_prob AS market_probability,
        g.visitor_win AS actual_win
    FROM games AS g
    JOIN market_prices AS mp
        ON g.game_id = mp.game_id

    UNION ALL

    SELECT
        'Home' AS team_location,
        mp.home_market_role AS market_role,
        mp.home_no_vig_prob AS market_probability,
        g.home_win AS actual_win
    FROM games AS g
    JOIN market_prices AS mp
        ON g.game_id = mp.game_id
)

SELECT
    team_location,
    market_role,
    COUNT(*) AS games,
    AVG(market_probability) AS average_market_probability,
    AVG(actual_win) AS actual_win_rate,
    AVG(actual_win) - AVG(market_probability)
        AS pricing_error
FROM team_market_observations
GROUP BY
    team_location,
    market_role
ORDER BY
    team_location,
    market_role;
"""


louisville_rolling_query = """
SELECT
    game_date,
    opponent,
    louisville_win,
    louisville_no_vig_prob AS market_probability,

    SUM(louisville_win) OVER (
        ORDER BY game_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_actual_wins,

    SUM(louisville_no_vig_prob) OVER (
        ORDER BY game_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_expected_wins,

    AVG(louisville_pricing_error) OVER (
        ORDER BY game_date
        ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
    ) AS rolling_5_game_pricing_error

FROM louisville_case_study
ORDER BY game_date;
"""


market_overview_df = run_sql_query(market_overview_query)
team_rankings_df = run_sql_query(team_rankings_query)
segment_sql_df = run_sql_query(segment_query)
louisville_rolling_df = run_sql_query(louisville_rolling_query)

louisville_rolling_df["game_date"] = pd.to_datetime(
    louisville_rolling_df["game_date"]
)


metrics_df = load_csv(
    DATA_DIR / "real_metrics_2021_22.csv"
)

calibration_df = load_csv(
    DATA_DIR / "real_calibration_2021_22.csv"
)

louisville_df = load_csv(
    DATA_DIR / "louisville_market_analysis_2021_22.csv",
    parse_dates=["game_date"],
)


quality_report_path = (
    SQL_OUTPUT_DIR
    / "data_quality_report.csv"
)

if quality_report_path.exists():
    quality_report_df = load_csv(quality_report_path)
else:
    quality_report_df = pd.DataFrame(
        columns=[
            "check_name",
            "issue_count",
            "status",
        ]
    )


brier_score = metrics_df.loc[
    metrics_df["metric"] == "brier_score",
    "value",
].iloc[0]

log_loss = metrics_df.loc[
    metrics_df["metric"] == "log_loss",
    "value",
].iloc[0]

overview = market_overview_df.iloc[0]


overview_tab, teams_tab, louisville_tab, quality_tab = st.tabs(
    [
        "Market Overview",
        "Team Explorer",
        "Louisville Case Study",
        "Data Quality",
    ]
)


with overview_tab:
    st.subheader("SQL-Powered Market Overview")

    st.caption(
        "These metrics are calculated directly from the SQLite "
        "games and market_prices tables."
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Games analyzed",
            f"{int(overview['games_analyzed']):,}",
        )

    with col2:
        st.metric(
            "Average sportsbook vig",
            f"{overview['average_vig'] * 100:.2f}%",
        )

    with col3:
        st.metric(
            "Visitor win rate",
            f"{overview['visitor_win_rate'] * 100:.1f}%",
        )

    with col4:
        st.metric(
            "Home win rate",
            f"{overview['home_win_rate'] * 100:.1f}%",
        )

    st.subheader("Probability Accuracy")

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
        "Lower Brier score and log loss values indicate more "
        "accurate probability estimates. These metrics evaluate "
        "whether closing no-vig probabilities aligned with actual "
        "game outcomes."
    )

    st.subheader("Market Calibration")

    st.write(
        "Calibration compares average market-implied probability "
        "with actual win rate. A well-calibrated market should "
        "produce similar values."
    )

    calibration_chart_path = (
        CHART_DIR
        / "real_calibration_2021_22.png"
    )

    if calibration_chart_path.exists():
        st.image(
            str(calibration_chart_path),
            use_container_width=True,
        )

    calibration_display_df = calibration_df.copy()

    calibration_display_df["avg_market_prob"] = (
        calibration_display_df["avg_market_prob"] * 100
    ).round(2)

    calibration_display_df["actual_win_rate"] = (
        calibration_display_df["actual_win_rate"] * 100
    ).round(2)

    calibration_display_df["calibration_error"] = (
        calibration_display_df["calibration_error"] * 100
    ).round(2)

    calibration_display_df = calibration_display_df.rename(
        columns={
            "prob_bucket": "Probability bucket",
            "games": "Team observations",
            "avg_market_prob": "Average market probability (%)",
            "actual_win_rate": "Actual win rate (%)",
            "calibration_error": "Calibration error (pp)",
        }
    )

    st.dataframe(
        calibration_display_df,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Favorite and Underdog Segments")

    segment_display_df = segment_sql_df.copy()

    segment_display_df["average_market_probability"] = (
        segment_display_df["average_market_probability"] * 100
    ).round(2)

    segment_display_df["actual_win_rate"] = (
        segment_display_df["actual_win_rate"] * 100
    ).round(2)

    segment_display_df["pricing_error"] = (
        segment_display_df["pricing_error"] * 100
    ).round(2)

    segment_display_df = segment_display_df.rename(
        columns={
            "team_location": "Location",
            "market_role": "Market role",
            "games": "Team observations",
            "average_market_probability": (
                "Average market probability (%)"
            ),
            "actual_win_rate": "Actual win rate (%)",
            "pricing_error": "Pricing error (pp)",
        }
    )

    st.dataframe(
        segment_display_df,
        use_container_width=True,
        hide_index=True,
    )


with teams_tab:
    st.subheader("Team Performance Relative to Market Expectations")

    st.write(
        "Actual wins are compared with expected wins calculated by "
        "summing each team's closing no-vig win probabilities."
    )

    ranking_option = st.radio(
        "Ranking view",
        [
            "Most above expectation",
            "Most below expectation",
        ],
        horizontal=True,
    )

    number_of_teams = st.slider(
        "Number of teams to display",
        min_value=5,
        max_value=25,
        value=10,
    )

    if ranking_option == "Most above expectation":
        ranking_chart_df = team_rankings_df.head(
            number_of_teams
        ).copy()

        ranking_chart_df = ranking_chart_df.sort_values(
            "wins_above_expectation"
        )

        chart_title = (
            "Teams Most Above Market-Expected Wins"
        )
    else:
        ranking_chart_df = team_rankings_df.tail(
            number_of_teams
        ).copy()

        ranking_chart_df = ranking_chart_df.sort_values(
            "wins_above_expectation",
            ascending=False,
        )

        chart_title = (
            "Teams Most Below Market-Expected Wins"
        )

    ranking_chart_df["wins_above_expectation"] = (
        ranking_chart_df["wins_above_expectation"]
        .round(2)
    )

    ranking_figure = px.bar(
        ranking_chart_df,
        x="wins_above_expectation",
        y="team_name",
        orientation="h",
        title=chart_title,
        labels={
            "wins_above_expectation": (
                "Actual wins minus expected wins"
            ),
            "team_name": "Team",
        },
    )

    st.plotly_chart(
        ranking_figure,
        use_container_width=True,
    )

    rankings_display_df = team_rankings_df.copy()

    rankings_display_df["expected_wins"] = (
        rankings_display_df["expected_wins"].round(2)
    )

    rankings_display_df["wins_above_expectation"] = (
        rankings_display_df[
            "wins_above_expectation"
        ].round(2)
    )

    rankings_display_df = rankings_display_df.rename(
        columns={
            "team_name": "Team",
            "games": "Games",
            "actual_wins": "Actual wins",
            "expected_wins": "Expected wins",
            "wins_above_expectation": (
                "Wins above expectation"
            ),
        }
    )

    st.dataframe(
        rankings_display_df,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Individual Team Explorer")

    selected_team = st.selectbox(
        "Choose a team",
        sorted(team_rankings_df["team_name"].tolist()),
    )

    team_games_query = """
    SELECT
        g.game_date,
        CASE
            WHEN vt.team_name = ?
                THEN ht.team_name
            ELSE vt.team_name
        END AS opponent,

        CASE
            WHEN vt.team_name = ?
                THEN 'Away'
            ELSE 'Home'
        END AS location,

        CASE
            WHEN vt.team_name = ?
                THEN g.visitor_win
            ELSE g.home_win
        END AS actual_win,

        CASE
            WHEN vt.team_name = ?
                THEN mp.visitor_no_vig_prob
            ELSE mp.home_no_vig_prob
        END AS market_probability,

        CASE
            WHEN vt.team_name = ?
                THEN mp.visitor_pricing_error
            ELSE mp.home_pricing_error
        END AS pricing_error

    FROM games AS g
    JOIN market_prices AS mp
        ON g.game_id = mp.game_id
    JOIN teams AS vt
        ON g.visitor_team_id = vt.team_id
    JOIN teams AS ht
        ON g.home_team_id = ht.team_id

    WHERE vt.team_name = ?
       OR ht.team_name = ?

    ORDER BY g.game_date;
    """

    team_games_df = run_sql_query(
        team_games_query,
        params=(
            selected_team,
            selected_team,
            selected_team,
            selected_team,
            selected_team,
            selected_team,
            selected_team,
        ),
    )

    team_games_df["game_date"] = pd.to_datetime(
        team_games_df["game_date"]
    )

    selected_team_summary = team_rankings_df.loc[
        team_rankings_df["team_name"] == selected_team
    ].iloc[0]

    team_col1, team_col2, team_col3, team_col4 = (
        st.columns(4)
    )

    with team_col1:
        st.metric(
            "Games",
            int(selected_team_summary["games"]),
        )

    with team_col2:
        st.metric(
            "Actual wins",
            int(selected_team_summary["actual_wins"]),
        )

    with team_col3:
        st.metric(
            "Expected wins",
            f"{selected_team_summary['expected_wins']:.1f}",
        )

    with team_col4:
        st.metric(
            "Wins vs. expectation",
            (
                f"{selected_team_summary['wins_above_expectation']:+.1f}"
            ),
        )

    team_games_df["cumulative_actual_wins"] = (
        team_games_df["actual_win"].cumsum()
    )

    team_games_df["cumulative_expected_wins"] = (
        team_games_df["market_probability"].cumsum()
    )

    team_trend_df = team_games_df.melt(
        id_vars=["game_date"],
        value_vars=[
            "cumulative_actual_wins",
            "cumulative_expected_wins",
        ],
        var_name="series",
        value_name="wins",
    )

    team_trend_df["series"] = team_trend_df[
        "series"
    ].replace(
        {
            "cumulative_actual_wins": (
                "Cumulative actual wins"
            ),
            "cumulative_expected_wins": (
                "Cumulative expected wins"
            ),
        }
    )

    team_figure = px.line(
        team_trend_df,
        x="game_date",
        y="wins",
        color="series",
        title=(
            f"{selected_team}: Actual vs. Market-Expected Wins"
        ),
        labels={
            "game_date": "Date",
            "wins": "Cumulative wins",
            "series": "",
        },
    )

    st.plotly_chart(
        team_figure,
        use_container_width=True,
    )

    team_display_df = team_games_df[
        [
            "game_date",
            "opponent",
            "location",
            "actual_win",
            "market_probability",
            "pricing_error",
        ]
    ].copy()

    team_display_df["market_probability"] = (
        team_display_df["market_probability"] * 100
    ).round(1)

    team_display_df["pricing_error"] = (
        team_display_df["pricing_error"] * 100
    ).round(1)

    team_display_df["actual_win"] = (
        team_display_df["actual_win"]
        .map(
            {
                1: "Win",
                0: "Loss",
            }
        )
    )

    team_display_df = team_display_df.rename(
        columns={
            "game_date": "Date",
            "opponent": "Opponent",
            "location": "Location",
            "actual_win": "Result",
            "market_probability": (
                "No-vig probability (%)"
            ),
            "pricing_error": "Pricing error (pp)",
        }
    )

    st.dataframe(
        team_display_df,
        use_container_width=True,
        hide_index=True,
    )


with louisville_tab:
    st.subheader("Louisville Basketball Pricing Case Study")

    louisville_actual_wins = (
        louisville_df["louisville_win"].sum()
    )

    louisville_expected_wins = (
        louisville_df["louisville_no_vig_prob"].sum()
    )

    louisville_average_probability = (
        louisville_df["louisville_no_vig_prob"].mean()
    )

    worst_rolling_error = (
        louisville_rolling_df[
            "rolling_5_game_pricing_error"
        ].min()
    )

    lou_col1, lou_col2, lou_col3, lou_col4 = (
        st.columns(4)
    )

    with lou_col1:
        st.metric(
            "Games",
            len(louisville_df),
        )

    with lou_col2:
        st.metric(
            "Actual wins",
            int(louisville_actual_wins),
        )

    with lou_col3:
        st.metric(
            "Expected wins",
            f"{louisville_expected_wins:.1f}",
        )

    with lou_col4:
        st.metric(
            "Largest 5-game pricing gap",
            f"{worst_rolling_error * 100:.1f} pp",
        )

    st.write(
        "Louisville entered many games with meaningful market-implied "
        "win probabilities but finished approximately four wins below "
        "the closing market's cumulative expectation."
    )

    louisville_trend_df = (
        louisville_rolling_df[
            [
                "game_date",
                "cumulative_actual_wins",
                "cumulative_expected_wins",
            ]
        ]
        .melt(
            id_vars=["game_date"],
            var_name="series",
            value_name="wins",
        )
    )

    louisville_trend_df["series"] = (
        louisville_trend_df["series"].replace(
            {
                "cumulative_actual_wins": (
                    "Cumulative actual wins"
                ),
                "cumulative_expected_wins": (
                    "Cumulative expected wins"
                ),
            }
        )
    )

    louisville_figure = px.line(
        louisville_trend_df,
        x="game_date",
        y="wins",
        color="series",
        title=(
            "Louisville Actual vs. Market-Expected Wins"
        ),
        labels={
            "game_date": "Date",
            "wins": "Cumulative wins",
            "series": "",
        },
    )

    st.plotly_chart(
        louisville_figure,
        use_container_width=True,
    )

    rolling_error_df = louisville_rolling_df.copy()

    rolling_error_df["rolling_5_game_pricing_error_pp"] = (
        rolling_error_df[
            "rolling_5_game_pricing_error"
        ] * 100
    )

    rolling_error_figure = px.line(
        rolling_error_df,
        x="game_date",
        y="rolling_5_game_pricing_error_pp",
        markers=True,
        title=(
            "Louisville Rolling Five-Game Pricing Error"
        ),
        labels={
            "game_date": "Date",
            "rolling_5_game_pricing_error_pp": (
                "Pricing error (percentage points)"
            ),
        },
    )

    rolling_error_figure.add_hline(
        y=0,
        line_dash="dash",
    )

    st.plotly_chart(
        rolling_error_figure,
        use_container_width=True,
    )

    st.write(
        "Negative pricing error indicates that Louisville won less "
        "frequently than its market-implied probabilities predicted "
        "during that rolling five-game period."
    )

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

    louisville_display_df["louisville_win"] = (
        louisville_display_df["louisville_win"]
        .map(
            {
                1: "Win",
                0: "Loss",
            }
        )
    )

    louisville_display_df["louisville_no_vig_prob"] = (
        louisville_display_df[
            "louisville_no_vig_prob"
        ] * 100
    ).round(1)

    louisville_display_df["louisville_pricing_error"] = (
        louisville_display_df[
            "louisville_pricing_error"
        ] * 100
    ).round(1)

    louisville_display_df = louisville_display_df.rename(
        columns={
            "game_date": "Date",
            "opponent": "Opponent",
            "louisville_win": "Result",
            "louisville_moneyline": "Moneyline",
            "louisville_no_vig_prob": (
                "No-vig probability (%)"
            ),
            "louisville_market_role": "Market role",
            "louisville_pricing_error": (
                "Pricing error (pp)"
            ),
        }
    )

    st.dataframe(
        louisville_display_df,
        use_container_width=True,
        hide_index=True,
    )


with quality_tab:
    st.subheader("Automated Data-Quality Monitoring")

    st.write(
        "The analytical pipeline validates game identifiers, team "
        "mappings, scores, outcomes, moneylines, probabilities, and "
        "relationships between SQL tables."
    )

    if quality_report_df.empty:
        st.warning(
            "The data-quality report has not been generated. Run "
            "`python scripts/15_run_data_quality_checks.py`."
        )
    else:
        passed_checks = (
            quality_report_df["status"] == "PASS"
        ).sum()

        failed_checks = (
            quality_report_df["status"] == "FAIL"
        ).sum()

        total_issues = quality_report_df[
            "issue_count"
        ].sum()

        quality_col1, quality_col2, quality_col3 = (
            st.columns(3)
        )

        with quality_col1:
            st.metric(
                "Checks passed",
                f"{passed_checks}/{len(quality_report_df)}",
            )

        with quality_col2:
            st.metric(
                "Checks failed",
                int(failed_checks),
            )

        with quality_col3:
            st.metric(
                "Total issues detected",
                int(total_issues),
            )

        if failed_checks == 0:
            st.success(
                "All automated data-quality checks passed."
            )
        else:
            st.error(
                "One or more data-quality checks failed."
            )

        quality_display_df = (
            quality_report_df.copy()
        )

        quality_display_df["check_name"] = (
            quality_display_df["check_name"]
            .str.replace("_", " ")
            .str.title()
        )

        quality_display_df = (
            quality_display_df.rename(
                columns={
                    "check_name": "Check",
                    "issue_count": "Issues",
                    "status": "Status",
                }
            )
        )

        st.dataframe(
            quality_display_df,
            use_container_width=True,
            hide_index=True,
        )

    st.subheader("Pipeline Architecture")

    st.code(
        """
Raw sportsbook and NCAA data
        ↓
Python cleaning and team-name mapping
        ↓
No-vig probability calculations
        ↓
SQLite relational database
        ↓
SQL joins, CTEs, aggregations, and window functions
        ↓
Automated data-quality validation
        ↓
Interactive Streamlit analytics dashboard
        """,
        language="text",
    )
