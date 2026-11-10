"""Command-line entry point for netutil."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from netutil import __version__
from netutil.errors import NetutilError
from netutil.jsonlog import configure_logging
from netutil.service import load_interfaces

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level argument parser."""
    ap = argparse.ArgumentParser(
        prog="net-utils",
        description="Small, typed network automation helpers. Lab project, not production.",
    )
    ap.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    ap.add_argument("-v", "--verbose", action="store_true", help="enable debug logging")

    sub = ap.add_subparsers(dest="command", required=True, metavar="COMMAND")

    p = sub.add_parser("parse", help="parse 'show interfaces' output into structured data")
    p.add_argument(
        "--input", type=Path, required=True, help="file containing show interfaces output"
    )
    p.add_argument(
        "--format", choices=["json"], default="json", help="output format (default: json)"
    )
    p.set_defaults(func=_cmd_parse)

    return ap


def _cmd_parse(args: argparse.Namespace) -> int:
    """Load, validate and print the interfaces as JSON."""
    interfaces = load_interfaces(args.input)
    logger.info("parsed interfaces", extra={"count": len(interfaces), "path": str(args.input)})
    data = {name: iface.model_dump() for name, iface in interfaces.items()}
    json.dump(data, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


def _error_payload(exc: NetutilError) -> dict[str, Any]:
    """Describe a failure as data, for scripts that call the CLI."""
    payload: dict[str, Any] = {
        "ok": False,
        "error": type(exc).__name__,
        "exit_code": exc.exit_code,
        "message": str(exc),
    }
    problems = getattr(exc, "problems", None)
    if problems is not None:
        payload["problems"] = problems
    return payload


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return a process exit code."""
    args = build_parser().parse_args(argv)
    configure_logging(args.verbose)
    logger.debug("net-utils %s starting", __version__)

    try:
        return int(args.func(args))
    except NetutilError as exc:
        logger.error(
            "command failed",
            extra={"error": type(exc).__name__, "exit_code": exc.exit_code, "detail": str(exc)},
        )
        json.dump(_error_payload(exc), sys.stdout, indent=2)
        sys.stdout.write("\n")
        return exc.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
