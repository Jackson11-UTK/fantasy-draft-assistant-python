from pathlib import Path

import pandas as pd


BOARD_FILE = Path("data/processed/player_board.csv")
ADP_FILE = Path("data/raw/espn_adp_2026.csv")


def main():
    board = pd.read_csv(BOARD_FILE)
    adp = pd.read_csv(ADP_FILE)

    adp = adp[
        [
            "espn_id",
            "ownership_adp",
        ]
    ].rename(
        columns={
            "ownership_adp": "espn_adp"
        }
    )

    board = board.merge(
        adp,
        on="espn_id",
        how="left"
    )

    board["adp_gap"] = (
        board["espn_adp"] - board["ecr"]
    )

    board.to_csv(
        BOARD_FILE,
        index=False
    )

    print("\nADP JOIN COMPLETE")
    print("Rows:", len(board))

    print("\nPlayers with ESPN ADP:")
    print(board["espn_adp"].notna().sum())

    print("\nTop 25:")
    print(
        board[
            [
                "player",
                "position",
                "team",
                "ecr",
                "espn_adp",
                "adp_gap",
            ]
        ]
        .sort_values("ecr")
        .head(25)
        .to_string(index=False)
    )

    print("\nBIGGEST POSITIVE ADP GAPS:")
    print(
        board[
            [
                "player",
                "position",
                "team",
                "ecr",
                "espn_adp",
                "adp_gap",
            ]
        ]
        .dropna(subset=["espn_adp"])
        .sort_values(
            "adp_gap",
            ascending=False
        )
        .head(20)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()