"""Private report identity loaded only from the process environment."""

import os

from cops_and_robbers_rl.environment.game_state import Student

STUDENT_NAME_ENV = "MARL_STUDENT_NAME"
STUDENT_ID_ENV = "MARL_STUDENT_ID"


def load_report_students() -> tuple[Student, ...]:
    """Return report identity without embedding private values in source control."""
    return (
        Student(
            role="A",
            full_name=os.getenv(STUDENT_NAME_ENV, "Student A"),
            id=os.getenv(STUDENT_ID_ENV, "not-configured"),
        ),
    )
