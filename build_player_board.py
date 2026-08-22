from pathlib import Path

import nflreadpy as nfl
import polars as pl


OUT = Path("data/processed/player_board.csv")


def main():
    rankings = nfl.load_ff_rankings(type="draft")
    player_ids = nfl.load_ff_playerids()

    board = (
        rankings
        .filter(
            (pl.col("ecr_type") == "ro")
            & (pl.col("page_type") == "redraft-overall")
            & (pl.col("pos").is_in(["QB", "RB", "WR", "TE", "K", "DST"]))
        )
        .select([
            "player",
            "id",
            "pos",
            "team",
            "ecr",
            "sd",
            "best",
            "worst",
            "bye",
            "scrape_date",
        ])
        .rename({
            "pos": "position"
        })
        .sort("ecr")
    )

    ids = (
        player_ids
        .select([
            "fantasypros_id",
            "espn_id",
            "sleeper_id",
            "yahoo_id",
            "gsis_id",
        ])
    )

    board = (
        board
        .join(
            ids,
            left_on="id",
            right_on="fantasypros_id",
            how="left"
        )
    )

    OUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    board.write_csv(OUT)

    print("\nPLAYER BOARD CREATED")
    print("Rows:", board.height)

    print("\nColumns:")
    print(board.columns)

    print("\nTop 25:")
    print(board.head(25))

    print("\nMissing ESPN IDs:")
    print(
        board
        .filter(pl.col("espn_id").is_null())
        .select([
            "player",
            "position",
            "team",
            "ecr"
        ])
        .head(20)
    )


if __name__ == "__main__":
    main()