import math

import pandas as pd
import pytest

from src.backtest import (
    american_odds_profit,
    calculate_bet_return,
    calculate_max_drawdown,
    summarize_backtest,
)


def test_positive_american_odds_profit() -> None:
    profit = american_odds_profit(
        american_odds=200,
        stake=1.0,
    )

    assert profit == pytest.approx(2.0)


def test_negative_american_odds_profit() -> None:
    profit = american_odds_profit(
        american_odds=-200,
        stake=1.0,
    )

    assert profit == pytest.approx(0.5)


def test_custom_stake_profit() -> None:
    profit = american_odds_profit(
        american_odds=150,
        stake=2.0,
    )

    assert profit == pytest.approx(3.0)


def test_winning_bet_return() -> None:
    net_return = calculate_bet_return(
        american_odds=-150,
        won=1,
        stake=1.0,
    )

    assert net_return == pytest.approx(
        100 / 150
    )


def test_losing_bet_return() -> None:
    net_return = calculate_bet_return(
        american_odds=250,
        won=0,
        stake=1.0,
    )

    assert net_return == pytest.approx(-1.0)


def test_invalid_outcome_raises_error() -> None:
    with pytest.raises(ValueError):
        calculate_bet_return(
            american_odds=-110,
            won=2,
        )


def test_zero_odds_raise_error() -> None:
    with pytest.raises(ValueError):
        american_odds_profit(
            american_odds=0,
        )


def test_nonpositive_stake_raises_error() -> None:
    with pytest.raises(ValueError):
        american_odds_profit(
            american_odds=-110,
            stake=0,
        )


def test_max_drawdown() -> None:
    returns = pd.Series(
        [
            1.0,
            1.0,
            -1.0,
            -1.0,
            -1.0,
            2.0,
        ]
    )

    drawdown = calculate_max_drawdown(
        returns
    )

    assert drawdown == pytest.approx(3.0)


def test_empty_max_drawdown() -> None:
    drawdown = calculate_max_drawdown(
        pd.Series(
            dtype=float
        )
    )

    assert drawdown == pytest.approx(0.0)


def test_backtest_summary() -> None:
    observations_df = pd.DataFrame(
        {
            "american_odds": [
                100,
                -200,
                150,
                -110,
            ],
            "actual_win": [
                1,
                1,
                0,
                0,
            ],
            "game_date": pd.to_datetime(
                [
                    "2022-01-01",
                    "2022-01-02",
                    "2022-01-03",
                    "2022-01-04",
                ]
            ),
        }
    )

    summary = summarize_backtest(
        observations_df=observations_df,
        stake=1.0,
    )

    expected_profit = (
        1.0
        + 0.5
        - 1.0
        - 1.0
    )

    assert summary["bets"] == 4
    assert summary["wins"] == 2
    assert summary["losses"] == 2
    assert summary["hit_rate"] == pytest.approx(0.5)
    assert summary["total_staked"] == pytest.approx(4.0)
    assert summary["net_profit"] == pytest.approx(
        expected_profit
    )
    assert summary["roi"] == pytest.approx(
        expected_profit / 4.0
    )
    assert summary["maximum_drawdown"] >= 0


def test_empty_backtest_summary() -> None:
    observations_df = pd.DataFrame(
        {
            "american_odds": pd.Series(
                dtype=float
            ),
            "actual_win": pd.Series(
                dtype=int
            ),
            "game_date": pd.Series(
                dtype="datetime64[ns]"
            ),
        }
    )

    summary = summarize_backtest(
        observations_df=observations_df,
    )

    assert summary["bets"] == 0
    assert summary["wins"] == 0
    assert summary["losses"] == 0
    assert summary["total_staked"] == pytest.approx(0.0)
    assert summary["net_profit"] == pytest.approx(0.0)
    assert summary["maximum_drawdown"] == pytest.approx(0.0)
    assert math.isnan(summary["roi"])


def test_missing_required_column_raises_error() -> None:
    observations_df = pd.DataFrame(
        {
            "american_odds": [-110],
            "actual_win": [1],
        }
    )

    with pytest.raises(
        ValueError,
        match="Missing required columns",
    ):
        summarize_backtest(
            observations_df=observations_df,
        )
