"""Local-observation pursuit heuristic for the cop."""

from cops_and_robbers_rl.agents.base_agent import BaseAgent
from cops_and_robbers_rl.agents.local_policy import (
    distance_after,
    legal_movement_actions,
    opponent_offset,
)
from cops_and_robbers_rl.environment.actions import Action, ActionType
from cops_and_robbers_rl.environment.game_state import Role
from cops_and_robbers_rl.environment.observations import LocalObservation


class HeuristicCopAgent(BaseAgent):
    """Pursue a visible thief; otherwise explore locally legal cells."""

    def __init__(self, *, seed: int = 0) -> None:
        super().__init__(Role.COP, seed=seed)

    def _act(self, observation: LocalObservation) -> Action:
        legal = legal_movement_actions(observation)
        opponent = opponent_offset(observation)
        if opponent is not None:
            best_distance = min(distance_after(action, opponent) for action in legal)
            best = [action for action in legal if distance_after(action, opponent) == best_distance]
            return self._rng.choice(best)
        moving = [action for action in legal if action.kind is not ActionType.STAY]
        return self._rng.choice(moving or list(legal))
