"""Command-line entry point for autonomous baseline matches."""

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from cops_and_robbers_rl.agents import (
    BaseAgent,
    HeuristicCopAgent,
    HeuristicThiefAgent,
    RandomCopAgent,
    RandomThiefAgent,
)
from cops_and_robbers_rl.environment.game_state import MatchResult, Role
from cops_and_robbers_rl.runner.match_runner import DEFAULT_REPORT_PATH
from cops_and_robbers_rl.sdk.sdk import CopsAndRobbersSDK
from cops_and_robbers_rl.shared.paths import DEFAULT_GAME_CONFIG


def build_parser() -> argparse.ArgumentParser:
    """Build the project CLI parser."""
    parser = argparse.ArgumentParser(description="Cops and Robbers baseline match runner")
    subparsers = parser.add_subparsers(dest="command", required=True)
    play = subparsers.add_parser("play", help="run a six-sub-game autonomous match")
    play.add_argument("--config", default=str(DEFAULT_GAME_CONFIG))
    play.add_argument("--cop-agent", choices=("heuristic", "random"), default="heuristic")
    play.add_argument("--thief-agent", choices=("heuristic", "random"), default="heuristic")
    play.add_argument("--seed", type=int, default=42)
    play.add_argument("--output", type=Path, default=DEFAULT_REPORT_PATH)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the requested SDK workflow and return a process status."""
    args = build_parser().parse_args(argv)
    if args.command == "play":
        sdk = CopsAndRobbersSDK.from_config(args.config)
        result = sdk.run_match_and_save(
            _build_agent(Role.COP, args.cop_agent, args.seed),
            _build_agent(Role.THIEF, args.thief_agent, args.seed + 1),
            output_path=args.output,
        )
        print(json.dumps(_summary(result, sdk.last_technical_failures, args.output), indent=2))
        return 0
    raise RuntimeError(f"unsupported command: {args.command}")


def _build_agent(role: Role, kind: str, seed: int) -> BaseAgent:
    if role is Role.COP:
        return HeuristicCopAgent(seed=seed) if kind == "heuristic" else RandomCopAgent(seed=seed)
    return HeuristicThiefAgent(seed=seed) if kind == "heuristic" else RandomThiefAgent(seed=seed)


def _summary(result: MatchResult, technical_failures: int, output: Path) -> dict[str, object]:
    report = result.to_report_dict()
    wins = {"cop": 0, "thief": 0}
    for game in report["sub_games"]:
        wins[game["winner"]] += 1
    return {
        "sub_games": len(report["sub_games"]),
        "wins": wins,
        "totals": report["totals"],
        "technical_failures_retried": technical_failures,
        "report": str(output),
    }


if __name__ == "__main__":
    raise SystemExit(main())
