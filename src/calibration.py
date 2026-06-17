import pandas as pd


def create_probability_buckets(
    df: pd.DataFrame,
    prob_col: str,
    outcome_col: str,
    bucket_size: float = 0.10
) -> pd.DataFrame:
    """
    Group games into probability buckets and compare market-implied probabilities
    against actual win rates.

    Example:
    If the market says teams in a bucket have about a 60% chance to win,
    do they actually win about 60% of the time?
    """
    clean_df = df.copy()

    bins = [i * bucket_size for i in range(int(1 / bucket_size) + 1)]

    clean_df["prob_bucket"] = pd.cut(
        clean_df[prob_col],
        bins=bins,
        include_lowest=True
    )

    calibration_df = (
        clean_df
        .groupby("prob_bucket", observed=True)
        .agg(
            games=(outcome_col, "count"),
            avg_market_prob=(prob_col, "mean"),
            actual_win_rate=(outcome_col, "mean")
        )
        .reset_index()
    )

    calibration_df["calibration_error"] = (
        calibration_df["actual_win_rate"] - calibration_df["avg_market_prob"]
    )

    return calibration_df


def summarize_by_segment(
    df: pd.DataFrame,
    segment_col: str,
    prob_col: str,
    outcome_col: str
) -> pd.DataFrame:
    """
    Summarize market performance by a segment, such as favorite vs. underdog.

    For each segment, calculate:
    - number of games
    - average market probability
    - actual win rate
    - average pricing error
    """
    segment_df = (
        df
        .groupby(segment_col)
        .agg(
            games=(outcome_col, "count"),
            avg_market_prob=(prob_col, "mean"),
            actual_win_rate=(outcome_col, "mean")
        )
        .reset_index()
    )

    segment_df["avg_pricing_error"] = (
        segment_df["actual_win_rate"] - segment_df["avg_market_prob"]
    )

    return segment_df