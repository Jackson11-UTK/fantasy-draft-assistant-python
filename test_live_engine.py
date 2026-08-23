import pandas as pd

from src.config import LEAGUES
from src.projections import (
    load_razzball,
    add_projection_match,
)
from src.live_draft import LiveDraft


# ---------------------------------------------------------
# LOAD BOARD + PROJECTIONS
# ---------------------------------------------------------

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
# CREATE LIVE DRAFT
# ---------------------------------------------------------

league_key = "karns"
league = LEAGUES[league_key]

draft = LiveDraft(
    board,
    league,
)


# ---------------------------------------------------------
# SIMULATE FIRST THREE PICKS
# ---------------------------------------------------------

draft.draft_player(
    "Jahmyr Gibbs",
    my_pick=False,
)

draft.draft_player(
    "Bijan Robinson",
    my_pick=False,
)

draft.draft_player(
    "Ja'Marr Chase",
    my_pick=False,
)


# ---------------------------------------------------------
# WE ARE NOW AT PICK 4
# ---------------------------------------------------------

result = draft.get_recommendations(
    league_key
)

columns = [
    "player",
    "position",
    "ecr",
    "espn_adp",
    "vor",
    "draft_score",
    "roster_need",
    "p_survive_next_pick",
    "decision_score",
    "recommendation",
]


print("=" * 125)
print("LIVE DRAFT ENGINE")
print("=" * 125)

print()
print("Current pick:", draft.current_pick)
print("My roster:", draft.get_roster())
print()

print("BEST AVAILABLE AT PICK 4")
print("-" * 125)

display = (
    result[columns]
    .head(15)
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
            "roster_need": "{:.2f}".format,
            "p_survive_next_pick": "{:.1f}%".format,
            "decision_score": "{:.1f}".format,
        },
    )
)


# ---------------------------------------------------------
# MAKE OUR PICK
# ---------------------------------------------------------

best_pick = result.iloc[0]

print()
print("=" * 125)
print("OUR PICK")
print("=" * 125)

print(
    best_pick["player"],
    f"({best_pick['position']})"
)

draft.draft_player(
    best_pick["player"],
    my_pick=True,
)


# ---------------------------------------------------------
# VERIFY STATE CHANGED
# ---------------------------------------------------------

print()
print("Current pick:", draft.current_pick)
print("My roster:", draft.get_roster())

new_result = draft.get_recommendations(
    league_key
)

print()
print("Previous pick still available?")
print(
    best_pick["player"]
    in new_result["player"].tolist()
)

print()
print("NEW TOP 5:")
print("-" * 125)

print(
    new_result[
        [
            "player",
            "position",
            "decision_score",
            "recommendation",
        ]
    ]
    .head(5)
    .to_string(index=False)
)