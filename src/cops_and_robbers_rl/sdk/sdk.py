"""Stable SDK facade for autonomous match workflows."""

from pathlib import Path

from cops_and_robbers_rl.agents.base_agent import BaseAgent
from cops_and_robbers_rl.agents.random_agents import RandomCopAgent, RandomThiefAgent
from cops_and_robbers_rl.environment.game_state import MatchResult, Student
from cops_and_robbers_rl.environment.rules import GameEngine
from cops_and_robbers_rl.runner.match_runner import DEFAULT_REPORT_PATH, MatchRunner
from cops_and_robbers_rl.shared.config import GameConfig, load_game_config


class CopsAndRobbersSDK:
    """Single public entry point for game engine business workflows."""

    def __init__(self, config: GameConfig) -> None:
        self.config = config
        self.last_technical_failures = 0

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
        """Create a deterministic sub-game engine for testing or debugging."""
        return GameEngine(self.config, sub_game_id=sub_game_id, seed=seed)

    def run_match(
        self,
        cop_agent: BaseAgent | None = None,
        thief_agent: BaseAgent | None = None,
        *,
        group_name: str = "BenEli1",
        students: tuple[Student, ...] = (Student("A", "Ben Eli", "319086435"),),
        github_repo: str = "https://github.com/BenEli1/CopsAndRobbersRL",
    ) -> MatchResult:
        """Run six valid sub-games with decentralized execution agents."""
        runner = self._runner(cop_agent, thief_agent)
        result = runner.run(
            group_name=group_name,
            students=students,
            github_repo=github_repo,
        )
        self.last_technical_failures = runner.technical_failures
        return result

    def run_match_and_save(
        self,
        cop_agent: BaseAgent | None = None,
        thief_agent: BaseAgent | None = None,
        *,
        output_path: str | Path = DEFAULT_REPORT_PATH,
    ) -> MatchResult:
        """Run a match and save its exact JSON report preview."""
        result = self.run_match(cop_agent, thief_agent)
        MatchRunner.save_report(result, output_path)
        return result

    def _runner(self, cop_agent: BaseAgent | None, thief_agent: BaseAgent | None) -> MatchRunner:
        return MatchRunner(
            self.config,
            cop_agent or RandomCopAgent(seed=self.config.random_seed),
            thief_agent or RandomThiefAgent(seed=self.config.random_seed + 1),
        )
