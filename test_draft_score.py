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
from src.draft_score import add_draft_score


board = pd.read_csv(
    "data/processed/player_board.csv"
)

projections = load_razzball(
    "data/raw/razzball.csv"
)

board = add_projection_match(
    board,
    projections,
)


for league_key in [
    "karns",
    "mo_better",
]:

    league = LEAGUES[league_key]

    result = add_vor(
        board,
        league_key,
        league,
    )

    result = add_draft_score(
        result
    )

    # Only use relevant offensive players with projections
    result = result[
        result["position"].isin(
            ["QB", "RB", "WR", "TE"]
        )
        & result["razzball_name"].notna()
    ].copy()

    print()
    print("=" * 110)
    print(league["name"].upper())
    print("=" * 110)

    print(
        "Replacement ranks:",
        replacement_ranks(league)
    )

    columns = [
        "player",
        "position",
        "ecr",
        "espn_adp",
        "vor",
        "vor_score",
        "ecr_score",
        "adp_score",
        "certainty_score",
        "market_gap",
        "draft_score",
    ]

    print("\nTOP 30 DRAFT SCORE")
    print("-" * 110)

    print(
        result
        .sort_values(
            "draft_score",
            ascending=False,
        )[columns]
        .head(30)
        .to_string(
            index=False,
            float_format=lambda x: f"{x:.1f}",
        )
    )

    print("\nBIGGEST ECR VS ESPN VALUES")
    print("-" * 110)

    print(
        result[
            result["espn_adp"].notna()
        ]
        .sort_values(
            "market_gap",
            ascending=False,
        )[
            [
                "player",
                "position",
                "ecr",
                "espn_adp",
                "market_gap",
                "draft_score",
            ]
        ]
        .head(15)
        .to_string(
            index=False,
            float_format=lambda x: f"{x:.1f}",
        )
    )

    print("\nCHIG")
    print("-" * 110)

    print(
        result[
            result["player"]
            .str.contains(
                "Chig",
                case=False,
                na=False,
            )
        ][columns]
        .to_string(
            index=False,
            float_format=lambda x: f"{x:.1f}",
        )
    )