# Phased TODO and Definition of Done

Status legend: `[ ]` not started, `[~]` in progress, `[x]` complete, `[!]` blocked. Documentation completion does not imply implementation completion.

## P0 - Documentation gate

- [x] **P0.1** Review the three source PDFs and establish precedence. **DoD:** README and PRDs name the sources and no requirement contradicts the exercise PDF.
- [x] **P0.2** Define product, formal model, architecture, risks, and measurable criteria. **DoD:** all required Markdown files exist, cross-link correctly, and distinguish POSG from cooperative Dec-POMDP assumptions.
- [x] **P0.3** Define environment collision/illegal-action semantics as a proposed ADR. **DoD:** edge cases are enumerated; final approval is still required before code.
- [ ] **P0.4** Human approval of documentation. **Owner:** student. **DoD:** ambiguities (group code/members and ADR-003) are resolved and implementation is explicitly authorized.

## P1 - Project foundation

- [x] **P1.1** Create `pyproject.toml` and package skeleton using `uv`. **DoD:** `uv sync --extra dev` succeeds from a clean checkout; no `requirements.txt`; package version starts at `1.00`.
- [~] **P1.2** Add config schemas and example files. **DoD:** default game schema/config is complete and strictly validated; training/MCP/Gmail configs remain deferred to their phases.
- [x] **P1.3** Establish CI/quality tooling. **DoD:** pytest, coverage >=85%, Ruff check/format, and secret scanning run in CI.
- [~] **P1.4** Add `.env-example`, ignore rules, paths, structured logging, and version service. **DoD:** environment placeholders and ignore rules exist; structured redacted logging and secret-scan fixtures remain pending.

## P2 - Deterministic environment (TDD)

- [x] **P2.1** Implement typed actions, state, configs, and results. **DoD:** immutable typed models and requested boundary tests pass.
- [x] **P2.2** Implement reset and spawn invariants. **DoD:** seeded engines create legal distinct positions and fixed invalid positions are rejected.
- [x] **P2.3** Implement action validation, barriers, movement, capture, and timeout. **DoD:** requested movement, capture, barrier, blocking, limit, and timeout tests pass deterministically.
- [x] **P2.4** Implement local observation and training-only global state. **DoD:** radius/masking, typed debug/training access, and execution-agent local-observation enforcement are tested.
- [x] **P2.5** Implement scoring and six-sub-game orchestration. **DoD:** authoritative scoring, six valid results, and bounded retry of technical agent failures are tested.

## P3 - SDK and baseline agents

- [x] **P3.1** Implement the public SDK facade and DTOs. **DoD:** all deterministic-engine workflows used to date are callable without importing internal modules.
- [x] **P3.2** Implement random and heuristic policies. **DoD:** seeded local random policies are reproducible; heuristic cop pursues and heuristic thief evades without privileged state.
- [x] **P3.3** Add headless CLI through SDK. **DoD:** the documented command runs a default match and emits validated report-ready JSON to stdout.
- [ ] **P3.4** Establish baseline evaluation. **DoD:** multiple fixed seeds produce recorded win/capture/survival metrics with configs and uncertainty summary.

## P4 - IQL baseline

- [x] **P4.1** Specify observation/action encodings and replay schema. **DoD:** local encoding, movement masking, terminal flags, seeded replay, and centralized trace boundaries are implemented and tested.
- [x] **P4.2** Implement independent learners. **DoD:** tabular Bellman update has an exact unit test and smoke training populates both Q-tables.
- [~] **P4.3** Train and evaluate IQL. **DoD:** JSON checkpoints, required plots, staged training, fixed-opponent comparisons, and a small held-out seed diagnostic run; robust research-grade evaluation remains pending.
- [~] **P4.4** Analyze non-stationarity. **DoD:** limitations, non-convergence warning, and small held-out diagnostic are recorded; broader instability evidence remains pending.

## P5 - CTDE/value factorization

- [ ] **P5.1** Freeze the competitive training formulation. **DoD:** document rewards/mixer objective and why it is a simplified empirical CTDE comparison.
- [~] **P5.2** Implement centralized replay and VDN training. **DoD:** a bounded centralized training trace stores global/joint transitions while exported IQL policies remain local-only; an actual VDN mixer is not implemented.
- [ ] **P5.3** Add CTDE leakage and IGM tests. **DoD:** execution boundary rejects global state; VDN additivity/argmax consistency is tested on controlled tensors.
- [ ] **P5.4** Compare VDN with IQL/baselines. **DoD:** same held-out seeds and metrics; curves and limitations recorded.
- [ ] **P5.5 Optional** Add QMIX. **DoD:** monotonic mixer gradients are non-negative, IGM test passes, and comparison is fair. Remains optional if schedule/risk gate fails.
- [ ] **P5.6 Optional** Add LSTM/GRU memory. **DoD:** recurrent state reset/masking is tested and ablation shows whether memory helps partial observability.

## P6 - GUI

- [x] **P6.1** Build SDK-backed GUI view model and renderer. **DoD:** Tkinter imports only the public SDK session/DTO and contains no transition or scoring rules.
- [x] **P6.2** Display required state and controls. **DoD:** grid, labeled agents/barriers, sub-game, move, scores, winner, reset/step/run controls are visible beyond color alone.
- [x] **P6.3** Add screenshot workflow. **DoD:** PostScript export and a reproducible native Windows PNG capture are implemented; real GUI evidence is linked from the teacher index.
- [ ] **P6.4** Test responsiveness. **DoD:** match/training work does not block the event loop and close/pause behavior is covered.

## P7 - MCP communication

- [x] **P7.1** Implement schemas, auth, health, and action contracts. **DoD:** local-only observation schemas, structured actions, health metadata, and invalid-token rejection are tested; services emit no application observation/token logs.
- [~] **P7.2** Implement separate cop/thief localhost services. **DoD:** distinct FastMCP processes/ports answered real streamable-HTTP calls; authenticated network evidence remains pending.
- [~] **P7.3** Implement SDK remote policy adapter through gatekeeper. **DoD:** timeout, bounded retry, typed failure, and explicit local fallback are tested; queue/backpressure remain pending.
- [ ] **P7.4** Run local end-to-end match. **DoD:** six valid sub-games complete using both services; technical failure recovery evidence is retained.
- [ ] **P7.5 Optional** Deploy to cloud. **DoD:** TLS, secret manager, health probes, revocation, restricted access, and sanitized deployment guide are verified. Otherwise document as future work.

## P8 - Reporting and Gmail

- [x] **P8.1** Implement exact report schema. **DoD:** positive/negative schema tests cover six games, totals, identities, ISO timestamps, moves, winners, and timezone.
- [x] **P8.2** Implement canonical dry-run output. **DoD:** JSON and text previews are atomically written only after six valid games validate.
- [~] **P8.3** Implement Gmail adapter through gatekeeper. **DoD:** optional Gmail SMTP is double-gated and environment-only; delivery ledger/idempotency and bounded provider retry remain pending.
- [ ] **P8.4 Optional** Verify one live email. **DoD:** explicit operator consent/config, successful provider receipt, redacted audit log, and no credential artifact.

## P9 - Submission and final-project evidence

- [ ] **P9.1** Complete experiments and plots. **DoD:** baselines, IQL, and completed CTDE methods use documented seeds/configs and honest statistical summaries; current IQL evidence remains smoke plus small diagnostic only.
- [x] **P9.2** Update `SUMMARY_REPORT.md`. **DoD:** generated evidence is linked and every unsupported feature is explicitly marked not implemented.
- [~] **P9.3** Final security and quality audit. **DoD:** 49 local tests, 89.26% coverage, lint, format, headless match, MCP smoke, previews, links, and privacy scans pass; remote CI confirmation remains before tagging.
- [x] **P9.4** Documentation audit. **DoD:** `FINAL_AUDIT.md` checks README, code, evidence, and non-claims; PROMPT_LOG is current.
- [ ] **P9.5** Tag submission version. **DoD:** meaningful Git history, chosen license, credits, release notes, and immutable version tag.

## P10 - Optional bonus game

- [ ] **P10.1** Agree protocol/config with another group. **DoD:** both repos, group identities, service contracts, authentication, and scoring are mutually confirmed.
- [ ] **P10.2** Run six role-swapped games. **DoD:** Group 1 is cop in 1-3, Group 2 in 4-6; both produce identical signed/canonical results.
- [ ] **P10.3** Submit bonus evidence. **DoD:** each group sends one mutually agreed report and documents opponent, scores, claims, repositories, and screenshots.
