"""Reliable six-sub-game orchestration for autonomous local agents."""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from cops_and_robbers_rl.agents.base_agent import BaseAgent
from cops_and_robbers_rl.environment.game_state import (
    MatchResult,
    Role,
    Student,
    SubGameResult,
)
from cops_and_robbers_rl.environment.rules import GameEngine
from cops_and_robbers_rl.environment.scoring import Score, score_for_winner
from cops_and_robbers_rl.shared.config import GameConfig
from cops_and_robbers_rl.shared.identity import load_report_students
from cops_and_robbers_rl.shared.paths import RESULTS_ROOT

_JERUSALEM = ZoneInfo("Asia/Jerusalem")
DEFAULT_REPORT_PATH = RESULTS_ROOT / "report_email_preview.json"


class MatchExecutionError(RuntimeError):
    """Raised when technical failures exhaust the retry budget."""


class MatchRunner:
    """Run valid sub-games while isolating agents to local observations."""

    def __init__(
        self,
        config: GameConfig,
        cop_agent: BaseAgent,
        thief_agent: BaseAgent,
        *,
        max_attempts_per_sub_game: int = 3,
    ) -> None:
        if cop_agent.role is not Role.COP or thief_agent.role is not Role.THIEF:
            raise ValueError("MatchRunner requires cop and thief role agents")
        if config.num_games != 6:
            raise ValueError("assignment full matches require exactly six sub-games")
        if max_attempts_per_sub_game <= 0:
            raise ValueError("max_attempts_per_sub_game must be positive")
        self.config = config
        self.cop_agent = cop_agent
        self.thief_agent = thief_agent
        self.max_attempts_per_sub_game = max_attempts_per_sub_game
        self.technical_failures = 0

    def run(
        self,
        *,
        group_name: str = "BenEli1",
        students: tuple[Student, ...] | None = None,
        github_repo: str = "https://github.com/BenEli1/CopsAndRobbersRL",
    ) -> MatchResult:
        """Run the configured number of valid sub-games and aggregate scores."""
        self.technical_failures = 0
        games = tuple(
            self._run_valid_sub_game(game_id) for game_id in range(1, self.config.num_games + 1)
        )
        totals = Score(
            cop=sum(game.scores.cop for game in games),
            thief=sum(game.scores.thief for game in games),
        )
        return MatchResult(
            group_name=group_name,
            students=students if students is not None else load_report_students(),
            github_repo=github_repo,
            timezone="Asia/Jerusalem",
            sub_games=games,
            totals=totals,
        )

    def run_and_save(self, output_path: str | Path = DEFAULT_REPORT_PATH) -> MatchResult:
        """Run a match and atomically save the exact report JSON preview."""
        result = self.run()
        self.save_report(result, output_path)
        return result

    @staticmethod
    def save_report(result: MatchResult, output_path: str | Path) -> Path:
        """Atomically write a UTF-8 report JSON preview."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        payload = json.dumps(result.to_report_dict(), indent=2, ensure_ascii=False) + "\n"
        temporary.write_text(payload, encoding="utf-8")
        temporary.replace(path)
        return path

    def _run_valid_sub_game(self, sub_game_id: int) -> SubGameResult:
        seed = self.config.random_seed + sub_game_id - 1
        last_error: Exception | None = None
        for _attempt in range(1, self.max_attempts_per_sub_game + 1):
            try:
                return self._run_sub_game(sub_game_id, seed)
            except Exception as exc:  # Technical agent/runtime failures are retried.
                self.technical_failures += 1
                last_error = exc
        raise MatchExecutionError(
            f"sub-game {sub_game_id} failed after {self.max_attempts_per_sub_game} attempts"
        ) from last_error

    def _run_sub_game(self, sub_game_id: int, seed: int) -> SubGameResult:
        engine = GameEngine(self.config, sub_game_id=sub_game_id, seed=seed)
        self.cop_agent.reset(seed)
        self.thief_agent.reset(seed)
        start = datetime.now(_JERUSALEM)
        while not engine.state.terminal:
            cop_observation, thief_observation = engine.observations()
            engine.step(
                self.cop_agent.act(cop_observation),
                self.thief_agent.act(thief_observation),
            )
        end = datetime.now(_JERUSALEM)
        winner = engine.state.winner
        if winner not in {Role.COP, Role.THIEF}:
            raise MatchExecutionError("terminal sub-game has no winner")
        return SubGameResult(
            id=sub_game_id,
            start=start,
            end=end,
            moves=engine.state.moves_completed,
            winner=winner,
            scores=score_for_winner(winner.value, self.config.scoring),
        )
