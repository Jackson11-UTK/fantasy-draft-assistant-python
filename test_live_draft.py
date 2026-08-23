import pandas as pd

from src.config import LEAGUES
from src.live_draft import LiveDraft


# ---------------------------------------------------------
# LOAD
# ---------------------------------------------------------

board = pd.read_csv(
    "data/processed/player_board.csv"
)

league = LEAGUES["karns"]

draft = LiveDraft(
    board,
    league,
)


# ---------------------------------------------------------
# START
# ---------------------------------------------------------

print("=" * 70)
print("START")
print("=" * 70)

print("Current pick:", draft.current_pick)
print("Roster:", draft.get_roster())


# ---------------------------------------------------------
# SIMULATE FIRST FOUR PICKS
#
# Karns draft slot = 4
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

draft.draft_player(
    "Puka Nacua",
    my_pick=True,
)


# ---------------------------------------------------------
# RESULTS
# ---------------------------------------------------------

print()
print("=" * 70)
print("AFTER FOUR PICKS")
print("=" * 70)

print()
print("Current pick:")
print(draft.current_pick)

print()
print("All drafted:")
for player in draft.get_drafted():
    print("-", player)

print()
print("MY ROSTER:")
for player in draft.get_roster():
    print(
        f"- {player['player']} ({player['position']})"
    )


# ---------------------------------------------------------
# TEAM ROSTERS
# ---------------------------------------------------------

print()
print("=" * 70)
print("TEAM ROSTERS")
print("=" * 70)

for team_slot in range(
    1,
    league["teams"] + 1,
):

    roster = draft.get_team_roster(
        team_slot
    )

    if roster:

        print()
        print(f"Team {team_slot}:")

        for player in roster:

            print(
                f"- Pick {player['pick']}: "
                f"{player['player']} "
                f"({player['position']})"
            )


# ---------------------------------------------------------
# AVAILABILITY CHECK
# ---------------------------------------------------------

available = draft.get_available()

names = available["player"].tolist()

print()
print("=" * 70)
print("AVAILABILITY CHECK")
print("=" * 70)

for player in [
    "Jahmyr Gibbs",
    "Bijan Robinson",
    "Ja'Marr Chase",
    "Puka Nacua",
]:

    print(
        player,
        "AVAILABLE?"
        if player in names
        else "DRAFTED",
    )


# ---------------------------------------------------------
# PICK OWNERSHIP CHECK
# ---------------------------------------------------------

print()
print("=" * 70)
print("PICK OWNERSHIP CHECK")
print("=" * 70)

for pick in [
    1,
    2,
    3,
    4,
    12,
    13,
    21,
    24,
    25,
    28,
]:

    print(
        f"Pick {pick}: "
        f"Team {draft.team_slot_for_pick(pick)}"
    )