"""Immutable environment, sub-game, and match result models."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any

from cops_and_robbers_rl.environment.grid import Position
from cops_and_robbers_rl.environment.scoring import Score


class Role(StrEnum):
    """Agent roles in the game."""

    COP = "cop"
    THIEF = "thief"


class TerminalReason(StrEnum):
    """Valid ways for a sub-game to finish."""

    CAPTURE = "capture"
    MOVE_LIMIT = "move_limit"


@dataclass(frozen=True, slots=True)
class GameState:
    """Complete internal state owned by the environment."""

    sub_game_id: int
    cop_position: Position
    thief_position: Position
    barriers: frozenset[Position]
    moves_completed: int
    terminal: bool = False
    winner: Role | None = None
    terminal_reason: TerminalReason | None = None


@dataclass(frozen=True, slots=True)
class GlobalTrainingState:
    """Privileged state available only through explicit training/debug APIs."""

    grid_size: tuple[int, int]
    cop_position: Position
    thief_position: Position
    barriers: frozenset[Position]
    moves_completed: int
    terminal: bool


@dataclass(frozen=True, slots=True)
class SubGameResult:
    """Authoritative result for one valid completed sub-game."""

    id: int
    start: datetime
    end: datetime
    moves: int
    winner: Role
    scores: Score

    def to_report_dict(self) -> dict[str, Any]:
        """Serialize fields required by the assignment email JSON."""
        return {
            "id": self.id,
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "moves": self.moves,
            "winner": self.winner.value,
            "scores": self.scores.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class Student:
    """Student identity included in the final report."""

    role: str
    full_name: str
    id: str

    def to_report_dict(self) -> dict[str, str]:
        """Serialize student identity without transformation."""
        return {"role": self.role, "full_name": self.full_name, "id": self.id}


@dataclass(frozen=True, slots=True)
class MatchResult:
    """Complete, report-ready result for a six-sub-game match."""

    group_name: str
    students: tuple[Student, ...]
    github_repo: str
    timezone: str
    sub_games: tuple[SubGameResult, ...]
    totals: Score

    def to_report_dict(self) -> dict[str, Any]:
        """Return the exact top-level assignment report structure."""
        return {
            "group_name": self.group_name,
            "students": [student.to_report_dict() for student in self.students],
            "github_repo": self.github_repo,
            "timezone": self.timezone,
            "sub_games": [game.to_report_dict() for game in self.sub_games],
            "totals": self.totals.to_dict(),
        }
