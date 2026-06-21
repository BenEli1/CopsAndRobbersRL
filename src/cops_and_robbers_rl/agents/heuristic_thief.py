"""Local-observation evasion heuristic for the thief."""

from cops_and_robbers_rl.agents.base_agent import BaseAgent
from cops_and_robbers_rl.agents.local_policy import (
    distance_after,
    legal_movement_actions,
    opponent_offset,
)
from cops_and_robbers_rl.environment.actions import Action, ActionType
from cops_and_robbers_rl.environment.game_state import Role
from cops_and_robbers_rl.environment.observations import LocalObservation


class HeuristicThiefAgent(BaseAgent):
    """Maximize distance from a visible cop; otherwise explore or wait."""

    def __init__(self, *, seed: int = 0) -> None:
        super().__init__(Role.THIEF, seed=seed)

    def _act(self, observation: LocalObservation) -> Action:
        legal = legal_movement_actions(observation)
        opponent = opponent_offset(observation)
        if opponent is not None:
            best_distance = max(distance_after(action, opponent) for action in legal)
            best = [action for action in legal if distance_after(action, opponent) == best_distance]
            return self._rng.choice(best)
        moving = [action for action in legal if action.kind is not ActionType.STAY]
        if moving and self._rng.random() < 0.75:
            return self._rng.choice(moving)
        return Action(ActionType.STAY)
