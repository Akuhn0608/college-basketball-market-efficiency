from pathlib import Path
import re
import unicodedata

import pandas as pd


KAGGLE_DIR = Path("data/raw/kaggle_2026")
ODDS_PATH = Path("data/processed/ncaab_odds_games_2021_22.csv")
OUTPUT_DIR = Path("data/processed")

MAPPED_OUTPUT_PATH = OUTPUT_DIR / "ncaab_odds_games_2021_22_mapped.csv"
UNMATCHED_OUTPUT_PATH = OUTPUT_DIR / "unmatched_odds_team_names_2021_22.csv"


def normalize_team_name(name: str) -> str:
    """
    Convert team names into a standard comparison format.

    Examples:
        "UC San Diego" -> "ucsandiego"
        "St.Peter's" -> "stpeters"
        "North-Carolina" -> "northcarolina"
    """
    if pd.isna(name):
        return ""

    text = str(name).lower().strip()

    # Remove accents, such as é -> e.
    text = unicodedata.normalize("NFKD", text)
    text = "".join(
        character
        for character in text
        if not unicodedata.combining(character)
    )

    # Keep only letters and numbers.
    text = re.sub(r"[^a-z0-9]", "", text)

    return text


teams_df = pd.read_csv(KAGGLE_DIR / "MTeams.csv")

spellings_df = pd.read_csv(
    KAGGLE_DIR / "MTeamSpellings.csv",
    encoding="cp1252",
)

odds_df = pd.read_csv(
    ODDS_PATH,
    parse_dates=["game_date"],
)

# Include Kaggle's official names as additional spellings.
official_names_df = teams_df[
    ["TeamName", "TeamID"]
].rename(
    columns={"TeamName": "TeamNameSpelling"}
)

all_names_df = pd.concat(
    [
        spellings_df,
        official_names_df,
    ],
    ignore_index=True,
)

all_names_df["normalized_name"] = all_names_df[
    "TeamNameSpelling"
].apply(normalize_team_name)

# Check whether one normalized name points to multiple TeamIDs.
ambiguous_names = (
    all_names_df
    .groupby("normalized_name")["TeamID"]
    .nunique()
)

ambiguous_names = ambiguous_names[
    ambiguous_names > 1
].index

print("Ambiguous normalized names:", len(ambiguous_names))

# Remove ambiguous names so we do not assign an incorrect team.
safe_names_df = all_names_df[
    ~all_names_df["normalized_name"].isin(ambiguous_names)
].copy()

name_to_team_id = (
    safe_names_df
    .drop_duplicates("normalized_name")
    .set_index("normalized_name")["TeamID"]
    .to_dict()
)

# Odds-source abbreviations that cannot be matched through
# punctuation and spacing removal alone.
manual_aliases = {
    "arkansaslr": 1114,          # Arkansas Little Rock
    "calirvine": 1414,           # UC Irvine
    "calsantabarb": 1364,        # UC Santa Barbara
    "charlestonsou": 1149,       # Charleston Southern
    "charlotteu": 1150,          # Charlotte
    "collcharleston": 1158,      # College of Charleston
    "denveru": 1176,             # Denver
    "detroitu": 1178,            # Detroit
    "etennesseest": 1190,        # East Tennessee State
    "fairdickinson": 1192,       # Fairleigh Dickinson
    "flagulfcoast": 1195,        # Florida Gulf Coast
    "geowashington": 1203,       # George Washington
    "houstonu": 1222,            # Houston
    "idahou": 1225,              # Idaho
    "indianau": 1231,            # Indiana
    "memphisu": 1272,            # Memphis
    "neworleansu": 1309,         # New Orleans
    "nocolorado": 1294,          # Northern Colorado
    "noillinois": 1296,          # Northern Illinois
    "portlandu": 1339,           # Portland
    "socarolinast": 1354,        # South Carolina State
    "soillinois": 1356,          # Southern Illinois
    "texsanantonio": 1427,       # UT San Antonio
    "ullafayette": 1418,         # Louisiana
    "ulmonroe": 1419,            # Louisiana-Monroe
    "utriograndevalley": 1410,   # UT Rio Grande Valley
    "utahu": 1428,               # Utah
    "washingtonu": 1449,         # Washington
    "wiscgreenbay": 1453,        # Green Bay
    "wiscmilwaukee": 1454,       # Milwaukee
}

# Add manual aliases before mapping the odds data.
name_to_team_id.update(manual_aliases)

team_id_to_name = (
    teams_df
    .set_index("TeamID")["TeamName"]
    .to_dict()
)

# Normalize odds-source team names.
odds_df["visitor_normalized_name"] = odds_df[
    "visitor_team"
].apply(normalize_team_name)

odds_df["home_normalized_name"] = odds_df[
    "home_team"
].apply(normalize_team_name)

# Map names to official Kaggle TeamIDs.
odds_df["visitor_team_id"] = odds_df[
    "visitor_normalized_name"
].map(name_to_team_id)

odds_df["home_team_id"] = odds_df[
    "home_normalized_name"
].map(name_to_team_id)

# Attach official Kaggle team names.
odds_df["visitor_official_name"] = odds_df[
    "visitor_team_id"
].map(team_id_to_name)

odds_df["home_official_name"] = odds_df[
    "home_team_id"
].map(team_id_to_name)

odds_df["both_teams_mapped"] = (
    odds_df["visitor_team_id"].notna()
    & odds_df["home_team_id"].notna()
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
odds_df.to_csv(MAPPED_OUTPUT_PATH, index=False)

# Create a report of every unmatched source name.
visitor_unmatched = odds_df.loc[
    odds_df["visitor_team_id"].isna(),
    ["visitor_team", "visitor_normalized_name"],
].rename(
    columns={
        "visitor_team": "source_team_name",
        "visitor_normalized_name": "normalized_name",
    }
)

home_unmatched = odds_df.loc[
    odds_df["home_team_id"].isna(),
    ["home_team", "home_normalized_name"],
].rename(
    columns={
        "home_team": "source_team_name",
        "home_normalized_name": "normalized_name",
    }
)

unmatched_df = pd.concat(
    [visitor_unmatched, home_unmatched],
    ignore_index=True,
)

unmatched_df = (
    unmatched_df
    .drop_duplicates()
    .sort_values("source_team_name")
)

unmatched_df.to_csv(
    UNMATCHED_OUTPUT_PATH,
    index=False,
)

print("Mapped odds data saved to:", MAPPED_OUTPUT_PATH)
print("Unmatched-name report saved to:", UNMATCHED_OUTPUT_PATH)

print()
print("Total games:", len(odds_df))
print(
    "Games with both teams mapped:",
    int(odds_df["both_teams_mapped"].sum()),
)
print(
    "Games missing at least one team mapping:",
    int((~odds_df["both_teams_mapped"]).sum()),
)
print(
    "Unique unmatched team names:",
    len(unmatched_df),
)

print()
print("Mapping rate:")
print(
    f"{odds_df['both_teams_mapped'].mean() * 100:.2f}%"
)

print()
print("Remaining unmatched names:")
print(unmatched_df.to_string(index=False))

print()
print("Louisville odds games found:")

louisville_games = odds_df[
    (odds_df["visitor_team_id"] == 1257)
    | (odds_df["home_team_id"] == 1257)
]

print(
    louisville_games[
        [
            "game_date",
            "visitor_team",
            "home_team",
            "visitor_team_id",
            "home_team_id",
            "visitor_moneyline",
            "home_moneyline",
        ]
    ].head(10)
)

print("Louisville games:", len(louisville_games))
