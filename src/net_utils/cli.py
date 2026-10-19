"""Command-line entry point for net_utils."""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Sequence

from net_utils import __version__

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level argument parser."""
    parser = argparse.ArgumentParser(
        prog="net-utils",
        description="Small, typed network automation helpers. Lab project, not production.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("-v", "--verbose", action="store_true", help="enable debug logging")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return a process exit code."""
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    logger.debug("net-utils %s starting", __version__)
    sys.stdout.write(f"net-utils {__version__}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
