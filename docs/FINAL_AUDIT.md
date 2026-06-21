# Final Exercise 06 Audit

Audit date: 2026-06-21 (Asia/Jerusalem)

## Verdict

The repository provides a strong, runnable Exercise 06 foundation: deterministic six-game mechanics, decentralized observations, baseline agents, tabular IQL, a polished SDK-backed GUI, learning plots, safe Gmail previews, and local MCP services. It does **not** justify claims of robust MARL performance, completed VDN/QMIX, cloud deployment, live Gmail delivery, or a bonus opponent match.

The code and documents are submission-consistent, but two release items remain outside the implementation itself:

1. the privacy-sanitized local Git history still requires explicit approval before force-updating GitHub; and
2. robust held-out multi-seed evaluation remains incomplete.

## Checklist

| Check | Status | Evidence and limits |
|---|---|---|
| Exercise 06 coverage | Partial | Core game, SDK, GUI, IQL, reporting, and local MCP exist. Robust research and CTDE comparison remain incomplete. |
| Exactly six sub-games | Pass | `MatchRunner` rejects non-six-game configs; tests verify ordered IDs `1..6`, retries, and totals. |
| Configuration over hardcoding | Pass with noted constants | Game, MCP, and Gmail settings use validated YAML; credentials and student identity use environment variables. Assignment timezone and six-game rule are intentional invariants. |
| Local observations | Pass | Execution agents accept `LocalObservation`; privileged global state is exposed only through explicit training/debug APIs. |
| Dec-POMDP/POSG explanation | Pass | PRD/PLAN/MARL PRD distinguish the course Dec-POMDP notation from the competitive POSG formulation. |
| IQL/CTDE/VDN/QMIX scope | Honest partial | Tabular IQL and centralized trace scaffolding exist. VDN/QMIX are documented extension contracts, not claimed implementations. |
| GUI evidence | Pass | The themed Tkinter dashboard is SDK-backed and has a genuine target-machine screenshot in `assets/evidence/`. |
| Learning/loss plots | Pass as pipeline evidence | Four committed SVG plots exist. They are explicitly labeled smoke evidence, not convergence or superiority evidence. |
| Gmail JSON report | Pass | Exactly six results are schema-validated; JSON and text previews are atomically generated after the match. |
| Gmail safety | Pass for dry-run | Default is dry-run. Sending requires config opt-in, CLI opt-in, environment credentials, and non-placeholder identity. Live receipt is not claimed. |
| MCP communication | Partial | Separate localhost roles, schemas, auth checks, retries, and contract smoke exist. Authenticated full remote six-game match is pending. |
| `uv` only | Pass | `pyproject.toml` and `uv.lock` are authoritative; README and CI use `uv`; no `requirements.txt` exists. |
| Tests and coverage | Pass | 47 tests pass; business-logic coverage is 89.25% against the 85% gate. Native rendering is visually verified and excluded from the metric. |
| Ruff | Pass | `ruff check` and `ruff format --check` pass. |
| Secrets/private files | Pass locally | No committed credentials, student ID, PDFs/DOCX, private keys, certificates, or generated private reports are in the sanitized reachable history. |
| README/docs consistency | Pass | Commands, evidence, implemented status, and explicit non-claims match the current code. |

## Reporting audit

The canonical JSON contains exactly `group_name`, `students`, `github_repo`, `timezone`, `sub_games`, and `totals`. Every sub-game contains ID, ISO timestamp range, moves, winner, and role scores. Validation checks ordered six-game IDs, timezone, timestamp offsets/order, move bounds, winner values, score types, and recomputed totals.

Dry-run produces:

- `results/report_email_preview.json` — exact canonical body;
- `results/report_email_preview.txt` — target, subject, and identical body; and
- console output naming the configured target and subject.

## Security and privacy audit

- `.env`, generated reports, PDFs/DOCX, keys, certificates, and common credential exports are ignored.
- `.env-example` contains placeholders only.
- Student identity and Gmail credentials are environment-backed.
- CI includes Gitleaks history scanning.
- Binary screenshots were visually inspected and contain no student ID or credential.
- Historical personal data was removed from the local rewritten history; remote replacement is intentionally blocked until the destructive force-push is explicitly approved.

## Submission blockers and honest limitations

- Do not claim VDN, QMIX, cloud MCP, live Gmail, or bonus completion.
- Do not claim the existing IQL smoke proves convergence or outperformance.
- Run held-out multi-seed evaluation if research marks materially affect the grade.
- Select a project license and tag only after the final GitHub history decision.
