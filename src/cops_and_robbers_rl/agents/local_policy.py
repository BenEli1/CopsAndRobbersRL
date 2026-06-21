"""Pure helpers for reasoning over egocentric local observations."""

from cops_and_robbers_rl.environment.actions import Action, ActionType
from cops_and_robbers_rl.environment.observations import CellKind, LocalObservation

ACTION_OFFSETS = {
    ActionType.UP: (-1, 0),
    ActionType.DOWN: (1, 0),
    ActionType.LEFT: (0, -1),
    ActionType.RIGHT: (0, 1),
}
_TRAVERSABLE = {CellKind.EMPTY, CellKind.OPPONENT}


def legal_movement_actions(observation: LocalObservation) -> tuple[Action, ...]:
    """Infer legal cardinal movement and stay from adjacent visible cells."""
    visible = {(cell.row_offset, cell.column_offset): cell.kind for cell in observation.cells}
    actions = [
        Action(kind)
        for kind, offset in ACTION_OFFSETS.items()
        if visible.get(offset) in _TRAVERSABLE
    ]
    actions.append(Action(ActionType.STAY))
    return tuple(actions)


def opponent_offset(observation: LocalObservation) -> tuple[int, int] | None:
    """Return the visible opponent's relative coordinate, if present."""
    for cell in observation.cells:
        if cell.kind is CellKind.OPPONENT:
            return cell.row_offset, cell.column_offset
    return None


def distance_after(action: Action, opponent: tuple[int, int]) -> int:
    """Compute Manhattan distance to an opponent after one local move."""
    row_delta, column_delta = ACTION_OFFSETS.get(action.kind, (0, 0))
    return abs(opponent[0] - row_delta) + abs(opponent[1] - column_delta)
