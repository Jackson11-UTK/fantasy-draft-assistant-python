import pandas as pd

from src.config import LEAGUES
from src.projections import (
    load_razzball,
    add_projection_match,
)
from src.live_draft import LiveDraft


# ---------------------------------------------------------
# LOAD BOARD
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
# LEAGUE
# ---------------------------------------------------------

league_key = "karns"
league = LEAGUES[league_key]

draft = LiveDraft(
    board,
    league,
)


# ---------------------------------------------------------
# SIMULATE FIRST 27 PICKS
#
# Use ESPN ADP order, but let LiveDraft automatically
# assign each player to the correct team slot.
# ---------------------------------------------------------

draftable = (
    board[
        board["position"].isin(
            ["QB", "RB", "WR", "TE"]
        )
        & board["espn_adp"].notna()
    ]
    .sort_values("espn_adp")
    .copy()
)


first_27 = (
    draftable
    .head(27)["player"]
    .tolist()
)


for player_name in first_27:

    # Pick 4 and pick 21 belong to us in Karns.
    my_pick = draft.is_my_pick()

    draft.draft_player(
        player_name,
        my_pick=my_pick,
    )


# ---------------------------------------------------------
# WE SHOULD NOW BE AT PICK 28
# ---------------------------------------------------------

print("=" * 115)
print("SURVIVAL ADJUSTMENT TEST - PICK 28")
print("=" * 115)

print()
print("Current pick:", draft.current_pick)
print("My roster:", draft.get_roster())


# ---------------------------------------------------------
# SHOW TEAM ROSTERS
# ---------------------------------------------------------

print()
print("=" * 115)
print("TEAM ROSTERS AFTER 27 PICKS")
print("=" * 115)


for team_slot in range(
    1,
    league["teams"] + 1,
):

    roster = draft.get_team_roster(
        team_slot
    )

    positions = [
        player["position"]
        for player in roster
    ]

    names = [
        player["player"]
        for player in roster
    ]

    print(
        f"Team {team_slot:>2}: "
        f"{positions} | "
        f"{', '.join(names)}"
    )


# ---------------------------------------------------------
# GET UPDATED RECOMMENDATIONS
# ---------------------------------------------------------

result = draft.get_recommendations(
    league_key
)


columns = [
    "player",
    "position",
    "ecr",
    "espn_adp",
    "base_survive_next_pick",
    "opponent_demand_index",
    "p_survive_next_pick",
]


display = (
    result[
        columns
    ]
    .head(40)
    .copy()
)


display[
    "base_survive_next_pick"
] *= 100


display[
    "p_survive_next_pick"
] *= 100


print()
print("=" * 115)
print("BASE VS OPPONENT-ADJUSTED SURVIVAL")
print("=" * 115)


print(
    display.to_string(
        index=False,
        formatters={
            "ecr": "{:.1f}".format,
            "espn_adp": "{:.1f}".format,
            "base_survive_next_pick": "{:.1f}%".format,
            "opponent_demand_index": "{:.2f}".format,
            "p_survive_next_pick": "{:.1f}%".format,
        },
    )
)