"""Stable project paths independent of the process working directory."""

from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PACKAGE_ROOT.parent
PROJECT_ROOT = SRC_ROOT.parent
CONFIG_ROOT = PROJECT_ROOT / "config"
DEFAULT_GAME_CONFIG = CONFIG_ROOT / "default_game.yaml"
DEFAULT_MCP_CONFIG = CONFIG_ROOT / "mcp.yaml"
RESULTS_ROOT = PROJECT_ROOT / "results"
