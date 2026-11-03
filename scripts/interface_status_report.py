"""Print a health summary of interfaces from a 'show interfaces' file."""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Sequence
from pathlib import Path

from netutil.parser import parse_interfaces, read_text_file
from netutil.report import BUCKETS, status_summary

logger = logging.getLogger(__name__)

LABELS = {
    "healthy": "Healthy (up/up)",
    "admin_down": "Administratively down",
    "down": "Down (check cable/peer)",
    "suspicious": "Suspicious (mixed state)",
}


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Interface status report.")
    ap.add_argument("path", type=Path, help="file containing show interfaces output")
    ap.add_argument(
        "--fail-on-down",
        action="store_true",
        help="exit 1 if any interface is down or suspicious",
    )
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
    if not interfaces:
        logger.error("No interfaces found in %s", args.path)
        return 2

    summary = status_summary(interfaces)
    for bucket in BUCKETS:
        names = summary[bucket]
        sys.stdout.write(f"{LABELS[bucket]}: {len(names)}\n")
        for name in names:
            sys.stdout.write(f"  {name}\n")

    if args.fail_on_down and (summary["down"] or summary["suspicious"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
