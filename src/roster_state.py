from __future__ import annotations

from collections import Counter


FLEX_POSITIONS = {"RB", "WR", "TE"}


def roster_counts(roster: list[dict]) -> dict[str, int]:
    """
    Count how many players we currently have at each position.
    """

    counts = Counter(
        player["position"]
        for player in roster
    )

    return dict(counts)


def starter_needs(
    roster: list[dict],
    league: dict,
) -> dict[str, int]:
    """
    Estimate remaining starting-position needs.

    FLEX is handled separately because RB/WR/TE can fill it.
    """

    counts = roster_counts(roster)
    starters = league["starters"]

    needs = {}

    for pos in ["QB", "RB", "WR", "TE"]:
        required = starters.get(pos, 0)
        have = counts.get(pos, 0)

        needs[pos] = max(
            required - have,
            0,
        )

    flex_required = starters.get("FLEX", 0)

    rb_extra = max(
        counts.get("RB", 0) - starters.get("RB", 0),
        0,
    )

    wr_extra = max(
        counts.get("WR", 0) - starters.get("WR", 0),
        0,
    )

    te_extra = max(
        counts.get("TE", 0) - starters.get("TE", 0),
        0,
    )

    flex_filled = min(
        rb_extra + wr_extra + te_extra,
        flex_required,
    )

    needs["FLEX"] = max(
        flex_required - flex_filled,
        0,
    )

    return needs


def position_need_score(
    position: str,
    roster: list[dict],
    league: dict,
) -> float:
    """
    Return a 0-1 measure of how useful another player
    at this position is to our current roster.

    1.0 = strong roster need
    0.0 = little immediate roster need
    """

    counts = roster_counts(roster)
    needs = starter_needs(
        roster,
        league,
    )

    # K/DST are handled later in draft strategy.
    if position in {"K", "DST"}:
        return 0.0

    # Empty required starting position.
    if needs.get(position, 0) > 0:
        return 1.0

    # RB/WR/TE can still satisfy FLEX.
    if (
        position in FLEX_POSITIONS
        and needs.get("FLEX", 0) > 0
    ):
        return 0.85

    # Starting lineup is filled, but depth still matters.
    if position == "RB":
        if counts.get("RB", 0) < 4:
            return 0.60
        return 0.30

    if position == "WR":
        if counts.get("WR", 0) < 4:
            return 0.60
        return 0.30

    if position == "TE":
        if counts.get("TE", 0) < 2:
            return 0.40
        return 0.15

    if position == "QB":
        if counts.get("QB", 0) < 2:
            return 0.30
        return 0.10

    return 0.0