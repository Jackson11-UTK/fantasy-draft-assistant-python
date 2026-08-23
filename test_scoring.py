import pandas as pd

from src.config import LEAGUES
from src.projections import load_razzball, add_projection_match
from src.scoring import score_offense


# Load our main player board
board = pd.read_csv(
    "data/processed/player_board.csv"
)

# Load and clean Razzball projections
projections = load_razzball(
    "data/raw/razzball.csv"
)

# Match Razzball projections to our player board
board = add_projection_match(
    board,
    projections
)


# Calculate projected points under BOTH league scoring systems
board["karns_points"] = score_offense(
    board,
    LEAGUES["karns"]
)

board["mo_better_points"] = score_offense(
    board,
    LEAGUES["mo_better"]
)


# Only inspect players who actually matched Razzball
matched = board[
    board["razzball_name"].notna()
].copy()


columns = [
    "player",
    "position",
    "ecr",
    "espn_adp",
    "karns_points",
    "mo_better_points",
]


print("\n" + "=" * 85)
print("TOP 30 BY ECR")
print("=" * 85)

print(
    matched
    .sort_values("ecr")
    [columns]
    .head(30)
    .to_string(
        index=False,
        float_format=lambda x: f"{x:.1f}"
    )
)


print("\n" + "=" * 85)
print("TOP 15 PROJECTED KARNS SCORERS")
print("=" * 85)

print(
    matched
    .sort_values(
        "karns_points",
        ascending=False
    )
    [columns]
    .head(15)
    .to_string(
        index=False,
        float_format=lambda x: f"{x:.1f}"
    )
)


print("\n" + "=" * 85)
print("CHIG CHECK")
print("=" * 85)

print(
    matched[
        matched["player"]
        .str.contains(
            "Chig",
            case=False,
            na=False
        )
    ][columns]
    .to_string(
        index=False,
        float_format=lambda x: f"{x:.1f}"
    )
)