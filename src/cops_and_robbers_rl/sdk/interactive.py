"""SDK-owned interactive session used by native user interfaces."""

from dataclasses import dataclass

from cops_and_robbers_rl.agents.base_agent import BaseAgent
from cops_and_robbers_rl.agents.heuristic_cop import HeuristicCopAgent
from cops_and_robbers_rl.agents.heuristic_thief import HeuristicThiefAgent
from cops_and_robbers_rl.environment.game_state import Role
from cops_and_robbers_rl.environment.grid import Position
from cops_and_robbers_rl.environment.rules import GameEngine
from cops_and_robbers_rl.environment.scoring import Score
from cops_and_robbers_rl.shared.config import GameConfig
from cops_and_robbers_rl.shared.paths import RESULTS_ROOT

DEFAULT_SCREENSHOT_DIR = RESULTS_ROOT / "screenshots"


@dataclass(frozen=True, slots=True)
class InteractiveSnapshot:
    """Read-only display state exposed by the public SDK layer."""

    grid_size: tuple[int, int]
    sub_game_id: int
    num_games: int
    moves_completed: int
    max_moves: int
    cop_position: Position
    thief_position: Position
    barriers: frozenset[Position]
    terminal: bool
    winner: Role | None
    sub_game_score: Score
    match_score: Score
    full_match_complete: bool


class InteractiveSession:
    """Advance heuristic agents while keeping rules inside the environment."""

    def __init__(
        self,
        config: GameConfig,
        cop_agent: BaseAgent | None = None,
        thief_agent: BaseAgent | None = None,
    ) -> None:
        self.config = config
        self.cop_agent = cop_agent or HeuristicCopAgent(seed=config.random_seed)
        self.thief_agent = thief_agent or HeuristicThiefAgent(seed=config.random_seed + 1)
        if self.cop_agent.role is not Role.COP or self.thief_agent.role is not Role.THIEF:
            raise ValueError("interactive session requires cop and thief role agents")
        self._match_score = Score(0, 0)
        self._sub_game_score = Score(0, 0)
        self._score_recorded = False
        self._full_match_complete = False
        self._engine = self._new_engine(1)

    @property
    def snapshot(self) -> InteractiveSnapshot:
        """Return the current renderer-safe snapshot."""
        state = self._engine.state
        return InteractiveSnapshot(
            grid_size=self.config.grid_size,
            sub_game_id=state.sub_game_id,
            num_games=self.config.num_games,
            moves_completed=state.moves_completed,
            max_moves=self.config.max_moves,
            cop_position=state.cop_position,
            thief_position=state.thief_position,
            barriers=state.barriers,
            terminal=state.terminal,
            winner=state.winner,
            sub_game_score=self._sub_game_score,
            match_score=self._match_score,
            full_match_complete=self._full_match_complete,
        )

    def reset(self) -> InteractiveSnapshot:
        """Reset the interactive match to sub-game one."""
        self._match_score = Score(0, 0)
        self._full_match_complete = False
        self._engine = self._new_engine(1)
        return self.snapshot

    def step(self) -> InteractiveSnapshot:
        """Advance one legal environment turn from local observations."""
        if self._engine.state.terminal:
            return self.snapshot
        cop_observation, thief_observation = self._engine.observations()
        result = self._engine.step(
            self.cop_agent.act(cop_observation),
            self.thief_agent.act(thief_observation),
        )
        if result.scores is not None and not self._score_recorded:
            self._sub_game_score = result.scores
            self._match_score = Score(
                self._match_score.cop + result.scores.cop,
                self._match_score.thief + result.scores.thief,
            )
            self._score_recorded = True
        return self.snapshot

    def run_sub_game(self) -> InteractiveSnapshot:
        """Run the current sub-game to a terminal state."""
        while not self._engine.state.terminal:
            self.step()
        return self.snapshot

    def run_full_match(self) -> InteractiveSnapshot:
        """Run all six configured sub-games and retain the last board."""
        self.reset()
        for sub_game_id in range(1, self.config.num_games + 1):
            if sub_game_id > 1:
                self._engine = self._new_engine(sub_game_id)
            self.run_sub_game()
        self._full_match_complete = True
        return self.snapshot

    def _new_engine(self, sub_game_id: int) -> GameEngine:
        seed = self.config.random_seed + sub_game_id - 1
        self.cop_agent.reset(seed)
        self.thief_agent.reset(seed)
        self._sub_game_score = Score(0, 0)
        self._score_recorded = False
        return GameEngine(self.config, sub_game_id=sub_game_id, seed=seed)
