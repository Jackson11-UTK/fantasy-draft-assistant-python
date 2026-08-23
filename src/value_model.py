from __future__ import annotations

import pandas as pd

from src.scoring import score_offense


def replacement_ranks(league: dict) -> dict[str, int]:
    """
    Estimate replacement level from starting lineup demand.

    FLEX demand is allocated:
        40% RB
        55% WR
         5% TE

    Bench depth is intentionally NOT included here.
    Bench scarcity will be handled separately by the draft model.
    """

    teams = league["teams"]
    starters = league["starters"]

    qb = teams * starters["QB"]
    rb = teams * starters["RB"]
    wr = teams * starters["WR"]
    te = teams * starters["TE"]

    flex_spots = teams * starters.get("FLEX", 0)

    rb += round(flex_spots * 0.40)
    wr += round(flex_spots * 0.55)
    te += round(flex_spots * 0.05)

    return {
        "QB": int(qb),
        "RB": int(rb),
        "WR": int(wr),
        "TE": int(te),
    }


def add_vor(
    df: pd.DataFrame,
    league_key: str,
    league: dict,
) -> pd.DataFrame:

    out = df.copy()

    points_col = f"{league_key}_points"

    out[points_col] = score_offense(
        out,
        league,
    )

    out["position_rank"] = pd.NA
    out["replacement_points"] = pd.NA
    out["vor"] = pd.NA

    levels = replacement_ranks(league)

    for position, replacement_rank in levels.items():

        mask = (
            (out["position"] == position)
            & (out["razzball_name"].notna())
        )

        position_players = (
            out.loc[mask]
            .sort_values(
                points_col,
                ascending=False,
            )
            .copy()
        )

        if position_players.empty:
            continue

        ranks = pd.Series(
            range(1, len(position_players) + 1),
            index=position_players.index,
        )

        out.loc[
            position_players.index,
            "position_rank"
        ] = ranks

        replacement_index = min(
            replacement_rank - 1,
            len(position_players) - 1,
        )

        replacement_points = (
            position_players
            .iloc[replacement_index]
            [points_col]
        )

        position_mask = (
            out["position"] == position
        )

        out.loc[
            position_mask,
            "replacement_points"
        ] = replacement_points

        out.loc[
            position_mask,
            "vor"
        ] = (
            out.loc[position_mask, points_col]
            - replacement_points
        )

    for col in [
        "position_rank",
        "replacement_points",
        "vor",
    ]:
        out[col] = pd.to_numeric(
            out[col],
            errors="coerce",
        )

    return out