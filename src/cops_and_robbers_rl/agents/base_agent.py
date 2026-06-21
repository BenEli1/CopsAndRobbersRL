"""Common interface for decentralized execution agents."""

from abc import ABC, abstractmethod
from random import Random

from cops_and_robbers_rl.environment.actions import Action
from cops_and_robbers_rl.environment.game_state import Role
from cops_and_robbers_rl.environment.observations import LocalObservation


class BaseAgent(ABC):
    """Agent contract restricted to radius-limited local observations."""

    def __init__(self, role: Role, *, seed: int = 0) -> None:
        self.role = role
        self._base_seed = seed
        self._rng = Random(seed)

    def reset(self, sub_game_seed: int) -> None:
        """Reset per-sub-game stochastic state reproducibly."""
        self._rng = Random(self._base_seed ^ sub_game_seed)

    def act(self, observation: LocalObservation) -> Action:
        """Validate role isolation and choose an action from local data."""
        if not isinstance(observation, LocalObservation):
            raise TypeError("agents accept LocalObservation only")
        if observation.role is not self.role:
            message = f"{self.role.value} agent received {observation.role.value} observation"
            raise ValueError(message)
        return self._act(observation)

    @abstractmethod
    def _act(self, observation: LocalObservation) -> Action:
        """Choose an action using only the supplied local observation."""
