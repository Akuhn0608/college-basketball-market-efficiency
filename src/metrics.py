from sklearn.metrics import brier_score_loss, log_loss


def calculate_brier_score(outcomes, probabilities) -> float:
    """
    Calculate Brier score for probability predictions.

    Lower is better.
    A perfect model has a Brier score of 0.
    """
    return brier_score_loss(outcomes, probabilities)


def calculate_log_loss(outcomes, probabilities) -> float:
    """
    Calculate log loss for probability predictions.

    Lower is better.
    Log loss heavily penalizes confident wrong predictions.
    """
    return log_loss(outcomes, probabilities)