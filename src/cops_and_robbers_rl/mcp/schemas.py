"""JSON contracts that preserve the decentralized observation boundary."""

from typing import Any

from cops_and_robbers_rl.environment.actions import Action, ActionType
from cops_and_robbers_rl.environment.game_state import Role
from cops_and_robbers_rl.environment.observations import (
    CellKind,
    LocalObservation,
    ObservedCell,
)

SCHEMA_VERSION = "1.00"
_FORBIDDEN = {"global_state", "cop_position", "thief_position", "absolute_position"}


class MCPPayloadError(ValueError):
    """Raised when an MCP request or response violates its schema."""


def observation_to_json(observation: LocalObservation) -> dict[str, Any]:
    return {
        "role": observation.role.value,
        "radius": observation.radius,
        "cells": [
            {
                "row_offset": cell.row_offset,
                "column_offset": cell.column_offset,
                "kind": cell.kind.value,
            }
            for cell in observation.cells
        ],
        "moves_completed": observation.moves_completed,
        "moves_remaining": observation.moves_remaining,
        "barriers_remaining": observation.barriers_remaining,
    }


def observation_from_json(payload: dict[str, Any]) -> LocalObservation:
    if _FORBIDDEN.intersection(payload):
        raise MCPPayloadError("privileged or absolute state is forbidden")
    expected = {
        "role",
        "radius",
        "cells",
        "moves_completed",
        "moves_remaining",
        "barriers_remaining",
    }
    if set(payload) != expected or not isinstance(payload.get("cells"), list):
        raise MCPPayloadError("invalid local observation schema")
    try:
        cells = tuple(
            ObservedCell(
                int(cell["row_offset"]), int(cell["column_offset"]), CellKind(cell["kind"])
            )
            for cell in payload["cells"]
        )
        return LocalObservation(
            role=Role(payload["role"]),
            radius=int(payload["radius"]),
            cells=cells,
            moves_completed=int(payload["moves_completed"]),
            moves_remaining=int(payload["moves_remaining"]),
            barriers_remaining=int(payload["barriers_remaining"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise MCPPayloadError("invalid local observation value") from exc


def action_response(role: Role, request_id: str, action: Action) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "request_id": request_id,
        "role": role.value,
        "action": action.kind.value,
        "target": (
            {"row": action.target.row, "column": action.target.column} if action.target else None
        ),
    }


def validate_action_response(payload: dict[str, Any], role: Role, request_id: str) -> Action:
    expected = {"schema_version", "request_id", "role", "action", "target"}
    if set(payload) != expected:
        raise MCPPayloadError("invalid action response schema")
    if payload["schema_version"] != SCHEMA_VERSION or payload["request_id"] != request_id:
        raise MCPPayloadError("stale or incompatible action response")
    if payload["role"] != role.value or payload["target"] is not None:
        raise MCPPayloadError("wrong role or unsupported remote barrier target")
    try:
        return Action(ActionType(payload["action"]))
    except (TypeError, ValueError) as exc:
        raise MCPPayloadError("invalid action value") from exc
