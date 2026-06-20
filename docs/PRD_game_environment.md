# PRD - Game Environment

## 1. Purpose and scope

Define a deterministic, configurable, UI-independent grid environment for one cop and one thief. It owns rules, state transitions, observations, terminal detection, and scores; it does not own training, rendering, networking, or email.

## 2. Inputs, outputs, and setup

- **Setup:** validated game config, sub-game ID, random seed, optional fixed spawn positions.
- **Step input:** one `CopAction` and one `ThiefAction`, both selected from the same pre-step local observations.
- **Step output:** immutable next state, per-agent local observations, per-agent rewards, legality metadata, completed-move count, and terminal reason.
- **Match output:** six `SubGameResult` objects with authoritative winners/scores and totals.

## 3. Configuration contract

```yaml
schema_version: "1.00"
grid_size: [5, 5]
max_moves: 25
num_games: 6
max_barriers: 5
observation_radius: 1
random_seed: 42
allow_stay: true
illegal_action_policy: stay
crossing_counts_as_capture: true
scoring:
  cop_win: 20
  thief_win: 10
  cop_loss: 5
  thief_loss: 5
```

Rows/columns must be positive and capable of holding two agents; `max_moves` and `num_games` are positive; `max_barriers >= 0`; radius is non-negative; all score values are non-negative. The submission profile fixes `num_games=6`, while tests may use smaller values only as fixtures.

## 4. State and invariants

Global state contains grid dimensions, cop/thief coordinates, barrier set, barriers remaining, completed moves, sub-game ID, seed/RNG state, terminal status, winner, and scores. At every observable boundary:

- agent positions are in bounds and not on barriers;
- pre-terminal spawn positions differ;
- barriers are unique and in bounds;
- placed barriers never exceed `max_barriers`;
- completed moves are in `0..max_moves` and increase once per resolved joint step;
- after terminal state, `step` rejects mutation;
- winner, terminal reason, and score tuple agree.

## 5. Actions

Both agents support `UP`, `DOWN`, `LEFT`, `RIGHT`, and (when enabled) `STAY`. The cop additionally supports `PLACE_BARRIER(target_cell)`. A barrier placement consumes the cop action and does not move the cop.

An action is illegal if malformed, disabled, out of bounds, enters a barrier, places outside the grid, places on either agent, duplicates a barrier, targets a non-adjacent cell (chosen v1 rule), or exceeds the barrier budget. Under the submission default, illegal actions deterministically normalize to `STAY` and return an `illegal_action` reason. Configuration may choose `error` for development tests, but never a silent random substitute.

## 6. Joint-step resolution

This section freezes the proposed ADR-003 behavior once approved:

1. Snapshot the pre-step state and generate both local observations.
2. Collect both action intents without showing either current intent to the other agent.
3. Validate actions against the pre-step state.
4. If legal, place the cop barrier; barrier placement consumes the cop action. A barrier cannot target the thief's current or intended destination.
5. Compute both movement destinations from the same pre-step state. Invalid destinations become current positions.
6. Apply both destinations simultaneously.
7. Capture occurs if final positions match **or** the agents directly swap their starting positions when `crossing_counts_as_capture=true`.
8. Increment the completed-move counter exactly once.
9. If captured, terminate with a cop win. Otherwise, if completed moves equals `max_moves`, terminate with a thief win.
10. Produce rewards, local observations, and immutable result metadata.

This deterministic resolution avoids first-mover advantage. Same-target movement is capture. Agents do not block one another because overlap is the capture condition.

## 7. Capture, timeout, and scoring

| Terminal reason | Winner | Cop score | Thief score |
|---|---:|---:|---:|
| Capture before or on move 25 | `cop` | 20 | 5 |
| No capture after resolving move 25 | `thief` | 5 | 10 |

Configuration supplies score values, but the table is the binding default. A capture on the last resolved move takes precedence over timeout. Training rewards may be shaped only in `training.yaml`; authoritative match scores never change and reporting consumes them directly.

## 8. Partial observations

For agent `i`, observation `o_i` is an egocentric square with Chebyshev radius `r` around its position. It includes:

- self position represented egocentrically at the center;
- visible cells tagged as empty, wall/out-of-bounds, barrier, or opponent;
- own remaining barrier count for the cop (zero/not-applicable for thief);
- completed moves and moves remaining;
- previous own action and legality flag if memory features are enabled.

Cells outside the radius are `UNKNOWN`; absolute opponent coordinates are never emitted when unseen. The local observation encoder must work at grid edges without leaking map padding semantics beyond `WALL`.

`GlobalTrainingState` may include exact positions and barriers only for centralized training, evaluator diagnostics, and read-only GUI rendering. It is a different type from `LocalObservation` and is rejected by policy/MCP inference contracts.

## 9. Spawn and reset

Spawn is derived from the sub-game seed and samples two distinct legal cells. Reproducibility requires a local injected RNG, not process-global randomness. Fixed spawns may be supplied for tests/evaluation. Reset clears barriers, count, histories, outcome, and scores. If legal distinct placement is impossible, configuration fails before a match.

## 10. Match and technical failures

A full match contains exactly six valid sub-games. Each new sub-game uses a derived deterministic seed and fresh state. A policy/network/runtime error produces `TechnicalFailure`, not a winner or score. The orchestrator may retry according to bounded config; only valid completed sub-games count toward six. Exhaustion aborts the match and blocks report finalization.

## 11. Edge-case matrix

| Case | Expected behavior |
|---|---|
| Move beyond boundary / into barrier | Normalize to `STAY`, record illegal reason. |
| Both move to same empty cell | Capture. |
| Cop and thief swap cells | Capture under default crossing rule. |
| Both stay in same cell | State should already have terminated; otherwise capture invariant fires. |
| Cop places barrier and thief targets that cell | Placement is rejected by the v1 no-intended-destination rule; no hidden first-mover advantage. |
| Barrier on occupied/existing/out-of-range cell | Illegal placement; cop stays; budget unchanged. |
| Sixth barrier request | Illegal; budget remains zero. |
| Capture on move 25 | Cop wins; capture precedes timeout. |
| Step after terminal | Typed error; no state mutation. |
| Observation radius exceeds grid | Entire reachable board visible, with no out-of-grid coordinates leaked. |
| Same seed and policies | Same non-time trace. |

## 12. Acceptance tests

- **ENV-AC-1:** Every invariant holds for randomized legal action sequences across supported grid sizes.
- **ENV-AC-2:** A table-driven test covers all movement/crossing/same-target combinations.
- **ENV-AC-3:** Barriers block both agents, consume a cop action, and never exceed five under defaults.
- **ENV-AC-4:** The observation encoder hides every opponent/barrier cell outside radius and exposes visible ones correctly at corners/edges.
- **ENV-AC-5:** Global state cannot be passed to any execution policy or serialized by MCP action requests.
- **ENV-AC-6:** Capture/timeout produce exactly the configured score tuple, including capture on the final move.
- **ENV-AC-7:** Same seed/config/action trace yields identical canonical transition records.
- **ENV-AC-8:** A match has exactly six valid sub-games; technical failures do not count.

## 13. Limitations and alternatives

The exercise does not fully specify simultaneous crossing, barrier target range, or conflict order. The rules above are an explicit, testable proposal and must be approved before implementation. Sequential turns were rejected because they create observation and first-mover asymmetry. Random illegal-action replacement was rejected because it harms reproducibility.
