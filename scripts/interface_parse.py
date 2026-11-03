"""Parse 'show interfaces' output from a file; forwards to the netutil CLI."""

from __future__ import annotations

import sys
from collections.abc import Sequence

from netutil.cli import main as cli_main


def main(argv: Sequence[str] | None = None) -> int:
    """Take one file path and run `netutil parse --input PATH`."""
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1:
        sys.stderr.write("usage: interface_parse.py FILE\n")
        return 2
    return cli_main(["parse", "--input", args[0]])


if __name__ == "__main__":
    raise SystemExit(main())
