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


# =========================================================
# PAGE SETUP
# =========================================================

st.set_page_config(
    page_title="Fantasy Draft Assistant 2026",
    layout="wide",
)


# =========================================================
# CUSTOM STYLING
# =========================================================

st.markdown(
    """
    <style>

    /* --------------------------------------------------
       APP BACKGROUND
       -------------------------------------------------- */

    .stApp {
        background: #081a33;
        color: #f8fafc;
    }

    .block-container {
        max-width: 1500px;
        padding-top: 1.4rem;
        padding-left: 1.7rem;
        padding-right: 1.7rem;
        padding-bottom: 3rem;
    }


    /* --------------------------------------------------
       GLOBAL TEXT
       -------------------------------------------------- */

    html,
    body,
    [class*="css"] {
        color: #f8fafc;
    }

    h1,
    h2,
    h3,
    h4,
    h5,
    h6 {
        color: #ffffff !important;
        font-weight: 750;
    }

    p,
    label,
    span {
        color: inherit;
    }

    .main-title {
        color: #ffffff;
        font-size: 2.55rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }

    .section-subtitle {
        color: #b7c4d8;
        font-size: 0.9rem;
        margin-top: -0.45rem;
        margin-bottom: 0.9rem;
    }


    /* --------------------------------------------------
       SIDEBAR
       -------------------------------------------------- */

    section[data-testid="stSidebar"] {
        background: #0d2342;
        border-right: 1px solid #203b60;
    }

    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span {
        color: #f8fafc !important;
    }


    /* --------------------------------------------------
       METRIC CARDS
       -------------------------------------------------- */

    div[data-testid="stMetric"] {
        background: #132b4c;
        border: 1px solid #2b476b;
        padding: 11px 13px;
        border-radius: 10px;
    }

    div[data-testid="stMetric"] label {
        color: #c6d2e3 !important;
    }

    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
    }


    /* --------------------------------------------------
       STATUS BOXES
       -------------------------------------------------- */

    .status-box {
        background: #132b4c;
        border: 1px solid #2b476b;
        border-left: 5px solid #3b82f6;
        border-radius: 9px;
        padding: 11px 14px;
        color: #ffffff;
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: 16px;
    }

    .on-clock {
        border-left-color: #22c55e;
        background: #123726;
    }

    .next-up {
        border-left-color: #f59e0b;
        background: #3d2d10;
    }


    /* --------------------------------------------------
       LEADER BOX
       -------------------------------------------------- */

    .leader-box {
        background: #123726;
        border: 1px solid #2d6b49;
        border-left: 5px solid #22c55e;
        border-radius: 9px;
        padding: 10px 13px;
        color: #ffffff;
        font-weight: 700;
        margin-bottom: 10px;
    }


    /* --------------------------------------------------
       QUICK DRAFT CARDS
       -------------------------------------------------- */

    .draft-card {
        background: #f8fafc;
        border: 1px solid #d7deea;
        border-radius: 10px;
        padding: 12px 14px;
        min-height: 108px;
        margin-bottom: 6px;
        color: #111827;
        border-left: 6px solid #64748b;
    }

    .draft-card-rb {
        border-left-color: #22c55e;
    }

    .draft-card-wr {
        border-left-color: #3b82f6;
    }

    .draft-card-qb {
        border-left-color: #ef4444;
    }

    .draft-card-te {
        border-left-color: #a855f7;
    }

    .player-name {
        color: #111827;
        font-size: 1rem;
        font-weight: 800;
        margin-bottom: 6px;
    }

    .player-line {
        color: #4b5563;
        font-size: 0.84rem;
        line-height: 1.5;
    }

    .bye-warning {
        color: #b45309;
        font-size: 0.8rem;
        font-weight: 750;
        margin-top: 5px;
    }


    /* --------------------------------------------------
       BUTTONS
       -------------------------------------------------- */

    div.stButton > button {
        border-radius: 8px;
        font-weight: 650;
        border: 1px solid #3b82f6;
    }

    div.stButton > button:not(:disabled) {
        background: #0f2b50;
        color: #ffffff;
    }

    div.stButton > button:not(:disabled):hover {
        background: #173d6b;
        border-color: #60a5fa;
        color: #ffffff;
    }

    div.stButton > button:disabled {
        background: #e5e7eb;
        color: #9ca3af;
        border-color: #d1d5db;
    }


    /* --------------------------------------------------
       INPUTS
       -------------------------------------------------- */

    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    input {
        background-color: #102846 !important;
        color: #ffffff !important;
        border-color: #355275 !important;
    }

    input::placeholder {
        color: #94a3b8 !important;
    }

    [data-testid="stMultiSelect"] span {
        color: #ffffff !important;
    }


    /* --------------------------------------------------
       DATAFRAMES / TABLE AREA
       -------------------------------------------------- */

    div[data-testid="stDataFrame"] {
        background: #102846;
        border: 1px solid #2b476b;
        border-radius: 9px;
        overflow: hidden;
    }


    /* --------------------------------------------------
       DIVIDERS
       -------------------------------------------------- */

    hr {
        border-color: #284465;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="main-title">Fantasy Draft Assistant 2026</div>',
    unsafe_allow_html=True,
)

# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_board():

    board = pd.read_csv(
        PLAYER_FILE
    )

    projections = load_razzball(
        RAZZBALL_FILE
    )

    board = add_projection_match(
        board,
        projections,
    )

    return board


board = load_board()


# =========================================================
# LEAGUE SETTINGS
# =========================================================

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


# =========================================================
# LIVE DRAFT STATE
# =========================================================

state_key = f"live_draft_{league_key}"


if state_key not in st.session_state:

    st.session_state[state_key] = LiveDraft(
        board=board,
        league=league,
    )


draft = st.session_state[state_key]

draft.league = league


# =========================================================
# RESET / UNDO CONTROLS
# =========================================================

if "confirm_reset" not in st.session_state:
    st.session_state.confirm_reset = False


# ---------------------------------------------------------
# NORMAL RESET BUTTON
# ---------------------------------------------------------

if not st.session_state.confirm_reset:

    if st.sidebar.button(
        "Reset Draft",
        use_container_width=True,
    ):
        st.session_state.confirm_reset = True
        st.rerun()


# ---------------------------------------------------------
# RESET CONFIRMATION
# ---------------------------------------------------------

else:

    st.sidebar.error(
        "RESET ENTIRE DRAFT?"
    )

    st.sidebar.caption(
        "This removes every recorded pick and your entire roster."
    )

    reset_cancel_col, reset_confirm_col = st.sidebar.columns(2)

    with reset_cancel_col:

        if st.button(
            "Cancel",
            key="cancel_reset",
            use_container_width=True,
        ):
            st.session_state.confirm_reset = False
            st.rerun()

    with reset_confirm_col:

        if st.button(
            "Confirm Reset",
            key="confirm_reset_button",
            use_container_width=True,
            type="primary",
        ):
            draft.reset()
            st.session_state.confirm_reset = False
            st.rerun()


# ---------------------------------------------------------
# UNDO LAST PICK
# ---------------------------------------------------------

if st.sidebar.button(
    "Undo Last Pick",
    use_container_width=True,
    disabled=len(draft.get_drafted()) == 0,
):

    draft.undo_last_pick()

    # If reset confirmation happened to be open,
    # close it when another draft action occurs.
    st.session_state.confirm_reset = False

    st.rerun()

# =========================================================
# DRAFT TURN MATH
# =========================================================

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


next_my_pick = (
    future_my_picks[0]
    if future_my_picks
    else None
)


picks_until_my_turn = (
    next_my_pick - current_pick
    if next_my_pick is not None
    else None
)


future_after_next = [
    pick
    for pick in my_picks
    if next_my_pick is not None
    and pick > next_my_pick
]


following_my_pick = (
    future_after_next[0]
    if future_after_next
    else None
)


# =========================================================
# SIDEBAR STATUS
# =========================================================

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


if following_my_pick is not None:

    st.sidebar.caption(
        f"Following pick: {following_my_pick}"
    )


st.sidebar.metric(
    "Players Drafted",
    len(draft.get_drafted()),
)


st.sidebar.metric(
    "My Players",
    len(draft.get_roster()),
)


# =========================================================
# TURN BANNER
# =========================================================

if is_my_pick:

    st.markdown(
        f'<div class="status-box on-clock">YOU ARE ON THE CLOCK — PICK {current_pick}</div>',
        unsafe_allow_html=True,
    )

elif picks_until_my_turn == 1:

    st.markdown(
        f'<div class="status-box next-up">YOU ARE NEXT — PICK {next_my_pick}</div>',
        unsafe_allow_html=True,
    )

else:

    st.markdown(
        f'<div class="status-box">Next pick: {next_my_pick} &nbsp;&nbsp; | &nbsp;&nbsp; {picks_until_my_turn} picks until your turn</div>',
        unsafe_allow_html=True,
    )


# =========================================================
# RECOMMENDATIONS
# =========================================================

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


# =========================================================
# CURRENT ROSTER DETAILS
# =========================================================

roster = draft.get_roster()


if roster:

    roster_df = pd.DataFrame(
        roster
    )

    roster_details = (
        board[
            [
                "player",
                "team",
                "bye",
            ]
        ]
        .drop_duplicates(
            subset=["player"]
        )
    )

    roster_df = roster_df.merge(
        roster_details,
        on="player",
        how="left",
    )

else:

    roster_df = pd.DataFrame(
        columns=[
            "player",
            "position",
            "team",
            "bye",
        ]
    )


# =========================================================
# BYE CONFLICT FUNCTIONS
# =========================================================

def bye_conflict_for_player(
    player_row,
) -> bool:

    if roster_df.empty:
        return False

    player_bye = player_row.get(
        "bye"
    )

    player_pos = player_row.get(
        "position"
    )

    if pd.isna(player_bye):
        return False

    conflict = roster_df[
        (roster_df["position"] == player_pos)
        & (roster_df["bye"] == player_bye)
    ]

    return not conflict.empty


def bye_conflict_names(
    player_row,
) -> list[str]:

    if roster_df.empty:
        return []

    player_bye = player_row.get(
        "bye"
    )

    player_pos = player_row.get(
        "position"
    )

    if pd.isna(player_bye):
        return []

    conflicts = roster_df[
        (roster_df["position"] == player_pos)
        & (roster_df["bye"] == player_bye)
    ]

    return conflicts[
        "player"
    ].tolist()


# =========================================================
# OPPONENT DEMAND LABEL
# =========================================================

def opponent_demand_label(
    demand_index: float,
) -> str:
    """
    Convert the opponent-demand number into
    something readable during the draft.
    """

    if pd.isna(demand_index):
        return "Unknown"

    if demand_index >= 1.12:
        return "High"

    if demand_index >= 1.04:
        return "Slightly High"

    if demand_index <= 0.88:
        return "Low"

    if demand_index <= 0.96:
        return "Slightly Low"

    return "Neutral"

# =========================================================
# MAIN TABS
# =========================================================

assistant_tab, draft_board_tab = st.tabs(
    [
        "Draft Assistant",
        "League Draft Board",
    ]
)

with assistant_tab:

# =========================================================
    # TOP AVAILABLE
    # =========================================================
    
    st.subheader(
        "Top Available"
    )
    
    
    top_available = (
        recommendations
        .head(7)
        .copy()
    )
    
    
    leader = top_available.iloc[0]
    
    
    st.markdown(
        (
            '<div class="leader-box">'
            f'Model leader: {leader["player"]} ({leader["position"]})'
            f' &nbsp; | &nbsp; Decision Score {leader["decision_score"]:.1f}'
            '</div>'
        ),
        unsafe_allow_html=True,
    )
    
    
    top_available[
        "opponent_demand"
    ] = (
        top_available[
            "opponent_demand_index"
        ]
        .apply(
            opponent_demand_label
        )
    )
    
    
    top_cols = [
        "player",
        "position",
        "bye",
        "decision_score",
        "espn_adp",
        "ecr",
        "base_survive_next_pick",
        "opponent_demand",
        "p_survive_next_pick",
        "recommendation",
    ]
    
    
    top_display = top_available[
        top_cols
    ].copy()
    
    
    top_display[
        "base_survive_next_pick"
    ] *= 100
    
    
    top_display[
        "p_survive_next_pick"
    ] *= 100
    
    
    top_display = top_display.rename(
        columns={
            "player": "Player",
            "position": "Pos",
            "bye": "Bye",
            "decision_score": "Decision",
            "espn_adp": "ESPN ADP",
            "ecr": "ECR",
            "base_survive_next_pick": "Base Survive %",
            "opponent_demand": "Opponent Demand",
            "p_survive_next_pick": "Adjusted Survive %",
            "recommendation": "Recommendation",
        }
    )
    
    
    st.dataframe(
        top_display,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Decision":
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
    
            "Base Survive %":
                st.column_config.NumberColumn(
                    format="%.1f%%"
                ),
    
            "Adjusted Survive %":
                st.column_config.NumberColumn(
                    format="%.1f%%"
                ),
        },
    )
    
    
    # =========================================================
    # QUICK DRAFT
    # =========================================================
    
    st.divider()
    
    st.subheader(
        "Quick Draft"
    )
    
    st.markdown(
        '<div class="section-subtitle">Top 8 available players by ESPN ADP</div>',
        unsafe_allow_html=True,
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
    
                pos_class = str(
                    player["position"]
                ).lower()
    
    
                bye_value = (
                    int(player["bye"])
                    if pd.notna(
                        player["bye"]
                    )
                    else "-"
                )
    
    
                conflict = bye_conflict_for_player(
                    player
                )
    
    
                conflict_players = (
                    bye_conflict_names(
                        player
                    )
                )
    
    
                if conflict:
    
                    names = ", ".join(
                        conflict_players
                    )
    
                    conflict_line = (
                        f'<div class="bye-warning">'
                        f'Bye conflict with {names}'
                        f'</div>'
                    )
    
                else:
    
                    conflict_line = ""
    
    
                card_html = (
                    f'<div class="draft-card draft-card-{pos_class}">'
                    f'<div class="player-name">{player["player"]}</div>'
                    f'<div class="player-line">'
                    f'{player["position"]} | '
                    f'{player["team"]} | '
                    f'Bye {bye_value}'
                    f'</div>'
                    f'<div class="player-line">'
                    f'ADP {player["espn_adp"]:.1f} | '
                    f'ECR {player["ecr"]:.1f}'
                    f'</div>'
                    f'{conflict_line}'
                    f'</div>'
                )
    
    
                st.markdown(
                    card_html,
                    unsafe_allow_html=True,
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
    
    
    # =========================================================
    # MY ROSTER
    # =========================================================
    
    st.divider()
    
    st.subheader(
        "My Roster"
    )
    
    
    if not roster_df.empty:
    
        roster_display = roster_df[
            [
                "player",
                "team",
                "position",
                "bye",
            ]
        ].copy()
    
    
        roster_display = roster_display.rename(
            columns={
                "player": "Player",
                "team": "Team",
                "position": "Pos",
                "bye": "Bye",
            }
        )
    
    
        st.dataframe(
            roster_display,
            hide_index=True,
            use_container_width=True,
        )
    
    else:
    
        st.info(
            "No players drafted to your team yet."
        )
    
    
    # =========================================================
    # AVAILABLE PLAYER BOARD
    # =========================================================
    
    st.divider()
    
    st.subheader(
        "Available Player Board"
    )
    
    
    # ---------------------------------------------------------
    # POSITION FILTER
    # ---------------------------------------------------------
    
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
    
    
    # ---------------------------------------------------------
    # PLAYER SEARCH
    # ---------------------------------------------------------
    
    search = st.text_input(
        "Player search",
        placeholder="Type a player name...",
    )
    
    
    # ---------------------------------------------------------
    # RECORD ANY AVAILABLE PLAYER
    # ---------------------------------------------------------
    
    available_names = (
        recommendations[
            "player"
        ]
        .dropna()
        .drop_duplicates()
        .tolist()
    )
    
    
    selected_player = st.selectbox(
        "Record any available player",
        options=available_names,
    )
    
    
    selected_row = recommendations[
        recommendations[
            "player"
        ]
        == selected_player
    ].iloc[0]
    
    
    selected_conflict = (
        bye_conflict_for_player(
            selected_row
        )
    )
    
    
    if selected_conflict:
    
        names = ", ".join(
            bye_conflict_names(
                selected_row
            )
        )
    
    
        bye_value = (
            int(
                selected_row["bye"]
            )
            if pd.notna(
                selected_row["bye"]
            )
            else "-"
        )
    
    
        st.warning(
            f"Bye-week overlap: {selected_player} is a "
            f"{selected_row['position']} with Bye {bye_value}. "
            f"You already have {names} at the same position "
            f"with that bye. You can still draft this player."
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
    # FILTER MAIN TABLE
    # ---------------------------------------------------------
    
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
    
    
    # ---------------------------------------------------------
    # BYE CONFLICT
    # ---------------------------------------------------------
    
    display_board[
        "bye_conflict"
    ] = display_board.apply(
        bye_conflict_for_player,
        axis=1,
    )
    
    
    display_board[
        "bye_conflict"
    ] = display_board[
        "bye_conflict"
    ].map(
        {
            True: "YES",
            False: "",
        }
    )
    
    
    # ---------------------------------------------------------
    # OPPONENT DEMAND
    # ---------------------------------------------------------
    
    display_board[
        "opponent_demand"
    ] = (
        display_board[
            "opponent_demand_index"
        ]
        .apply(
            opponent_demand_label
        )
    )
    
    
    # ---------------------------------------------------------
    # CONVERT PROBABILITIES TO PERCENTAGES
    # ---------------------------------------------------------
    
    display_board[
        "base_survive_next_pick"
    ] *= 100
    
    
    display_board[
        "p_survive_next_pick"
    ] *= 100
    
    
    # ---------------------------------------------------------
    # DISPLAY COLUMNS
    # ---------------------------------------------------------
    
    display_cols = [
        "player",
        "team",
        "position",
        "bye",
        "ecr",
        "espn_adp",
        "market_gap",
        "vor",
        "decision_score",
        "base_survive_next_pick",
        "opponent_demand",
        "p_survive_next_pick",
        "bye_conflict",
        "recommendation",
    ]
    
    
    display_board = display_board[
        display_cols
    ].copy()
    
    
    display_board = display_board.rename(
        columns={
            "player": "Player",
            "team": "Team",
            "position": "Pos",
            "bye": "Bye",
            "ecr": "ECR",
            "espn_adp": "ESPN ADP",
            "market_gap": "ADP Gap",
            "vor": "VOR",
            "decision_score": "Decision",
            "base_survive_next_pick": "Base Survive %",
            "opponent_demand": "Opponent Demand",
            "p_survive_next_pick": "Adjusted Survive %",
            "bye_conflict": "Bye Conflict",
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
    
            "Decision":
                st.column_config.NumberColumn(
                    format="%.1f"
                ),
    
            "Base Survive %":
                st.column_config.NumberColumn(
                    format="%.1f%%"
                ),
    
            "Adjusted Survive %":
                st.column_config.NumberColumn(
                    format="%.1f%%"
                ),
        },
)

# =========================================================
# TAB 2 - LEAGUE DRAFT BOARD
# =========================================================

with draft_board_tab:

    st.subheader(
        "League Draft Board"
    )

    st.caption(
        "Live view of every team's drafted players."
    )

    all_rosters = (
        draft.get_all_team_rosters()
    )

    my_slot = league.get(
        "draft_slot"
    )


    # -----------------------------------------------------
    # TEAM NAMES
    #
    # Karns names can be replaced later with actual
    # owner/team names once we want them.
    # -----------------------------------------------------

    team_names = {
        slot: (
            "My Team"
            if slot == my_slot
            else f"Team {slot}"
        )
        for slot in range(
            1,
            league["teams"] + 1,
        )
    }


    # -----------------------------------------------------
    # BOARD STYLING
    # -----------------------------------------------------

    st.markdown(
        """
        <style>

        .draft-board-team {
            background: #0f223d;
            border: 1px solid #314966;
            border-radius: 9px;
            overflow: hidden;
            margin-bottom: 16px;
        }

        .draft-board-my-team {
            border: 2px solid #6ea8ff;
        }

        .draft-board-header {
            background: #162f52;
            color: #ffffff;
            font-weight: 800;
            padding: 9px 10px;
            font-size: 0.9rem;
            text-align: center;
        }

        .draft-board-player {
            color: #111827;
            padding: 8px 9px;
            border-top: 1px solid rgba(0,0,0,0.15);
        }

        .draft-board-player-name {
            font-weight: 800;
            font-size: 0.86rem;
        }

        .draft-board-player-meta {
            font-size: 0.72rem;
            margin-top: 2px;
            color: rgba(17,24,39,0.78);
        }

        .draft-board-qb {
            background: #d4869c;
        }

        .draft-board-rb {
            background: #86cfb7;
        }

        .draft-board-wr {
            background: #68afd1;
        }

        .draft-board-te {
            background: #dfa65e;
        }

        .draft-board-empty {
            padding: 12px 10px;
            color: #9fb0c3;
            font-size: 0.8rem;
            text-align: center;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


    # -----------------------------------------------------
    # RENDER TEAM COLUMNS
    # -----------------------------------------------------

    team_slots = list(
        range(
            1,
            league["teams"] + 1,
        )
    )

    teams_per_row = 4


    for start in range(
        0,
        len(team_slots),
        teams_per_row,
    ):

        row_slots = team_slots[
            start:start + teams_per_row
        ]

        cols = st.columns(
            len(row_slots)
        )


        for col, team_slot in zip(
            cols,
            row_slots,
        ):

            with col:

                roster = all_rosters.get(
                    team_slot,
                    [],
                )

                team_class = (
                    " draft-board-my-team"
                    if team_slot == my_slot
                    else ""
                )


                html = (
                    f'<div class="draft-board-team{team_class}">'
                    f'<div class="draft-board-header">'
                    f'{team_names[team_slot]}'
                    f'</div>'
                )


                if roster:

                    for player in roster:

                        player_name = (
                            player["player"]
                        )

                        position = (
                            player["position"]
                        )

                        pick_number = (
                            player["pick"]
                        )

                        position_class = (
                            str(position)
                            .lower()
                        )


                        player_match = board[
                            board["player"]
                            == player_name
                        ]


                        if not player_match.empty:

                            nfl_team = (
                                player_match
                                .iloc[0]
                                .get(
                                    "team",
                                    "-"
                                )
                            )

                        else:

                            nfl_team = "-"


                        html += (
                            f'<div class="draft-board-player '
                            f'draft-board-{position_class}">'
                            f'<div class="draft-board-player-name">'
                            f'{player_name}'
                            f'</div>'
                            f'<div class="draft-board-player-meta">'
                            f'{position} | '
                            f'{nfl_team} | '
                            f'Pick {pick_number}'
                            f'</div>'
                            f'</div>'
                        )

                else:

                    html += (
                        '<div class="draft-board-empty">'
                        'No picks yet'
                        '</div>'
                    )


                html += '</div>'


                st.markdown(
                    html,
                    unsafe_allow_html=True,
                )