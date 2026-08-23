import pandas as pd

from src.projections import (
    add_projection_match,
    load_razzball,
)


board = pd.read_csv(
    "data/processed/player_board.csv"
)

projections = load_razzball(
    "data/raw/razzball.csv"
)

merged = add_projection_match(
    board,
    projections
)


skill = merged[
    merged["position"].isin(
        ["QB", "RB", "WR", "TE"]
    )
].copy()


print("\nTOTAL QB/RB/WR/TE ON BOARD:")
print(len(skill))

print("\nMATCHED:")
print(skill["razzball_name"].notna().sum())

print("\nMATCH RATE:")
print(
    round(
        100
        * skill["razzball_name"].notna().mean(),
        1
    ),
    "%"
)


print("\nTOP 150 ECR MATCH RATE:")

top150 = skill.sort_values("ecr").head(150)

print(
    round(
        100
        * top150["razzball_name"].notna().mean(),
        1
    ),
    "%"
)


print("\nTOP 150 UNMATCHED:")

print(
    top150[
        top150["razzball_name"].isna()
    ][
        [
            "player",
            "position",
            "team",
            "ecr",
        ]
    ]
    .to_string(index=False)
)


print("\nMATCH EXAMPLES:")

print(
    skill[
        skill["razzball_name"].notna()
    ][
        [
            "player",
            "razzball_name",
            "position",
            "team",
            "razzball_team",
            "ecr",
            "razzball_ppr",
        ]
    ]
    .sort_values("ecr")
    .head(25)
    .to_string(index=False)
)