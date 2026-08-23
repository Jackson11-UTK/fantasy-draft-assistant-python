from __future__ import annotations

import pandas as pd


def mark_drafted(
    df: pd.DataFrame,
    drafted_players: list[str],
) -> pd.DataFrame:
    """
    Mark players as drafted while preserving
    players who were already marked drafted.
    """

    out = df.copy()

    # Create drafted column only if it does not exist yet.
    if "drafted" not in out.columns:
        out["drafted"] = False

    drafted_set = {
        name.strip().lower()
        for name in drafted_players
    }

    new_drafted = (
        out["player"]
        .str.strip()
        .str.lower()
        .isin(drafted_set)
    )

    # Preserve previous drafted players AND add new ones.
    out["drafted"] = (
        out["drafted"] | new_drafted
    )

    return out


def available_players(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Return only players who have not been drafted.
    """

    if "drafted" not in df.columns:
        return df.copy()

    return df[
        ~df["drafted"]
    ].copy()


def draft_player(
    df: pd.DataFrame,
    player_name: str,
) -> pd.DataFrame:
    """
    Mark one player as drafted.
    """

    out = df.copy()

    if "drafted" not in out.columns:
        out["drafted"] = False

    mask = (
        out["player"]
        .str.strip()
        .str.lower()
        == player_name.strip().lower()
    )

    if not mask.any():
        raise ValueError(
            f"Player not found: {player_name}"
        )

    out.loc[
        mask,
        "drafted"
    ] = True

    return out