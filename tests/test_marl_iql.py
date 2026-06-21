"""Tests for tabular IQL, encoding, persistence, and training outputs."""

import json
from dataclasses import replace
from pathlib import Path

import pytest

from cops_and_robbers_rl.environment.actions import Action, ActionType
from cops_and_robbers_rl.environment.game_state import Role
from cops_and_robbers_rl.environment.rules import GameEngine
from cops_and_robbers_rl.main import main
from cops_and_robbers_rl.marl.iql import IQLAgent, encode_observation
from cops_and_robbers_rl.marl.metrics import EpisodeMetric, save_line_plot, save_metrics
from cops_and_robbers_rl.marl.trainer import (
    IQLTrainer,
    TrainingConfig,
    save_baseline_comparison,
    save_training_outputs,
)
from cops_and_robbers_rl.runner.match_runner import MatchRunner
from cops_and_robbers_rl.shared.config import GameConfig


def _cop_observation():
    return GameEngine(replace(GameConfig(), max_moves=3), seed=7).observations()[0]


def test_q_update_matches_bellman_equation() -> None:
    observation = _cop_observation()
    agent = IQLAgent(Role.COP, alpha=0.5, gamma=0.9, epsilon=0.0)
    agent.q_table[encode_observation(observation)] = {ActionType.STAY.value: 2.0}

    error = agent.update(observation, Action(ActionType.UP), 1.0, observation, False)

    assert error == pytest.approx(2.8)
    assert agent.q_table[encode_observation(observation)][ActionType.UP.value] == pytest.approx(1.4)


def test_local_observation_encoding_is_stable_and_contains_no_coordinates() -> None:
    encoded = encode_observation(_cop_observation())
    payload = json.loads(encoded)

    assert encoded == encode_observation(_cop_observation())
    assert set(payload) == {
        "role",
        "radius",
        "cells",
        "moves_remaining",
        "barriers_remaining",
    }
    assert "position" not in encoded


def test_training_smoke_and_centralized_trace_boundary() -> None:
    game = replace(GameConfig(), max_moves=3)
    result = IQLTrainer(game, TrainingConfig(episodes=4, batch_size=2)).train()

    assert len(result.metrics) == 4
    assert result.centralized_transitions >= 4
    assert result.cop_agent.q_table
    assert result.thief_agent.q_table


def test_metrics_and_required_plots_are_saved(tmp_path: Path) -> None:
    metric = EpisodeMetric(1, 1.0, -1.0, 0.5, 0.4, 2, "cop")
    metrics_path = save_metrics([metric], tmp_path / "metrics.json")
    plot_path = save_line_plot([1.0, 2.0], tmp_path / "plot.svg", title="Test", y_label="Y")
    trained = IQLTrainer(
        replace(GameConfig(), max_moves=2), TrainingConfig(episodes=2, batch_size=1)
    ).train()
    outputs = save_training_outputs(trained, tmp_path / "results")
    comparison = save_baseline_comparison(
        replace(GameConfig(), max_moves=1), trained, tmp_path / "results"
    )

    assert json.loads(metrics_path.read_text(encoding="utf-8"))[0]["winner"] == "cop"
    assert plot_path.read_text(encoding="utf-8").startswith("<svg")
    assert all(path.exists() for path in outputs.values())
    assert set(comparison) == {
        "random cop",
        "heuristic cop",
        "learned cop",
        "random thief",
        "heuristic thief",
        "learned thief",
    }
    assert (tmp_path / "results" / "plots" / "baseline_comparison.svg").exists()


def test_saved_learned_agents_run_in_match_runner(tmp_path: Path) -> None:
    config = replace(GameConfig(), max_moves=2)
    trained = IQLTrainer(config, TrainingConfig(episodes=2, batch_size=1)).train()
    cop_path = trained.cop_agent.save(tmp_path / "cop.json")
    thief_path = trained.thief_agent.save(tmp_path / "thief.json")

    result = MatchRunner(
        config,
        IQLAgent.load(cop_path, seed=3),
        IQLAgent.load(thief_path, seed=4),
    ).run()

    assert len(result.sub_games) == 6


def test_staged_training_cli_generates_analysis_outputs(tmp_path: Path, capsys) -> None:
    exit_code = main(
        ["train", "--staged", "--episodes", "1", "--output", str(tmp_path / "results")]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["episodes"] == 1
    assert payload["centralized_transitions"] > 0
    assert set(payload["comparison_role_wins"]) == {
        "random cop",
        "heuristic cop",
        "learned cop",
        "random thief",
        "heuristic thief",
        "learned thief",
    }
    assert (tmp_path / "results" / "plots" / "loss_curve.svg").exists()
