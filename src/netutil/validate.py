"""Validation of parsed interface records."""

from __future__ import annotations

from typing import Any, TypeGuard

VALID_STATUS = {"up", "down", "administratively down"}
VALID_PROTOCOL = {"up", "down"}
REQUIRED_STR = ("status", "protocol")
POSITIVE_INT = ("mtu", "bandwidth_kbit")
NON_NEGATIVE_INT = ("input_errors", "delay")


def validate_records(interfaces: dict[str, dict[str, Any]]) -> list[str]:
    """Return a list of human-readable problems. An empty list means valid."""
    problems: list[str] = []

    if not interfaces:
        return ["no interfaces found"]

    for name in sorted(interfaces):
        rec = interfaces[name]

        status = rec.get("status")
        if status not in VALID_STATUS:
            problems.append(f"{name}: unknown status {status!r}")

        protocol = rec.get("protocol")
        if protocol not in VALID_PROTOCOL:
            problems.append(f"{name}: unknown protocol {protocol!r}")

        for field in POSITIVE_INT:
            value = rec.get(field)
            if not _is_int(value) or value <= 0:
                problems.append(f"{name}: {field} must be a positive integer, got {value!r}")

        for field in NON_NEGATIVE_INT:
            value = rec.get(field)
            if not _is_int(value) or value < 0:
                problems.append(f"{name}: {field} must be a non-negative integer, got {value!r}")

        description = rec.get("description")
        if description is not None and not isinstance(description, str):
            problems.append(f"{name}: description must be text or None, got {description!r}")

    return problems


def _is_int(value: Any) -> TypeGuard[int]:
    """True for real ints only. bool is a subclass of int, so exclude it."""
    return isinstance(value, int) and not isinstance(value, bool)
