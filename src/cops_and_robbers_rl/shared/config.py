"""Validated YAML configuration for the deterministic game."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from cops_and_robbers_rl.shared.paths import DEFAULT_GAME_CONFIG


class ConfigError(ValueError):
    """Raised when game configuration is missing or invalid."""


@dataclass(frozen=True, slots=True)
class ScoringConfig:
    """Authoritative scores assigned at sub-game termination."""

    cop_win: int = 20
    thief_win: int = 10
    cop_loss: int = 5
    thief_loss: int = 5

    def __post_init__(self) -> None:
        if any(value < 0 for value in self.as_tuple()):
            raise ConfigError("scoring values must be non-negative")

    def as_tuple(self) -> tuple[int, int, int, int]:
        """Return values in stable assignment order."""
        return self.cop_win, self.thief_win, self.cop_loss, self.thief_loss


@dataclass(frozen=True, slots=True)
class GameConfig:
    """Validated game settings used by the engine and SDK."""

    grid_size: tuple[int, int] = (5, 5)
    max_moves: int = 25
    num_games: int = 6
    max_barriers: int = 5
    observation_radius: int = 1
    random_seed: int = 42
    allow_stay: bool = True
    illegal_action_policy: str = "stay"
    crossing_counts_as_capture: bool = True
    scoring: ScoringConfig = ScoringConfig()
    schema_version: str = "1.00"

    def __post_init__(self) -> None:
        rows, columns = self.grid_size
        if rows <= 0 or columns <= 0 or rows * columns < 2:
            raise ConfigError("grid_size must contain at least two cells")
        if self.max_moves <= 0 or self.num_games <= 0:
            raise ConfigError("max_moves and num_games must be positive")
        if self.max_barriers < 0 or self.observation_radius < 0:
            raise ConfigError("max_barriers and observation_radius must be non-negative")
        if self.illegal_action_policy not in {"stay", "error"}:
            raise ConfigError("illegal_action_policy must be 'stay' or 'error'")


_ROOT_KEYS = {
    "schema_version",
    "grid_size",
    "max_moves",
    "num_games",
    "max_barriers",
    "observation_radius",
    "random_seed",
    "allow_stay",
    "illegal_action_policy",
    "crossing_counts_as_capture",
    "scoring",
}
_SCORING_KEYS = {"cop_win", "thief_win", "cop_loss", "thief_loss"}


def _reject_unknown(data: dict[str, Any], allowed: set[str], section: str) -> None:
    unknown = set(data) - allowed
    if unknown:
        raise ConfigError(f"unknown {section} keys: {', '.join(sorted(unknown))}")


def load_game_config(path: str | Path | None = None) -> GameConfig:
    """Load and strictly validate a game configuration YAML file."""
    config_path = Path(path) if path is not None else DEFAULT_GAME_CONFIG
    try:
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ConfigError(f"unable to load config {config_path}: {exc}") from exc
    if not isinstance(raw, dict):
        raise ConfigError("game config must be a YAML mapping")
    _reject_unknown(raw, _ROOT_KEYS, "game config")
    scoring_raw = raw.get("scoring", {})
    if not isinstance(scoring_raw, dict):
        raise ConfigError("scoring must be a mapping")
    _reject_unknown(scoring_raw, _SCORING_KEYS, "scoring")
    try:
        grid_size = tuple(raw.get("grid_size", (5, 5)))
        if len(grid_size) != 2:
            raise ConfigError("grid_size must contain exactly two integers")
        return GameConfig(
            schema_version=str(raw.get("schema_version", "1.00")),
            grid_size=(int(grid_size[0]), int(grid_size[1])),
            max_moves=int(raw.get("max_moves", 25)),
            num_games=int(raw.get("num_games", 6)),
            max_barriers=int(raw.get("max_barriers", 5)),
            observation_radius=int(raw.get("observation_radius", 1)),
            random_seed=int(raw.get("random_seed", 42)),
            allow_stay=bool(raw.get("allow_stay", True)),
            illegal_action_policy=str(raw.get("illegal_action_policy", "stay")),
            crossing_counts_as_capture=bool(raw.get("crossing_counts_as_capture", True)),
            scoring=ScoringConfig(**scoring_raw),
        )
    except (TypeError, ValueError) as exc:
        if isinstance(exc, ConfigError):
            raise
        raise ConfigError(f"invalid game config value: {exc}") from exc
