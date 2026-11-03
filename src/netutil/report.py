"""Summaries of parsed interface data."""

from __future__ import annotations

from typing import Any

BUCKETS = ("healthy", "admin_down", "down", "suspicious")


def classify(record: dict[str, Any]) -> str:
    """Return the bucket name for one parsed interface record."""
    status = record.get("status")
    protocol = record.get("protocol")
    if status == "administratively down":
        return "admin_down"
    if status == "up" and protocol == "up":
        return "healthy"
    if status == "down" and protocol == "down":
        return "down"
    return "suspicious"


def status_summary(interfaces: dict[str, dict[str, Any]]) -> dict[str, list[str]]:
    """Group interface names by health. Every bucket is always present, names sorted."""
    summary: dict[str, list[str]] = {bucket: [] for bucket in BUCKETS}
    for name, record in interfaces.items():
        summary[classify(record)].append(name)
    for names in summary.values():
        names.sort()
    return summary
