from __future__ import annotations

import math

import pandas as pd

from src.draft_state import (
    mark_drafted,
    available_players,
)
from src.value_model import add_vor
from src.draft_score import add_draft_score
from src.survival import add_survival_metrics
from src.decision_engine import add_decision_metrics


class LiveDraft:
    """
    Tracks the live fantasy draft.

    In addition to drafted players and our roster,
    this class now tracks the roster of EVERY team
    based on the snake-draft pick order.
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

        # Every action is stored for undo.
        self.history: list[dict] = []

        # Pick waiting to happen.
        self.current_pick = 1

        # Track every team's roster by draft slot.
        self.team_rosters: dict[int, list[dict]] = {
            slot: []
            for slot in range(
                1,
                league["teams"] + 1,
            )
        }


    # =====================================================
    # SNAKE DRAFT MATH
    # =====================================================

    def team_slot_for_pick(
        self,
        overall_pick: int,
    ) -> int:
        """
        Return the draft-slot/team that owns an overall pick.

        Example in a 12-team league:

        Round 1:
        pick 1 -> team 1
        pick 4 -> team 4
        pick 12 -> team 12

        Round 2:
        pick 13 -> team 12
        pick 21 -> team 4
        pick 24 -> team 1
        """

        teams = self.league["teams"]

        round_num = math.ceil(
            overall_pick / teams
        )

        position_in_round = (
            (overall_pick - 1) % teams
        ) + 1

        if round_num % 2 == 1:

            return position_in_round

        return (
            teams
            - position_in_round
            + 1
        )


    def is_my_pick(
        self,
        overall_pick: int | None = None,
    ) -> bool:
        """
        Return True when the specified pick belongs to us.
        Defaults to the current pick.
        """

        if overall_pick is None:
            overall_pick = self.current_pick

        my_slot = self.league.get(
            "draft_slot"
        )

        if my_slot is None:
            return False

        return (
            self.team_slot_for_pick(
                overall_pick
            )
            == my_slot
        )


    # =====================================================
    # RECORD PICK
    # =====================================================

    def draft_player(
        self,
        player_name: str,
        my_pick: bool = False,
    ):
        """
        Record one player selection.

        The team receiving the player is determined
        automatically from the current overall pick.
        """

        available = available_players(
            self.board
        )

        match = available[
            available["player"]
            == player_name
        ]

        if match.empty:

            raise ValueError(
                f"{player_name} is not available."
            )

        player = match.iloc[0]

        pick_number = self.current_pick

        team_slot = self.team_slot_for_pick(
            pick_number
        )

        my_slot = self.league.get(
            "draft_slot"
        )

        # -------------------------------------------------
        # SAFETY CHECK
        # -------------------------------------------------

        if (
            my_slot is not None
            and team_slot == my_slot
            and not my_pick
        ):

            raise ValueError(
                f"Pick {pick_number} belongs to your team. "
                "Record this selection as My Team."
            )

        if (
            my_slot is not None
            and team_slot != my_slot
            and my_pick
        ):

            raise ValueError(
                f"Pick {pick_number} belongs to Team "
                f"{team_slot}, not your team."
            )


        # -------------------------------------------------
        # SAVE HISTORY FOR UNDO
        # -------------------------------------------------

        action = {
            "pick": pick_number,
            "team_slot": team_slot,
            "player": player_name,
            "position": player["position"],
            "my_pick": my_pick,
        }

        self.history.append(
            action
        )


        # -------------------------------------------------
        # MARK PLAYER DRAFTED
        # -------------------------------------------------

        self.board = mark_drafted(
            self.board,
            [player_name],
        )

        self.drafted_players.append(
            player_name
        )


        # -------------------------------------------------
        # ADD TO TEAM ROSTER
        # -------------------------------------------------

        roster_entry = {
            "player": player_name,
            "position": player["position"],
            "pick": pick_number,
        }

        self.team_rosters[
            team_slot
        ].append(
            roster_entry
        )


        # -------------------------------------------------
        # ADD TO OUR ROSTER
        # -------------------------------------------------

        if my_pick:

            self.my_roster.append(
                {
                    "player": player_name,
                    "position": player["position"],
                }
            )


        # Advance draft.
        self.current_pick += 1


    # =====================================================
    # UNDO
    # =====================================================

    def undo_last_pick(
        self,
    ):
        """
        Undo the most recent selection.

        Restores:
        - player availability
        - overall pick
        - league-team roster
        - our roster, when applicable
        """

        if not self.history:

            raise ValueError(
                "There are no picks to undo."
            )


        last = self.history.pop()

        player_name = last["player"]
        team_slot = last["team_slot"]


        # -------------------------------------------------
        # MAKE PLAYER AVAILABLE AGAIN
        # -------------------------------------------------

        mask = (
            self.board["player"]
            .str.strip()
            .str.lower()
            == player_name
            .strip()
            .lower()
        )

        if "drafted" in self.board.columns:

            self.board.loc[
                mask,
                "drafted"
            ] = False


        # -------------------------------------------------
        # DRAFTED LIST
        # -------------------------------------------------

        if self.drafted_players:

            self.drafted_players.pop()


        # -------------------------------------------------
        # TEAM ROSTER
        # -------------------------------------------------

        team_roster = self.team_rosters[
            team_slot
        ]

        for i in range(
            len(team_roster) - 1,
            -1,
            -1,
        ):

            if (
                team_roster[i]["player"]
                == player_name
            ):

                team_roster.pop(i)
                break


        # -------------------------------------------------
        # OUR ROSTER
        # -------------------------------------------------

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


        # Restore exact pick.
        self.current_pick = last["pick"]

        return last


    # =====================================================
    # GETTERS
    # =====================================================

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


    def get_team_roster(
        self,
        team_slot: int,
    ) -> list[dict]:
        """
        Return one fantasy team's current roster.
        """

        return [
            player.copy()
            for player in self.team_rosters[
                team_slot
            ]
        ]


    def get_all_team_rosters(
        self,
    ) -> dict[int, list[dict]]:
        """
        Return every fantasy team's current roster.
        """

        return {
            slot: [
                player.copy()
                for player in roster
            ]
            for slot, roster
            in self.team_rosters.items()
        }


    # =====================================================
    # RECOMMENDATIONS
    # =====================================================

    def get_recommendations(
        self,
        league_key: str,
    ) -> pd.DataFrame:

        result = self.board.copy()


        # -------------------------------------------------
        # PLAYER VALUE
        # -------------------------------------------------

        result = add_vor(
            result,
            league_key,
            self.league,
        )

        result = add_draft_score(
            result
        )


        # -------------------------------------------------
        # SURVIVAL
        # -------------------------------------------------

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


        # -------------------------------------------------
        # AVAILABLE PLAYERS ONLY
        # -------------------------------------------------

        result = available_players(
            result
        )

        result = result[
            result["position"].isin(
                [
                    "QB",
                    "RB",
                    "WR",
                    "TE",
                ]
            )
            & result[
                "razzball_name"
            ].notna()
        ].copy()


        # -------------------------------------------------
        # ROSTER-AWARE DECISION MODEL
        # -------------------------------------------------

        result = add_decision_metrics(
            result,
            roster=self.my_roster,
            league=self.league,
        )


        result = add_survival_metrics(
    result,
    current_pick=self.current_pick,
    draft_slot=draft_slot,
    teams=self.league["teams"],
    team_rosters=self.team_rosters,
    league=self.league,
)

        return result


    # =====================================================
    # RESET
    # =====================================================

    def reset(
        self,
    ):

        self.board = (
            self.original_board.copy()
        )

        self.drafted_players = []

        self.my_roster = []

        self.history = []

        self.current_pick = 1

        self.team_rosters = {
            slot: []
            for slot in range(
                1,
                self.league["teams"] + 1,
            )
        }