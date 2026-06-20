"""Deterministic simultaneous-step game engine."""

from dataclasses import dataclass

from cops_and_robbers_rl.environment.actions import Action, ActionType
from cops_and_robbers_rl.environment.game_state import (
    GameState,
    GlobalTrainingState,
    Role,
    TerminalReason,
)
from cops_and_robbers_rl.environment.grid import Grid, Position
from cops_and_robbers_rl.environment.observations import LocalObservation
from cops_and_robbers_rl.environment.scoring import Score, score_for_winner
from cops_and_robbers_rl.environment.transitions import (
    IllegalActionError,
    build_observations,
    resolve_move,
    spawn_positions,
    validate_barrier,
)
from cops_and_robbers_rl.shared.config import GameConfig

__all__ = ["GameEngine", "IllegalActionError", "StepResult"]


@dataclass(frozen=True, slots=True)
class StepResult:
    """State transition plus decentralized observations and legality metadata."""

    state: GameState
    cop_observation: LocalObservation
    thief_observation: LocalObservation
    cop_action_legal: bool
    thief_action_legal: bool
    cop_illegal_reason: str | None
    thief_illegal_reason: str | None
    scores: Score | None


class GameEngine:
    """Own deterministic rules for one sub-game."""

    def __init__(
        self,
        config: GameConfig,
        *,
        sub_game_id: int = 1,
        seed: int | None = None,
        cop_start: Position | None = None,
        thief_start: Position | None = None,
    ) -> None:
        self.config = config
        self.grid = Grid(*config.grid_size)
        cop_position, thief_position = spawn_positions(
            config, self.grid, seed, cop_start, thief_start
        )
        self._state = GameState(
            sub_game_id=sub_game_id,
            cop_position=cop_position,
            thief_position=thief_position,
            barriers=frozenset(),
            moves_completed=0,
        )

    @property
    def state(self) -> GameState:
        """Return the immutable internal state snapshot."""
        return self._state

    def observations(self) -> tuple[LocalObservation, LocalObservation]:
        """Return local observations for cop and thief."""
        return build_observations(self._state, self.grid, self.config)

    def global_state_for_training(self) -> GlobalTrainingState:
        """Return privileged state through an explicit training/debug API."""
        state = self._state
        return GlobalTrainingState(
            grid_size=self.config.grid_size,
            cop_position=state.cop_position,
            thief_position=state.thief_position,
            barriers=state.barriers,
            moves_completed=state.moves_completed,
            terminal=state.terminal,
        )

    def step(self, cop_action: Action, thief_action: Action) -> StepResult:
        """Resolve simultaneous action intents and advance exactly one move."""
        previous = self._state
        if previous.terminal:
            raise RuntimeError("cannot step a terminal sub-game")

        thief_destination, thief_legal, thief_reason = resolve_move(
            self.config,
            self.grid,
            Role.THIEF,
            thief_action,
            previous.thief_position,
            previous.barriers,
        )
        cop_destination, cop_legal, cop_reason = resolve_move(
            self.config,
            self.grid,
            Role.COP,
            cop_action,
            previous.cop_position,
            previous.barriers,
        )
        barriers = previous.barriers
        if cop_action.kind is ActionType.PLACE_BARRIER:
            cop_destination = previous.cop_position
            cop_legal, cop_reason = validate_barrier(
                self.config, self.grid, previous, cop_action, thief_destination
            )
            if cop_legal and cop_action.target is not None:
                barriers = barriers | {cop_action.target}

        captured = cop_destination == thief_destination
        crossed = (
            self.config.crossing_counts_as_capture
            and cop_destination == previous.thief_position
            and thief_destination == previous.cop_position
        )
        moves_completed = previous.moves_completed + 1
        terminal = captured or crossed or moves_completed >= self.config.max_moves
        winner = Role.COP if captured or crossed else Role.THIEF if terminal else None
        reason = self._terminal_reason(captured or crossed, terminal)
        self._state = GameState(
            sub_game_id=previous.sub_game_id,
            cop_position=cop_destination,
            thief_position=thief_destination,
            barriers=frozenset(barriers),
            moves_completed=moves_completed,
            terminal=terminal,
            winner=winner,
            terminal_reason=reason,
        )
        cop_observation, thief_observation = self.observations()
        scores = score_for_winner(winner.value, self.config.scoring) if winner else None
        return StepResult(
            state=self._state,
            cop_observation=cop_observation,
            thief_observation=thief_observation,
            cop_action_legal=cop_legal,
            thief_action_legal=thief_legal,
            cop_illegal_reason=cop_reason,
            thief_illegal_reason=thief_reason,
            scores=scores,
        )

    @staticmethod
    def _terminal_reason(captured: bool, terminal: bool) -> TerminalReason | None:
        if captured:
            return TerminalReason.CAPTURE
        if terminal:
            return TerminalReason.MOVE_LIMIT
        return None
