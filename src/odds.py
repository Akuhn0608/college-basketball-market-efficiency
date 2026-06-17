def american_to_implied_prob(odds: float) -> float:
    """
    Convert American odds to implied probability before removing vig.

    Examples:
    +150 -> 0.4000
    -200 -> 0.6667
    """
    if odds > 0:
        return 100 / (odds + 100)
    elif odds < 0:
        return abs(odds) / (abs(odds) + 100)
    else:
        raise ValueError("American odds cannot be zero.")


def implied_prob_to_american(prob: float) -> float:
    """
    Convert implied probability to American odds.

    Examples:
    0.4000 -> +150
    0.6667 -> about -200
    """
    if prob <= 0 or prob >= 1:
        raise ValueError("Probability must be between 0 and 1.")

    if prob > 0.5:
        return -100 * prob / (1 - prob)
    else:
        return 100 * (1 - prob) / prob