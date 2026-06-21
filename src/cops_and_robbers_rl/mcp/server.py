"""Optional FastMCP server factory shared by separate role entry points."""

from pathlib import Path
from typing import Any

from cops_and_robbers_rl.agents import HeuristicCopAgent, HeuristicThiefAgent
from cops_and_robbers_rl.environment.game_state import Role
from cops_and_robbers_rl.mcp.config import load_mcp_config
from cops_and_robbers_rl.mcp.gatekeeper import AgentGatekeeper, MCPUnavailableError


def create_server(role: Role, config_path: str | Path | None = None):
    """Create a role-isolated FastMCP server without importing MCP at startup."""
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise MCPUnavailableError("install with 'uv sync --extra mcp'") from exc
    config = load_mcp_config(config_path)
    endpoint = config.endpoint(role)
    agent = HeuristicCopAgent() if role is Role.COP else HeuristicThiefAgent()
    gatekeeper = AgentGatekeeper(config, agent)
    server = FastMCP(
        f"cops-and-robbers-{role.value}",
        host=endpoint.host,
        port=endpoint.port,
        json_response=True,
    )

    @server.tool()
    def choose_action(request: dict[str, Any], token: str | None = None) -> dict[str, Any]:
        """Choose one action from a radius-limited JSON observation."""
        return gatekeeper.choose_action(request, token)

    @server.tool()
    def health() -> dict[str, Any]:
        """Return non-secret local readiness metadata."""
        return {
            "ready": True,
            "role": role.value,
            "schema_version": config.schema_version,
            "transport": config.transport,
        }

    return server, config


def run_server(role: Role, config_path: str | Path | None = None) -> None:
    server, config = create_server(role, config_path)
    server.run(transport=config.transport)
