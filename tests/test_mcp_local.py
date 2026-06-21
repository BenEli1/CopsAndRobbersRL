"""Local MCP schemas, auth, fallback, and smoke tests."""

import json
from dataclasses import replace

import pytest

from cops_and_robbers_rl.agents import HeuristicCopAgent
from cops_and_robbers_rl.environment.actions import ActionType
from cops_and_robbers_rl.environment.game_state import Role
from cops_and_robbers_rl.environment.rules import GameEngine
from cops_and_robbers_rl.main import main
from cops_and_robbers_rl.mcp import cop_server, thief_server
from cops_and_robbers_rl.mcp.config import load_mcp_config
from cops_and_robbers_rl.mcp.gatekeeper import (
    AgentGatekeeper,
    MCPAuthenticationError,
    MCPUnavailableError,
    RemotePolicy,
)
from cops_and_robbers_rl.mcp.schemas import (
    SCHEMA_VERSION,
    MCPPayloadError,
    action_response,
    observation_from_json,
    observation_to_json,
    validate_action_response,
)
from cops_and_robbers_rl.shared.config import GameConfig


def _cop_observation():
    return GameEngine(GameConfig(), seed=4).observations()[0]


def _request() -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "request_id": "request-1",
        "role": "cop",
        "observation": observation_to_json(_cop_observation()),
    }


def test_observation_json_round_trip_contains_no_global_state() -> None:
    payload = observation_to_json(_cop_observation())

    assert observation_from_json(payload) == _cop_observation()
    assert "position" not in json.dumps(payload)


def test_action_response_schema_round_trip() -> None:
    response = action_response(Role.COP, "request-1", HeuristicCopAgent().act(_cop_observation()))
    action = validate_action_response(response, Role.COP, "request-1")

    assert action.kind in {
        ActionType.UP,
        ActionType.DOWN,
        ActionType.LEFT,
        ActionType.RIGHT,
        ActionType.STAY,
    }
    assert set(response) == {"schema_version", "request_id", "role", "action", "target"}


def test_invalid_token_is_rejected_when_auth_enabled(monkeypatch) -> None:
    config = replace(load_mcp_config(), auth_enabled=True)
    monkeypatch.setenv(config.token_env, "correct-local-test-token")
    gatekeeper = AgentGatekeeper(config, HeuristicCopAgent())

    with pytest.raises(MCPAuthenticationError, match="invalid MCP token"):
        gatekeeper.choose_action(_request(), "wrong-token")


def test_missing_configured_token_fails_closed(monkeypatch) -> None:
    config = replace(load_mcp_config(), auth_enabled=True)
    monkeypatch.delenv(config.token_env, raising=False)

    with pytest.raises(MCPAuthenticationError, match="missing"):
        AgentGatekeeper(config, HeuristicCopAgent()).choose_action(_request(), None)


def test_gatekeeper_returns_valid_action_and_rejects_privileged_state() -> None:
    config = load_mcp_config()
    gatekeeper = AgentGatekeeper(config, HeuristicCopAgent())

    response = gatekeeper.choose_action(_request(), None)
    privileged = _request()
    privileged["observation"]["global_state"] = {"cop_position": [0, 0]}

    assert validate_action_response(response, Role.COP, "request-1")
    with pytest.raises(MCPPayloadError, match="privileged"):
        gatekeeper.choose_action(privileged, None)


class _TimeoutTransport:
    def __init__(self) -> None:
        self.calls = 0

    def call(self, endpoint, request, token, timeout):
        self.calls += 1
        raise TimeoutError("synthetic timeout")


class _SuccessTransport:
    def __init__(self, config) -> None:
        self.gatekeeper = AgentGatekeeper(config, HeuristicCopAgent())

    def call(self, endpoint, request, token, timeout):
        assert endpoint.url.endswith(":8101/mcp")
        assert timeout > 0
        return self.gatekeeper.choose_action(request, token)


def test_timeout_uses_bounded_retry_then_local_fallback() -> None:
    config = load_mcp_config()
    transport = _TimeoutTransport()
    policy = RemotePolicy(
        Role.COP,
        config,
        transport=transport,
        fallback_agent=HeuristicCopAgent(seed=3),
    )

    action = policy.act(_cop_observation())

    assert transport.calls == config.max_attempts
    assert action.kind is not ActionType.PLACE_BARRIER


def test_remote_policy_success_and_failure_without_fallback() -> None:
    config = load_mcp_config()
    policy = RemotePolicy(Role.COP, config, transport=_SuccessTransport(config))

    policy.reset(8)
    assert policy.act(_cop_observation()).kind is not ActionType.PLACE_BARRIER
    with pytest.raises(MCPUnavailableError, match="bounded attempts"):
        RemotePolicy(Role.COP, config, transport=_TimeoutTransport()).act(_cop_observation())


@pytest.mark.parametrize(
    ("module", "role"),
    ((cop_server, Role.COP), (thief_server, Role.THIEF)),
)
def test_role_server_entrypoints_delegate_to_shared_factory(monkeypatch, module, role) -> None:
    called = []
    monkeypatch.setattr(
        module, "run_server", lambda actual_role, path: called.append((actual_role, path))
    )

    assert module.main(["--config", "config/mcp.yaml"]) == 0
    assert called == [(role, "config/mcp.yaml")]


def test_local_mcp_smoke_cli_documents_distinct_ports(capsys) -> None:
    assert main(["mcp-smoke"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["success"]
    assert payload["mode"] == "in_process_contract_fallback"
    assert payload["ports"]["cop"] != payload["ports"]["thief"]
    assert set(payload["actions"]) == {"cop", "thief"}
