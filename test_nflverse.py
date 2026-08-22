import nflreadpy as nfl
import polars as pl


rankings = nfl.load_ff_rankings(type="draft")


print("\nSCRAPE DATES:")
print(
    rankings
    .group_by("scrape_date")
    .len()
    .sort("scrape_date", descending=True)
    .head(10)
)


print("\nECR TYPES:")
print(
    rankings
    .group_by("ecr_type")
    .len()
    .sort("len", descending=True)
)


print("\nREDRAFT PAGE TYPES:")
print(
    rankings
    .filter(
        pl.col("ecr_type").str.starts_with("r")
    )
    .group_by(
        ["ecr_type", "page_type"]
    )
    .len()
    .sort(
        ["ecr_type", "len"],
        descending=[False, True]
    )
)


print("\nREDRAFT OVERALL CANDIDATES:")
print(
    rankings
.filter(
    (pl.col("ecr_type") == "ro")
    & (pl.col("page_type") == "redraft-overall")
    & (pl.col("pos").is_in(["QB", "RB", "WR", "TE", "K", "DST"]))
)
    .select(
        [
            "player",
            "pos",
            "team",
            "ecr",
            "sd",
            "best",
            "worst",
            "page_type",
            "scrape_date"
        ]
    )
    .sort("ecr")
    .head(25)
)