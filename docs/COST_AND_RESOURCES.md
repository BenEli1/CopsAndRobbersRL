# Cost and Resource Awareness

## Current implementation

The implemented project makes no paid LLM, cloud, or Gmail API calls. The deterministic engine, tabular IQL trainer, Tkinter GUI, and MCP services run locally, so direct provider cost is **$0**. The real costs are developer time, CPU time, memory, electricity, and CI minutes. This statement applies only to the current local implementation; it is not a claim that future cloud deployment is free.

## Scaling model

| Workflow | Main scaling driver | Current bounded default |
|---|---|---|
| Match | `num_games * max_moves` environment steps | `6 * 25 = 150` maximum steps |
| Tabular IQL training | episodes, steps per episode, replay updates | Explicit CLI episode limit; CPU-only |
| Q-table storage | distinct encoded local observations times legal actions | Sparse dictionaries; no GPU/model service |
| MCP inference | requests times retry attempts | Two localhost services, 5-second timeout, 2 attempts |
| CI | commits/PRs times test runtime | One test/lint job plus one secret scan |

The local observation encoding is bounded by the configured radius, while global state is retained only in the centralized training trace. Increasing grid size, observation radius, episode count, seed count, or replay capacity increases compute and memory. Multi-seed research is intentionally a scheduled batch, not an unbounded default.

## Measurement protocol

For reportable experiments, record wall-clock duration, episode and environment-step counts, peak process memory, machine/CPU, seed list, configuration, commit SHA, and output hashes. Compare algorithms on the same seed and evaluation budgets. A result without its resource budget is not a fair comparison.

Recommended local commands:

```powershell
Measure-Command { uv run cops-and-robbers play --seed 42 }
Measure-Command { uv run cops-and-robbers train --episodes 200 }
```

## Future external-service budget

Before cloud or LLM-backed policies are enabled, define a monthly ceiling and enforce per-match request, token, timeout, and retry limits. Estimate usage with:

```text
monthly cost = matches/month * calls/match * average billable units/call * provider rate
```

Provider rates are intentionally not hardcoded because they change. Record the dated pricing source and measured average request size when selecting a provider. Keep localhost/dry-run modes as the default, add alerts at 50%, 80%, and 100% of budget, and fail closed at the hard cap. Gmail delivery remains one final report per completed match, never one message per step.

## Design decisions that control cost

- Deterministic and heuristic baselines require no inference service.
- Tabular IQL is CPU-only and inspectable; deep models are deferred until justified by evidence.
- Local MCP is validated before any cloud deployment.
- Bounded retries prevent technical failures from multiplying requests indefinitely.
- Fixed seeds and committed configs reduce wasteful reruns.
- CI uses locked dependencies and short deterministic tests.
