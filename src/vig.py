from src.odds import american_to_implied_prob


def remove_vig_two_way(team_a_odds: float, team_b_odds: float) -> dict:
    """
    Remove vig from a two-way market like a college basketball moneyline.

    Returns implied probabilities, market vig, and no-vig probabilities.
    """
    team_a_imp = american_to_implied_prob(team_a_odds)
    team_b_imp = american_to_implied_prob(team_b_odds)

    total_imp = team_a_imp + team_b_imp

    return {
        "team_a_implied_prob": team_a_imp,
        "team_b_implied_prob": team_b_imp,
        "market_vig": total_imp - 1,
        "team_a_no_vig_prob": team_a_imp / total_imp,
        "team_b_no_vig_prob": team_b_imp / total_imp,
    }