# Product Requirements Document

## 1. Product definition

Cops and Robbers RL is a local-first Python research and demonstration system for a competitive two-agent pursuit-evasion game. It must produce a reproducible six-sub-game match, compare baseline and learned policies under partial observability, visualize play, expose agent decisions through independent MCP services, and generate one final JSON report.

Although the lecture introduces cooperative Dec-POMDP methods, this cop-versus-thief game has separate, opposing objectives and is therefore more precisely a partially observable stochastic game (POSG). Dec-POMDP notation remains useful for documenting state, joint actions, observations, transitions, and CTDE data boundaries; claims about cooperative VDN/QMIX must be scoped and evaluated honestly.

## 2. Users and needs

| User | Need |
|---|---|
| Student developer | A modular, testable submission with reproducible experiments and no hidden configuration. |
| Course grader | One-command setup, traceable rules, measurable evidence, honest completion status, and clear theory-to-code mapping. |
| Research observer | Learning curves, baseline comparisons, seeds/configs, limitations, and inspectable match records. |
| Demonstration operator | A stable GUI and local MCP workflow that can recover from service failures. |
| Future project team | Extension points for larger grids, memory, richer CTDE algorithms, cloud services, and bonus games. |

## 3. Goals and success metrics

1. **Rule correctness:** 100% of specified rule/edge-case tests pass for capture, timeout, barriers, scoring, and six-game aggregation.
2. **Reproducibility:** two headless runs with the same seed, config, and policies produce identical transition logs and reports.
3. **Execution privacy:** automated tests prove policy inputs contain local observations/history only; global state is inaccessible to execution policy APIs.
4. **Engineering quality:** `uv sync` succeeds; tests pass with at least 85% implemented-code coverage; Ruff reports zero violations.
5. **Comparative evidence:** IQL and the scoped CTDE candidate are evaluated against random and heuristic baselines on the same held-out seeds, with confidence-aware aggregate metrics.
6. **Operational completeness:** a local six-game run can use two independently started MCP services and produce one schema-valid dry-run report.
7. **Honesty:** documents and UI distinguish planned, implemented, experimentally validated, and optional features.

## 4. Functional requirements

### FR-1 Configuration

The system shall load versioned YAML through the SDK and validate `grid_size`, `max_moves`, `num_games`, `max_barriers`, four scoring values, `observation_radius`, `random_seed`, training hyperparameters, and MCP/Gmail settings. Binding defaults are `5 x 5`, 25, 6, 5, and scores `20/10/5/5`. Private student identity is supplied only through ignored environment variables.

### FR-2 Environment and match lifecycle

The environment shall reset to legal distinct positions; accept one action per agent per step; apply deterministic, documented resolution order; block illegal movement; detect capture; stop at the move limit; retry technical failures; and aggregate exactly six valid sub-games. Detailed semantics are in [`PRD_game_environment.md`](PRD_game_environment.md).

### FR-3 Policies and observations

The system shall provide random, heuristic cop, heuristic thief, and trainable policy interfaces. Each execution policy receives only its local observation and permitted history. A training-only interface may receive global state and joint transitions.

### FR-4 MARL training and evaluation

The system shall implement IQL as a baseline, then a deliberately scoped CTDE/value-factorization comparison (VDN first). It shall record per-agent returns, wins, capture time, survival rate, loss, exploration, and held-out evaluation results. QMIX and recurrent memory are optional until explicitly accepted.

### FR-5 SDK

All business workflows shall be callable through one public SDK facade. CLI, GUI, MCP adapters, and reporting adapters shall delegate to it and shall not reproduce rules, scoring, or report aggregation.

### FR-6 GUI

The GUI shall display the grid, cop, thief, barriers, sub-game, completed moves, current/cumulative score, terminal winner, and controls. It shall save reproducible screenshots and remain separate from the game engine.

### FR-7 MCP communication

The system shall expose independent cop and thief services, first on localhost at distinct configurable ports. Requests shall be authenticated by revocable bearer tokens, validated, timed out, rate-limited through a shared gatekeeper, and logged without secrets. Failure modes are defined in [`PRD_mcp_communication.md`](PRD_mcp_communication.md).

### FR-8 Final report

After exactly six valid sub-games, the system shall generate one schema-valid JSON email body for an explicitly configured course recipient. Dry-run shall write `results/report_email_preview.json`; live sending is disabled by default and must never expose credentials or identity data.

## 5. Non-functional requirements

- **Correctness:** deterministic core transitions; explicit invariants; defensive schema validation.
- **Maintainability:** OOP with single responsibilities, dependency inversion, no duplicated business logic, and roughly 150 logical code lines per code file.
- **Testability:** injected clock, RNG, policies, transports, and mail sender; unit and integration seams.
- **Performance:** a headless default match completes without artificial delay; evaluation supports batching or multiprocessing only after deterministic correctness.
- **Reliability:** invalid configs fail before execution; MCP retries are bounded; technical failures never become scored games.
- **Security:** no embedded credentials; least privilege; token redaction; Git ignore and secret scanning.
- **Portability:** Python 3.11+ and `uv`; Windows is a first-class local environment; relative project paths only.
- **Usability:** actionable errors, documented commands, accessible GUI colors plus labels/shapes, and no silent fallbacks.
- **Observability:** structured logs contain match/sub-game/request correlation IDs without private tokens.

## 6. Acceptance criteria

| ID | Given / when / then evidence |
|---|---|
| AC-1 | Given the default config, when a match completes, then it contains six valid ordered sub-games and at most 25 completed moves each. |
| AC-2 | Given identical seed/config/policies, when two headless matches run, then their state/action/outcome traces match byte-for-byte after excluding timestamps. |
| AC-3 | Given both agents enter the same cell under the approved resolution rule, then the cop wins and scores are `cop=20`, `thief=5`. |
| AC-4 | Given no capture after move 25, then the thief wins and scores are `cop=5`, `thief=10`. |
| AC-5 | Given five placed barriers, when the cop requests another, then the documented illegal-action policy applies and no sixth barrier appears. |
| AC-6 | Given a runtime policy call, then global coordinates outside the observation radius are absent from its input. |
| AC-7 | Given a training batch, then global state is available only inside the trainer/mixer boundary and never serialized to execution requests. |
| AC-8 | Given local cop and thief services, then both answer authenticated health/action requests on distinct configured ports; invalid tokens receive no policy output. |
| AC-9 | Given one transient MCP failure, then bounded recovery follows policy; given exhaustion, the sub-game is a technical failure and is retried rather than scored. |
| AC-10 | Given six valid sub-games in dry-run mode, then exactly one preview file matches the documented JSON schema and contains Asia/Jerusalem timestamps. |
| AC-11 | Given an incomplete or five-game match, then reporting refuses to send or finalize. |
| AC-12 | Given a clean checkout after implementation, then `uv sync`, pytest coverage gate, Ruff check, and a headless smoke match all pass. |

## 7. Assumptions, dependencies, and constraints

- The exercise PDF overrides the lecture and software guidelines on conflict.
- Student names, IDs, group metadata, and any Student B/C identities are private runtime configuration and must be confirmed outside source control before live reporting.
- Local model training is required; cloud hosting is a later deployment step.
- Internet, Gmail, and cloud credentials may be unavailable during grading, so deterministic local and dry-run paths are mandatory.
- VDN/QMIX were designed for cooperative team reward. Applying value factorization to a competitive two-agent POSG requires a clearly stated training formulation; no cooperative-optimality claim is implied.

## 8. Out of scope for version 1

- Real-world robotics, continuous movement, hidden human intervention, and more than one cop/thief.
- Guaranteed Nash-equilibrium convergence.
- Mandatory OLoRA, large pretrained models, QMIX, QPLEX, MAPPO, LSTM, or GRU.
- Production cloud SLA, public unauthenticated endpoints, and committed Gmail credentials.
- Bonus inter-group competition until the core acceptance criteria pass.

## 9. Milestones

1. Documentation approval.
2. Project skeleton and deterministic engine.
3. SDK, random/heuristic baselines, and match reporting objects.
4. IQL baseline and evaluation harness.
5. VDN CTDE comparison and leakage tests.
6. GUI and screenshot evidence.
7. Local two-service MCP integration.
8. Gmail dry-run, optional live send, final analysis, and submission audit.

## 10. Risks

| Risk | Impact | Mitigation / evidence |
|---|---|---|
| Competitive POSG mismatched with cooperative VDN/QMIX assumptions | Invalid algorithm claims | Treat POSG as primary model; document training payoff; compare empirically; label simplified CTDE. |
| Ambiguous simultaneous movement/crossing | Non-reproducible wins | Freeze resolution order in the environment PRD and unit-test every collision case before coding. |
| Global-state leakage | Invalid CTDE evaluation | Separate types/interfaces and add negative tests at SDK/MCP boundaries. |
| Small-grid overfitting | Misleading curves | Held-out seeds, multiple grid sizes, baseline comparison, and uncertainty summaries. |
| MCP/cloud instability | Failed match | Local-first path, bounded retry, health checks, technical-failure replay, no silent action substitution. |
| Credential leakage | Security/submission failure | Environment variables, example files, ignore rules, redaction, secret scan. |
| Schedule pressure | Pretend-complete features | Phase gates; optional features remain unchecked and described as future work. |

## 11. Future and bonus extensions

The final project can add multiple cops/thieves, procedurally generated maps, recurrent policies, QMIX/QPLEX/MAPPO comparisons, curriculum learning, experiment tracking, and containerized authenticated cloud deployment.

The optional bonus game uses six inter-group sub-games: Group 1 is cop for games 1-3 and Group 2 for games 4-6. Both repositories and teams must be named, both teams must send mutually agreed equivalent reports, and the README must record opponent, final score, bonus claim, and screenshots. It is blocked until core reporting and protocol compatibility are stable.
