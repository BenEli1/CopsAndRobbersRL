"""Dry-run-first Gmail reporting with environment-only credentials."""

import json
import os
import smtplib
from dataclasses import dataclass
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from typing import Any

import yaml

from cops_and_robbers_rl.environment.game_state import MatchResult
from cops_and_robbers_rl.shared.paths import DEFAULT_GMAIL_CONFIG


class ReportSchemaError(ValueError):
    """Raised when a completed match cannot form the assignment report."""


@dataclass(frozen=True, slots=True)
class GmailConfig:
    target_email: str
    subject_template: str
    dry_run: bool
    smtp_host: str
    smtp_port: int
    sender_env: str
    app_password_env: str


@dataclass(frozen=True, slots=True)
class ReportDelivery:
    json_path: Path
    text_path: Path
    target_email: str
    subject: str
    sent: bool
    mode: str


def load_gmail_config(path: str | Path | None = None) -> GmailConfig:
    """Load non-secret email settings; credentials remain in the environment."""
    source = Path(path) if path else DEFAULT_GMAIL_CONFIG
    raw = yaml.safe_load(source.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ReportSchemaError("Gmail config must be a mapping")
    _exact_keys(raw, {"schema_version", "target_email", "subject_template", "dry_run", "smtp"})
    smtp = raw.get("smtp")
    if not isinstance(smtp, dict):
        raise ReportSchemaError("smtp must be a mapping")
    _exact_keys(smtp, {"host", "port", "sender_env", "app_password_env"})
    config = GmailConfig(
        target_email=str(raw.get("target_email", "")),
        subject_template=str(raw.get("subject_template", "")),
        dry_run=bool(raw.get("dry_run", True)),
        smtp_host=str(smtp.get("host", "smtp.gmail.com")),
        smtp_port=int(smtp.get("port", 465)),
        sender_env=str(smtp.get("sender_env", "GMAIL_SENDER")),
        app_password_env=str(smtp.get("app_password_env", "GMAIL_APP_PASSWORD")),
    )
    if "@" not in config.target_email or "{group_name}" not in config.subject_template:
        raise ReportSchemaError("target email and group-aware subject template are required")
    if not 1 <= config.smtp_port <= 65535:
        raise ReportSchemaError("SMTP port must be valid")
    return config


class GmailReporter:
    """Validate a completed match, write previews, and optionally send once."""

    def __init__(self, config: GmailConfig) -> None:
        self.config = config

    def deliver(
        self,
        result: MatchResult,
        output_path: str | Path,
        *,
        allow_send: bool = False,
    ) -> ReportDelivery:
        report = result.to_report_dict()
        validate_report(report)
        json_path = Path(output_path)
        text_path = json_path.with_suffix(".txt")
        subject = self.config.subject_template.format(group_name=result.group_name)
        body = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
        preview = f"To: {self.config.target_email}\nSubject: {subject}\n\n{body}"
        _atomic_write(json_path, body)
        _atomic_write(text_path, preview)
        print(f"Target email: {self.config.target_email}")
        print(f"Subject: {subject}")

        sender = os.getenv(self.config.sender_env)
        password = os.getenv(self.config.app_password_env)
        if self.config.dry_run or not allow_send:
            return self._result(json_path, text_path, subject, False, "dry_run")
        if not sender or not password:
            return self._result(json_path, text_path, subject, False, "dry_run_missing_credentials")
        if any(student["id"] == "000000000" for student in report["students"]):
            return self._result(json_path, text_path, subject, False, "dry_run_missing_identity")
        try:
            self._send(sender, password, subject, body)
        except (OSError, smtplib.SMTPException):
            return self._result(json_path, text_path, subject, False, "send_failed")
        return self._result(json_path, text_path, subject, True, "sent")

    def _send(self, sender: str, password: str, subject: str, body: str) -> None:
        message = EmailMessage()
        message["From"] = sender
        message["To"] = self.config.target_email
        message["Subject"] = subject
        message.set_content(body)
        with smtplib.SMTP_SSL(self.config.smtp_host, self.config.smtp_port, timeout=15) as smtp:
            smtp.login(sender, password)
            smtp.send_message(message)

    def _result(
        self,
        json_path: Path,
        text_path: Path,
        subject: str,
        sent: bool,
        mode: str,
    ) -> ReportDelivery:
        return ReportDelivery(
            json_path=json_path,
            text_path=text_path,
            target_email=self.config.target_email,
            subject=subject,
            sent=sent,
            mode=mode,
        )


def validate_report(report: dict[str, Any]) -> None:
    """Validate the exact six-game assignment report and authoritative totals."""
    _exact_keys(
        report,
        {"group_name", "students", "github_repo", "timezone", "sub_games", "totals"},
    )
    if report["timezone"] != "Asia/Jerusalem" or not report["group_name"]:
        raise ReportSchemaError("group name and Asia/Jerusalem timezone are required")
    students = report["students"]
    if not isinstance(students, list) or not students:
        raise ReportSchemaError("at least one student entry is required")
    for student in students:
        _exact_keys(student, {"role", "full_name", "id"})
        if not str(student["id"]).isdigit() or len(str(student["id"])) != 9:
            raise ReportSchemaError("student IDs must be nine decimal characters")
    games = report["sub_games"]
    if not isinstance(games, list) or len(games) != 6:
        raise ReportSchemaError("report must contain exactly six sub-games")
    totals = {"cop": 0, "thief": 0}
    for expected_id, game in enumerate(games, 1):
        _exact_keys(game, {"id", "start", "end", "moves", "winner", "scores"})
        _exact_keys(game["scores"], {"cop", "thief"})
        if game["id"] != expected_id or game["winner"] not in {"cop", "thief"}:
            raise ReportSchemaError("sub-game IDs or winner values are invalid")
        if not isinstance(game["moves"], int) or not 1 <= game["moves"] <= 25:
            raise ReportSchemaError("sub-game moves must be integers from 1 to 25")
        start, end = datetime.fromisoformat(game["start"]), datetime.fromisoformat(game["end"])
        if start.utcoffset() is None or end.utcoffset() is None or end < start:
            raise ReportSchemaError("sub-game end must not precede start")
        if not all(isinstance(game["scores"][role], int) for role in ("cop", "thief")):
            raise ReportSchemaError("scores must be integers")
        totals["cop"] += int(game["scores"]["cop"])
        totals["thief"] += int(game["scores"]["thief"])
    if report["totals"] != totals:
        raise ReportSchemaError("report totals do not equal sub-game score sums")


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def _exact_keys(raw: object, expected: set[str]) -> None:
    if not isinstance(raw, dict) or set(raw) != expected:
        raise ReportSchemaError(f"expected keys: {', '.join(sorted(expected))}")
