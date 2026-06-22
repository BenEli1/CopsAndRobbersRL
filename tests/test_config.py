"""Configuration loading tests."""

from pathlib import Path

import pytest

from cops_and_robbers_rl.shared.config import ConfigError, load_game_config


def test_default_config_loads_assignment_values() -> None:
    config = load_game_config()

    assert config.grid_size == (5, 5)
    assert config.max_moves == 25
    assert config.num_games == 6
    assert config.max_barriers == 5
    assert config.scoring.as_tuple() == (20, 10, 5, 5)


def test_unknown_config_key_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "bad.yaml"
    path.write_text("grid_size: [5, 5]\nunknown: true\n", encoding="utf-8")

    with pytest.raises(ConfigError, match="unknown game config keys"):
        load_game_config(path)


def test_nondefault_yaml_values_are_not_replaced_by_code_defaults(tmp_path: Path) -> None:
    path = tmp_path / "custom.yaml"
    path.write_text(
        """schema_version: "1.00"
grid_size: [4, 6]
max_moves: 17
num_games: 6
max_barriers: 3
observation_radius: 2
random_seed: 7
allow_stay: false
illegal_action_policy: error
crossing_counts_as_capture: false
scoring:
  cop_win: 13
  thief_win: 11
  cop_loss: 2
  thief_loss: 3
""",
        encoding="utf-8",
    )

    config = load_game_config(path)

    assert config.grid_size == (4, 6)
    assert config.max_moves == 17
    assert config.max_barriers == 3
    assert config.scoring.as_tuple() == (13, 11, 2, 3)
