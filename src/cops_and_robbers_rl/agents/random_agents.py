"""Seeded random movement baselines."""

from cops_and_robbers_rl.agents.base_agent import BaseAgent
from cops_and_robbers_rl.agents.local_policy import legal_movement_actions
from cops_and_robbers_rl.environment.actions import Action
from cops_and_robbers_rl.environment.game_state import Role
from cops_and_robbers_rl.environment.observations import LocalObservation


class _RandomMovementAgent(BaseAgent):
    def _act(self, observation: LocalObservation) -> Action:
        return self._rng.choice(legal_movement_actions(observation))


class RandomCopAgent(_RandomMovementAgent):
    """Cop baseline selecting uniformly from locally legal movement actions."""

    def __init__(self, *, seed: int = 0) -> None:
        super().__init__(Role.COP, seed=seed)


class RandomThiefAgent(_RandomMovementAgent):
    """Thief baseline selecting uniformly from locally legal movement actions."""

    def __init__(self, *, seed: int = 0) -> None:
        super().__init__(Role.THIEF, seed=seed)
