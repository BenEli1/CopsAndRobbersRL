"""Radius-limited observations for decentralized execution."""

from dataclasses import dataclass
from enum import StrEnum

from cops_and_robbers_rl.environment.game_state import GameState, Role
from cops_and_robbers_rl.environment.grid import Grid, Position


class CellKind(StrEnum):
    """Semantic content visible in a local observation cell."""

    EMPTY = "empty"
    SELF = "self"
    OPPONENT = "opponent"
    BARRIER = "barrier"
    WALL = "wall"


@dataclass(frozen=True, slots=True)
class ObservedCell:
    """Cell content at an egocentric relative coordinate."""

    row_offset: int
    column_offset: int
    kind: CellKind


@dataclass(frozen=True, slots=True)
class LocalObservation:
    """Information permitted to one agent during execution."""

    role: Role
    radius: int
    cells: tuple[ObservedCell, ...]
    moves_completed: int
    moves_remaining: int
    barriers_remaining: int

    @property
    def opponent_visible(self) -> bool:
        """Return whether the opponent is inside the local view."""
        return any(cell.kind is CellKind.OPPONENT for cell in self.cells)


def build_local_observation(
    state: GameState,
    role: Role,
    grid: Grid,
    radius: int,
    max_moves: int,
    max_barriers: int,
) -> LocalObservation:
    """Build an egocentric observation without absolute hidden coordinates."""
    origin = state.cop_position if role is Role.COP else state.thief_position
    opponent = state.thief_position if role is Role.COP else state.cop_position
    cells: list[ObservedCell] = []
    for row_offset in range(-radius, radius + 1):
        for column_offset in range(-radius, radius + 1):
            position = origin.offset(row_offset, column_offset)
            kind = _cell_kind(position, origin, opponent, state.barriers, grid)
            cells.append(ObservedCell(row_offset, column_offset, kind))
    barriers_remaining = max_barriers - len(state.barriers) if role is Role.COP else 0
    return LocalObservation(
        role=role,
        radius=radius,
        cells=tuple(cells),
        moves_completed=state.moves_completed,
        moves_remaining=max_moves - state.moves_completed,
        barriers_remaining=barriers_remaining,
    )


def _cell_kind(
    position: Position,
    origin: Position,
    opponent: Position,
    barriers: frozenset[Position],
    grid: Grid,
) -> CellKind:
    if not grid.contains(position):
        return CellKind.WALL
    if position == origin:
        return CellKind.SELF
    if position == opponent:
        return CellKind.OPPONENT
    if position in barriers:
        return CellKind.BARRIER
    return CellKind.EMPTY
