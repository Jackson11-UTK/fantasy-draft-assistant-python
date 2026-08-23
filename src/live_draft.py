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

        # Pick waiting to happen.
        self.current_pick = 1


    def draft_player(
        self,
        player_name: str,
        my_pick: bool = False,
    ):
        """
        Record one draft selection.

        my_pick=False:
            another team drafted the player

        my_pick=True:
            we drafted the player
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


    def get_available(
        self,
    ) -> pd.DataFrame:
        """
        Return players who have not been drafted.
        """

        return available_players(
            self.board
        )


    def get_roster(
        self,
    ) -> list[dict]:
        """
        Return our current roster.
        """

        return self.my_roster.copy()


    def get_drafted(
        self,
    ) -> list[str]:
        """
        Return all drafted players in draft order.
        """

        return self.drafted_players.copy()


    def get_recommendations(
        self,
        league_key: str,
    ) -> pd.DataFrame:
        """
        Run the complete recommendation model using
        the current live draft state.

        Accounts for:
        - drafted players
        - our roster
        - league scoring
        - VOR
        - ECR / ESPN ADP
        - survival probability
        - roster needs
        """

        result = self.board.copy()

        # ---------------------------------------------
        # PLAYER VALUE
        # ---------------------------------------------

        result = add_vor(
            result,
            league_key,
            self.league,
        )

        result = add_draft_score(
            result
        )

        # ---------------------------------------------
        # NEXT-PICK SURVIVAL
        # ---------------------------------------------

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

        # ---------------------------------------------
        # REMOVE DRAFTED / NON-DRAFTABLE PLAYERS
        # BEFORE LABELING BEST PICK
        # ---------------------------------------------

        result = available_players(
            result
        )

        result = result[
            result["position"].isin(
                ["QB", "RB", "WR", "TE"]
            )
            & result["razzball_name"].notna()
        ].copy()

        # ---------------------------------------------
        # ROSTER-AWARE DECISION MODEL
        # ---------------------------------------------

        result = add_decision_metrics(
            result,
            roster=self.my_roster,
            league=self.league,
        )

        # ---------------------------------------------
        # BEST RECOMMENDATION FIRST
        # ---------------------------------------------

        result = result.sort_values(
            "decision_score",
            ascending=False,
        )

        return result


    def reset(
        self,
    ):
        """
        Reset the entire draft.
        """

        self.board = self.original_board.copy()
        self.drafted_players = []
        self.my_roster = []
        self.current_pick = 1