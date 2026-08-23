from pathlib import Path

import pandas as pd
import streamlit as st

from src.config import LEAGUES
from src.projections import (
    load_razzball,
    add_projection_match,
)
from src.live_draft import LiveDraft


PLAYER_FILE = Path("data/processed/player_board.csv")
RAZZBALL_FILE = Path("data/raw/razzball.csv")


# ---------------------------------------------------------
# PAGE SETUP
# ---------------------------------------------------------

st.set_page_config(
    page_title="Fantasy Draft Assistant 2026",
    page_icon="🏈",
    layout="wide",
)

st.title("Fantasy Draft Assistant 2026")


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

@st.cache_data
def load_board():
    board = pd.read_csv(PLAYER_FILE)

    projections = load_razzball(
        RAZZBALL_FILE
    )

    board = add_projection_match(
        board,
        projections,
    )

    return board


board = load_board()


# ---------------------------------------------------------
# LEAGUE SETTINGS
# ---------------------------------------------------------

league_key = st.sidebar.selectbox(
    "League",
    options=[
        "karns",
        "mo_better",
    ],
    format_func=lambda key: LEAGUES[key]["name"],
)

league = LEAGUES[league_key].copy()


if league_key == "mo_better":

    slot = st.sidebar.number_input(
        "Draft slot",
        min_value=1,
        max_value=league["teams"],
        value=1,
        step=1,
    )

    league["draft_slot"] = int(slot)


st.sidebar.markdown(
    f"**Teams:** {league['teams']}"
)

if league.get("draft_slot"):

    st.sidebar.markdown(
        f"**Draft slot:** {league['draft_slot']}"
    )


# ---------------------------------------------------------
# LIVE DRAFT STATE
# ---------------------------------------------------------

state_key = f"live_draft_{league_key}"


if state_key not in st.session_state:

    st.session_state[state_key] = LiveDraft(
        board=board,
        league=league,
    )


draft = st.session_state[state_key]

draft.league = league


if st.sidebar.button(
    "Reset Draft",
    use_container_width=True,
):

    draft.reset()
    st.rerun()


# ---------------------------------------------------------
# DRAFT TURN MATH
# ---------------------------------------------------------

def my_pick_numbers(
    teams: int,
    draft_slot: int,
    rounds: int = 30,
) -> list[int]:

    picks = []

    for round_num in range(
        1,
        rounds + 1,
    ):

        if round_num % 2 == 1:

            pick = (
                (round_num - 1)
                * teams
                + draft_slot
            )

        else:

            pick = (
                round_num
                * teams
                - draft_slot
                + 1
            )

        picks.append(pick)

    return picks


draft_slot = league.get(
    "draft_slot"
)

if draft_slot is None:

    st.error(
        "Draft slot must be set before using live draft mode."
    )

    st.stop()


my_picks = my_pick_numbers(
    teams=league["teams"],
    draft_slot=draft_slot,
)


current_pick = draft.current_pick

is_my_pick = (
    current_pick in my_picks
)


future_my_picks = [
    pick
    for pick in my_picks
    if pick >= current_pick
]


if future_my_picks:

    next_my_pick = future_my_picks[0]

else:

    next_my_pick = None


if next_my_pick is not None:

    picks_until_my_turn = (
        next_my_pick
        - current_pick
    )

else:

    picks_until_my_turn = None


# ---------------------------------------------------------
# SIDEBAR DRAFT STATUS
# ---------------------------------------------------------

st.sidebar.divider()


st.sidebar.metric(
    "Current Overall Pick",
    current_pick,
)


if is_my_pick:

    st.sidebar.metric(
        "Your Turn",
        "NOW",
    )

else:

    st.sidebar.metric(
        "Your Next Pick",
        next_my_pick
        if next_my_pick is not None
        else "-",
    )

    st.sidebar.metric(
        "Picks Until Your Turn",
        picks_until_my_turn
        if picks_until_my_turn is not None
        else "-",
    )


st.sidebar.metric(
    "Players Drafted",
    len(draft.get_drafted()),
)


st.sidebar.metric(
    "My Players",
    len(draft.get_roster()),
)


# ---------------------------------------------------------
# TURN BANNER
# ---------------------------------------------------------

if is_my_pick:

    st.success(
        f"🔥 YOU'RE ON THE CLOCK — PICK {current_pick}"
    )

else:

    if picks_until_my_turn == 1:

        st.warning(
            f"⏳ YOU'RE NEXT — Pick {next_my_pick}"
        )

    else:

        st.info(
            f"Next pick: {next_my_pick} • "
            f"{picks_until_my_turn} picks until your turn"
        )


# ---------------------------------------------------------
# RECOMMENDATIONS
# ---------------------------------------------------------

try:

    recommendations = draft.get_recommendations(
        league_key
    )

except ValueError as error:

    st.error(str(error))
    st.stop()


if recommendations.empty:

    st.warning(
        "No available offensive players remain."
    )

    st.stop()


# ---------------------------------------------------------
# BEST PICK
# ---------------------------------------------------------

best = recommendations.iloc[0]


st.subheader(
    "Best Pick Right Now"
)


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Player",
        best["player"],
    )


with col2:

    st.metric(
        "Position",
        best["position"],
    )


with col3:

    st.metric(
        "Decision Score",
        f"{best['decision_score']:.1f}",
    )


with col4:

    survival = (
        best["p_survive_next_pick"]
        * 100
    )

    st.metric(
        "Chance Available Next Pick",
        f"{survival:.1f}%",
    )


st.success(
    f"{best['recommendation']}: "
    f"{best['player']} "
    f"({best['position']})"
)


# ---------------------------------------------------------
# ALTERNATIVES
# ---------------------------------------------------------

alternatives = recommendations[
    recommendations[
        "recommendation"
    ].isin(
        [
            "STRONG ALTERNATIVE",
            "ALTERNATIVE",
        ]
    )
].head(5)


if not alternatives.empty:

    st.subheader(
        "Alternatives"
    )

    alt_display = alternatives[
        [
            "player",
            "position",
            "decision_score",
            "espn_adp",
            "ecr",
            "p_survive_next_pick",
            "recommendation",
        ]
    ].copy()

    alt_display[
        "p_survive_next_pick"
    ] *= 100

    alt_display = alt_display.rename(
        columns={
            "player": "Player",
            "position": "Pos",
            "decision_score": "Decision Score",
            "espn_adp": "ESPN ADP",
            "ecr": "ECR",
            "p_survive_next_pick": "Survive %",
            "recommendation": "Recommendation",
        }
    )

    st.dataframe(
        alt_display,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Decision Score":
                st.column_config.NumberColumn(
                    format="%.1f"
                ),
            "ESPN ADP":
                st.column_config.NumberColumn(
                    format="%.1f"
                ),
            "ECR":
                st.column_config.NumberColumn(
                    format="%.1f"
                ),
            "Survive %":
                st.column_config.NumberColumn(
                    format="%.1f%%"
                ),
        },
    )


# ---------------------------------------------------------
# RECORD DRAFT PICK
# ---------------------------------------------------------

st.divider()

st.subheader(
    "Record Draft Pick"
)


st.caption(
    "Quick picks — top 8 available players by ESPN ADP"
)


quick_picks = (
    recommendations[
        recommendations[
            "espn_adp"
        ].notna()
    ]
    .sort_values(
        "espn_adp"
    )
    .head(8)
    .copy()
)


for start in range(
    0,
    len(quick_picks),
    4,
):

    row_players = quick_picks.iloc[
        start:start + 4
    ]

    cols = st.columns(4)


    for col, (_, player) in zip(
        cols,
        row_players.iterrows(),
    ):

        with col:

            st.markdown(
                f"**{player['player']}**"
            )

            st.caption(
                f"{player['position']} | "
                f"ADP {player['espn_adp']:.1f} | "
                f"ECR {player['ecr']:.1f}"
            )


            if st.button(
                "Other Team",
                key=f"quick_other_{player['player']}",
                use_container_width=True,
                disabled=is_my_pick,
            ):

                draft.draft_player(
                    player["player"],
                    my_pick=False,
                )

                st.rerun()


            if st.button(
                "My Team",
                key=f"quick_mine_{player['player']}",
                use_container_width=True,
                disabled=not is_my_pick,
            ):

                draft.draft_player(
                    player["player"],
                    my_pick=True,
                )

                st.rerun()


# ---------------------------------------------------------
# SEARCH / FALLBACK
# ---------------------------------------------------------

st.markdown(
    "##### Search any available player"
)


available_names = (
    recommendations[
        "player"
    ]
    .dropna()
    .drop_duplicates()
    .tolist()
)


selected_player = st.selectbox(
    "Player selected",
    options=available_names,
)


button_col1, button_col2 = st.columns(2)


with button_col1:

    if st.button(
        "Drafted by Other Team",
        key="search_other",
        use_container_width=True,
        disabled=is_my_pick,
    ):

        draft.draft_player(
            selected_player,
            my_pick=False,
        )

        st.rerun()


with button_col2:

    if st.button(
        "Draft to My Team",
        key="search_mine",
        use_container_width=True,
        disabled=not is_my_pick,
    ):

        draft.draft_player(
            selected_player,
            my_pick=True,
        )

        st.rerun()


# ---------------------------------------------------------
# MY ROSTER
# ---------------------------------------------------------

st.divider()

st.subheader(
    "My Roster"
)


roster = draft.get_roster()


if roster:

    roster_df = pd.DataFrame(
        roster
    )

    roster_df = roster_df.rename(
        columns={
            "player": "Player",
            "position": "Pos",
        }
    )

    st.dataframe(
        roster_df,
        hide_index=True,
        use_container_width=True,
    )

else:

    st.info(
        "No players drafted to your team yet."
    )


# ---------------------------------------------------------
# PLAYER BOARD
# ---------------------------------------------------------

st.divider()

st.subheader(
    "Available Player Board"
)


position_filter = st.multiselect(
    "Positions",
    options=[
        "QB",
        "RB",
        "WR",
        "TE",
    ],
    default=[
        "QB",
        "RB",
        "WR",
        "TE",
    ],
)


search = st.text_input(
    "Player search"
)


display_board = recommendations[
    recommendations[
        "position"
    ].isin(
        position_filter
    )
].copy()


if search:

    display_board = display_board[
        display_board[
            "player"
        ]
        .str.contains(
            search,
            case=False,
            na=False,
        )
    ]


display_cols = [
    "player",
    "team",
    "position",
    "ecr",
    "espn_adp",
    "market_gap",
    "vor",
    "decision_score",
    "p_survive_next_pick",
    "recommendation",
]


display_board = display_board[
    display_cols
].copy()


display_board[
    "p_survive_next_pick"
] *= 100


display_board = display_board.rename(
    columns={
        "player": "Player",
        "team": "Team",
        "position": "Pos",
        "ecr": "ECR",
        "espn_adp": "ESPN ADP",
        "market_gap": "ADP Gap",
        "vor": "VOR",
        "decision_score": "Decision Score",
        "p_survive_next_pick": "Survive %",
        "recommendation": "Recommendation",
    }
)


st.dataframe(
    display_board,
    hide_index=True,
    use_container_width=True,
    height=700,
    column_config={
        "ECR":
            st.column_config.NumberColumn(
                format="%.1f"
            ),
        "ESPN ADP":
            st.column_config.NumberColumn(
                format="%.1f"
            ),
        "ADP Gap":
            st.column_config.NumberColumn(
                format="%+.1f"
            ),
        "VOR":
            st.column_config.NumberColumn(
                format="%.1f"
            ),
        "Decision Score":
            st.column_config.NumberColumn(
                format="%.1f"
            ),
        "Survive %":
            st.column_config.NumberColumn(
                format="%.1f%%"
            ),
    },
)