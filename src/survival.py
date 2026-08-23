from __future__ import annotations

import math

import pandas as pd


def next_pick(
    current_pick: int,
    draft_slot: int,
    teams: int,
) -> int:

    if current_pick < 1:
        raise ValueError("current_pick must be at least 1")

    if not 1 <= draft_slot <= teams:
        raise ValueError(
            "draft_slot must be between 1 and teams"
        )

    current_round = math.ceil(
        current_pick / teams
    )

    for round_num in range(
        current_round,
        current_round + 4,
    ):

        if round_num % 2 == 1:
            our_pick = (
                (round_num - 1) * teams
                + draft_slot
            )
        else:
            our_pick = (
                round_num * teams
                - draft_slot
                + 1
            )

        if our_pick > current_pick:
            return our_pick

    raise RuntimeError(
        "Could not determine next pick"
    )


def estimate_draft_sd(
    ecr_sd: float,
    best: float,
    worst: float,
) -> float:
    """
    Estimate uncertainty in draft position.

    FantasyPros expert disagreement gives us a useful
    signal for how uncertain a player's valuation is.

    We combine:
        - reported ECR SD
        - best/worst expert ranking range

    A floor prevents unrealistically tiny uncertainty.
    """

    candidates = []

    if pd.notna(ecr_sd):
        candidates.append(float(ecr_sd))

    if pd.notna(best) and pd.notna(worst):

        ranking_range = (
            float(worst)
            - float(best)
        )

        # Approximate SD from ranking range.
        range_sd = ranking_range / 4

        candidates.append(range_sd)

    if not candidates:
        return 12.0

    estimated = max(candidates)

    # Avoid unrealistically narrow distributions.
    return max(
        6.0,
        min(estimated, 30.0),
    )


def survival_probability(
    espn_adp: float,
    ecr: float,
    next_overall_pick: int,
    draft_sd: float,
) -> float:
    """
    Estimate probability player remains available
    at our next selection.
    """

    # If ESPN ADP is unavailable, ECR is our fallback
    # market-location estimate.
    if pd.notna(espn_adp):
        expected_pick = float(espn_adp)

    elif pd.notna(ecr):
        expected_pick = float(ecr)

    else:
        return float("nan")

    z = (
        next_overall_pick
        - expected_pick
    ) / draft_sd

    cdf = 0.5 * (
        1
        + math.erf(
            z / math.sqrt(2)
        )
    )

    survival = 1 - cdf

    return max(
        0.0,
        min(1.0, survival),
    )


def add_survival_metrics(
    df: pd.DataFrame,
    current_pick: int,
    draft_slot: int,
    teams: int,
) -> pd.DataFrame:

    out = df.copy()

    nxt = next_pick(
        current_pick=current_pick,
        draft_slot=draft_slot,
        teams=teams,
    )

    out["current_pick"] = current_pick
    out["next_pick"] = nxt

    out["draft_sd"] = out.apply(
        lambda row: estimate_draft_sd(
            row.get("sd"),
            row.get("best"),
            row.get("worst"),
        ),
        axis=1,
    )

    out["p_survive_next_pick"] = out.apply(
        lambda row: survival_probability(
            espn_adp=row.get("espn_adp"),
            ecr=row.get("ecr"),
            next_overall_pick=nxt,
            draft_sd=row["draft_sd"],
        ),
        axis=1,
    )

    out["p_gone_next_pick"] = (
        1
        - out["p_survive_next_pick"]
    )

    out["urgency_score"] = (
        out["p_gone_next_pick"]
        * 100
    )

    return out