"""Command-line entry point for the deterministic engine."""

import argparse
import json
from collections.abc import Sequence

from cops_and_robbers_rl.sdk.sdk import CopsAndRobbersSDK
from cops_and_robbers_rl.shared.paths import DEFAULT_GAME_CONFIG


def build_parser() -> argparse.ArgumentParser:
    """Build the project CLI parser."""
    parser = argparse.ArgumentParser(description="Cops and Robbers deterministic engine")
    subparsers = parser.add_subparsers(dest="command", required=True)
    play = subparsers.add_parser("play", help="run a headless configured match")
    play.add_argument("--config", default=str(DEFAULT_GAME_CONFIG))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the requested SDK workflow and return a process status."""
    args = build_parser().parse_args(argv)
    if args.command == "play":
        result = CopsAndRobbersSDK.from_config(args.config).run_match()
        print(json.dumps(result.to_report_dict(), indent=2))
        return 0
    raise RuntimeError(f"unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
