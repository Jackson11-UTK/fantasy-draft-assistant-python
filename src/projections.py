from __future__ import annotations

import re
import unicodedata

import pandas as pd


NAME_ALIASES = {
    "chig okonkwo": "chigoziem okonkwo",
}


def normalize_name(name: str) -> str:
    """Normalize player names so different sources match reliably."""

    if pd.isna(name):
        return ""

    name = unicodedata.normalize("NFKD", str(name))

    name = "".join(
        c for c in name
        if not unicodedata.combining(c)
    )

    name = name.lower()

    # Remove punctuation
    name = re.sub(r"[^a-z0-9\s]", "", name)

    # Remove common suffixes
    name = re.sub(
        r"\b(jr|sr|ii|iii|iv|v)\b",
        "",
        name
    )

    # Remove extra spaces
    name = re.sub(r"\s+", " ", name).strip()

    # Handle known source-specific name differences
    name = NAME_ALIASES.get(name, name)

    return name


def load_razzball(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    df = df.rename(
        columns={
            "Name": "razzball_name",
            "Pos": "position",
            "Team": "razzball_team",
            "Pass Yds": "pass_yds",
            "Pass TD": "pass_td",
            "Int": "pass_int",
            "Rush": "rush_att",
            "Rush Yds": "rush_yds",
            "Run TD": "rush_td",
            "Tgt": "targets",
            "Rec": "receptions",
            "Rec Yds": "rec_yds",
            "Rec TD": "rec_td",
            "STD PTS": "razzball_std",
            "1/2PPR PTS": "razzball_half_ppr",
            "PPR PTS": "razzball_ppr",
        }
    )

    df["match_name"] = (
        df["razzball_name"]
        .apply(normalize_name)
    )

    return df


def add_projection_match(
    board: pd.DataFrame,
    projections: pd.DataFrame
) -> pd.DataFrame:

    board = board.copy()

    board["match_name"] = (
        board["player"]
        .apply(normalize_name)
    )

    projection_cols = [
        "match_name",
        "position",
        "razzball_name",
        "razzball_team",
        "pass_yds",
        "pass_td",
        "pass_int",
        "rush_att",
        "rush_yds",
        "rush_td",
        "targets",
        "receptions",
        "rec_yds",
        "rec_td",
        "razzball_std",
        "razzball_half_ppr",
        "razzball_ppr",
    ]

    merged = board.merge(
        projections[projection_cols],
        on=["match_name", "position"],
        how="left",
        suffixes=("", "_razzball"),
    )

    return merged