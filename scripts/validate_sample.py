"""Validate a 'show interfaces' sample file and list any problems found."""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Sequence
from pathlib import Path

from netutil.parser import parse_interfaces, read_text_file
from netutil.validate import validate_records

logger = logging.getLogger(__name__)


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validate a show interfaces sample file.")
    ap.add_argument("path", type=Path, help="file containing show interfaces output")
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    try:
        text = read_text_file(args.path)
    except FileNotFoundError:
        logger.error("File not found: %s", args.path)
        return 2
    except (PermissionError, IsADirectoryError) as exc:
        logger.error("Cannot read %s: %s", args.path, exc.strerror)
        return 2
    except UnicodeDecodeError as exc:
        logger.error("%s is not a UTF-8 text file (%s)", args.path, exc.reason)
        return 2

    interfaces = parse_interfaces(text)
    problems = validate_records(interfaces)

    if problems:
        for problem in problems:
            sys.stdout.write(f"PROBLEM: {problem}\n")
        sys.stdout.write(f"INVALID: {len(problems)} problem(s) in {args.path}\n")
        return 2

    sys.stdout.write(f"OK: {len(interfaces)} interfaces valid in {args.path}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
