import pandas as pd

from src.config import LEAGUES
from src.projections import (
    load_razzball,
    add_projection_match,
)
from src.value_model import (
    add_vor,
    replacement_ranks,
)


board = pd.read_csv(
    "data/processed/player_board.csv"
)

projections = load_razzball(
    "data/raw/razzball.csv"
)

board = add_projection_match(
    board,
    projections
)


for league_key in ["karns", "mo_better"]:

    league = LEAGUES[league_key]

    levels = replacement_ranks(league)

    result = add_vor(
        board,
        league_key,
        league,
    )

    points_col = f"{league_key}_points"

    print()
    print("=" * 90)
    print(league["name"].upper())
    print("=" * 90)

    print("\nDYNAMIC REPLACEMENT RANKS")
    print(levels)

    columns = [
        "player",
        "position",
        "ecr",
        "espn_adp",
        points_col,
        "position_rank",
        "replacement_points",
        "vor",
    ]

    print("\nTOP 30 BY VOR")
    print("-" * 90)

    print(
        result[
            result["razzball_name"].notna()
        ]
        .sort_values(
            "vor",
            ascending=False
        )[columns]
        .head(30)
        .to_string(
            index=False,
            float_format=lambda x: f"{x:.1f}"
        )
    )

    print("\nREPLACEMENT PLAYERS")
    print("-" * 90)

    for position, rank in levels.items():

        position_pool = (
            result[
                (result["position"] == position)
                & (result["razzball_name"].notna())
            ]
            .sort_values(
                points_col,
                ascending=False
            )
        )

        if len(position_pool) < rank:
            print(
                f"{position}: not enough matched players "
                f"for rank {rank}"
            )
            continue

        replacement = position_pool.iloc[rank - 1]

        print(
            f"{position}{rank}: "
            f"{replacement['player']} - "
            f"{replacement[points_col]:.1f} pts"
        )