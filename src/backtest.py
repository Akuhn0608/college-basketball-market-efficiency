from typing import Dict

import numpy as np
import pandas as pd


def american_odds_profit(
    american_odds: float,
    stake: float = 1.0,
) -> float:
    """
    Calculate profit on a winning American-odds wager.

    The returned value excludes the original stake.
    """

    if pd.isna(american_odds):
        raise ValueError("American odds cannot be missing.")

    if american_odds == 0:
        raise ValueError("American odds cannot equal zero.")

    if stake <= 0:
        raise ValueError("Stake must be greater than zero.")

    if american_odds > 0:
        return stake * (american_odds / 100)

    return stake * (100 / abs(american_odds))


def calculate_bet_return(
    american_odds: float,
    won: int,
    stake: float = 1.0,
) -> float:
    """
    Calculate net return for one flat-stake observation.

    Winning return:
        profit implied by American odds

    Losing return:
        negative stake
    """

    if won not in (0, 1):
        raise ValueError("won must equal either 0 or 1.")

    if won == 1:
        return american_odds_profit(
            american_odds=american_odds,
            stake=stake,
        )

    return -stake


def calculate_max_drawdown(
    returns: pd.Series,
) -> float:
    """
    Calculate maximum drawdown from sequential net returns.

    Returns a positive number representing the largest decline
    from a prior cumulative-profit peak.
    """

    if returns.empty:
        return 0.0

    cumulative_profit = returns.cumsum()

    equity_curve = pd.concat(
        [
            pd.Series([0.0]),
            cumulative_profit.reset_index(drop=True),
        ],
        ignore_index=True,
    )

    running_peak = equity_curve.cummax()
    drawdown = running_peak - equity_curve

    return float(drawdown.max())


def summarize_backtest(
    observations_df: pd.DataFrame,
    stake: float = 1.0,
) -> Dict[str, float]:
    """
    Summarize performance for a set of market observations.

    Required columns:
        american_odds
        actual_win
        game_date
    """

    required_columns = {
        "american_odds",
        "actual_win",
        "game_date",
    }

    missing_columns = (
        required_columns
        - set(observations_df.columns)
    )

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    clean_df = observations_df.dropna(
        subset=[
            "american_odds",
            "actual_win",
            "game_date",
        ]
    ).copy()

    clean_df = clean_df.sort_values(
        "game_date"
    ).reset_index(drop=True)

    if clean_df.empty:
        return {
            "bets": 0,
            "wins": 0,
            "losses": 0,
            "hit_rate": np.nan,
            "total_staked": 0.0,
            "net_profit": 0.0,
            "roi": np.nan,
            "average_return": np.nan,
            "return_volatility": np.nan,
            "sharpe_like_ratio": np.nan,
            "maximum_drawdown": 0.0,
        }

    clean_df["net_return"] = clean_df.apply(
        lambda row: calculate_bet_return(
            american_odds=row["american_odds"],
            won=int(row["actual_win"]),
            stake=stake,
        ),
        axis=1,
    )

    bets = len(clean_df)
    wins = int(clean_df["actual_win"].sum())
    losses = bets - wins

    total_staked = bets * stake
    net_profit = clean_df["net_return"].sum()
    roi = net_profit / total_staked

    average_return = clean_df["net_return"].mean()

    return_volatility = clean_df[
        "net_return"
    ].std(ddof=1)

    if (
        pd.isna(return_volatility)
        or return_volatility == 0
    ):
        sharpe_like_ratio = np.nan
    else:
        sharpe_like_ratio = (
            average_return
            / return_volatility
        )

    maximum_drawdown = calculate_max_drawdown(
        clean_df["net_return"]
    )

    return {
        "bets": bets,
        "wins": wins,
        "losses": losses,
        "hit_rate": wins / bets,
        "total_staked": total_staked,
        "net_profit": float(net_profit),
        "roi": float(roi),
        "average_return": float(average_return),
        "return_volatility": float(
            return_volatility
        ),
        "sharpe_like_ratio": float(
            sharpe_like_ratio
        ) if not pd.isna(
            sharpe_like_ratio
        ) else np.nan,
        "maximum_drawdown": maximum_drawdown,
    }