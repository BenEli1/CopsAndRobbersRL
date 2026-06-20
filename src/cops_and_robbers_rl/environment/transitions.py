"""Pure validation, spawn, and observation helpers for game transitions."""

from random import Random

from cops_and_robbers_rl.environment.actions import Action, ActionType
from cops_and_robbers_rl.environment.game_state import GameState, Role
from cops_and_robbers_rl.environment.grid import Grid, Position
from cops_and_robbers_rl.environment.observations import LocalObservation, build_local_observation
from cops_and_robbers_rl.shared.config import GameConfig


class IllegalActionError(ValueError):
    """Raised in strict mode when an agent requests an illegal action."""


def resolve_move(
    config: GameConfig,
    grid: Grid,
    role: Role,
    action: Action,
    origin: Position,
    barriers: frozenset[Position],
) -> tuple[Position, bool, str | None]:
    """Validate a movement intent and normalize illegal movement to stay."""
    if action.kind is ActionType.PLACE_BARRIER:
        return _illegal(config, origin, f"{role.value} cannot use this barrier action")
    if action.kind is ActionType.STAY and not config.allow_stay:
        return _illegal(config, origin, "stay action is disabled")
    destination = action.destination(origin)
    if not grid.contains(destination):
        return _illegal(config, origin, "destination is outside the grid")
    if destination in barriers:
        return _illegal(config, origin, "destination is blocked by a barrier")
    return destination, True, None


def validate_barrier(
    config: GameConfig,
    grid: Grid,
    state: GameState,
    action: Action,
    thief_destination: Position,
) -> tuple[bool, str | None]:
    """Validate a cop barrier intent against the same pre-step state."""
    target = action.target
    reason = None
    if len(state.barriers) >= config.max_barriers:
        reason = "barrier limit reached"
    elif target is None or not grid.contains(target):
        reason = "barrier target is outside the grid"
    elif not state.cop_position.is_adjacent(target):
        reason = "barrier target must be orthogonally adjacent"
    elif target in state.barriers:
        reason = "barrier target is already blocked"
    elif target in {state.cop_position, state.thief_position, thief_destination}:
        reason = "barrier target is occupied or targeted by the thief"
    if reason is None:
        return True, None
    if config.illegal_action_policy == "error":
        raise IllegalActionError(reason)
    return False, reason


def spawn_positions(
    config: GameConfig,
    grid: Grid,
    seed: int | None,
    cop_start: Position | None,
    thief_start: Position | None,
) -> tuple[Position, Position]:
    """Return validated fixed positions or a reproducible distinct sample."""
    if (cop_start is None) != (thief_start is None):
        raise ValueError("both fixed start positions must be provided together")
    if cop_start is not None and thief_start is not None:
        if not grid.contains(cop_start) or not grid.contains(thief_start):
            raise ValueError("start positions must be inside the grid")
        if cop_start == thief_start:
            raise ValueError("cop and thief must start in different cells")
        return cop_start, thief_start
    rng = Random(config.random_seed if seed is None else seed)
    sampled = rng.sample(grid.positions(), 2)
    return sampled[0], sampled[1]


def build_observations(
    state: GameState, grid: Grid, config: GameConfig
) -> tuple[LocalObservation, LocalObservation]:
    """Build both decentralized observations from one state snapshot."""
    arguments = (
        grid,
        config.observation_radius,
        config.max_moves,
        config.max_barriers,
    )
    return (
        build_local_observation(state, Role.COP, *arguments),
        build_local_observation(state, Role.THIEF, *arguments),
    )


def _illegal(config: GameConfig, origin: Position, reason: str) -> tuple[Position, bool, str]:
    if config.illegal_action_policy == "error":
        raise IllegalActionError(reason)
    return origin, False, reason
