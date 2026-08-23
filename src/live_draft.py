from __future__ import annotations

import pandas as pd

from src.draft_state import mark_drafted, available_players
from src.value_model import add_vor
from src.draft_score import add_draft_score
from src.survival import add_survival_metrics
from src.decision_engine import add_decision_metrics


class LiveDraft:
    """
    Tracks the live draft and produces recommendations
    based on the current draft state.
    """

    def __init__(
        self,
        board: pd.DataFrame,
        league: dict,
    ):
        self.original_board = board.copy()
        self.board = board.copy()
        self.league = league

        self.drafted_players: list[str] = []
        self.my_roster: list[dict] = []

        # Stores each action so the most recent pick can be undone.
        self.history: list[dict] = []

        self.current_pick = 1


    def draft_player(
        self,
        player_name: str,
        my_pick: bool = False,
    ):
        """
        Record one draft selection.
        """

        available = available_players(
            self.board
        )

        match = available[
            available["player"] == player_name
        ]

        if match.empty:
            raise ValueError(
                f"{player_name} is not available."
            )

        player = match.iloc[0]

        # Save action BEFORE changing state.
        self.history.append(
            {
                "player": player_name,
                "position": player["position"],
                "my_pick": my_pick,
            }
        )

        self.board = mark_drafted(
            self.board,
            [player_name],
        )

        self.drafted_players.append(
            player_name
        )

        if my_pick:
            self.my_roster.append(
                {
                    "player": player_name,
                    "position": player["position"],
                }
            )

        self.current_pick += 1


    def undo_last_pick(
        self,
    ):
        """
        Undo the most recent draft selection.
        """

        if not self.history:
            raise ValueError(
                "There are no picks to undo."
            )

        last = self.history.pop()

        player_name = last["player"]

        # Mark player available again.
        mask = (
            self.board["player"]
            .str.strip()
            .str.lower()
            == player_name.strip().lower()
        )

        if "drafted" in self.board.columns:
            self.board.loc[
                mask,
                "drafted"
            ] = False

        # Remove most recent drafted-player entry.
        if self.drafted_players:
            self.drafted_players.pop()

        # If it was our player, remove it from our roster.
        if last["my_pick"]:

            for i in range(
                len(self.my_roster) - 1,
                -1,
                -1,
            ):

                if (
                    self.my_roster[i]["player"]
                    == player_name
                ):
                    self.my_roster.pop(i)
                    break

        # Move draft back one overall pick.
        self.current_pick = max(
            1,
            self.current_pick - 1,
        )

        return last


    def get_available(
        self,
    ) -> pd.DataFrame:

        return available_players(
            self.board
        )


    def get_roster(
        self,
    ) -> list[dict]:

        return self.my_roster.copy()


    def get_drafted(
        self,
    ) -> list[str]:

        return self.drafted_players.copy()


    def get_recommendations(
        self,
        league_key: str,
    ) -> pd.DataFrame:

        result = self.board.copy()

        result = add_vor(
            result,
            league_key,
            self.league,
        )

        result = add_draft_score(
            result
        )

        draft_slot = self.league.get(
            "draft_slot"
        )

        if draft_slot is None:
            raise ValueError(
                "League draft_slot must be set before "
                "live recommendations can be calculated."
            )

        result = add_survival_metrics(
            result,
            current_pick=self.current_pick,
            draft_slot=draft_slot,
            teams=self.league["teams"],
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

        result = add_decision_metrics(
            result,
            roster=self.my_roster,
            league=self.league,
        )

        result = result.sort_values(
            "decision_score",
            ascending=False,
        )

        return result


    def reset(
        self,
    ):

        self.board = self.original_board.copy()
        self.drafted_players = []
        self.my_roster = []
        self.history = []
        self.current_pick = 1