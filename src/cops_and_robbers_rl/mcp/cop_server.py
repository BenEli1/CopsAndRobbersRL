"""Independent local cop MCP server."""

import argparse
from collections.abc import Sequence

from cops_and_robbers_rl.environment.game_state import Role
from cops_and_robbers_rl.mcp.server import run_server


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="run the local cop MCP server")
    parser.add_argument("--config", default=None)
    args = parser.parse_args(argv)
    run_server(Role.COP, args.config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
