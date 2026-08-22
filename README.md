# Fantasy Draft Assistant 2026

Python + Streamlit fantasy-football draft assistant for two ESPN leagues.

## Leagues

### Karns FFL
- 12 teams
- Snake draft
- Draft slot: 4
- 16 rounds
- Full PPR
- 6-point passing TDs
- 1 point per 20 passing yards
- -2 interceptions
- -1 point per QB sack
- Exact draft composition:
  - 2 QB
  - 4 RB
  - 4 WR
  - 2 TE
  - 2 K
  - 2 DST

### Mo Better League
- 10 teams
- Snake draft
- Draft slot: random / TBD
- Full PPR
- 6-point passing TDs
- 1 point per 20 passing yards
- -2 interceptions
- -1 point per QB sack
- Larger RB/WR roster limits
- 9 bench spots
- Yardage-game and long-TD bonuses

## Project structure

```text
fantasy-draft-assistant-python/
├── app.py
├── refresh_data.py
├── pyproject.toml
├── README.md
├── src/
│   ├── config.py
│   ├── scoring.py
│   ├── draft_math.py
│   ├── data_sources.py
│   └── board.py
├── data/
│   ├── raw/
│   └── processed/
└── tests/
    └── test_draft_math.py
```

## Start here

From the project root:

```bash
uv sync
uv run streamlit run app.py
```

The app runs immediately. Until a real player file is created, it shows setup instructions rather than fake player data.

To refresh source data:

```bash
uv run python refresh_data.py
```

## Development plan

1. Pull 2026 projections and ADP.
2. Normalize player names / IDs.
3. Score raw projections under each league's exact rules.
4. Calculate replacement value and positional tiers.
5. Add ESPN ADP and ECR.
6. Model probability a player survives to your next pick.
7. Add live draft controls and roster tracking.
8. Add injuries, depth charts, news and risk flags.
9. Polish for draft-night use.
