from __future__ import annotations

import numpy as np
import pandas as pd


def _rank_percentile(
    series: pd.Series,
    lower_is_better: bool = False,
) -> pd.Series:
    """
    Convert a metric into a 0-100 percentile score.

    Higher score always means more desirable.
    """

    numeric = pd.to_numeric(
        series,
        errors="coerce",
    )

    if lower_is_better:
        pct = numeric.rank(
            pct=True,
            ascending=False,
        )
    else:
        pct = numeric.rank(
            pct=True,
            ascending=True,
        )

    return pct * 100


def add_draft_score(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create Draft Score v1.

    Components:
        40% VOR
        30% ECR
        20% ESPN ADP
        10% expert certainty

    Scores are converted to percentiles first so metrics
    with different raw scales can be combined.
    """

    out = df.copy()

    # -------------------------
    # VOR
    # -------------------------

    out["vor_score"] = _rank_percentile(
        out["vor"]
    )

    # -------------------------
    # Expert consensus rank
    # -------------------------

    out["ecr_score"] = _rank_percentile(
        out["ecr"],
        lower_is_better=True,
    )

    # -------------------------
    # ESPN draft market
    # -------------------------

    out["adp_score"] = _rank_percentile(
        out["espn_adp"],
        lower_is_better=True,
    )

    # Missing ESPN ADP should not destroy a player's score.
    # Fall back to ECR signal.
    out["adp_score"] = (
        out["adp_score"]
        .fillna(out["ecr_score"])
    )

    # -------------------------
    # Expert certainty
    # -------------------------

    # Lower FantasyPros SD = more agreement among experts.
    out["certainty_score"] = _rank_percentile(
        out["sd"],
        lower_is_better=True,
    )

    # Neutral fallback if SD is unavailable.
    out["certainty_score"] = (
        out["certainty_score"]
        .fillna(50.0)
    )

    # -------------------------
    # Composite score
    # -------------------------

    out["draft_score"] = (
        0.40 * out["vor_score"]
        + 0.30 * out["ecr_score"]
        + 0.20 * out["adp_score"]
        + 0.10 * out["certainty_score"]
    )

    # -------------------------
    # Market gap
    # -------------------------

    # Positive:
    # experts rank player earlier than ESPN drafters.
    #
    # Example:
    # ECR 20, ADP 35 -> +15
    #
    # Could potentially wait on the player.
    out["market_gap"] = (
        pd.to_numeric(
            out["espn_adp"],
            errors="coerce",
        )
        - pd.to_numeric(
            out["ecr"],
            errors="coerce",
        )
    )

    return out