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
# SIMULATE PICKS
# ---------------------------------------------------------

print("=" * 70)
print("START")
print("=" * 70)

print("Current pick:", draft.current_pick)
print("Roster:", draft.get_roster())


# Other team takes Gibbs
draft.draft_player(
    "Jahmyr Gibbs",
    my_pick=False,
)

# Other team takes Bijan
draft.draft_player(
    "Bijan Robinson",
    my_pick=False,
)

# We take Ja'Marr
draft.draft_player(
    "Ja'Marr Chase",
    my_pick=True,
)

# Other team takes Puka
draft.draft_player(
    "Puka Nacua",
    my_pick=False,
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
# VERIFY THEY ARE GONE
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
        "AVAILABLE?" if player in names else "DRAFTED",
    )