# Inter-Group Bonus Game Plan

Status: **planned only**. No external opponent match has been performed, mutually agreed, or claimed.

## Participants and preconditions

Two groups must agree in writing on group names, repository URLs, student metadata exchange, game configuration, scoring, observation/action schemas, MCP transport/authentication, timeout/retry behavior, timezone, and the canonical report format. Each group keeps credentials and student IDs outside Git.

Before play, both groups pin the same configuration and commit SHA, verify service health, exchange only revocable runtime credentials, and run a non-scoring contract smoke. A technical failure is retried under the agreed bounded policy and never counted as a valid sub-game.

## Six-sub-game role schedule

| Sub-games | Cop | Thief |
|---:|---|---|
| 1-3 | Group 1 | Group 2 |
| 4-6 | Group 2 | Group 1 |

The match is complete only after six valid sub-games. The engine remains authoritative for timestamps, moves, winner, per-role scores, and totals. Neither group may alter a completed result manually.

## Execution workflow

1. Record both group/repository identities and agreed commit/config hashes privately.
2. Start distinct authenticated cop and thief services and verify health.
3. Run sub-games 1-3 with Group 1 as cop and Group 2 as thief.
4. Swap service roles and run sub-games 4-6 with Group 2 as cop and Group 1 as thief.
5. Produce the canonical six-entry JSON report from authoritative results.
6. Both groups independently compare game IDs, timestamps, moves, winners, scores, and totals.
7. Resolve any mismatch before either group submits or sends a report.
8. Each group records the mutually agreed result, repositories, role schedule, and evidence in its README.

## Canonical report

The agreed JSON uses the same schema as the core project:

- `group_name`
- `students`
- `github_repo`
- `timezone: Asia/Jerusalem`
- six ordered `sub_games`, each with `id`, `start`, `end`, `moves`, `winner`, and `scores`
- authoritative `totals`

For a two-repository match, each group must also document the opponent group/repository and role mapping in its README or an agreed companion manifest. Private student identifiers remain outside Git and may appear only in the final private submission payload when required.

## Mutual agreement and evidence

Both groups must affirm that the JSON bodies are equivalent before reporting. Required evidence:

- screenshots showing both role configurations and final totals;
- sanitized service/health evidence without tokens;
- exact config and commit identifiers;
- both repository links;
- README section naming opponent, role schedule, final score, and bonus claim; and
- one mutually agreed final report per group.

## Failure and dispute handling

Network/service failures do not count as game outcomes. Preserve sanitized correlation IDs and timestamps, retry only under the agreed policy, and stop if implementations disagree on rules or scoring. Do not select whichever result is more favorable. If agreement cannot be reached, document the attempt as incomplete and make no bonus claim.
