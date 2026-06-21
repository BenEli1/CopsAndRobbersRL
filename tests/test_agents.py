"""Local-observation baseline-agent behavior tests."""

from cops_and_robbers_rl.agents import (
    HeuristicCopAgent,
    HeuristicThiefAgent,
    RandomCopAgent,
    RandomThiefAgent,
)
from cops_and_robbers_rl.agents.local_policy import (
    distance_after,
    legal_movement_actions,
    opponent_offset,
)
from cops_and_robbers_rl.environment.game_state import Role
from cops_and_robbers_rl.environment.grid import Position
from cops_and_robbers_rl.environment.rules import GameEngine
from cops_and_robbers_rl.shared.config import GameConfig


def test_baseline_agents_return_locally_legal_actions() -> None:
    engine = GameEngine(GameConfig(), cop_start=Position(2, 2), thief_start=Position(4, 4))
    cop_observation, thief_observation = engine.observations()
    agents_and_observations = (
        (RandomCopAgent(seed=1), cop_observation),
        (HeuristicCopAgent(seed=1), cop_observation),
        (RandomThiefAgent(seed=2), thief_observation),
        (HeuristicThiefAgent(seed=2), thief_observation),
    )

    for agent, observation in agents_and_observations:
        assert agent.act(observation) in legal_movement_actions(observation)


def test_heuristic_cop_moves_closer_to_visible_thief() -> None:
    engine = GameEngine(GameConfig(), cop_start=Position(2, 2), thief_start=Position(2, 3))
    observation, _ = engine.observations()
    opponent = opponent_offset(observation)
    assert opponent is not None

    selected = HeuristicCopAgent(seed=3).act(observation)

    assert distance_after(selected, opponent) < abs(opponent[0]) + abs(opponent[1])


def test_heuristic_thief_increases_distance_from_visible_cop() -> None:
    engine = GameEngine(GameConfig(), cop_start=Position(2, 2), thief_start=Position(2, 3))
    _, observation = engine.observations()
    opponent = opponent_offset(observation)
    assert opponent is not None

    selected = HeuristicThiefAgent(seed=4).act(observation)

    assert distance_after(selected, opponent) > abs(opponent[0]) + abs(opponent[1])


def test_agent_rejects_wrong_role_observation() -> None:
    engine = GameEngine(GameConfig(), seed=5)
    _, thief_observation = engine.observations()

    try:
        RandomCopAgent().act(thief_observation)
    except ValueError as exc:
        assert "cop agent received thief observation" in str(exc)
    else:
        raise AssertionError("cop accepted thief observation")

    assert thief_observation.role is Role.THIEF
