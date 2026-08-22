from pathlib import Path

import pandas as pd
import streamlit as st

from src.config import LEAGUES
from src.draft_math import snake_pick_numbers
from src.board import rank_for_league


PLAYER_FILE = Path("data/processed/player_board.csv")

st.set_page_config(
    page_title="Fantasy Draft Assistant 2026",
    page_icon="🏈",
    layout="wide",
)

st.title("Fantasy Draft Assistant 2026")

league_key = st.sidebar.selectbox(
    "League",
    options=["karns", "mo_better"],
    format_func=lambda key: LEAGUES[key]["name"],
)

league = LEAGUES[league_key]

st.sidebar.markdown(f"**Teams:** {league['teams']}")

if league_key == "karns":
    st.sidebar.markdown("**Draft slot:** 4")
    st.sidebar.markdown("**Draft:** 16-round snake")
else:
    st.sidebar.markdown("**Draft slot:** Random / TBD")

if league_key == "karns":
    picks = snake_pick_numbers(
        teams=league["teams"],
        slot=league["draft_slot"],
        rounds=league["rounds"],
    )

    st.subheader("Karns draft path")
    preview = " → ".join(
        f"{round_num}.{((pick - 1) % league['teams']) + 1:02d}"
        for round_num, pick in enumerate(picks[:8], start=1)
    )
    st.write(preview)

if not PLAYER_FILE.exists():
    st.info(
        "The app shell is ready. No fake player data is loaded. "
        "Run `uv run python refresh_data.py` from the project root to pull "
        "the first raw 2026 source snapshots."
    )

    st.markdown(
        """
### Build sequence

1. Pull raw projections and ADP.
2. Inspect the downloaded source columns.
3. Normalize player names and IDs.
4. Calculate Karns and Mo Better projected points.
5. Add ECR / ESPN ADP.
6. Add VOR, tiers and positional scarcity.
7. Add **Will he make it back?** probability.
8. Add live drafted-player and roster controls.
"""
    )

    if league_key == "karns":
        st.markdown("### Karns required draft composition")
        requirements = pd.DataFrame(
            {
                "Position": league["draft_requirements"].keys(),
                "Players to draft": league["draft_requirements"].values(),
            }
        )
        st.dataframe(requirements, hide_index=True, use_container_width=True)

    st.stop()

players = pd.read_csv(PLAYER_FILE)

positions = ["All"] + sorted(players["position"].dropna().unique().tolist())
position = st.sidebar.selectbox("Position", positions)
search = st.sidebar.text_input("Player search")

board = rank_for_league(players, league_key)

if position != "All":
    board = board[board["position"] == position]

if search:
    board = board[
        board["player"].str.contains(search, case=False, na=False)
    ]

display_cols = [
    c
    for c in [
        "player",
        "team",
        "position",
        "ecr",
        "espn_adp",
        "adp_gap",
        "bye",
        "sd",
        "best",
        "worst",
    ]
    if c in board.columns
]

st.subheader("Draft board")
rename_cols = {
    "player": "Player",
    "team": "Team",
    "position": "Pos",
    "ecr": "ECR",
    "espn_adp": "ESPN ADP",
    "adp_gap": "ADP Gap",
    "bye": "Bye",
    "sd": "ECR SD",
    "best": "Best Rank",
    "worst": "Worst Rank",
}

display_board = board[display_cols].rename(columns=rename_cols)
st.dataframe(
    display_board,
    hide_index=True,
    use_container_width=True,
    height=700,
    column_config={
        "ECR": st.column_config.NumberColumn(
            format="%.1f"
        ),
        "ESPN ADP": st.column_config.NumberColumn(
            format="%.1f"
        ),
        "ADP Gap": st.column_config.NumberColumn(
            format="%+.1f"
        ),
        "ECR SD": st.column_config.NumberColumn(
            format="%.1f"
        ),
    }
)
