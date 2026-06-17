from pathlib import Path
import sqlite3

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATABASE_PATH = (
    PROJECT_ROOT
    / "data"
    / "database"
    / "cbb_market_efficiency.db"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "sql_outputs"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


market_overview_query = """
SELECT
    COUNT(*) AS games_analyzed,
    ROUND(AVG(mp.market_vig) * 100, 2) AS average_vig_pct,
    ROUND(AVG(g.visitor_win) * 100, 2) AS visitor_win_rate_pct,
    ROUND(AVG(g.home_win) * 100, 2) AS home_win_rate_pct
FROM games AS g
JOIN market_prices AS mp
    ON g.game_id = mp.game_id;
"""


segment_query = """
WITH team_market_observations AS (
    SELECT
        g.game_id,
        'visitor' AS team_location,
        mp.visitor_market_role AS market_role,
        mp.visitor_no_vig_prob AS market_probability,
        g.visitor_win AS actual_win
    FROM games AS g
    JOIN market_prices AS mp
        ON g.game_id = mp.game_id

    UNION ALL

    SELECT
        g.game_id,
        'home' AS team_location,
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
    COUNT(*) AS team_games,
    ROUND(AVG(market_probability) * 100, 2) AS avg_market_probability_pct,
    ROUND(AVG(actual_win) * 100, 2) AS actual_win_rate_pct,
    ROUND(
        (AVG(actual_win) - AVG(market_probability)) * 100,
        2
    ) AS pricing_error_pp
FROM team_market_observations
GROUP BY
    team_location,
    market_role
ORDER BY
    team_location,
    market_role;
"""


team_performance_query = """
WITH team_observations AS (
    SELECT
        g.game_id,
        g.game_date,
        g.visitor_team_id AS team_id,
        g.visitor_win AS win,
        mp.visitor_no_vig_prob AS market_probability
    FROM games AS g
    JOIN market_prices AS mp
        ON g.game_id = mp.game_id

    UNION ALL

    SELECT
        g.game_id,
        g.game_date,
        g.home_team_id AS team_id,
        g.home_win AS win,
        mp.home_no_vig_prob AS market_probability
    FROM games AS g
    JOIN market_prices AS mp
        ON g.game_id = mp.game_id
)

SELECT
    t.team_name,
    COUNT(*) AS games,
    SUM(o.win) AS actual_wins,
    ROUND(SUM(o.market_probability), 2) AS expected_wins,
    ROUND(
        SUM(o.win) - SUM(o.market_probability),
        2
    ) AS wins_above_expectation
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


louisville_rolling_query = """
SELECT
    game_date,
    opponent,
    louisville_win,
    ROUND(louisville_no_vig_prob * 100, 2) AS market_probability_pct,

    SUM(louisville_win) OVER (
        ORDER BY game_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_actual_wins,

    ROUND(
        SUM(louisville_no_vig_prob) OVER (
            ORDER BY game_date
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ),
        2
    ) AS cumulative_expected_wins,

    ROUND(
        AVG(louisville_pricing_error) OVER (
            ORDER BY game_date
            ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
        ) * 100,
        2
    ) AS rolling_5_game_pricing_error_pp

FROM louisville_case_study
ORDER BY game_date;
"""


with sqlite3.connect(DATABASE_PATH) as connection:
    market_overview_df = pd.read_sql_query(
        market_overview_query,
        connection,
    )

    segment_df = pd.read_sql_query(
        segment_query,
        connection,
    )

    team_performance_df = pd.read_sql_query(
        team_performance_query,
        connection,
    )

    louisville_rolling_df = pd.read_sql_query(
        louisville_rolling_query,
        connection,
    )


market_overview_df.to_csv(
    OUTPUT_DIR / "market_overview.csv",
    index=False,
)

segment_df.to_csv(
    OUTPUT_DIR / "segment_summary.csv",
    index=False,
)

team_performance_df.to_csv(
    OUTPUT_DIR / "team_performance.csv",
    index=False,
)

louisville_rolling_df.to_csv(
    OUTPUT_DIR / "louisville_rolling.csv",
    index=False,
)


print("SQL analysis complete.")
print()
print("Outputs saved to:", OUTPUT_DIR)
print()
print("Market overview:")
print(market_overview_df)
print()
print("Top 10 teams above expectation:")
print(team_performance_df.head(10))
print()
print("Louisville rolling analysis:")
print(louisville_rolling_df.tail(10))