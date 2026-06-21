"""Strict local MCP endpoint configuration."""

from dataclasses import dataclass
from pathlib import Path

import yaml

from cops_and_robbers_rl.environment.game_state import Role
from cops_and_robbers_rl.shared.paths import DEFAULT_MCP_CONFIG


class MCPConfigError(ValueError):
    """Raised when MCP configuration is unsafe or malformed."""


@dataclass(frozen=True, slots=True)
class EndpointConfig:
    host: str
    port: int

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}/mcp"


@dataclass(frozen=True, slots=True)
class MCPConfig:
    schema_version: str
    transport: str
    cop: EndpointConfig
    thief: EndpointConfig
    auth_enabled: bool
    token_env: str
    action_timeout: float
    max_attempts: int

    def endpoint(self, role: Role) -> EndpointConfig:
        return self.cop if role is Role.COP else self.thief


def load_mcp_config(path: str | Path | None = None) -> MCPConfig:
    """Load local endpoints without ever loading a secret value."""
    source = Path(path) if path else DEFAULT_MCP_CONFIG
    raw = yaml.safe_load(source.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise MCPConfigError("MCP config must be a mapping")
    _keys(raw, {"schema_version", "transport", "cop", "thief", "auth", "timeouts", "retry"})
    cop, thief = _endpoint(raw.get("cop")), _endpoint(raw.get("thief"))
    auth, timeouts, retry = raw.get("auth"), raw.get("timeouts"), raw.get("retry")
    if not all(isinstance(item, dict) for item in (auth, timeouts, retry)):
        raise MCPConfigError("auth, timeouts, and retry must be mappings")
    _keys(auth, {"enabled", "token_env"})
    _keys(timeouts, {"action_seconds"})
    _keys(retry, {"max_attempts"})
    config = MCPConfig(
        schema_version=str(raw.get("schema_version", "1.00")),
        transport=str(raw.get("transport", "streamable-http")),
        cop=cop,
        thief=thief,
        auth_enabled=bool(auth.get("enabled", False)),
        token_env=str(auth.get("token_env", "MARL_MCP_TOKEN")),
        action_timeout=float(timeouts.get("action_seconds", 5.0)),
        max_attempts=int(retry.get("max_attempts", 2)),
    )
    if cop.port == thief.port or config.action_timeout <= 0 or config.max_attempts <= 0:
        raise MCPConfigError("ports must differ and timeout/retry values must be positive")
    if config.transport != "streamable-http":
        raise MCPConfigError("only streamable-http is supported locally")
    return config


def _endpoint(raw: object) -> EndpointConfig:
    if not isinstance(raw, dict):
        raise MCPConfigError("endpoint must be a mapping")
    _keys(raw, {"host", "port"})
    endpoint = EndpointConfig(str(raw.get("host", "127.0.0.1")), int(raw.get("port", 0)))
    if endpoint.host not in {"127.0.0.1", "localhost"} or not 1 <= endpoint.port <= 65535:
        raise MCPConfigError("local mode requires localhost and a valid port")
    return endpoint


def _keys(raw: dict, allowed: set[str]) -> None:
    unknown = set(raw) - allowed
    if unknown:
        raise MCPConfigError(f"unknown MCP config keys: {', '.join(sorted(unknown))}")
