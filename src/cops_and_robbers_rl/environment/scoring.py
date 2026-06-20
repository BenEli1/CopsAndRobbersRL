"""Authoritative assignment scoring."""

from dataclasses import dataclass
from typing import Literal

from cops_and_robbers_rl.shared.config import ScoringConfig

WinnerName = Literal["cop", "thief"]


@dataclass(frozen=True, slots=True)
class Score:
    """Cop and thief score pair."""

    cop: int
    thief: int

    def to_dict(self) -> dict[str, int]:
        """Return an email-report-compatible mapping."""
        return {"cop": self.cop, "thief": self.thief}


def score_for_winner(winner: WinnerName, config: ScoringConfig) -> Score:
    """Return assignment scores for a terminal winner."""
    if winner == "cop":
        return Score(cop=config.cop_win, thief=config.thief_loss)
    if winner == "thief":
        return Score(cop=config.cop_loss, thief=config.thief_win)
    raise ValueError(f"unsupported winner: {winner}")
