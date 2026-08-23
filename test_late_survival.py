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
# SIMULATE FIRST 75 PICKS
#
# We use ESPN ADP order to create a realistic draft shape.
# LiveDraft automatically assigns every player to the
# correct snake-draft team slot.
# ---------------------------------------------------------

draftable = (
    board[
        board["position"].isin(
            ["QB", "RB", "WR", "TE"]
        )
        & board["espn_adp"].notna()
    ]
    .sort_values(
        "espn_adp"
    )
    .copy()
)


first_75 = (
    draftable
    .head(75)["player"]
    .tolist()
)


for player_name in first_75:

    draft.draft_player(
        player_name,
        my_pick=draft.is_my_pick(),
    )


# ---------------------------------------------------------
# CURRENT STATE
# ---------------------------------------------------------

print("=" * 120)
print("LATE-ROUND SURVIVAL TEST")
print("=" * 120)

print()
print("Current pick:", draft.current_pick)
print("My roster:", draft.get_roster())


# ---------------------------------------------------------
# TEAM POSITION COUNTS
# ---------------------------------------------------------

print()
print("=" * 120)
print("TEAM POSITION COUNTS")
print("=" * 120)


for team_slot in range(
    1,
    league["teams"] + 1,
):

    roster = draft.get_team_roster(
        team_slot
    )

    counts = {
        "QB": 0,
        "RB": 0,
        "WR": 0,
        "TE": 0,
    }

    for player in roster:

        position = player["position"]

        if position in counts:
            counts[position] += 1

    print(
        f"Team {team_slot:>2}: "
        f"QB {counts['QB']} | "
        f"RB {counts['RB']} | "
        f"WR {counts['WR']} | "
        f"TE {counts['TE']}"
    )


# ---------------------------------------------------------
# RECOMMENDATIONS
# ---------------------------------------------------------

result = draft.get_recommendations(
    league_key
)


columns = [
    "player",
    "position",
    "ecr",
    "espn_adp",
    "current_round",
    "opponent_adjustment_strength",
    "base_survive_next_pick",
    "opponent_demand_index",
    "p_survive_next_pick",
]


display = (
    result[
        columns
    ]
    .head(50)
    .copy()
)


display[
    "base_survive_next_pick"
] *= 100

display[
    "p_survive_next_pick"
] *= 100


print()
print("=" * 120)
print("BASE VS ADJUSTED SURVIVAL")
print("=" * 120)


print(
    display.to_string(
        index=False,
        formatters={
            "ecr": "{:.1f}".format,
            "espn_adp": "{:.1f}".format,
            "opponent_adjustment_strength": "{:.2f}".format,
            "base_survive_next_pick": "{:.1f}%".format,
            "opponent_demand_index": "{:.2f}".format,
            "p_survive_next_pick": "{:.1f}%".format,
        },
    )
)


# ---------------------------------------------------------
# POSITION SUMMARY
# ---------------------------------------------------------

print()
print("=" * 120)
print("AVERAGE OPPONENT DEMAND BY POSITION")
print("=" * 120)


summary = (
    result[
        [
            "position",
            "opponent_demand_index",
        ]
    ]
    .drop_duplicates(
        subset=["position"]
    )
    .sort_values(
        "position"
    )
)


print(
    summary.to_string(
        index=False,
        formatters={
            "opponent_demand_index": "{:.2f}".format,
        },
    )
)