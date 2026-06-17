from src.vig import remove_vig_two_way


def test_remove_vig_two_way():
    result = remove_vig_two_way(-200, 150)

    assert round(result["team_a_implied_prob"], 4) == 0.6667
    assert round(result["team_b_implied_prob"], 4) == 0.4000
    assert round(result["market_vig"], 4) == 0.0667
    assert round(result["team_a_no_vig_prob"], 4) == 0.6250
    assert round(result["team_b_no_vig_prob"], 4) == 0.3750