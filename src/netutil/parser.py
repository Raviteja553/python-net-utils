import argparse
import logging
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

HEADER_RE = re.compile(
    r"^(?P<name>\S+)\s+is\s+(?P<status>[^,]+),\s+line\s+protocol\s+is\s+(?P<protocol>\S+)"
)
DESC_RE = re.compile(r"^\s+Description:\s*(?P<description>.+?)\s*$")
INT_FIELDS = {
    "mtu": re.compile(r"\bMTU\s+(\d+)\s+bytes"),
    "bandwidth_kbit": re.compile(r"\bBW\s+(\d+)\s+Kbit/sec"),
    "delay": re.compile(r"\bDLY\s+(\d+)\s+usec"),
    "input_errors": re.compile(r"(\d+)\s+input errors"),
}

EXPECTED = {
    "GigabitEthernet0/1": {
        "status": "up",
        "protocol": "up",
        "description": "UPLINK-TO-CORE",
        "mtu": 1500,
        "bandwidth_kbit": 1000000,
        "input_errors": 0,
        "delay": 10,
    },
    "GigabitEthernet0/2": {
        "status": "administratively down",
        "protocol": "down",
        "description": "SPARE-PORT",
        "mtu": 1500,
        "bandwidth_kbit": 1000000,
        "input_errors": 0,
        "delay": 10,
    },
    "GigabitEthernet0/3": {
        "status": "down",
        "protocol": "down",
        "description": "LAB-SERVER-02",
        "mtu": 1500,
        "bandwidth_kbit": 100000,
        "input_errors": 0,
        "delay": 100,
    },
    "TenGigabitEthernet1/0/1": {
        "status": "up",
        "protocol": "up",
        "description": None,
        "mtu": 9000,
        "bandwidth_kbit": 10000000,
        "input_errors": 42,
        "delay": 10,
    },
}


def read_text_file(path: Path) -> str:
    """Return the file's text. Raises OSError subclasses if it can't be read."""
    return path.read_text(encoding="utf-8")


def parse_interfaces(text: str) -> dict[str, dict[str, Any]]:
    interfaces: dict[str, dict[str, Any]] = {}
    current: dict[str, Any] | None = None

    for line in text.splitlines():
        if not line.strip():
            continue

        if not line[0].isspace():  # header line
            m = HEADER_RE.match(line)
            if m:
                logger.debug("Matched header for %s", m["name"])
                current = {
                    "status": m["status"],
                    "protocol": m["protocol"],
                    "description": None,
                    "mtu": None,
                    "bandwidth_kbit": None,
                    "input_errors": None,
                    "delay": None,
                }
                interfaces[m["name"]] = current
            else:
                logger.warning("Skipping unrecognised header line: %s", line)
                current = None
            continue

        if current is None:  # detail line with no owner
            continue

        d = DESC_RE.match(line)
        if d:
            current["description"] = d["description"]

        for key, rx in INT_FIELDS.items():
            f = rx.search(line)
            if f:
                current[key] = int(f.group(1))

    return interfaces


def self_check(result: dict[str, dict[str, Any]]) -> bool:
    """Compare a parse of the sample file against EXPECTED."""
    if result == EXPECTED:
        logger.info("OK: parser matches expected")
        return True
    for name in sorted(set(EXPECTED) | set(result)):
        if result.get(name) != EXPECTED.get(name):
            logger.error("MISMATCH %s", name)
            logger.error("  expected: %s", EXPECTED.get(name))
            logger.error("  got:      %s", result.get(name))
    return False


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Parse 'show interfaces' output.")
    ap.add_argument("path", type=Path, help="file containing show interfaces output")
    ap.add_argument("-v", "--verbose", action="store_true", help="show DEBUG messages")
    ap.add_argument(
        "--check", action="store_true", help="compare the result with the built-in expected answer"
    )
    args = ap.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    try:
        text = read_text_file(args.path)
    except FileNotFoundError:
        logger.error("File not found: %s", args.path)
        return 1
    except (PermissionError, IsADirectoryError) as exc:
        logger.error("Cannot read %s: %s", args.path, exc.strerror)
        return 1

    result = parse_interfaces(text)
    logger.info("Parsed %d interfaces", len(result))

    if args.check:
        return 0 if self_check(result) else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
