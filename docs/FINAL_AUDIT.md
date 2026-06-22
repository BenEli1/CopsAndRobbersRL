# Final Exercise 06 Audit

Audit date: 2026-06-23 (Asia/Jerusalem)

## Verdict and recommended score

The submission is locally ready: deterministic six-game mechanics, decentralized observations, baseline agents, tabular IQL, the SDK-backed GUI, reproducible evidence, validated dry-run reporting, and local MCP services all run. The honest recommended self-score is **92/100**. Points are reserved because robust held-out multi-seed research, VDN/QMIX, a remote six-game MCP match, cloud deployment, live Gmail receipt, and the optional bonus match are not complete.

## Assignment checklist

| Requirement | Status | Evidence and limit |
|---|---|---|
| Root README plus PRD/PLAN/TODO | Implemented | Required docs and separate mechanism PRDs are present. |
| 5x5, 25 moves, six games, five barriers, 20/10/5/5 | Implemented | `config/default_game.yaml` is asserted by tests; a nondefault-YAML test proves configured values are not replaced by code defaults. |
| Exactly six valid sub-games | Implemented | `MatchRunner` rejects other match lengths, retries technical failures, and reports ordered IDs `1..6` or raises a typed failure. |
| Exact report and totals | Implemented | Schema validation checks keys, ISO timestamps, move bounds, winners, six games, and recomputed totals. |
| SDK-only business workflows | Implemented | CLI, GUI session, runner, training entry, MCP adapters, and reporter use the SDK/domain interfaces. |
| Partial observation and MARL theory | Implemented | Summary/PRDs explain MARL, local observations, Dec-POMDP versus POSG, CTDE, IQL, VDN/QMIX scope, limitations, and ethics. |
| IQL | Implemented baseline | Tabular replay-backed training and smoke plots exist; convergence and superiority are not claimed. |
| VDN/QMIX | Not implemented | Documented extension only. |
| GUI commands and evidence | Implemented | Standard GUI startup and completed `gui --demo` capture were verified on Windows. |
| Local MCP | Partial/implemented MVP | Separate services/ports, health/action contracts, local observations, optional auth, timeout/retry/fallback, and smoke tests exist. Full remote match/cloud are future work. |
| Gmail reporting | Partial/implemented dry-run | Default is preview-only. Sending additionally requires CLI opt-in, config opt-in, environment credentials, and non-placeholder identity; live receipt is unverified. |
| Privacy and secrets | Implemented locally | Identity/credentials are environment-only, `.env-example` is placeholder-only, generated reports are ignored, and the recipient address appears only in Gmail YAML. |
| `uv`, Ruff, pytest, coverage, CI | Implemented locally | Locked project and CI workflow exist; exact local results are below. |

## Exact verification results

Executed from the repository root on 2026-06-23:

| Command | Result |
|---|---|
| `uv sync --extra dev --system-certs` | Passed; 49 packages resolved. |
| `uv sync --extra dev --extra mcp --system-certs` | Passed; optional MCP SDK 1.28.0 installed. |
| `uv run ruff check .` | Passed: `All checks passed!` |
| `uv run ruff format --check .` | Passed: 56 files already formatted. |
| `uv run pytest` | Passed: 49 tests in 0.49 s. |
| `uv run pytest --cov=cops_and_robbers_rl --cov-report=term-missing --cov-fail-under=85` | Passed: 49 tests; 89.26% coverage. |
| `uv run cops-and-robbers play --config config/default_game.yaml --seed 42 --output results/report_email_preview.json` | Passed: 6 games, cop/thief wins 1/5, totals 45/55, zero technical retries, dry-run preview. |
| `uv run python -m cops_and_robbers_rl.main mcp-smoke` | Passed: in-process contract fallback, SDK installed, cop/thief ports 8101/8102, legal role actions. |
| `powershell -File scripts/capture_cli_evidence.ps1` | Passed; regenerated headless-match and MCP screenshots from real output. |
| `powershell -File scripts/capture_gui.ps1` | Passed; regenerated a completed game-6-of-6 native GUI screenshot after bounded autoplay. |
| `uv run cops-and-robbers gui --config config/default_game.yaml` | Startup smoke passed; native GUI remained running until the audit process closed it. |

Generated JSON/text previews are intentionally Git-ignored because private identity may be supplied locally. Committed screenshots and plots contain no private identity.

## Known limitations

- The IQL plots are a small pipeline smoke, not robust held-out evidence.
- VDN and QMIX are not implemented; the centralized trace is CTDE-inspired scaffolding, not a centralized critic.
- MCP cloud deployment and a full six-game remote-service match are not implemented.
- Live Gmail delivery and receipt are not verified; dry-run remains the safe default.
- No inter-group bonus match has occurred.
- A project license and immutable release tag remain release-administration choices, not runtime blockers.

## Submission recommendation

Submit the tested submission branch and private Moodle PDF identity together. Do not claim incomplete research, cloud, live-email, or bonus items. Recommended self-score: **92/100**.
