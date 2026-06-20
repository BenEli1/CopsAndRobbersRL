"""Stable SDK facade for deterministic game workflows."""

from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from cops_and_robbers_rl.environment.actions import Action, ActionType
from cops_and_robbers_rl.environment.game_state import (
    MatchResult,
    Role,
    Student,
    SubGameResult,
)
from cops_and_robbers_rl.environment.observations import LocalObservation
from cops_and_robbers_rl.environment.rules import GameEngine
from cops_and_robbers_rl.environment.scoring import Score, score_for_winner
from cops_and_robbers_rl.shared.config import GameConfig, load_game_config

Policy = Callable[[LocalObservation], Action]
_JERUSALEM = ZoneInfo("Asia/Jerusalem")


def _stay_policy(_observation: LocalObservation) -> Action:
    return Action(ActionType.STAY)


class CopsAndRobbersSDK:
    """Single public entry point for game engine business workflows."""

    def __init__(self, config: GameConfig) -> None:
        self.config = config

    @classmethod
    def from_config(cls, path: str | Path | None = None) -> "CopsAndRobbersSDK":
        """Build the SDK from a validated YAML configuration."""
        return cls(load_game_config(path))

    def create_sub_game(
        self,
        sub_game_id: int,
        *,
        seed: int | None = None,
    ) -> GameEngine:
        """Create a deterministic sub-game engine."""
        return GameEngine(self.config, sub_game_id=sub_game_id, seed=seed)

    def run_match(
        self,
        cop_policy: Policy = _stay_policy,
        thief_policy: Policy = _stay_policy,
        *,
        group_name: str = "BenEli1",
        students: tuple[Student, ...] = (Student("A", "Ben Eli", "000000000"),),
        github_repo: str = "https://github.com/BenEli1/CopsAndRobbersRL",
    ) -> MatchResult:
        """Run configured sub-games and return an email-report-ready result."""
        results = tuple(
            self._run_sub_game(
                sub_game_id,
                self.config.random_seed + sub_game_id - 1,
                cop_policy,
                thief_policy,
            )
            for sub_game_id in range(1, self.config.num_games + 1)
        )
        totals = Score(
            cop=sum(game.scores.cop for game in results),
            thief=sum(game.scores.thief for game in results),
        )
        return MatchResult(
            group_name=group_name,
            students=students,
            github_repo=github_repo,
            timezone="Asia/Jerusalem",
            sub_games=results,
            totals=totals,
        )

    def _run_sub_game(
        self,
        sub_game_id: int,
        seed: int,
        cop_policy: Policy,
        thief_policy: Policy,
    ) -> SubGameResult:
        engine = self.create_sub_game(sub_game_id, seed=seed)
        start = datetime.now(_JERUSALEM)
        while not engine.state.terminal:
            cop_observation, thief_observation = engine.observations()
            engine.step(cop_policy(cop_observation), thief_policy(thief_observation))
        end = datetime.now(_JERUSALEM)
        winner = engine.state.winner
        if winner not in {Role.COP, Role.THIEF}:
            raise RuntimeError("terminal sub-game has no winner")
        scores = score_for_winner(winner.value, self.config.scoring)
        return SubGameResult(
            id=sub_game_id,
            start=start,
            end=end,
            moves=engine.state.moves_completed,
            winner=winner,
            scores=scores,
        )
