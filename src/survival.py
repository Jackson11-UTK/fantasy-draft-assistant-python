from __future__ import annotations

import math

import pandas as pd

from src.roster_state import position_need_score


# =========================================================
# SNAKE DRAFT MATH
# =========================================================

def team_slot_for_pick(
    overall_pick: int,
    teams: int,
) -> int:
    """
    Return the team/draft slot that owns an overall pick.
    """

    round_num = math.ceil(
        overall_pick / teams
    )

    position_in_round = (
        (overall_pick - 1) % teams
    ) + 1

    if round_num % 2 == 1:
        return position_in_round

    return (
        teams
        - position_in_round
        + 1
    )


def next_pick(
    current_pick: int,
    draft_slot: int,
    teams: int,
) -> int:
    """
    Return our next FUTURE selection.
    """

    if current_pick < 1:
        raise ValueError(
            "current_pick must be at least 1"
        )

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
                (round_num - 1)
                * teams
                + draft_slot
            )

        else:

            our_pick = (
                round_num
                * teams
                - draft_slot
                + 1
            )

        if our_pick > current_pick:
            return our_pick

    raise RuntimeError(
        "Could not determine next pick"
    )


def opponent_slots_before_next_pick(
    current_pick: int,
    next_overall_pick: int,
    draft_slot: int,
    teams: int,
) -> list[int]:
    """
    Return every opposing team slot that selects
    before our next pick.

    Duplicate team slots are intentional because a team
    can pick twice across a snake-draft turn.
    """

    current_owner = team_slot_for_pick(
        current_pick,
        teams,
    )

    if current_owner == draft_slot:
        start_pick = current_pick + 1
    else:
        start_pick = current_pick

    slots = []

    for pick in range(
        start_pick,
        next_overall_pick,
    ):

        slot = team_slot_for_pick(
            pick,
            teams,
        )

        if slot != draft_slot:
            slots.append(slot)

    return slots


# =========================================================
# ROUND-BASED ADJUSTMENT STRENGTH
# =========================================================

def roster_adjustment_strength(
    current_pick: int,
    teams: int,
) -> float:
    """
    Increase the importance of opponent roster construction
    as the draft progresses.

    Approximate strength by round:

    Round 1: 0.45
    Round 2: 0.60
    Round 3: 0.75
    Round 4: 0.90
    Round 5: 1.05
    Round 6: 1.20
    Round 7: 1.35
    Round 8: 1.50
    Round 9+: capped at 1.60

    Early:
        ADP / ECR dominate.

    Later:
        Actual roster needs become more informative.
    """

    round_num = math.ceil(
        current_pick / teams
    )

    strength = (
        0.45
        + 0.15 * (round_num - 1)
    )

    return min(
        strength,
        1.60,
    )


# =========================================================
# BASE DRAFT UNCERTAINTY
# =========================================================

def estimate_draft_sd(
    ecr_sd: float,
    best: float,
    worst: float,
) -> float:
    """
    Estimate uncertainty in player draft position using
    FantasyPros expert disagreement.
    """

    candidates = []

    if pd.notna(ecr_sd):
        candidates.append(
            float(ecr_sd)
        )

    if (
        pd.notna(best)
        and pd.notna(worst)
    ):

        ranking_range = (
            float(worst)
            - float(best)
        )

        range_sd = (
            ranking_range / 4
        )

        candidates.append(
            range_sd
        )

    if not candidates:
        return 12.0

    estimated = max(
        candidates
    )

    return max(
        6.0,
        min(
            estimated,
            30.0,
        ),
    )


def base_survival_probability(
    espn_adp: float,
    ecr: float,
    next_overall_pick: int,
    draft_sd: float,
) -> float:
    """
    Estimate survival probability from market draft
    position before opponent roster adjustments.
    """

    if pd.notna(espn_adp):

        expected_pick = float(
            espn_adp
        )

    elif pd.notna(ecr):

        expected_pick = float(
            ecr
        )

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

    survival = (
        1 - cdf
    )

    return max(
        0.0,
        min(
            1.0,
            survival,
        ),
    )


# =========================================================
# OPPONENT POSITION DEMAND
# =========================================================

def opponent_demand_index(
    position: str,
    upcoming_team_slots: list[int],
    team_rosters: dict[int, list[dict]],
    league: dict,
) -> float:
    """
    Estimate how strongly the teams selecting before us
    need a particular position.

    1.00 = neutral demand
    >1.00 = above-normal demand
    <1.00 = below-normal demand
    """

    if (
        not upcoming_team_slots
        or not team_rosters
    ):
        return 1.0

    positions = [
        "QB",
        "RB",
        "WR",
        "TE",
    ]

    relative_needs = []

    for team_slot in upcoming_team_slots:

        roster = team_rosters.get(
            team_slot,
            [],
        )

        needs = {
            pos: position_need_score(
                pos,
                roster,
                league,
            )
            for pos in positions
        }

        average_need = (
            sum(needs.values())
            / len(positions)
        )

        if average_need <= 0:

            relative_need = 1.0

        else:

            relative_need = (
                needs[position]
                / average_need
            )

        # Prevent one roster from dominating the signal.
        relative_need = max(
            0.40,
            min(
                relative_need,
                1.80,
            ),
        )

        relative_needs.append(
            relative_need
        )

    demand = (
        sum(relative_needs)
        / len(relative_needs)
    )

    return max(
        0.65,
        min(
            demand,
            1.45,
        ),
    )


# =========================================================
# ADJUST SURVIVAL
# =========================================================

def adjust_survival_for_demand(
    base_survival: float,
    demand_index: float,
    adjustment_strength: float,
) -> float:
    """
    Adjust survival probability using opponent demand.

    High demand:
        player less likely to survive.

    Low demand:
        player more likely to survive.

    adjustment_strength increases as the draft progresses.
    """

    if pd.isna(base_survival):
        return float("nan")

    base_survival = max(
        0.0001,
        min(
            base_survival,
            0.9999,
        ),
    )

    base_gone = (
        1 - base_survival
    )

    gone_odds = (
        base_gone
        / base_survival
    )

    adjusted_odds = (
        gone_odds
        * (
            demand_index
            ** adjustment_strength
        )
    )

    adjusted_gone = (
        adjusted_odds
        / (
            1 + adjusted_odds
        )
    )

    adjusted_survival = (
        1 - adjusted_gone
    )

    return max(
        0.0,
        min(
            1.0,
            adjusted_survival,
        ),
    )


# =========================================================
# MAIN FUNCTION
# =========================================================

def add_survival_metrics(
    df: pd.DataFrame,
    current_pick: int,
    draft_slot: int,
    teams: int,
    team_rosters: dict[int, list[dict]] | None = None,
    league: dict | None = None,
) -> pd.DataFrame:
    """
    Add market-based and opponent-adjusted survival metrics.
    """

    out = df.copy()

    nxt = next_pick(
        current_pick=current_pick,
        draft_slot=draft_slot,
        teams=teams,
    )

    current_round = math.ceil(
        current_pick / teams
    )

    adjustment_strength = (
        roster_adjustment_strength(
            current_pick=current_pick,
            teams=teams,
        )
    )

    out["current_pick"] = (
        current_pick
    )

    out["current_round"] = (
        current_round
    )

    out["next_pick"] = (
        nxt
    )

    out[
        "opponent_adjustment_strength"
    ] = adjustment_strength


    # -----------------------------------------------------
    # UNCERTAINTY
    # -----------------------------------------------------

    out["draft_sd"] = out.apply(
        lambda row: estimate_draft_sd(
            row.get("sd"),
            row.get("best"),
            row.get("worst"),
        ),
        axis=1,
    )


    # -----------------------------------------------------
    # BASE MARKET SURVIVAL
    # -----------------------------------------------------

    out[
        "base_survive_next_pick"
    ] = out.apply(
        lambda row:
            base_survival_probability(
                espn_adp=row.get(
                    "espn_adp"
                ),
                ecr=row.get(
                    "ecr"
                ),
                next_overall_pick=nxt,
                draft_sd=row[
                    "draft_sd"
                ],
            ),
        axis=1,
    )


    # -----------------------------------------------------
    # UPCOMING OPPONENTS
    # -----------------------------------------------------

    upcoming_slots = (
        opponent_slots_before_next_pick(
            current_pick=current_pick,
            next_overall_pick=nxt,
            draft_slot=draft_slot,
            teams=teams,
        )
    )


    # -----------------------------------------------------
    # POSITION DEMAND
    # -----------------------------------------------------

    if (
        team_rosters is None
        or league is None
    ):

        out[
            "opponent_demand_index"
        ] = 1.0

    else:

        out[
            "opponent_demand_index"
        ] = out[
            "position"
        ].apply(
            lambda position:
                opponent_demand_index(
                    position=position,
                    upcoming_team_slots=upcoming_slots,
                    team_rosters=team_rosters,
                    league=league,
                )
        )


    # -----------------------------------------------------
    # FINAL SURVIVAL
    # -----------------------------------------------------

    out[
        "p_survive_next_pick"
    ] = out.apply(
        lambda row:
            adjust_survival_for_demand(
                base_survival=row[
                    "base_survive_next_pick"
                ],
                demand_index=row[
                    "opponent_demand_index"
                ],
                adjustment_strength=row[
                    "opponent_adjustment_strength"
                ],
            ),
        axis=1,
    )


    out[
        "p_gone_next_pick"
    ] = (
        1
        - out[
            "p_survive_next_pick"
        ]
    )


    out[
        "urgency_score"
    ] = (
        out[
            "p_gone_next_pick"
        ]
        * 100
    )

    return out