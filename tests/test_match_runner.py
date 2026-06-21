"""Full match orchestration and preview-report tests."""

import json
from dataclasses import replace
from pathlib import Path

from cops_and_robbers_rl.agents import BaseAgent, HeuristicCopAgent, HeuristicThiefAgent
from cops_and_robbers_rl.environment.actions import Action, ActionType
from cops_and_robbers_rl.environment.game_state import Role
from cops_and_robbers_rl.environment.observations import LocalObservation
from cops_and_robbers_rl.runner.match_runner import MatchRunner
from cops_and_robbers_rl.shared.config import GameConfig


class _StayAgent(BaseAgent):
    def _act(self, observation: LocalObservation) -> Action:
        assert isinstance(observation, LocalObservation)
        return Action(ActionType.STAY)


class _FlakyCopAgent(_StayAgent):
    def __init__(self) -> None:
        super().__init__(Role.COP)
        self.failures_remaining = 1

    def _act(self, observation: LocalObservation) -> Action:
        if self.failures_remaining:
            self.failures_remaining -= 1
            raise RuntimeError("synthetic transient failure")
        return super()._act(observation)


def test_full_match_generates_valid_report_json(tmp_path: Path) -> None:
    config = replace(GameConfig(), max_moves=5)
    runner = MatchRunner(
        config,
        HeuristicCopAgent(seed=10),
        HeuristicThiefAgent(seed=20),
    )
    output = tmp_path / "report_email_preview.json"

    result = runner.run_and_save(output)
    payload = json.loads(output.read_text(encoding="utf-8"))

    assert payload == result.to_report_dict()
    assert payload["timezone"] == "Asia/Jerusalem"
    assert len(payload["sub_games"]) == 6
    assert [game["id"] for game in payload["sub_games"]] == list(range(1, 7))
    assert all(1 <= game["moves"] <= 5 for game in payload["sub_games"])
    assert payload["totals"] == {
        "cop": sum(game["scores"]["cop"] for game in payload["sub_games"]),
        "thief": sum(game["scores"]["thief"] for game in payload["sub_games"]),
    }


def test_transient_technical_failure_still_produces_six_games() -> None:
    runner = MatchRunner(
        replace(GameConfig(), max_moves=1),
        _FlakyCopAgent(),
        _StayAgent(Role.THIEF),
    )

    result = runner.run()

    assert len(result.sub_games) == 6
    assert runner.technical_failures == 1
