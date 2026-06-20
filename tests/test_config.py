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
