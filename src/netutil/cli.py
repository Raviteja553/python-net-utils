from __future__ import annotations

import argparse
import json
import logging
import sys
from collections.abc import Sequence
from pathlib import Path

from netutil import __version__
from netutil.parser import parse_interfaces, read_text_file

logger = logging.getLogger(__name__)

EXIT_OK = 0
EXIT_BAD_INPUT = 2


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
    """Read the input file, parse it, write the result to stdout."""
    try:
        text = read_text_file(args.input)
    except FileNotFoundError:
        logger.error("File not found: %s", args.input)
        return EXIT_BAD_INPUT
    except (PermissionError, IsADirectoryError) as exc:
        logger.error("Cannot read %s: %s", args.input, exc.strerror)
        return EXIT_BAD_INPUT
    except UnicodeDecodeError as exc:
        logger.error("%s is not a UTF-8 text file (%s)", args.input, exc.reason)
        return EXIT_BAD_INPUT

    result = parse_interfaces(text)
    if not result:
        logger.error("No interfaces found in %s; is this 'show interfaces' output?", args.input)
        return EXIT_BAD_INPUT

    logger.info("Parsed %d interfaces", len(result))
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return EXIT_OK


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return a process exit code."""
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    logger.debug("net-utils %s starting", __version__)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
