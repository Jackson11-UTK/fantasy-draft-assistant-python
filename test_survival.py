import pandas as pd

from src.survival import add_survival_metrics, next_pick


def main():
    path = "data/processed/player_board.csv"

    df = pd.read_csv(path)

    # Simulate Karns.
    # We draft from slot 4 in a 12-team snake.
    current_pick = 28
    draft_slot = 4
    teams = 12

    print("=" * 100)
    print("SNAKE DRAFT TEST")
    print("=" * 100)

    nxt = next_pick(
        current_pick=current_pick,
        draft_slot=draft_slot,
        teams=teams,
    )

    print("Current pick:", current_pick)
    print("Next pick:", nxt)
    print("Picks until next turn:", nxt - current_pick)

    result = add_survival_metrics(
        df,
        current_pick=current_pick,
        draft_slot=draft_slot,
        teams=teams,
    )

    cols = [
    "player",
    "position",
    "ecr",
    "espn_adp",
    "draft_sd",
    "p_survive_next_pick",
    "p_gone_next_pick",
    "urgency_score",
]

    result = result[
        result["position"].isin(["QB", "RB", "WR", "TE"])
    ].copy()

    result = result.sort_values(
        "urgency_score",
        ascending=False,
    )

    print()
    print("=" * 100)
    print("MOST LIKELY TO BE GONE BEFORE OUR NEXT PICK")
    print("=" * 100)

    display = result[cols].head(40).copy()

    display["p_survive_next_pick"] *= 100
    display["p_gone_next_pick"] *= 100

    print(
        display.to_string(
            index=False,
            formatters={
                "ecr": "{:.1f}".format,
                "espn_adp": "{:.1f}".format,
                "p_survive_next_pick": "{:.1f}%".format,
                "p_gone_next_pick": "{:.1f}%".format,
                "urgency_score": "{:.1f}".format,
            },
        )
    )

    print()
    print("=" * 100)
    print("CHIG CHECK")
    print("=" * 100)

    chig = result[
        result["player"].str.contains(
            "Chig",
            case=False,
            na=False,
        )
    ][cols].copy()

    chig["p_survive_next_pick"] *= 100
    chig["p_gone_next_pick"] *= 100

    print(
        chig.to_string(
            index=False,
            formatters={
                "ecr": "{:.1f}".format,
                "espn_adp": "{:.1f}".format,
                "p_survive_next_pick": "{:.1f}%".format,
                "p_gone_next_pick": "{:.1f}%".format,
                "urgency_score": "{:.1f}".format,
            },
        )
    )


if __name__ == "__main__":
    main()