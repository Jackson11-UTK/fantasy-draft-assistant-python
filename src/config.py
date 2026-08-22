"""League configuration.

Keep league-specific settings here so the rest of the project can remain generic.
"""

LEAGUES = {
    "karns": {
        "name": "Karns FFL",
        "teams": 12,
        "draft_type": "snake",
        "draft_slot": 4,
        "rounds": 16,
        "starters": {
            "QB": 1,
            "RB": 2,
            "WR": 2,
            "TE": 1,
            "FLEX": 1,
            "K": 1,
            "DST": 1,
        },
        "draft_requirements": {
            "QB": 2,
            "RB": 4,
            "WR": 4,
            "TE": 2,
            "K": 2,
            "DST": 2,
        },
        "scoring": {
            "pass_yards_per_point": 20,
            "pass_td": 6,
            "interception": -2,
            "qb_sack": -1,
            "rush_yards_per_point": 10,
            "rush_td": 6,
            "reception": 1,
            "rec_yards_per_point": 10,
            "rec_td": 6,
            "two_point": 2,
            "fumble_lost": -1,
        },
    },

    "mo_better": {
        "name": "Mo Better League",
        "teams": 10,
        "draft_type": "snake",
        "draft_slot": None,
        "rounds": None,
        "starters": {
            "QB": 1,
            "RB": 2,
            "WR": 2,
            "TE": 1,
            "FLEX": 1,
            "K": 1,
            "DST": 1,
        },
        "roster_max": {
            "QB": 2,
            "RB": 5,
            "WR": 5,
            "TE": 2,
            "K": 2,
            "DST": 2,
        },
        "bench": 9,
        "scoring": {
            "pass_yards_per_point": 20,
            "pass_td": 6,
            "interception": -2,
            "qb_sack": -1,
            "rush_yards_per_point": 10,
            "rush_td": 6,
            "reception": 1,
            "rec_yards_per_point": 10,
            "rec_td": 6,
            "two_point": 2,
            "fumble_lost": -2,

            # Game-level bonuses. We will estimate expected values later.
            "pass_300_399": 3,
            "pass_400_plus": 4,
            "rush_td_50_plus": 1,
            "rush_100_199": 2,
            "rush_200_plus": 3,
            "rec_td_50_plus": 1,
            "rec_100_199": 1,
            "rec_200_plus": 2,
        },
    },
}
