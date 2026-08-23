from src.config import LEAGUES
from src.roster_state import (
    roster_counts,
    starter_needs,
    position_need_score,
)


league = LEAGUES["karns"]


scenarios = {
    "RB / RB start": [
        {
            "player": "RB One",
            "position": "RB",
        },
        {
            "player": "RB Two",
            "position": "RB",
        },
    ],

    "WR / WR start": [
        {
            "player": "WR One",
            "position": "WR",
        },
        {
            "player": "WR Two",
            "position": "WR",
        },
    ],

    "RB / WR start": [
        {
            "player": "RB One",
            "position": "RB",
        },
        {
            "player": "WR One",
            "position": "WR",
        },
    ],
}


for name, roster in scenarios.items():

    print()
    print("=" * 70)
    print(name)
    print("=" * 70)

    print(
        "Roster:",
        roster_counts(roster),
    )

    print(
        "Starter needs:",
        starter_needs(
            roster,
            league,
        ),
    )

    print()

    for position in [
        "QB",
        "RB",
        "WR",
        "TE",
    ]:

        score = position_need_score(
            position,
            roster,
            league,
        )

        print(
            f"{position}: {score:.2f}"
        )