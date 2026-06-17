import argparse
import subprocess
import sys
import time
from pathlib import Path
from typing import List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"


CORE_PIPELINE = [
    "05_build_real_game_data.py",
    "07_clean_odds_2021_22.py",
    "09_map_odds_team_names.py",
    "10_calculate_real_market_probabilities.py",
    "11_analyze_real_market_efficiency.py",
    "12_generate_real_charts.py",
    "13_build_sql_database.py",
    "14_run_sql_analysis.py",
    "15_run_data_quality_checks.py",
    "16_run_market_backtests.py",
    "17_bootstrap_backtest_uncertainty.py",
    "18_validate_candidate_edge.py",
    "19_adjust_for_multiple_testing.py",
    "20_load_backtests_to_sql.py",
]


DOWNLOAD_SCRIPT = "06_download_odds_2021_22.py"


def run_script(script_name: str) -> None:
    """
    Run one project script and stop the pipeline if it fails.
    """

    script_path = SCRIPTS_DIR / script_name

    if not script_path.exists():
        raise FileNotFoundError(
            f"Pipeline script not found: {script_path}"
        )

    print()
    print("=" * 72)
    print(f"Running: {script_name}")
    print("=" * 72)

    start_time = time.time()

    completed_process = subprocess.run(
        [
            sys.executable,
            str(script_path),
        ],
        cwd=PROJECT_ROOT,
        check=False,
    )

    elapsed_seconds = time.time() - start_time

    if completed_process.returncode != 0:
        print()
        print(
            f"Pipeline stopped because {script_name} failed "
            f"with exit code {completed_process.returncode}."
        )

        sys.exit(
            completed_process.returncode
        )

    print()
    print(
        f"Completed {script_name} "
        f"in {elapsed_seconds:.1f} seconds."
    )


def build_pipeline(
    include_download: bool,
) -> List[str]:
    """
    Return the ordered list of scripts to execute.
    """

    pipeline = CORE_PIPELINE.copy()

    if include_download:
        download_position = pipeline.index(
            "07_clean_odds_2021_22.py"
        )

        pipeline.insert(
            download_position,
            DOWNLOAD_SCRIPT,
        )

    return pipeline


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run the full college basketball market-efficiency "
            "analysis pipeline."
        )
    )

    parser.add_argument(
        "--include-download",
        action="store_true",
        help=(
            "Download the 2021–22 odds archive before cleaning. "
            "Leave this off when the raw odds file already exists."
        ),
    )

    args = parser.parse_args()

    pipeline = build_pipeline(
        include_download=args.include_download,
    )

    print("College Basketball Market Efficiency Pipeline")
    print()
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Python executable: {sys.executable}")
    print(f"Scripts scheduled: {len(pipeline)}")

    pipeline_start_time = time.time()

    for script_name in pipeline:
        run_script(script_name)

    total_seconds = (
        time.time()
        - pipeline_start_time
    )

    print()
    print("=" * 72)
    print("FULL PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 72)
    print(
        f"Total execution time: "
        f"{total_seconds:.1f} seconds"
    )
    print()
    print("Final outputs include:")
    print("- cleaned and mapped market data")
    print("- no-vig probabilities and calibration metrics")
    print("- charts and Louisville analysis")
    print("- SQLite relational database")
    print("- SQL analytical outputs")
    print("- automated data-quality report")
    print("- backtesting and risk metrics")
    print("- bootstrap and robustness analysis")
    print("- multiple-testing-adjusted results")


if __name__ == "__main__":
    main()
