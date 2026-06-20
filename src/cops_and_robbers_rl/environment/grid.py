"""Grid coordinates and boundary operations."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, order=True)
class Position:
    """Zero-based row and column coordinate."""

    row: int
    column: int

    def offset(self, row_delta: int, column_delta: int) -> "Position":
        """Return a position translated by the supplied delta."""
        return Position(self.row + row_delta, self.column + column_delta)

    def is_adjacent(self, other: "Position") -> bool:
        """Return whether another cell is orthogonally adjacent."""
        return abs(self.row - other.row) + abs(self.column - other.column) == 1


@dataclass(frozen=True, slots=True)
class Grid:
    """Rectangular grid boundary helper."""

    rows: int
    columns: int

    def __post_init__(self) -> None:
        if self.rows <= 0 or self.columns <= 0:
            raise ValueError("grid dimensions must be positive")

    def contains(self, position: Position) -> bool:
        """Return whether a coordinate is inside the grid."""
        return 0 <= position.row < self.rows and 0 <= position.column < self.columns

    def positions(self) -> tuple[Position, ...]:
        """Return all grid positions in stable row-major order."""
        return tuple(
            Position(row, column) for row in range(self.rows) for column in range(self.columns)
        )
