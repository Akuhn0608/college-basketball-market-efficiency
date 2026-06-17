from src.odds import american_to_implied_prob, implied_prob_to_american


def test_positive_american_odds():
    assert round(american_to_implied_prob(150), 4) == 0.4000


def test_negative_american_odds():
    assert round(american_to_implied_prob(-200), 4) == 0.6667


def test_invalid_zero_odds():
    try:
        american_to_implied_prob(0)
    except ValueError:
        assert True
    else:
        assert False


def test_implied_prob_to_american_favorite():
    assert round(implied_prob_to_american(0.6667), 0) == -200


def test_implied_prob_to_american_underdog():
    assert round(implied_prob_to_american(0.4), 0) == 150