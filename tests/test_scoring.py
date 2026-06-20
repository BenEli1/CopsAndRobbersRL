"""Assignment scoring tests."""

import pytest

from cops_and_robbers_rl.environment.scoring import score_for_winner
from cops_and_robbers_rl.shared.config import ScoringConfig


def test_assignment_scoring() -> None:
    scoring = ScoringConfig()

    assert score_for_winner("cop", scoring).to_dict() == {"cop": 20, "thief": 5}
    assert score_for_winner("thief", scoring).to_dict() == {"cop": 5, "thief": 10}


def test_unknown_winner_is_rejected() -> None:
    with pytest.raises(ValueError, match="unsupported winner"):
        score_for_winner("draw", ScoringConfig())  # type: ignore[arg-type]
