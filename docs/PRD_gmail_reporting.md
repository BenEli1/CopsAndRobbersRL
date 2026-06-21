# PRD - Gmail Reporting

> **Implementation status (2026-06-21):** exact six-game schema validation, atomic JSON/text previews, console target/subject output, environment-only identity/credentials, and a double-gated optional Gmail SMTP adapter are implemented. No live email has been sent or claimed.

## 1. Purpose

After all six valid sub-games, generate one canonical JSON report and either write an exact dry-run preview or explicitly send one email to a privately configured course recipient. Reporting consumes authoritative `MatchResult` objects and never recalculates outcomes.

## 2. Preconditions and lifecycle

1. Match is complete with exactly six valid, ordered IDs `1..6`.
2. Each result has start/end timestamps, moves, winner, and authoritative scores.
3. Student/group/repository metadata is configured and validated.
4. Totals equal the sum of sub-game scores.
5. A canonical JSON body is created and schema-validated.
6. In default dry-run mode, it is atomically written to `results/report_email_preview.json` and an email-style text preview is written to `results/report_email_preview.txt`.
7. In explicit live mode, the same canonical body is submitted once through the Gmail SMTP adapter.

Incomplete matches, technical failures, missing required identities, bad timestamps, or inconsistent totals block finalization.

## 3. Exact JSON shape

This is a **synthetic, schema-valid fixture copied in spirit from the assignment format**. Its game values are documentation examples only and are not evidence that this repository ran a match:

```json
{
  "group_name": "BenEli1",
  "students": [
    {
      "role": "A",
      "full_name": "Ben Eli",
      "id": "000000000"
    }
  ],
  "github_repo": "https://github.com/BenEli1/CopsAndRobbersRL",
  "timezone": "Asia/Jerusalem",
  "sub_games": [
    {
      "id": 1,
      "start": "2026-06-17T18:00:05+03:00",
      "end": "2026-06-17T18:02:40+03:00",
      "moves": 17,
      "winner": "cop",
      "scores": {"cop": 20, "thief": 5}
    },
    {"id": 2, "start": "2026-06-17T18:03:10+03:00", "end": "2026-06-17T18:06:02+03:00", "moves": 25, "winner": "thief", "scores": {"cop": 5, "thief": 10}},
    {"id": 3, "start": "2026-06-17T18:06:30+03:00", "end": "2026-06-17T18:08:11+03:00", "moves": 11, "winner": "cop", "scores": {"cop": 20, "thief": 5}},
    {"id": 4, "start": "2026-06-17T18:08:40+03:00", "end": "2026-06-17T18:11:20+03:00", "moves": 22, "winner": "cop", "scores": {"cop": 20, "thief": 5}},
    {"id": 5, "start": "2026-06-17T18:11:45+03:00", "end": "2026-06-17T18:14:33+03:00", "moves": 25, "winner": "thief", "scores": {"cop": 5, "thief": 10}},
    {"id": 6, "start": "2026-06-17T18:15:00+03:00", "end": "2026-06-17T18:17:09+03:00", "moves": 14, "winner": "cop", "scores": {"cop": 20, "thief": 5}}
  ],
  "totals": {"cop": 90, "thief": 40}
}
```

At runtime, synthetic fixtures and placeholders are forbidden and all scores are JSON integers. The assignment example expects multiple student roles in a normal team, while current supplied metadata contains only Student A. The implementation shall accept 1-3 configured students but live submission must be blocked until the actual course team membership/group-code requirement is confirmed.

## 4. Schema rules

- No undeclared top-level fields in the submission payload unless the assignment format is revised.
- Student IDs are exactly nine decimal characters and remain strings.
- Repository is an HTTPS GitHub URL.
- `timezone` is the literal `Asia/Jerusalem`.
- Exactly six unique ascending sub-games exist.
- Timestamps are ISO 8601, include an offset, use Jerusalem local time, and `end >= start`.
- `moves` is an integer `1..25` for a completed game.
- Winner is `cop` or `thief`; scores match configured authoritative rules.
- Totals are computed once from trusted results and verified against the six entries.

## 5. Dry-run behavior

`dry_run: true` is the immutable repository default. The preview directory is created safely and both files are written atomically with UTF-8 and stable indentation/key order. Re-running overwrites the same previews and does not create multiple emails.

## 6. Live Gmail behavior

Live delivery requires `dry_run: false`, the explicit `--send-email` CLI flag, a configured sender, non-placeholder identity metadata, and credentials from environment variables. The implemented adapter uses Gmail SMTP over SSL with an app password. Missing credentials or identity returns a dry-run status and retains both previews without crashing the match workflow.

Use an idempotency key derived from match ID and canonical payload hash. Retry only transient failures with bounded exponential backoff. Because email provider calls can have ambiguous outcomes, do not automatically resend after an unknown post-submit response without checking the delivery ledger/operator decision.

## 7. Credential and privacy safety

- `.env-example` contains names/placeholders only; `.env`, OAuth tokens, client secrets, app passwords, and refresh tokens are ignored.
- Credentials are never printed, serialized into reports, screenshots, test artifacts, or exception messages.
- Tests use fake senders and synthetic addresses except the fixed recipient contract.
- Logs contain payload hash/status but may omit student IDs/report body in normal mode.
- Rotate/revoke any credential suspected of exposure; secret scanning is a release gate.

## 8. Failure handling

| Failure | Behavior |
|---|---|
| Fewer/more than six valid games | Refuse preview finalization and live send. |
| Inconsistent score/winner/totals | Validation error; no output/send. |
| Missing team metadata | Dry-run may use clearly invalid placeholders only in docs/tests; live mode blocked. |
| Preview filesystem error | Typed delivery error; original match result retained. |
| Gmail auth/permission error | Fail closed; no credential logging; operator guidance. |
| Transient quota/network error | Bounded gatekeeper retry. |
| Ambiguous send outcome | Record unknown status and require reconciliation; avoid blind duplicate. |

## 9. Acceptance criteria

- **MAIL-AC-1:** Exactly six valid results produce a payload matching the documented shape; any incomplete/inconsistent match is rejected.
- **MAIL-AC-2:** Dry-run is default and writes the exact body to JSON plus an email-style text preview without network access.
- **MAIL-AC-3:** Exactly one final report action occurs per match; never one email per sub-game.
- **MAIL-AC-4:** All timestamps include correct Asia/Jerusalem offset handling, including daylight-saving transitions.
- **MAIL-AC-5:** Credentials appear only in environment-backed provider setup and never in Git/logs/artifacts.
- **MAIL-AC-6:** Mocked live delivery proves recipient, subject, body identity, idempotency, rate/retry, and failure behavior.
- **MAIL-AC-7:** No live-send claim is made until provider receipt is verified.

## 10. Subject and configuration

The committed non-secret config targets `rmisegal+marl@gmail.com` and uses `[MARL Exercise 06] {group_name} - Final Report`. Sender, app password, and student identity remain private environment configuration.
