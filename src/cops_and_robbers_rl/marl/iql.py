"""Tabular Independent Q-Learning for decentralized execution."""

import json
from pathlib import Path

from cops_and_robbers_rl.agents.base_agent import BaseAgent
from cops_and_robbers_rl.agents.local_policy import legal_movement_actions
from cops_and_robbers_rl.environment.actions import Action, ActionType
from cops_and_robbers_rl.environment.game_state import Role
from cops_and_robbers_rl.environment.observations import LocalObservation


def encode_observation(observation: LocalObservation) -> str:
    """Encode only radius-limited execution data as a stable table key."""
    payload = {
        "role": observation.role.value,
        "radius": observation.radius,
        "cells": [cell.kind.value for cell in observation.cells],
        "moves_remaining": observation.moves_remaining,
        "barriers_remaining": observation.barriers_remaining,
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


class IQLAgent(BaseAgent):
    """Epsilon-greedy tabular learner operating on local observations only."""

    def __init__(
        self,
        role: Role,
        *,
        alpha: float = 0.2,
        gamma: float = 0.95,
        epsilon: float = 0.1,
        seed: int = 0,
    ) -> None:
        super().__init__(role, seed=seed)
        if not 0 < alpha <= 1 or not 0 <= gamma <= 1 or not 0 <= epsilon <= 1:
            raise ValueError("alpha, gamma, and epsilon must be valid probabilities")
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.q_table: dict[str, dict[str, float]] = {}

    def _act(self, observation: LocalObservation) -> Action:
        legal = legal_movement_actions(observation)
        if self._rng.random() < self.epsilon:
            return self._rng.choice(legal)
        values = self.q_table.get(encode_observation(observation), {})
        best_value = max((values.get(action.kind.value, 0.0) for action in legal), default=0.0)
        best = [action for action in legal if values.get(action.kind.value, 0.0) == best_value]
        return self._rng.choice(best)

    def update(
        self,
        observation: LocalObservation,
        action: Action,
        reward: float,
        next_observation: LocalObservation,
        done: bool,
    ) -> float:
        """Apply one Q-learning update and return absolute TD error."""
        key = encode_observation(observation)
        values = self.q_table.setdefault(key, {})
        old_value = values.get(action.kind.value, 0.0)
        next_values = self.q_table.get(encode_observation(next_observation), {})
        legal_next = legal_movement_actions(next_observation)
        bootstrap = (
            0.0
            if done
            else max(
                (next_values.get(candidate.kind.value, 0.0) for candidate in legal_next),
                default=0.0,
            )
        )
        td_error = reward + self.gamma * bootstrap - old_value
        values[action.kind.value] = old_value + self.alpha * td_error
        return abs(td_error)

    def save(self, path: str | Path) -> Path:
        """Save a portable JSON policy checkpoint."""
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        payload = {"role": self.role.value, "q_table": self.q_table}
        destination.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
        return destination

    @classmethod
    def load(cls, path: str | Path, *, seed: int = 0) -> "IQLAgent":
        """Load a greedy execution policy from a JSON checkpoint."""
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        agent = cls(Role(payload["role"]), epsilon=0.0, seed=seed)
        agent.q_table = {
            str(state): {str(action): float(value) for action, value in values.items()}
            for state, values in payload["q_table"].items()
        }
        return agent


MOVEMENT_ACTIONS = tuple(
    Action(kind) for kind in ActionType if kind is not ActionType.PLACE_BARRIER
)
