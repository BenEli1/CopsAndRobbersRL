"""Grid boundary tests."""

import pytest

from cops_and_robbers_rl.environment.grid import Grid, Position


def test_grid_bounds_are_zero_based() -> None:
    grid = Grid(5, 5)

    assert grid.contains(Position(0, 0))
    assert grid.contains(Position(4, 4))
    assert not grid.contains(Position(-1, 0))
    assert not grid.contains(Position(5, 4))
    assert len(grid.positions()) == 25


def test_invalid_grid_dimensions_fail() -> None:
    with pytest.raises(ValueError, match="positive"):
        Grid(0, 5)
