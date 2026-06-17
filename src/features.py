import pandas as pd

from src.vig import remove_vig_two_way


def clean_sample_odds_data(input_path: str, output_path: str) -> pd.DataFrame:
    """
    Load sample college basketball odds data, add outcome and no-vig probability columns,
    then save the cleaned dataset.
    """
    df = pd.read_csv(input_path)

    # Create outcome column: 1 if Team A won, 0 if Team A lost
    df["team_a_win"] = (df["team_a_score"] > df["team_b_score"]).astype(int)

    # Apply vig removal row by row
    probability_rows = []

    for _, row in df.iterrows():
        probs = remove_vig_two_way(row["team_a_odds"], row["team_b_odds"])
        probability_rows.append(probs)

    probs_df = pd.DataFrame(probability_rows)

    # Combine original data with probability columns
    clean_df = pd.concat([df, probs_df], axis=1)

    # Add pricing error: actual result minus market probability
    clean_df["team_a_pricing_error"] = (
        clean_df["team_a_win"] - clean_df["team_a_no_vig_prob"]
    )

    # Identify whether Team A was the favorite or underdog.
    # In American odds, negative odds mean the team is favored.
    clean_df["team_a_is_favorite"] = clean_df["team_a_odds"] < clean_df["team_b_odds"]

    clean_df["team_a_market_role"] = clean_df["team_a_is_favorite"].map(
        {
            True: "favorite",
            False: "underdog"
        }
    )

    clean_df.to_csv(output_path, index=False)

    return clean_df


def create_team_case_study(
    df: pd.DataFrame,
    team_name: str
) -> pd.DataFrame:
    """
    Create a team-specific case study dataset.

    This filters games where the selected team appears as Team A or Team B.
    It then creates columns from the selected team's perspective.
    """
    team_games = df[
        (df["team_a"] == team_name) | (df["team_b"] == team_name)
    ].copy()

    team_games["case_study_team"] = team_name

    team_games["team_score"] = team_games.apply(
        lambda row: row["team_a_score"] if row["team_a"] == team_name else row["team_b_score"],
        axis=1
    )

    team_games["opponent"] = team_games.apply(
        lambda row: row["team_b"] if row["team_a"] == team_name else row["team_a"],
        axis=1
    )

    team_games["opponent_score"] = team_games.apply(
        lambda row: row["team_b_score"] if row["team_a"] == team_name else row["team_a_score"],
        axis=1
    )

    team_games["team_win"] = (
        team_games["team_score"] > team_games["opponent_score"]
    ).astype(int)

    team_games["team_odds"] = team_games.apply(
        lambda row: row["team_a_odds"] if row["team_a"] == team_name else row["team_b_odds"],
        axis=1
    )

    team_games["team_no_vig_prob"] = team_games.apply(
        lambda row: row["team_a_no_vig_prob"] if row["team_a"] == team_name else row["team_b_no_vig_prob"],
        axis=1
    )

    team_games["team_pricing_error"] = (
        team_games["team_win"] - team_games["team_no_vig_prob"]
    )

    team_games["team_market_role"] = team_games["team_odds"].apply(
        lambda odds: "favorite" if odds < 0 else "underdog"
    )

    return team_games