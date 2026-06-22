# Prompt and Decision Log

This log preserves material AI-assisted-development prompts and resulting decisions without storing hidden chain-of-thought, secrets, or fabricated execution evidence. Dates use Asia/Jerusalem.

## 2026-06-20 - Prompt 1: documentation-first architecture

### User direction (summary)

Act as senior architect for Exercise 06; read repository and three course PDFs in precedence order; do not implement code; create README plus PRD/PLAN/TODO and mechanism PRDs; cover MARL theory, deterministic game, SDK/OOP architecture, GUI, two MCP services, Gmail JSON/dry-run, testing, risks, and extension plans.

### Decisions recorded

- Documentation precedes implementation.
- Exercise PDF overrides lecture, which overrides software guidelines.
- Python plus `uv`; no `pip`-managed workflow or `requirements.txt` source of truth.
- SDK is the sole business-logic entry point for CLI/GUI/integrations.
- The game is a competitive POSG; Dec-POMDP notation remains course-required context.
- Local observations are execution inputs; global state is training-only (plus non-policy rendering/diagnostics).
- IQL is the baseline; VDN is the first scoped CTDE candidate; QMIX/LSTM/GRU/OLoRA are optional until implemented and evaluated.
- Two independent local MCP services precede any cloud deployment.
- Reporting defaults to one dry-run JSON preview after six valid games; no credentials in Git.

### Open decisions

- Confirm actual eight-character group code if `BenEli1` is not accepted.
- Confirm Student B/C identities or that this is an approved one-person submission.
- Approve the proposed simultaneous movement/crossing/barrier conflict semantics in PLAN ADR-003 and environment PRD.
- Select project code license before release.

## 2026-06-20 - Request: periodic GitHub publishing

### User direction (summary)

Push code periodically to GitHub.

### Decision recorded

An hourly safe-push automation was requested: skip clean runs, inspect changes for secrets/unsafe artifacts, run available validation, commit only appropriate validated changes, and push the current branch. This operational request does not change documentation-first scope and does not authorize implementing features before review.

## 2026-06-20 - Prompt 2: strict documentation review

### User direction (summary)

Grade every Markdown document against an explicit checklist, improve all docs directly, and do not implement code.

### Baseline findings

- Only an empty `README.md` existed.
- Required `docs/PRD.md`, `PLAN.md`, `TODO.md`, four mechanism PRDs, `SUMMARY_REPORT.md`, and `PROMPT_LOG.md` were absent.
- The documentation baseline therefore failed the checklist before remediation.

### Review actions and decisions

- Read all three PDFs and visually checked representative source pages for rule, CTDE, and documentation requirements.
- Rebuilt README as an honest documentation-phase manual with planned `uv` install/run/test/GUI/MCP commands, config/report guidance, troubleshooting, and status labels.
- Added measurable product and mechanism acceptance criteria.
- Added C4-style Mermaid context/container/component/class, sequence, CTDE data-flow, and deployment views.
- Added ADRs for SDK-only access, POSG framing, deterministic simultaneous resolution, IQL/VDN scope, local-first MCP, dry-run reporting, YAML/env config, and GUI choice.
- Defined six-game lifecycle, authoritative scoring, barrier rules, local observation/global training types, technical-failure behavior, and unresolved assignment ambiguities.
- Defined exact report shape while marking all example outcomes/timestamps as placeholders, not results.
- Added phase/task Definitions of Done and left every implementation item unchecked.
- Added a summary evidence register that explicitly says nothing has been implemented, trained, deployed, or sent.

### Grader checklist disposition after remediation

| Document/check | Disposition |
|---|---|
| README install/uv/run/test/GUI/config/reports/troubleshooting | Covered; commands labeled planned until implementation |
| PRD product/users/goals/FR/NFR/criteria/out-of-scope | Covered |
| PLAN architecture/OOP/SDK/data flow/C4/ADRs/tests | Covered |
| TODO phases plus per-task DoD | Covered |
| Game environment mechanics/observations/state/scoring/config/edges | Covered; collision ADR awaits human approval |
| MARL Dec-POMDP/POSG/CTDE/IQL/VDN-QMIX/non-stationarity/IGM/memory/metrics | Covered with competitive-method caveat |
| MCP two services/local first/cloud/auth/ports/failures | Covered |
| Gmail exact JSON/dry-run/safety/single final email | Covered; team metadata remains open |
| Summary placeholders without false results | Covered |
| Prompt and decision trace | Covered |

## Logging policy for future prompts

For each material prompt, record the date, user intent summary, changed requirements, chosen/rejected alternatives, affected documents, unresolved questions, and verification evidence. Never record credentials, private tokens, hidden reasoning, or claim a command/test/result that did not occur.

## 2026-06-20 - Prompt 3: scaffold and deterministic engine

### User direction (summary)

Implement only the `uv` project scaffold, validated default config, deterministic game engine modules, SDK wrapper, CLI, and requested tests. Explicitly defer MARL networks, MCP, Gmail, and GUI.

### Decisions and delivered scope

- Added an installable `src` package with Python 3.11+, PyYAML, Windows timezone data, pytest, coverage, and Ruff locked by `uv`.
- Implemented immutable positions, actions, game state, observations, scores, sub-game results, and report-ready match results.
- Implemented simultaneous actions, deterministic illegal-action-to-stay behavior, capture/timeout, optional adjacent barriers, five-barrier limit, and seeded distinct spawning.
- Kept full coordinates behind the explicit `global_state_for_training()` method; decentralized observations are egocentric and radius-limited.
- Added an SDK facade and a headless `play` command. Default policies stay in place and are smoke-test controls, not AI agents.
- Verification: `uv run pytest` passed 14 tests, `uv run ruff check` passed, and the CLI produced six valid default sub-games and report-ready JSON.

### Explicitly deferred

MARL learners/networks, heuristic agents, replay/training, GUI, MCP, Gmail delivery/dry-run files, cloud deployment, and research results.

## 2026-06-20 - Prompt 4: baseline agents and match runner

### User direction (summary)

Add random and heuristic cop/thief agents, enforce local-observation-only execution, run six valid sub-games with technical-failure recovery, print a CLI summary, and save the exact report preview JSON. Continue to defer MARL networks, GUI, MCP, and live Gmail.

### Decisions and delivered scope

- Added a `BaseAgent` contract that rejects non-local and wrong-role observations.
- Added seeded random agents and deterministic-seeded heuristic pursuit/evasion agents.
- Heuristic barriers remain disabled because the existing barrier action requires an absolute target while decentralized observations intentionally omit absolute self coordinates; enabling them now would violate the information boundary.
- Added `MatchRunner` with bounded retry so transient agent/runtime failures do not count as valid sub-games.
- Added SDK and CLI selection for random/heuristic agents plus atomic `results/report_email_preview.json` output.
- Added behavior, isolation, retry, six-game, and JSON tests. Local verification reached 20 passing tests before the final lint correction pass.

# Prompt 5 — Simple Python GUI

- **Request:** Add a simple Tkinter GUI as a thin SDK layer, required state and controls, practical image export, a `uv` command, documentation, and GUI-independent tests.
- **Decision:** Added an SDK-owned `InteractiveSession` so Tkinter receives immutable snapshots and never imports or reproduces environment rules.
- **Decision:** Heuristic agents are the default, with the existing `BaseAgent` contract retained as the extension point for learned agents.
- **Decision:** Canvas export uses Tkinter's built-in color PostScript support to avoid an imaging dependency; a genuine PNG screenshot remains a submission-time task and is not fabricated.
- **Validation:** `23 passed`; Ruff check and format pass; Tkinter 8.6 imports successfully.

## 2026-06-21 - Prompt 6: MARL training baseline and analysis

- **Request:** Implement submission-safe IQL, replay/data collection, CTDE-inspired training, metrics, staged grids, plots, baseline comparison, persistence, tests, and honest VDN/QMIX scope.
- **Decision:** Use tabular IQL to keep the baseline reproducible, inspectable, CPU-only, and directly compatible with `BaseAgent` and `MatchRunner`.
- **Decision:** Restrict execution to encoded `LocalObservation`; place global state and joint actions only in `CentralizedTrainingTrace` inside the trainer.
- **Decision:** Defer VDN/QMIX because cooperative IGM assumptions do not directly solve the competitive POSG. A documented extension contract defines the required theoretical and test gates.
- **Evidence:** Generated real SVG curves and fixed-opponent baseline comparison from a 40-episode-per-stage curriculum smoke run. These are pipeline evidence, not convergence evidence.
- **Validation:** 29 tests passed, coverage reached 88%, Ruff check/format passed, and all four SVG outputs parsed as valid XML.

## 2026-06-21 - Prompt 7: local MCP communication

- **Request:** Add separate local cop/thief MCP tools, configurable ports, environment-token placeholder, a gatekeeper, graceful dependency/server fallback, tests, CLI smoke, and documentation without requiring cloud deployment.
- **Decision:** Pin the optional official Python MCP SDK to stable v1 (`mcp[cli]>=1.27,<2`) while keeping core installation and in-process contract smoke dependency-free.
- **Decision:** Reject privileged/absolute fields at the schema boundary; role agents receive reconstructed `LocalObservation` only.
- **Decision:** Keep auth disabled in the zero-secret default config but fail closed with constant-time comparison whenever enabled. Cloud OAuth/Bearer auth remains future work.
- **Evidence:** Separate FastMCP processes started on configured ports 8101/8102, and the official streamable-HTTP client received valid cop/thief actions. No cloud service was deployed.
- **Validation:** 39 tests passed, coverage reached 85.33%, Ruff check/format passed, and the dependency-safe CLI smoke succeeded with both configured roles.

## 2026-06-21 - Prompt 8: teacher-facing evidence and quality controls

- **Request:** Push any unpublished work and prepare genuine demo screenshots and evidence aligned with assessment feedback on configuration/security, research, version history, cost, extensibility, and quality standards.
- **Decision:** Add a deterministic `gui --demo` state plus Windows-native capture script so GUI evidence is reproducible and not fabricated.
- **Decision:** Commit rendered captures of real headless-match and MCP smoke output, while keeping generated private JSON reports ignored.
- **Decision:** Add GitHub Actions gates for locked setup, coverage, tests, Ruff lint/format, and Gitleaks history scanning.
- **Decision:** Add a teacher evidence index and an explicit cost/resource scaling model; retain honest labels for multi-seed research, CTDE, cloud, and Gmail work that is not complete.

## 2026-06-21 - Privacy and repository hygiene

- **Request:** Do not publish the student's ID, unnecessary PDFs, credentials, or other security-sensitive artifacts.
- **Decision:** Remove hardcoded identity and course-recipient data from code and documentation; load private report identity only from ignored environment variables.
- **Decision:** Use synthetic placeholders in public report examples and expand ignore rules for documents, keys, certificates, and credential exports.
- **Decision:** Audit tracked files, binary evidence, and reachable Git history rather than treating deletion from the latest commit as sufficient.

## 2026-06-21 - Prompt 8: Gmail reporting and safe dry-run

- **Request:** Generate the exact six-game JSON report, JSON/text previews, target/subject console output, and optional environment-credential Gmail delivery without committed secrets.
- **Decision:** Validate the exact payload and authoritative totals before writing; atomically write both previews after the completed match.
- **Decision:** Require config opt-in, CLI opt-in, environment credentials, and non-placeholder identity before SMTP delivery; missing values safely remain dry-run.
- **Decision:** Keep the requested course recipient and group-aware subject in non-secret YAML while keeping sender, app password, and student identity outside Git.

## 2026-06-21 - Prompt 9: final audit and bonus plan

- **Request:** Audit Exercise 06 coverage, code/config/theory/evidence/reporting/MCP/tooling/security/doc consistency and document the inter-group bonus protocol without claiming completion.
- **Decision:** Record pass/partial status in `FINAL_AUDIT.md`; keep multi-seed research, VDN/QMIX, remote MCP match, live Gmail, and bonus match as explicit limitations.
- **Decision:** Define six role-swapped bonus games, canonical JSON reconciliation, mutual agreement, screenshots, and README evidence in `BONUS_PLAN.md`.

## 2026-06-21 - Tkinter dashboard redesign

- **Request:** Improve the basic native GUI.
- **Decision:** Retain the SDK-only rendering boundary while adding a coherent dark theme, dashboard header, alternating grid, coordinates, agent depth/labels, metric cards, progress, legend, and clear action hierarchy.
- **Evidence:** Regenerated and visually inspected the real target-machine screenshot after correcting DPI/taskbar clipping.

## 2026-06-23 - Submission-readiness audit

- **Request:** Audit main and the draft MCP/evidence work, remove privacy leaks, finalize README and academic documentation, verify the assignment defaults/report contract, regenerate honest evidence, exercise MCP/Gmail safety, and run every quality gate.
- **Decision:** Use the completed local MCP/evidence lineage as the submission base because it contains the tested work absent from `main`; keep VDN/QMIX, cloud MCP, live Gmail receipt, a remote six-game MCP match, and robust held-out evaluation explicitly incomplete.
- **Decision:** Keep the course recipient only in `config/gmail.yaml`; tests and docs reference the loaded configuration rather than duplicating the address.
- **Decision:** Keep generated JSON/text previews ignored because local identity can populate them. Commit only anonymized screenshots and plots produced by reproducible commands.
- **Evidence correction:** Visual inspection found that the genuine GUI image was captured during autoplay while its caption claimed completion. The capture script now waits for the bounded six-game animation before taking the screenshot.
- **Verification in progress:** Fresh exact command results are recorded in `FINAL_AUDIT.md` and `TEACHER_EVIDENCE.md` only after execution.
