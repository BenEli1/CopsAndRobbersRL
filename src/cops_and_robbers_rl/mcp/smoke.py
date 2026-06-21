"""Dependency-safe local MCP contract smoke test."""

import os
from importlib.util import find_spec
from pathlib import Path
from typing import Any

from cops_and_robbers_rl.agents import HeuristicCopAgent, HeuristicThiefAgent
from cops_and_robbers_rl.environment.game_state import Role
from cops_and_robbers_rl.environment.rules import GameEngine
from cops_and_robbers_rl.mcp.config import load_mcp_config
from cops_and_robbers_rl.mcp.gatekeeper import AgentGatekeeper
from cops_and_robbers_rl.mcp.schemas import SCHEMA_VERSION, observation_to_json
from cops_and_robbers_rl.shared.config import load_game_config


def run_local_smoke(
    game_config_path: str | Path | None = None,
    mcp_config_path: str | Path | None = None,
) -> dict[str, Any]:
    """Exercise both role tools in-process, even when MCP is not installed."""
    game_config = load_game_config(game_config_path)
    mcp_config = load_mcp_config(mcp_config_path)
    engine = GameEngine(game_config, seed=game_config.random_seed)
    observations = dict(zip((Role.COP, Role.THIEF), engine.observations(), strict=True))
    agents = {Role.COP: HeuristicCopAgent(), Role.THIEF: HeuristicThiefAgent()}
    token = os.getenv(mcp_config.token_env) if mcp_config.auth_enabled else None
    actions = {}
    for role in (Role.COP, Role.THIEF):
        request = {
            "schema_version": SCHEMA_VERSION,
            "request_id": f"smoke-{role.value}",
            "role": role.value,
            "observation": observation_to_json(observations[role]),
        }
        response = AgentGatekeeper(mcp_config, agents[role]).choose_action(request, token)
        actions[role.value] = response["action"]
    return {
        "success": True,
        "mode": "in_process_contract_fallback",
        "mcp_sdk_installed": find_spec("mcp") is not None,
        "ports": {"cop": mcp_config.cop.port, "thief": mcp_config.thief.port},
        "actions": actions,
    }
