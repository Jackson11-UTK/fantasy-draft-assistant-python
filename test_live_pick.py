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
from src.draft_state import (
    mark_drafted,
    available_players,
)


# ---------------------------------------------------------
# LOAD DATA
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

current_pick = 28


# ---------------------------------------------------------
# SIMULATE FIRST 27 PICKS
# ---------------------------------------------------------

draftable = board[
    board["position"].isin(
        ["QB", "RB", "WR", "TE"]
    )
].copy()

first_27 = (
    draftable[
        draftable["espn_adp"].notna()
    ]
    .sort_values("espn_adp")
    .head(27)["player"]
    .tolist()
)

board = mark_drafted(
    board,
    first_27,
)


# ---------------------------------------------------------
# BASE MODEL
# ---------------------------------------------------------

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
    draft_slot=league["draft_slot"],
    teams=league["teams"],
)

result = available_players(
    result
)

result = result[
    result["position"].isin(
        ["QB", "RB", "WR", "TE"]
    )
    & result["razzball_name"].notna()
].copy()


# ---------------------------------------------------------
# ROSTER SCENARIOS
# ---------------------------------------------------------

roster_scenarios = {
    "RB / RB START": [
        {
            "player": "RB One",
            "position": "RB",
        },
        {
            "player": "RB Two",
            "position": "RB",
        },
    ],

    "WR / WR START": [
        {
            "player": "WR One",
            "position": "WR",
        },
        {
            "player": "WR Two",
            "position": "WR",
        },
    ],

    "RB / WR START": [
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


# ---------------------------------------------------------
# OUTPUT
# ---------------------------------------------------------

columns = [
    "player",
    "position",
    "ecr",
    "espn_adp",
    "vor",
    "draft_score",
    "roster_need",
    "p_survive_next_pick",
    "urgency_score",
    "decision_score",
    "recommendation",
]


print("=" * 125)
print("LIVE PICK TEST")
print("=" * 125)

print()
print("Current pick:", current_pick)
print(
    "Next pick:",
    result["next_pick"].iloc[0],
)

print()
print("SIMULATED FIRST 27 PICKS")
print("-" * 125)

for i, player in enumerate(
    first_27,
    start=1,
):
    print(
        f"{i:>2}. {player}"
    )


# ---------------------------------------------------------
# RUN EACH ROSTER SCENARIO
# ---------------------------------------------------------

for scenario_name, roster in roster_scenarios.items():

    scenario = add_decision_metrics(
        result,
        roster=roster,
        league=league,
    )

    display = (
        scenario
        .sort_values(
            "decision_score",
            ascending=False,
        )[columns]
        .head(15)
        .copy()
    )

    display["p_survive_next_pick"] *= 100

    print()
    print("=" * 125)
    print(scenario_name)
    print("=" * 125)

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
                "urgency_score": "{:.1f}".format,
                "decision_score": "{:.1f}".format,
            },
        )
    )