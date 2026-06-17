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

BACKTEST_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "backtests"
)


TABLE_FILES = {
    "market_strategy_backtests": (
        "market_strategy_summary_2021_22.csv"
    ),
    "probability_bucket_backtests": (
        "probability_bucket_backtest_2021_22.csv"
    ),
    "strategy_bootstrap_uncertainty": (
        "strategy_bootstrap_uncertainty_2021_22.csv"
    ),
    "bucket_bootstrap_uncertainty": (
        "bucket_bootstrap_uncertainty_2021_22.csv"
    ),
    "candidate_edge_time_validation": (
        "candidate_edge_time_validation_2021_22.csv"
    ),
    "candidate_edge_location_validation": (
        "candidate_edge_location_validation_2021_22.csv"
    ),
    "candidate_edge_monthly_validation": (
        "candidate_edge_monthly_validation_2021_22.csv"
    ),
    "bucket_multiple_testing_adjustment": (
        "bucket_multiple_testing_adjustment_2021_22.csv"
    ),
}


loaded_tables = []

with sqlite3.connect(DATABASE_PATH) as connection:
    for table_name, filename in TABLE_FILES.items():
        file_path = BACKTEST_DIR / filename

        if not file_path.exists():
            raise FileNotFoundError(
                f"Required backtest file not found: {file_path}"
            )

        dataframe = pd.read_csv(file_path)

        dataframe.to_sql(
            table_name,
            connection,
            if_exists="replace",
            index=False,
        )

        loaded_tables.append(
            {
                "table": table_name,
                "rows": len(dataframe),
            }
        )

    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS
        idx_bucket_adjustment_probability
        ON bucket_multiple_testing_adjustment(
            probability_bucket
        )
        """
    )

    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS
        idx_monthly_validation_month
        ON candidate_edge_monthly_validation(
            month
        )
        """
    )


loaded_tables_df = pd.DataFrame(
    loaded_tables
)

print("Backtest results loaded into SQLite.")
print()
print(
    loaded_tables_df.to_string(
        index=False
    )
)
print()
print("Database:", DATABASE_PATH)