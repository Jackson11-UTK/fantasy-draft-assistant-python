from __future__ import annotations

import pandas as pd


def rank_for_league(
    df: pd.DataFrame,
    league_key: str
) -> pd.DataFrame:

    out = df.copy()

    if league_key == "karns" and "karns_points" in out.columns:
        out["projected_points"] = out["karns_points"]

        return out.sort_values(
            ["projected_points", "ecr"],
            ascending=[False, True],
            na_position="last"
        )

    if league_key == "mo_better" and "mo_better_points" in out.columns:
        out["projected_points"] = out["mo_better_points"]

        return out.sort_values(
            ["projected_points", "ecr"],
            ascending=[False, True],
            na_position="last"
        )

    # Temporary ranking method:
    # until custom league projections are added,
    # just sort by current redraft ECR.
    return out.sort_values(
        "ecr",
        ascending=True,
        na_position="last"
    )