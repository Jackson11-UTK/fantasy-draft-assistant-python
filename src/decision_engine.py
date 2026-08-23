from __future__ import annotations

import pandas as pd

from src.roster_state import position_need_score


def add_decision_metrics(
    df: pd.DataFrame,
    roster: list[dict] | None = None,
    league: dict | None = None,
) -> pd.DataFrame:
    """
    Combine player quality, next-pick urgency, and roster need.

    decision_score:
        65% player quality
        25% urgency
        10% roster need

    Recommendations are relative to the best available player,
    rather than assigning TAKE NOW to many players independently.
    """

    out = df.copy()

    # ---------------------------------------------------------
    # ROSTER NEED
    # ---------------------------------------------------------

    if roster is None or league is None:
        out["roster_need"] = 0.5
    else:
        out["roster_need"] = out["position"].apply(
            lambda pos: position_need_score(
                pos,
                roster,
                league,
            )
        )

    # ---------------------------------------------------------
    # DECISION SCORE
    # ---------------------------------------------------------

    out["decision_score"] = (
        0.65 * out["draft_score"]
        + 0.25 * out["urgency_score"]
        + 0.10 * (out["roster_need"] * 100)
    )

    # ---------------------------------------------------------
    # FIND BEST AVAILABLE SCORE
    # ---------------------------------------------------------

    valid_scores = out["decision_score"].dropna()

    if valid_scores.empty:
        out["recommendation"] = "NO SCORE"
        return out

    best_score = valid_scores.max()

    # ---------------------------------------------------------
    # RELATIVE RECOMMENDATIONS
    # ---------------------------------------------------------

    def recommendation(row):

        score = row["decision_score"]
        survive = row["p_survive_next_pick"]
        gap = row["market_gap"]

        if pd.isna(score):
            return "NO SCORE"

        distance_from_best = best_score - score

        # Best overall option currently available.
        if distance_from_best < 0.01:
            return "BEST PICK"

        # Very close to the best option.
        if distance_from_best <= 4:
            return "STRONG ALTERNATIVE"

        # Still a legitimate alternative, but clearly behind the leaders.
        if distance_from_best <= 8:
            return "ALTERNATIVE"

        # Good player who is very likely to survive until our next pick.
        if (
            row["draft_score"] >= 80
            and survive >= 0.75
        ):
            return "WAIT"

        # Market is drafting this player much later than expert consensus,
        # and survival odds suggest we do not need to reach yet.
        if (
            pd.notna(gap)
            and gap >= 20
            and survive >= 0.60
        ):
            return "VALUE TARGET"

        return "NEUTRAL"

    out["recommendation"] = out.apply(
        recommendation,
        axis=1,
    )

    return out