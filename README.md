# Cops and Robbers RL

A documentation-first multi-agent reinforcement learning (MARL) project for Bar-Ilan University Vibe Coding Workshop Exercise 06. The planned product is a configurable grid-world match between an autonomous cop and thief, with partial observations, baseline policies, CTDE-inspired learning, a GUI, two MCP endpoints, and one final JSON email report.

> **Status:** the deterministic environment, baseline agents, six-game runner, SDK/CLI, Tkinter GUI, tabular IQL training, sample analysis plots, and JSON report preview are implemented. VDN/QMIX, MCP, and live Gmail delivery are not implemented.

## Source of truth

Requirements are interpreted in this order:

1. [`ex06.pdf`](ex06.pdf) - binding Exercise 06 rules.
2. [`L10-MARL.pdf`](L10-MARL.pdf) - MARL theory and reference architecture.
3. [`software_submission_guidelines-V3.pdf`](software_submission_guidelines-V3.pdf) - professional engineering standards.

See [`docs/PRD.md`](docs/PRD.md), [`docs/PLAN.md`](docs/PLAN.md), and [`docs/TODO.md`](docs/TODO.md) before implementation.

## Planned capabilities

- One match contains exactly six valid sub-games on a default `5 x 5` grid.
- A sub-game ends on capture or after 25 completed moves.
- The cop may place up to five blocking barriers; placing one consumes its action.
- Both agents execute from local observations. Global state is restricted to centralized training, evaluation instrumentation, and rendering.
- Seeded random and local-observation heuristic agents plus tabular IQL provide implemented baselines. Competitive VDN/QMIX remain explicitly scoped extensions.
- A GUI renders the grid, agents, barriers, sub-game, step, score, and winner.
- Separate cop and thief MCP services run locally on different ports before any cloud deployment.
- After six valid sub-games, the reporter creates one JSON email body. Dry-run is mandatory; live Gmail delivery is opt-in.

## Repository layout

```text
config/                 Versioned YAML configuration
docs/                   Requirements, architecture, tasks, and reports
src/cops_and_robbers_rl/
  sdk/                  Sole public entry point for business workflows
  environment/          Deterministic rules and observations
  agents/               Random, heuristic, and learned policies
  marl/                 IQL, replay, VDN, metrics, training
  gui/                   Rendering only; calls the SDK
  mcp/                   Two agent service adapters
  reporting/             Match schema and Gmail/dry-run adapters
tests/                   Unit and integration tests
results/                 Generated reports, plots, and screenshots
assets/                  Static documentation assets
```

## Installation

Prerequisites: Python 3.11+, Git, and [`uv`](https://docs.astral.sh/uv/). `uv` is the only supported package manager; do not use `pip` or add `requirements.txt`.

```powershell
git clone https://github.com/BenEli1/CopsAndRobbersRL.git
cd CopsAndRobbersRL
uv sync --extra dev
Copy-Item .env-example .env
```

`pyproject.toml`, `uv.lock`, and the default game config are present. Secrets belong only in a future `.env`, which is ignored by Git.

## Run

```powershell
# Available: headless six-sub-game match
uv run cops-and-robbers play --config config/default_game.yaml

# Choose seeded baseline policies and an output path
uv run cops-and-robbers play `
  --cop-agent heuristic `
  --thief-agent random `
  --seed 42 `
  --output results/report_email_preview.json
```

Launch the native GUI with heuristic agents:

```powershell
uv run python -m cops_and_robbers_rl.main gui

# Equivalent installed command with an explicit configuration
uv run cops-and-robbers gui --config config/default_game.yaml
```

Robust multi-seed research evaluation, MCP service, and Gmail commands remain future interfaces. The implemented CLI and GUI call the SDK; future consumers must do the same.

Train independent Q-learners and generate JSON metrics, checkpoints, learning curves, a loss curve, and a fair fixed-opponent baseline comparison:

```powershell
# Quick 5x5 run
uv run python -m cops_and_robbers_rl.main train --episodes 200

# Curriculum: 2x2 sanity, 3x3 calibration, 4x4 partial observation, 5x5 final
uv run python -m cops_and_robbers_rl.main train --staged --episodes 200
```

Outputs are written under `results/metrics/`, `results/models/`, and `results/plots/`. The committed SVGs are a 40-episode-per-stage smoke run, not evidence of convergence or superiority.

## Test and quality gates

```powershell
uv run pytest
uv run pytest --cov=cops_and_robbers_rl --cov-report=term-missing --cov-fail-under=85
uv run ruff check .
uv run ruff format --check .
```

Required gates are deterministic unit and integration tests, at least 85% coverage for implemented code, zero Ruff violations, no committed secrets, and reproducibility from a fixed seed. See the [test strategy](docs/PLAN.md#test-strategy).

## Configuration

Runtime values must never be hardcoded. Planned files are:

| File | Purpose |
|---|---|
| `config/default_game.yaml` | Grid size, six sub-games, 25 moves, barriers, scoring, observation radius, seed |
| `config/training.yaml` | Algorithm, episodes, discount, optimizer, replay, exploration, evaluation seeds |
| `config/mcp.yaml` | Cop/thief hosts and distinct ports, timeout, retry, token environment-variable name |
| `config/gmail.example.yaml` | Recipient, subject, dry-run, credential environment-variable names |

The SDK will validate ranges and reject unknown or unsafe values before a match starts. Full contracts appear in the mechanism PRDs.

## GUI

The implemented Tkinter GUI is a read-only renderer over SDK snapshots. It shows the configured grid, labeled cop (`C`), thief (`T`), barriers (`B`), current sub-game, move count, sub-game and cumulative scores, and terminal winner. Controls reset or advance one move, finish the current sub-game, run all six sub-games, and export the canvas as a color PostScript image under `results/screenshots/` by default.

The run buttons intentionally complete immediately rather than animate. Learned policies can later be supplied through the same `BaseAgent` interface without changing the renderer. Automated tests cover the display-independent interactive session; opening a native window requires a desktop with Tk 8.6.

[GUI screenshot placeholder](assets/gui/README.md) — replace with a real target-machine capture before submission.

## Reports and Gmail safety

The implemented CLI is dry-run only. After six valid sub-games, one report-ready JSON body is written atomically to:

```text
results/report_email_preview.json
```

Live delivery requires explicit configuration and credentials supplied through environment variables. Tokens, OAuth client secrets, app passwords, `.env`, and generated private reports must not be committed. See [`docs/PRD_gmail_reporting.md`](docs/PRD_gmail_reporting.md).

## Troubleshooting

| Symptom | Check |
|---|---|
| `uv` is not recognized | Install `uv`, open a new terminal, and verify `uv --version`. |
| `pyproject.toml` is missing | The checkout is incomplete or the command is running outside the repository root. |
| Repeated runs differ | Use the same config and `random_seed`; record package and config versions. |
| An agent sees the full board | Treat as a CTDE leakage defect; execution accepts only local observation/history. |
| MCP connection fails | Confirm both services use distinct configured ports, valid token, and localhost URLs. |
| Match has fewer than six results | Technical failures do not count; rerun the failed sub-game before reporting. |
| Gmail is not configured | Keep `dry_run: true`; inspect the preview JSON instead of sending. |
| GUI cannot open / `$DISPLAY` error | Run the command on a desktop session with Tkinter available; CI tests only GUI-independent logic. |
| GUI appears briefly busy | `Run sub-game` and `Run full match` execute synchronously; use `Step` for visual inspection. Training must remain headless. |

## Contributing

Follow docs-first development and TDD: update an approved PRD/PLAN/TODO item, write a failing test, implement the smallest change, then refactor. Business logic must be exposed through the SDK. Keep code files at or below 150 logical code lines where practical, use type hints and docstrings, and never bypass the central external-API gatekeeper.

## Project identity and license

- Repository: <https://github.com/BenEli1/CopsAndRobbersRL>
- Student A: Ben Eli (`000000000`)
- Course materials: copyright Dr. Yoram Segal; included as assignment sources, not relicensed.
- Project code license: **not yet selected**. Add a `LICENSE` before public release or reuse.

## Documentation index

- [Product requirements](docs/PRD.md)
- [Architecture and ADRs](docs/PLAN.md)
- [Phased tasks and Definition of Done](docs/TODO.md)
- [Game environment PRD](docs/PRD_game_environment.md)
- [MARL algorithm PRD](docs/PRD_marl_algorithm.md)
- [MCP communication PRD](docs/PRD_mcp_communication.md)
- [Gmail reporting PRD](docs/PRD_gmail_reporting.md)
- [Evidence-based summary report](docs/SUMMARY_REPORT.md)
- [Prompt and decision log](docs/PROMPT_LOG.md)
