"""Typed actions supported by the deterministic environment."""

from dataclasses import dataclass
from enum import StrEnum

from cops_and_robbers_rl.environment.grid import Position


class ActionType(StrEnum):
    """Discrete movement and cop-only barrier actions."""

    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    STAY = "stay"
    PLACE_BARRIER = "place_barrier"


_DELTAS = {
    ActionType.UP: (-1, 0),
    ActionType.DOWN: (1, 0),
    ActionType.LEFT: (0, -1),
    ActionType.RIGHT: (0, 1),
    ActionType.STAY: (0, 0),
}


@dataclass(frozen=True, slots=True)
class Action:
    """An action intent, optionally carrying a barrier target."""

    kind: ActionType
    target: Position | None = None

    def __post_init__(self) -> None:
        if (self.kind is ActionType.PLACE_BARRIER) != (self.target is not None):
            raise ValueError("only place_barrier actions require a target")

    @classmethod
    def barrier(cls, target: Position) -> "Action":
        """Construct a cop barrier-placement action."""
        return cls(ActionType.PLACE_BARRIER, target)

    def destination(self, origin: Position) -> Position:
        """Return the intended movement destination."""
        if self.kind is ActionType.PLACE_BARRIER:
            return origin
        row_delta, column_delta = _DELTAS[self.kind]
        return origin.offset(row_delta, column_delta)
