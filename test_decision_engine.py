import pandas as pd

from src.config import LEAGUES
from src.projections import (
    load_razzball,
    add_projection_match,
)
from src.value_model import add_vor
from src.draft_score import add_draft_score
from src.survival import add_survival_metrics
from src.decision_engine import add_decision_metrics


board = pd.read_csv(
    "data/processed/player_board.csv"
)

projections = load_razzball(
    "data/raw/razzball.csv"
)

board = add_projection_match(
    board,
    projections,
)


# ---------------------------------------------------------
# Simulate Karns pick 28
# ---------------------------------------------------------

league_key = "karns"
league = LEAGUES[league_key]

current_pick = 28
draft_slot = league["draft_slot"]
teams = league["teams"]


result = add_vor(
    board,
    league_key,
    league,
)

result = add_draft_score(
    result
)

result = add_survival_metrics(
    result,
    current_pick=current_pick,
    draft_slot=draft_slot,
    teams=teams,
)

result = add_decision_metrics(
    result
)


# Only draftable offensive players with projections
result = result[
    result["position"].isin(
        ["QB", "RB", "WR", "TE"]
    )
    & result["razzball_name"].notna()
].copy()


columns = [
    "player",
    "position",
    "ecr",
    "espn_adp",
    "vor",
    "draft_score",
    "p_survive_next_pick",
    "urgency_score",
    "market_gap",
    "decision_score",
    "recommendation",
]


print("=" * 125)
print("KARNS LIVE DRAFT DECISION TEST")
print("=" * 125)

print()
print(f"Current pick: {current_pick}")
print(
    "Next pick:",
    result["next_pick"].iloc[0]
)


print()
print("=" * 125)
print("TOP 30 DECISIONS")
print("=" * 125)

display = (
    result
    .sort_values(
        "decision_score",
        ascending=False,
    )[columns]
    .head(30)
    .copy()
)

display["p_survive_next_pick"] *= 100

print(
    display.to_string(
        index=False,
        formatters={
            "ecr": "{:.1f}".format,
            "espn_adp": "{:.1f}".format,
            "vor": "{:.1f}".format,
            "draft_score": "{:.1f}".format,
            "p_survive_next_pick": "{:.1f}%".format,
            "urgency_score": "{:.1f}".format,
            "market_gap": "{:+.1f}".format,
            "decision_score": "{:.1f}".format,
        },
    )
)


print()
print("=" * 125)
print("WAIT / VALUE TARGETS")
print("=" * 125)

wait = result[
    result["recommendation"].isin(
        ["WAIT", "VALUE - WAIT"]
    )
].copy()

wait = wait.sort_values(
    "draft_score",
    ascending=False,
)

wait_display = wait[
    [
        "player",
        "position",
        "ecr",
        "espn_adp",
        "draft_score",
        "p_survive_next_pick",
        "market_gap",
        "recommendation",
    ]
].head(20).copy()

wait_display["p_survive_next_pick"] *= 100

print(
    wait_display.to_string(
        index=False,
        formatters={
            "ecr": "{:.1f}".format,
            "espn_adp": "{:.1f}".format,
            "draft_score": "{:.1f}".format,
            "p_survive_next_pick": "{:.1f}%".format,
            "market_gap": "{:+.1f}".format,
        },
    )
)


print()
print("=" * 125)
print("CHIG")
print("=" * 125)

chig = result[
    result["player"].str.contains(
        "Chig",
        case=False,
        na=False,
    )
][columns].copy()

chig["p_survive_next_pick"] *= 100

print(
    chig.to_string(
        index=False,
        formatters={
            "ecr": "{:.1f}".format,
            "espn_adp": "{:.1f}".format,
            "vor": "{:.1f}".format,
            "draft_score": "{:.1f}".format,
            "p_survive_next_pick": "{:.1f}%".format,
            "urgency_score": "{:.1f}".format,
            "market_gap": "{:+.1f}".format,
            "decision_score": "{:.1f}".format,
        },
    )
)