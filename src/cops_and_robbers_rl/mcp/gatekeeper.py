"""Authenticated tool boundary, transport wrapper, and safe fallback policy."""

import asyncio
import hmac
import os
from typing import Any, Protocol

from cops_and_robbers_rl.agents.base_agent import BaseAgent
from cops_and_robbers_rl.environment.actions import Action
from cops_and_robbers_rl.environment.game_state import Role
from cops_and_robbers_rl.environment.observations import LocalObservation
from cops_and_robbers_rl.mcp.config import EndpointConfig, MCPConfig
from cops_and_robbers_rl.mcp.schemas import (
    SCHEMA_VERSION,
    MCPPayloadError,
    action_response,
    observation_from_json,
    observation_to_json,
    validate_action_response,
)


class MCPAuthenticationError(PermissionError):
    """Raised when local MCP authentication fails closed."""


class MCPUnavailableError(RuntimeError):
    """Raised when the optional transport or service is unavailable."""


class AgentTransport(Protocol):
    def call(
        self,
        endpoint: EndpointConfig,
        request: dict[str, Any],
        token: str | None,
        timeout: float,
    ) -> dict[str, Any]: ...


class AgentGatekeeper:
    """Validate auth and JSON before invoking one role-specific agent."""

    def __init__(self, config: MCPConfig, agent: BaseAgent) -> None:
        self.config = config
        self.agent = agent

    def choose_action(self, request: dict[str, Any], token: str | None) -> dict[str, Any]:
        self._authenticate(token)
        expected = {"schema_version", "request_id", "role", "observation"}
        if set(request) != expected or request.get("schema_version") != SCHEMA_VERSION:
            raise MCPPayloadError("invalid action request schema")
        if request.get("role") != self.agent.role.value:
            raise MCPPayloadError("request sent to wrong role server")
        observation_raw = request.get("observation")
        if not isinstance(observation_raw, dict):
            raise MCPPayloadError("observation must be a JSON object")
        observation = observation_from_json(observation_raw)
        if observation.role is not self.agent.role:
            raise MCPPayloadError("observation role does not match server")
        request_id = str(request["request_id"])
        return action_response(self.agent.role, request_id, self.agent.act(observation))

    def _authenticate(self, supplied: str | None) -> None:
        if not self.config.auth_enabled:
            return
        expected = os.getenv(self.config.token_env)
        if not expected:
            raise MCPAuthenticationError("configured token environment variable is missing")
        if not supplied or not hmac.compare_digest(supplied, expected):
            raise MCPAuthenticationError("invalid MCP token")


class MCPStreamableHTTPTransport:
    """Optional official MCP SDK client transport loaded only when called."""

    def call(
        self,
        endpoint: EndpointConfig,
        request: dict[str, Any],
        token: str | None,
        timeout: float,
    ) -> dict[str, Any]:
        try:
            from mcp import ClientSession
            from mcp.client.streamable_http import streamable_http_client
        except ImportError as exc:
            raise MCPUnavailableError("install the optional 'mcp' extra") from exc

        async def invoke() -> dict[str, Any]:
            async with (
                streamable_http_client(endpoint.url) as (read, write, _),
                ClientSession(read, write) as session,
            ):
                await session.initialize()
                result = await session.call_tool(
                    "choose_action", {"request": request, "token": token}
                )
                if result.isError or not isinstance(result.structuredContent, dict):
                    raise MCPUnavailableError("MCP server returned no structured action")
                return result.structuredContent

        try:
            return asyncio.run(asyncio.wait_for(invoke(), timeout=timeout))
        except TimeoutError:
            raise
        except MCPUnavailableError:
            raise
        except Exception as exc:
            raise MCPUnavailableError("MCP server unavailable") from exc


class RemotePolicy(BaseAgent):
    """MatchRunner-compatible client with bounded retry and local fallback."""

    def __init__(
        self,
        role: Role,
        config: MCPConfig,
        *,
        transport: AgentTransport | None = None,
        fallback_agent: BaseAgent | None = None,
        seed: int = 0,
    ) -> None:
        super().__init__(role, seed=seed)
        if fallback_agent is not None and fallback_agent.role is not role:
            raise ValueError("fallback role must match remote policy")
        self.config = config
        self.transport = transport or MCPStreamableHTTPTransport()
        self.fallback_agent = fallback_agent
        self._request_number = 0

    def reset(self, sub_game_seed: int) -> None:
        super().reset(sub_game_seed)
        self._request_number = 0
        if self.fallback_agent:
            self.fallback_agent.reset(sub_game_seed)

    def _act(self, observation: LocalObservation) -> Action:
        self._request_number += 1
        request_id = f"{self.role.value}-{self._request_number}"
        request = {
            "schema_version": SCHEMA_VERSION,
            "request_id": request_id,
            "role": self.role.value,
            "observation": observation_to_json(observation),
        }
        token = self._token()
        last_error: Exception | None = None
        for _ in range(self.config.max_attempts):
            try:
                response = self.transport.call(
                    self.config.endpoint(self.role),
                    request,
                    token,
                    self.config.action_timeout,
                )
                return validate_action_response(response, self.role, request_id)
            except (TimeoutError, OSError, MCPUnavailableError) as exc:
                last_error = exc
        if self.fallback_agent:
            return self.fallback_agent.act(observation)
        raise MCPUnavailableError("remote action failed after bounded attempts") from last_error

    def _token(self) -> str | None:
        if not self.config.auth_enabled:
            return None
        token = os.getenv(self.config.token_env)
        if not token:
            raise MCPAuthenticationError("client token environment variable is missing")
        return token
