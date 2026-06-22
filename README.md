# Cops and Robbers RL

A documentation-first multi-agent reinforcement learning (MARL) project for Bar-Ilan University Vibe Coding Workshop Exercise 06. It implements a configurable grid-world match between an autonomous cop and thief, with partial observations, baseline policies, tabular IQL, a GUI, two local MCP endpoints, and one final JSON report preview.

> **Status:** the deterministic environment, baseline agents, SDK/CLI, polished Tkinter dashboard, tabular IQL training, sample plots, local cop/thief MCP services, and validated JSON/text Gmail dry-run are implemented. VDN/QMIX, cloud MCP deployment, and verified live Gmail delivery are not implemented.

## Implementation status

| Area | Status | Honest boundary |
|---|---|---|
| Game, six-sub-game runner, SDK/CLI | Implemented | Technical failures are retried and exhausted retries fail safely. |
| Random/heuristic agents and tabular IQL | Implemented | The committed training run is a pipeline smoke, not proof of convergence. |
| Tkinter GUI and reproducible captures | Implemented | Native-window rendering requires a desktop session. |
| Local cop/thief MCP services | Implemented | In-process contracts and localhost services exist; cloud deployment does not. |
| Gmail reporting | Partial | Validated JSON/text dry-run is implemented; live delivery is unverified and disabled by default. |
| VDN/QMIX and robust multi-seed evaluation | Future | Documented as extensions; no implementation or performance claim. |

## Source of truth

Requirements are interpreted in this order:

1. `ex06.pdf` - binding Exercise 06 rules.
2. `L10-MARL.pdf` - MARL theory and reference architecture.
3. `software_submission_guidelines-V3.pdf` - professional engineering standards.

These course-provided source documents are intentionally ignored and not published in the repository.

See [`docs/PRD.md`](docs/PRD.md), [`docs/PLAN.md`](docs/PLAN.md), and [`docs/TODO.md`](docs/TODO.md) before implementation.

## Implemented game contract

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
  marl/                 Tabular IQL, replay, metrics, and training
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

Install the optional official MCP SDK only when running the two network services:

```powershell
uv sync --extra dev --extra mcp --system-certs
```

`pyproject.toml`, `uv.lock`, and the default configs are present. Secrets and report identity belong only in `.env` or process environment variables; `.env` is ignored by Git. Never commit a real student ID, token, or credential. The non-secret course recipient is defined once in `config/gmail.yaml`.

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

# Open a deterministic completed-match state for demonstrations
uv run cops-and-robbers gui --demo
```

Robust multi-seed research evaluation and cloud MCP deployment remain future interfaces. The implemented CLI, GUI, and reporter call the SDK; future consumers must do the same.

Train independent Q-learners and generate JSON metrics, checkpoints, learning curves, a loss curve, and a fair fixed-opponent baseline comparison:

```powershell
# Quick 5x5 run
uv run python -m cops_and_robbers_rl.main train --episodes 200

# Curriculum: 2x2 sanity, 3x3 calibration, 4x4 partial observation, 5x5 final
uv run python -m cops_and_robbers_rl.main train --staged --episodes 200
```

Outputs are written under `results/metrics/`, `results/models/`, and `results/plots/`. The committed SVGs are a 40-episode-per-stage smoke run, not evidence of convergence or superiority.

## Local MCP communication

The dependency-safe contract smoke uses both configured role tools in process. It works even when the optional SDK is absent:

```powershell
uv run python -m cops_and_robbers_rl.main mcp-smoke
```

For a real localhost run, install the `mcp` extra and start each role in a separate terminal:

```powershell
# Terminal 1 — http://127.0.0.1:8101/mcp
uv run --extra mcp cops-mcp-cop --config config/mcp.yaml

# Terminal 2 — http://127.0.0.1:8102/mcp
uv run --extra mcp cops-mcp-thief --config config/mcp.yaml
```

Both servers expose `health` and structured `choose_action` tools. `choose_action` accepts local observation JSON only. To test token rejection, set `auth.enabled: true` in `config/mcp.yaml` and provide `MARL_MCP_TOKEN` through the environment; never put its value in YAML. `RemotePolicy` provides bounded retries and an explicitly configured local-agent fallback when the optional SDK or server is unavailable.

## Test and quality gates

```powershell
uv run pytest
uv run pytest --cov=cops_and_robbers_rl --cov-report=term-missing --cov-fail-under=85
uv run ruff check .
uv run ruff format --check .
```

Required gates are deterministic unit and integration tests, at least 85% coverage for implemented code, zero Ruff violations, no committed secrets, and reproducibility from a fixed seed. See the [test strategy](docs/PLAN.md#test-strategy).

GitHub Actions enforces the locked install, coverage threshold, test suite, Ruff lint/format, and a history-wide Gitleaks credential scan on every push and pull request.

## Configuration

Runtime settings are versioned in YAML and validated before use:

| File | Purpose |
|---|---|
| `config/default_game.yaml` | Grid size, six sub-games, 25 moves, barriers, scoring, observation radius, seed |
| `config/mcp.yaml` | Cop/thief hosts and distinct ports, timeout, retry, token environment-variable name |
| `config/gmail.yaml` | Course recipient, group-aware subject, dry-run default, SMTP environment-variable names |

The SDK validates ranges and rejects unknown or unsafe game values before a match starts. Training episode count and staged mode are currently CLI options; a dedicated training YAML is future work.

## GUI

The Tkinter GUI is a read-only dashboard over SDK snapshots. It uses a themed tactical board, coordinate labels, role-colored score tiles, move progress, a six-game series tracker, compact legend, and a clear primary action while preserving labeled cop (`C`), thief (`T`), and barriers (`B`). **Animate match** plays all six games move-by-move without blocking Tkinter; Space pauses or resumes. Other controls reset, advance one move, finish the current sub-game, and export the canvas as color PostScript under `results/screenshots/`.

**Animate match** is the non-blocking playback path; the single-sub-game and immediate-completion controls remain available for fast inspection. Learned policies can later be supplied through the same `BaseAgent` interface without changing the renderer. Automated tests cover the display-independent interactive session; opening a native window requires a desktop with Tk 8.6.

[Real GUI and command demo evidence](docs/TEACHER_EVIDENCE.md) is captured from the target machine and can be reproduced with the scripts under `scripts/`.

## Reports and Gmail safety

After exactly six valid sub-games, the reporter validates the assignment schema and authoritative totals, prints the target email and group-aware subject, and atomically writes both previews:

```text
results/report_email_preview.json
results/report_email_preview.txt
```

Default `config/gmail.yaml` contains the single course-recipient definition, uses a group-aware subject, and keeps `dry_run: true`. The JSON file is the exact report body; the text file shows `To`, `Subject`, and the same body.

Real Gmail SMTP delivery requires all three gates: set `dry_run: false` in a private/local config, pass `--send-email`, and provide `GMAIL_SENDER` plus `GMAIL_APP_PASSWORD` in the environment. Missing credentials or placeholder student identity safely falls back to previews without crashing the match.

```powershell
# Safe default: no network send
uv run cops-and-robbers play --output results/report_email_preview.json

# Explicit opt-in; still requires dry_run: false and environment credentials
uv run cops-and-robbers play --send-email --gmail-config config/gmail.yaml
```

Tokens, OAuth client secrets, app passwords, `.env`, student IDs, and generated private reports must not be committed. See [`docs/PRD_gmail_reporting.md`](docs/PRD_gmail_reporting.md).

## Troubleshooting

| Symptom | Check |
|---|---|
| `uv` is not recognized | Install `uv`, open a new terminal, and verify `uv --version`. |
| `pyproject.toml` is missing | The checkout is incomplete or the command is running outside the repository root. |
| Repeated runs differ | Use the same config and `random_seed`; record package and config versions. |
| An agent sees the full board | Treat as a CTDE leakage defect; execution accepts only local observation/history. |
| MCP connection fails | Confirm both services use distinct configured ports, valid token, and localhost URLs. |
| `install the optional 'mcp' extra` | Run `uv sync --extra mcp --system-certs`, or keep using the in-process smoke fallback. |
| Match has fewer than six results | Technical failures do not count; rerun the failed sub-game before reporting. |
| Gmail is not configured | Keep `dry_run: true`; inspect the preview JSON instead of sending. |
| GUI cannot open / `$DISPLAY` error | Run the command on a desktop session with Tkinter available; CI tests only GUI-independent logic. |
| GUI appears briefly busy | `Run sub-game` and `Run full match` execute synchronously; use `Step` for visual inspection. Training must remain headless. |

## Evidence

- [Teacher evidence index](docs/TEACHER_EVIDENCE.md) with exact reproduction commands and expected outputs
- [Native GUI screenshot](assets/evidence/gui-full-match.png)
- [Headless six-game screenshot](assets/evidence/headless-match.png)
- [Local MCP smoke screenshot](assets/evidence/mcp-smoke.png)
- [IQL learning, loss, and baseline plots](results/plots/)
- Generated dry-run files: `results/report_email_preview.json` and `results/report_email_preview.txt` (ignored because local identity may be configured)

## Final submission checklist

- [x] Root README and mandatory PRD/PLAN/TODO documents are present.
- [x] Default YAML encodes the 5x5, 25-move, six-game, five-barrier, 20/10/5/5 contract.
- [x] CLI, GUI, IQL training, local MCP smoke, and dry-run reporting commands are documented.
- [x] Ruff, tests, coverage >=85%, and CI/secret scanning are configured.
- [x] Public files contain placeholders only for private identity and credentials.
- [ ] Add private student identity only to the Moodle PDF/local environment.
- [ ] Optionally run held-out multi-seed evaluation; do not overstate the existing smoke result.
- [ ] VDN/QMIX, cloud MCP, live Gmail receipt, and the bonus match remain future work.

## Contributing

Follow docs-first development and TDD: update an approved PRD/PLAN/TODO item, write a failing test, implement the smallest change, then refactor. Business logic must be exposed through the SDK. Keep code files at or below 150 logical code lines where practical, use type hints and docstrings, and never bypass the central external-API gatekeeper.

## Project identity and license

- Repository: <https://github.com/BenEli1/CopsAndRobbersRL>
- Student identity: private runtime configuration; intentionally omitted from Git
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
- [Teacher evidence index](docs/TEACHER_EVIDENCE.md)
- [Cost and resource awareness](docs/COST_AND_RESOURCES.md)
- [Final submission audit](docs/FINAL_AUDIT.md)
- [Inter-group bonus plan](docs/BONUS_PLAN.md)
