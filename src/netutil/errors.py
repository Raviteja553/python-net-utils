"""Exceptions raised by netutil.

Catch NetutilError to handle any netutil failure, or a subclass to handle one kind.
Each class carries the process exit code the CLI uses for it.
"""

from __future__ import annotations


class NetutilError(Exception):
    """Base class for all netutil errors."""

    exit_code: int = 1


class InputFileError(NetutilError):
    """The input file is missing, unreadable, a directory, or not UTF-8 text."""

    exit_code = 3


class ParseError(NetutilError):
    """Text could not be parsed into records."""

    exit_code = 4


class RecordValidationError(NetutilError):
    """Records were parsed but broke the validation rules."""

    exit_code = 5

    def __init__(self, problems: list[str]) -> None:
        self.problems = problems
        super().__init__(f"{len(problems)} validation problem(s)")


class DeviceUnreachableError(NetutilError):
    """A device could not be reached."""

    exit_code = 6

    def __init__(self, host: str) -> None:
        self.host = host
        super().__init__(f"device unreachable: {host}")
