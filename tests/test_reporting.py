"""Safe Gmail reporting and exact assignment-schema tests."""

import json
import smtplib
from dataclasses import replace
from pathlib import Path

import pytest

from cops_and_robbers_rl.reporting import (
    GmailReporter,
    ReportSchemaError,
    load_gmail_config,
    validate_report,
)
from cops_and_robbers_rl.sdk.sdk import CopsAndRobbersSDK
from cops_and_robbers_rl.shared.config import GameConfig


def _match():
    return CopsAndRobbersSDK(replace(GameConfig(), max_moves=2)).run_match()


def test_default_gmail_config_is_safe_and_group_aware() -> None:
    config = load_gmail_config()

    assert "@" in config.target_email
    assert config.dry_run is True
    assert "{group_name}" in config.subject_template


def test_report_schema_requires_six_games_and_correct_totals() -> None:
    report = _match().to_report_dict()
    validate_report(report)

    invalid_games = dict(report, sub_games=report["sub_games"][:-1])
    with pytest.raises(ReportSchemaError, match="exactly six"):
        validate_report(invalid_games)

    invalid_totals = dict(report, totals={"cop": 0, "thief": 0})
    with pytest.raises(ReportSchemaError, match="score sums"):
        validate_report(invalid_totals)

    invalid_identity = dict(report, students=[{"role": "A", "full_name": "X", "id": "bad"}])
    with pytest.raises(ReportSchemaError, match="nine decimal"):
        validate_report(invalid_identity)


def test_dry_run_writes_exact_json_and_text_previews(tmp_path: Path, capsys) -> None:
    result = _match()
    output = tmp_path / "report_email_preview.json"

    delivery = GmailReporter(load_gmail_config()).deliver(result, output)

    assert delivery.mode == "dry_run"
    assert delivery.sent is False
    assert json.loads(output.read_text(encoding="utf-8")) == result.to_report_dict()
    text = output.with_suffix(".txt").read_text(encoding="utf-8")
    assert f"To: {delivery.target_email}" in text
    assert "[MARL Exercise 06] BenEli1 - Final Report" in text
    printed = capsys.readouterr().out
    assert f"Target email: {delivery.target_email}" in printed
    assert "Subject:" in printed


def test_missing_credentials_does_not_crash_match_workflow(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("GMAIL_SENDER", raising=False)
    monkeypatch.delenv("GMAIL_APP_PASSWORD", raising=False)
    config_path = tmp_path / "gmail.yaml"
    config_path.write_text(
        """schema_version: "1.00"
target_email: recipient@example.invalid
subject_template: "[MARL Exercise 06] {group_name} - Final Report"
dry_run: false
smtp:
  host: smtp.gmail.com
  port: 465
  sender_env: GMAIL_SENDER
  app_password_env: GMAIL_APP_PASSWORD
""",
        encoding="utf-8",
    )
    sdk = CopsAndRobbersSDK(replace(GameConfig(), max_moves=2))
    output = tmp_path / "report_email_preview.json"

    result = sdk.run_match_and_save(
        output_path=output,
        gmail_config_path=config_path,
        allow_send=True,
    )

    assert len(result.sub_games) == 6
    delivery = sdk.last_delivery
    assert delivery is not None
    assert delivery.mode == "dry_run_missing_credentials"
    assert delivery.sent is False
    assert delivery.json_path.exists()
    assert delivery.text_path.exists()


def test_explicit_send_uses_environment_credentials(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("MARL_STUDENT_ID", "111111111")
    monkeypatch.setenv("GMAIL_SENDER", "sender@example.com")
    monkeypatch.setenv("GMAIL_APP_PASSWORD", "placeholder")
    config = replace(load_gmail_config(), dry_run=False)
    reporter = GmailReporter(config)
    sent: list[tuple[str, str, str]] = []
    monkeypatch.setattr(
        reporter,
        "_send",
        lambda sender, password, subject, body: sent.append((sender, subject, body)),
    )

    delivery = reporter.deliver(_match(), tmp_path / "report_email_preview.json", allow_send=True)

    assert delivery.mode == "sent"
    assert delivery.sent is True
    assert sent and sent[0][0] == "sender@example.com"
    assert "Final Report" in sent[0][1]


def test_smtp_failure_retains_previews(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("MARL_STUDENT_ID", "111111111")
    monkeypatch.setenv("GMAIL_SENDER", "sender@example.com")
    monkeypatch.setenv("GMAIL_APP_PASSWORD", "placeholder")
    reporter = GmailReporter(replace(load_gmail_config(), dry_run=False))

    def fail_send(*_args) -> None:
        raise smtplib.SMTPException("synthetic failure")

    monkeypatch.setattr(reporter, "_send", fail_send)
    delivery = reporter.deliver(_match(), tmp_path / "report_email_preview.json", allow_send=True)

    assert delivery.mode == "send_failed"
    assert delivery.sent is False
    assert delivery.json_path.exists() and delivery.text_path.exists()
