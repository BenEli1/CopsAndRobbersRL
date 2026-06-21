"""Independent learners with an explicit centralized-training data boundary."""

from dataclasses import dataclass, replace
from pathlib import Path

from cops_and_robbers_rl.agents import (
    HeuristicCopAgent,
    HeuristicThiefAgent,
    RandomCopAgent,
    RandomThiefAgent,
)
from cops_and_robbers_rl.environment.game_state import Role
from cops_and_robbers_rl.environment.rules import GameEngine
from cops_and_robbers_rl.marl.iql import IQLAgent
from cops_and_robbers_rl.marl.metrics import (
    EpisodeMetric,
    save_comparison_plot,
    save_line_plot,
    save_metrics,
)
from cops_and_robbers_rl.marl.replay_buffer import (
    CentralizedTrainingTrace,
    CentralizedTransition,
    LocalTransition,
    ReplayBuffer,
)
from cops_and_robbers_rl.runner.match_runner import MatchRunner
from cops_and_robbers_rl.shared.config import GameConfig


@dataclass(frozen=True, slots=True)
class TrainingConfig:
    episodes: int = 200
    batch_size: int = 16
    replay_capacity: int = 5_000
    alpha: float = 0.2
    gamma: float = 0.95
    epsilon_start: float = 0.8
    epsilon_end: float = 0.05
    seed: int = 42

    def __post_init__(self) -> None:
        if self.episodes <= 0 or self.batch_size <= 0 or self.replay_capacity <= 0:
            raise ValueError("training sizes must be positive")


@dataclass(slots=True)
class TrainingResult:
    cop_agent: IQLAgent
    thief_agent: IQLAgent
    metrics: list[EpisodeMetric]
    centralized_transitions: int


class IQLTrainer:
    """Train two independent local policies and retain CTDE-ready joint traces."""

    def __init__(self, game_config: GameConfig, training_config: TrainingConfig) -> None:
        self.game_config = game_config
        self.training_config = training_config

    def train(
        self,
        cop_agent: IQLAgent | None = None,
        thief_agent: IQLAgent | None = None,
    ) -> TrainingResult:
        cfg = self.training_config
        cop = cop_agent or IQLAgent(
            Role.COP, alpha=cfg.alpha, gamma=cfg.gamma, epsilon=cfg.epsilon_start, seed=cfg.seed
        )
        thief = thief_agent or IQLAgent(
            Role.THIEF,
            alpha=cfg.alpha,
            gamma=cfg.gamma,
            epsilon=cfg.epsilon_start,
            seed=cfg.seed + 1,
        )
        cop_replay = ReplayBuffer(cfg.replay_capacity, seed=cfg.seed)
        thief_replay = ReplayBuffer(cfg.replay_capacity, seed=cfg.seed + 1)
        central_trace = CentralizedTrainingTrace(cfg.replay_capacity)
        metrics: list[EpisodeMetric] = []
        for episode in range(cfg.episodes):
            fraction = episode / max(cfg.episodes - 1, 1)
            epsilon = cfg.epsilon_start + fraction * (cfg.epsilon_end - cfg.epsilon_start)
            cop.epsilon = thief.epsilon = epsilon
            metrics.append(
                self._run_episode(episode, cop, thief, cop_replay, thief_replay, central_trace)
            )
        return TrainingResult(cop, thief, metrics, len(central_trace))

    def _run_episode(
        self,
        episode: int,
        cop: IQLAgent,
        thief: IQLAgent,
        cop_replay: ReplayBuffer,
        thief_replay: ReplayBuffer,
        central_trace: CentralizedTrainingTrace,
    ) -> EpisodeMetric:
        seed = self.training_config.seed + episode
        engine = GameEngine(self.game_config, seed=seed)
        cop.reset(seed)
        thief.reset(seed)
        cop_losses: list[float] = []
        thief_losses: list[float] = []
        cop_return = thief_return = 0.0
        while not engine.state.terminal:
            cop_obs, thief_obs = engine.observations()
            global_state = engine.global_state_for_training()
            cop_action, thief_action = cop.act(cop_obs), thief.act(thief_obs)
            result = engine.step(cop_action, thief_action)
            done = result.state.terminal
            cop_reward, thief_reward = self._rewards(result.state.winner, done)
            cop_return += cop_reward
            thief_return += thief_reward
            cop_replay.append(
                LocalTransition(cop_obs, cop_action, cop_reward, result.cop_observation, done)
            )
            thief_replay.append(
                LocalTransition(
                    thief_obs, thief_action, thief_reward, result.thief_observation, done
                )
            )
            central_trace.append(
                CentralizedTransition(
                    global_state,
                    cop_action,
                    thief_action,
                    cop_reward,
                    thief_reward,
                    engine.global_state_for_training(),
                    done,
                )
            )
            cop_losses.extend(self._learn_batch(cop, cop_replay))
            thief_losses.extend(self._learn_batch(thief, thief_replay))
        winner = engine.state.winner
        return EpisodeMetric(
            episode=episode + 1,
            cop_return=cop_return,
            thief_return=thief_return,
            cop_loss=_mean(cop_losses),
            thief_loss=_mean(thief_losses),
            moves=engine.state.moves_completed,
            winner=winner.value if winner else "unknown",
        )

    def _learn_batch(self, agent: IQLAgent, replay: ReplayBuffer) -> list[float]:
        return [
            agent.update(
                item.observation, item.action, item.reward, item.next_observation, item.done
            )
            for item in replay.sample(self.training_config.batch_size)
        ]

    @staticmethod
    def _rewards(winner: Role | None, done: bool) -> tuple[float, float]:
        if not done:
            return -0.01, 0.01
        return (1.0, -1.0) if winner is Role.COP else (-1.0, 1.0)


def train_staged(
    base_config: GameConfig, training_config: TrainingConfig
) -> tuple[TrainingResult, dict[str, TrainingResult]]:
    """Curriculum train on 2x2 through the configured final grid."""
    stages: dict[str, TrainingResult] = {}
    cop: IQLAgent | None = None
    thief: IQLAgent | None = None
    for size in (2, 3, 4, 5):
        config = replace(base_config, grid_size=(size, size))
        result = IQLTrainer(config, training_config).train(cop, thief)
        cop, thief = result.cop_agent, result.thief_agent
        stages[f"{size}x{size}"] = result
    return stages["5x5"], stages


def save_training_outputs(result: TrainingResult, output_root: str | Path) -> dict[str, Path]:
    """Save checkpoints, raw metrics, and required learning/loss plots."""
    root = Path(output_root)
    plots = root / "plots"
    outputs = {
        "metrics": save_metrics(result.metrics, root / "metrics" / "training.json"),
        "cop_model": result.cop_agent.save(root / "models" / "iql_cop.json"),
        "thief_model": result.thief_agent.save(root / "models" / "iql_thief.json"),
        "cop_curve": save_line_plot(
            [item.cop_return for item in result.metrics],
            plots / "learning_curve_cop.svg",
            title="IQL cop learning curve",
            y_label="Episode return",
        ),
        "thief_curve": save_line_plot(
            [item.thief_return for item in result.metrics],
            plots / "learning_curve_thief.svg",
            title="IQL thief learning curve",
            y_label="Episode return",
        ),
        "loss_curve": save_line_plot(
            [(item.cop_loss + item.thief_loss) / 2 for item in result.metrics],
            plots / "loss_curve.svg",
            title="Mean IQL TD error",
            y_label="Absolute TD error",
        ),
    }
    return outputs


def save_baseline_comparison(
    game_config: GameConfig, result: TrainingResult, output_root: str | Path
) -> dict[str, float]:
    """Compare each policy against the same fixed heuristic opponent."""
    result.cop_agent.epsilon = result.thief_agent.epsilon = 0.0
    cop_policies = {
        "random cop": RandomCopAgent(seed=1),
        "heuristic cop": HeuristicCopAgent(seed=1),
        "learned cop": result.cop_agent,
    }
    thief_policies = {
        "random thief": RandomThiefAgent(seed=2),
        "heuristic thief": HeuristicThiefAgent(seed=2),
        "learned thief": result.thief_agent,
    }
    wins: dict[str, float] = {}
    for name, cop in cop_policies.items():
        match = MatchRunner(game_config, cop, HeuristicThiefAgent(seed=2)).run()
        wins[name] = float(sum(game.winner is Role.COP for game in match.sub_games))
    for name, thief in thief_policies.items():
        match = MatchRunner(game_config, HeuristicCopAgent(seed=1), thief).run()
        wins[name] = float(sum(game.winner is Role.THIEF for game in match.sub_games))
    save_comparison_plot(wins, Path(output_root) / "plots" / "baseline_comparison.svg")
    return wins


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0
