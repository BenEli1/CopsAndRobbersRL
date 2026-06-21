"""Local replay and explicit centralized-training trace models."""

from collections import deque
from dataclasses import dataclass
from random import Random

from cops_and_robbers_rl.environment.actions import Action
from cops_and_robbers_rl.environment.game_state import GlobalTrainingState
from cops_and_robbers_rl.environment.observations import LocalObservation


@dataclass(frozen=True, slots=True)
class LocalTransition:
    """One decentralized learner transition."""

    observation: LocalObservation
    action: Action
    reward: float
    next_observation: LocalObservation
    done: bool


@dataclass(frozen=True, slots=True)
class CentralizedTransition:
    """Privileged joint data retained only by centralized training code."""

    global_state: GlobalTrainingState
    cop_action: Action
    thief_action: Action
    cop_reward: float
    thief_reward: float
    next_global_state: GlobalTrainingState
    done: bool


class ReplayBuffer:
    """Bounded reproducible replay storage."""

    def __init__(self, capacity: int = 10_000, *, seed: int = 0) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self._items: deque[LocalTransition] = deque(maxlen=capacity)
        self._rng = Random(seed)

    def append(self, transition: LocalTransition) -> None:
        self._items.append(transition)

    def sample(self, batch_size: int) -> tuple[LocalTransition, ...]:
        size = min(batch_size, len(self._items))
        return tuple(self._rng.sample(list(self._items), size))

    def __len__(self) -> int:
        return len(self._items)


class CentralizedTrainingTrace:
    """CTDE boundary: the only training store accepting global joint data."""

    def __init__(self, capacity: int = 10_000) -> None:
        self._items: deque[CentralizedTransition] = deque(maxlen=capacity)

    def append(self, transition: CentralizedTransition) -> None:
        self._items.append(transition)

    def __len__(self) -> int:
        return len(self._items)
