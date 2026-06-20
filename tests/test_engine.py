"""Deterministic game-rule tests."""

from dataclasses import replace

import pytest

from cops_and_robbers_rl.environment.actions import Action, ActionType
from cops_and_robbers_rl.environment.game_state import Role, TerminalReason
from cops_and_robbers_rl.environment.grid import Position
from cops_and_robbers_rl.environment.observations import CellKind
from cops_and_robbers_rl.environment.rules import GameEngine
from cops_and_robbers_rl.shared.config import GameConfig


def action(kind: ActionType) -> Action:
    return Action(kind)


def test_seeded_spawn_is_distinct_and_reproducible() -> None:
    first = GameEngine(GameConfig(), seed=7)
    second = GameEngine(GameConfig(), seed=7)

    assert first.state == second.state
    assert first.state.cop_position != first.state.thief_position

    with pytest.raises(ValueError, match="different cells"):
        GameEngine(GameConfig(), cop_start=Position(1, 1), thief_start=Position(1, 1))


def test_legal_and_illegal_movement() -> None:
    engine = GameEngine(GameConfig(), cop_start=Position(0, 0), thief_start=Position(4, 4))

    legal = engine.step(action(ActionType.DOWN), action(ActionType.STAY))
    assert legal.state.cop_position == Position(1, 0)
    assert legal.cop_action_legal

    illegal = engine.step(action(ActionType.LEFT), action(ActionType.STAY))
    assert illegal.state.cop_position == Position(1, 0)
    assert not illegal.cop_action_legal
    assert illegal.cop_illegal_reason == "destination is outside the grid"


def test_same_destination_is_capture() -> None:
    engine = GameEngine(GameConfig(), cop_start=Position(0, 0), thief_start=Position(0, 2))

    result = engine.step(action(ActionType.RIGHT), action(ActionType.LEFT))

    assert result.state.terminal
    assert result.state.winner is Role.COP
    assert result.state.terminal_reason is TerminalReason.CAPTURE
    assert result.state.cop_position == result.state.thief_position == Position(0, 1)
    assert result.scores is not None
    assert result.scores.to_dict() == {"cop": 20, "thief": 5}


def test_thief_wins_after_twenty_five_moves() -> None:
    engine = GameEngine(GameConfig(), cop_start=Position(0, 0), thief_start=Position(4, 4))

    result = None
    for _ in range(25):
        result = engine.step(action(ActionType.STAY), action(ActionType.STAY))

    assert result is not None
    assert result.state.terminal
    assert result.state.moves_completed == 25
    assert result.state.winner is Role.THIEF
    assert result.state.terminal_reason is TerminalReason.MOVE_LIMIT
    assert result.scores is not None
    assert result.scores.to_dict() == {"cop": 5, "thief": 10}


def test_barrier_limit_is_five() -> None:
    config = replace(GameConfig(), max_moves=50)
    engine = GameEngine(config, cop_start=Position(0, 0), thief_start=Position(4, 4))

    for row in range(5):
        placed = engine.step(Action.barrier(Position(row, 1)), action(ActionType.STAY))
        assert placed.cop_action_legal
        if row < 4:
            engine.step(action(ActionType.DOWN), action(ActionType.STAY))

    rejected = engine.step(Action.barrier(Position(3, 0)), action(ActionType.STAY))
    assert len(rejected.state.barriers) == 5
    assert not rejected.cop_action_legal
    assert rejected.cop_illegal_reason == "barrier limit reached"


def test_barrier_blocks_movement() -> None:
    engine = GameEngine(GameConfig(), cop_start=Position(0, 0), thief_start=Position(4, 4))
    engine.step(Action.barrier(Position(0, 1)), action(ActionType.STAY))

    blocked = engine.step(action(ActionType.RIGHT), action(ActionType.STAY))

    assert blocked.state.cop_position == Position(0, 0)
    assert not blocked.cop_action_legal
    assert blocked.cop_illegal_reason == "destination is blocked by a barrier"


def test_local_observation_hides_distant_opponent() -> None:
    engine = GameEngine(
        replace(GameConfig(), observation_radius=1),
        cop_start=Position(0, 0),
        thief_start=Position(4, 4),
    )

    cop_observation, _ = engine.observations()

    assert not cop_observation.opponent_visible
    assert all(cell.kind is not CellKind.OPPONENT for cell in cop_observation.cells)
    assert len(cop_observation.cells) == 9
    global_state = engine.global_state_for_training()
    assert global_state.thief_position == Position(4, 4)
