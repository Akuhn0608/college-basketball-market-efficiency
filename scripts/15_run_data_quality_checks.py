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

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "sql_outputs"
    / "data_quality_report.csv"
)


quality_queries = {
    "duplicate_game_ids": """
        SELECT COUNT(*) AS issue_count
        FROM (
            SELECT game_id
            FROM games
            GROUP BY game_id
            HAVING COUNT(*) > 1
        );
    """,

    "missing_team_ids": """
        SELECT COUNT(*) AS issue_count
        FROM games
        WHERE visitor_team_id IS NULL
           OR home_team_id IS NULL;
    """,

    "missing_moneylines": """
        SELECT COUNT(*) AS issue_count
        FROM market_prices
        WHERE visitor_moneyline IS NULL
           OR home_moneyline IS NULL;
    """,

    "invalid_scores": """
        SELECT COUNT(*) AS issue_count
        FROM games
        WHERE visitor_score < 0
           OR home_score < 0
           OR visitor_score IS NULL
           OR home_score IS NULL;
    """,

    "invalid_outcomes": """
        SELECT COUNT(*) AS issue_count
        FROM games
        WHERE visitor_win NOT IN (0, 1)
           OR home_win NOT IN (0, 1)
           OR visitor_win + home_win != 1;
    """,

    "invalid_probabilities": """
        SELECT COUNT(*) AS issue_count
        FROM market_prices
        WHERE visitor_no_vig_prob <= 0
           OR visitor_no_vig_prob >= 1
           OR home_no_vig_prob <= 0
           OR home_no_vig_prob >= 1;
    """,

    "probabilities_not_summing_to_one": """
        SELECT COUNT(*) AS issue_count
        FROM market_prices
        WHERE ABS(
            visitor_no_vig_prob
            + home_no_vig_prob
            - 1.0
        ) > 0.000001;
    """,

    "games_without_market_record": """
        SELECT COUNT(*) AS issue_count
        FROM games AS g
        LEFT JOIN market_prices AS mp
            ON g.game_id = mp.game_id
        WHERE mp.game_id IS NULL;
    """,

    "market_records_without_game": """
        SELECT COUNT(*) AS issue_count
        FROM market_prices AS mp
        LEFT JOIN games AS g
            ON mp.game_id = g.game_id
        WHERE g.game_id IS NULL;
    """,
}


results = []

with sqlite3.connect(DATABASE_PATH) as connection:
    for check_name, query in quality_queries.items():
        result_df = pd.read_sql_query(
            query,
            connection,
        )

        issue_count = int(
            result_df["issue_count"].iloc[0]
        )

        results.append(
            {
                "check_name": check_name,
                "issue_count": issue_count,
                "status": (
                    "PASS"
                    if issue_count == 0
                    else "FAIL"
                ),
            }
        )


quality_report_df = pd.DataFrame(results)

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)

quality_report_df.to_csv(
    OUTPUT_PATH,
    index=False,
)

print("Data-quality checks complete.")
print()
print(quality_report_df.to_string(index=False))
print()

failed_checks = quality_report_df[
    quality_report_df["status"] == "FAIL"
]

if failed_checks.empty:
    print("All data-quality checks passed.")
else:
    print(
        "Warning:",
        len(failed_checks),
        "data-quality checks failed.",
    )