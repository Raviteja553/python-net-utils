"""Exceptions raised by netutil.

Catch NetutilError to handle any netutil failure, or a subclass to handle one kind.
"""

from __future__ import annotations


class NetutilError(Exception):
    """Base class for all netutil errors."""


class ParseError(NetutilError):
    """Text could not be parsed into records."""


class RecordValidationError(NetutilError):
    """Records were parsed but broke the validation rules."""

    def __init__(self, problems: list[str]) -> None:
        self.problems = problems
        super().__init__(f"{len(problems)} validation problem(s)")


class DeviceUnreachableError(NetutilError):
    """A device could not be reached."""

    def __init__(self, host: str) -> None:
        self.host = host
        super().__init__(f"device unreachable: {host}")
