"""SDK match and report-schema tests."""

import json
from dataclasses import replace

from cops_and_robbers_rl.sdk.sdk import CopsAndRobbersSDK
from cops_and_robbers_rl.shared.config import GameConfig


def test_match_result_has_email_json_fields() -> None:
    sdk = CopsAndRobbersSDK(replace(GameConfig(), max_moves=1))

    result = sdk.run_match()
    report = result.to_report_dict()

    assert set(report) == {
        "group_name",
        "students",
        "github_repo",
        "timezone",
        "sub_games",
        "totals",
    }
    assert report["timezone"] == "Asia/Jerusalem"
    assert len(report["sub_games"]) == 6
    assert [game["id"] for game in report["sub_games"]] == list(range(1, 7))
    assert all(game["moves"] == 1 for game in report["sub_games"])
    assert all(game["winner"] in {"cop", "thief"} for game in report["sub_games"])
    assert report["totals"] == {
        "cop": sum(game["scores"]["cop"] for game in report["sub_games"]),
        "thief": sum(game["scores"]["thief"] for game in report["sub_games"]),
    }
    assert json.loads(json.dumps(report)) == report
