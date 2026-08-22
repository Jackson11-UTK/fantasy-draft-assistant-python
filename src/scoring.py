from __future__ import annotations

import pandas as pd


def _series(df: pd.DataFrame, column: str) -> pd.Series:
    if column not in df.columns:
        return pd.Series(0.0, index=df.index, dtype=float)

    return pd.to_numeric(df[column], errors="coerce").fillna(0.0)


def score_offense(df: pd.DataFrame, league: dict) -> pd.Series:
    """Score raw projected stats using one league's rules."""
    s = league["scoring"]

    points = (
        _series(df, "pass_yds") / s["pass_yards_per_point"]
        + _series(df, "pass_tds") * s["pass_td"]
        + _series(df, "pass_ints") * s["interception"]
        + _series(df, "proj_sacks_suffered") * s["qb_sack"]
        + _series(df, "rush_yds") / s["rush_yards_per_point"]
        + _series(df, "rush_tds") * s["rush_td"]
        + _series(df, "rec") * s["reception"]
        + _series(df, "rec_yds") / s["rec_yards_per_point"]
        + _series(df, "rec_tds") * s["rec_td"]
        + _series(df, "two_point_conversions") * s["two_point"]
        + _series(df, "fumbles_lost") * s["fumble_lost"]
    )

    # Mo Better's game-level bonuses cannot be inferred exactly from season totals.
    # Expected bonus columns can be added later and will automatically be included.
    if league["name"] == "Mo Better League":
        bonus_cols = [
            "exp_pass_bonus_pts",
            "exp_rush_bonus_pts",
            "exp_rec_bonus_pts",
            "exp_long_td_bonus_pts",
        ]

        for col in bonus_cols:
            points = points + _series(df, col)

    return points
