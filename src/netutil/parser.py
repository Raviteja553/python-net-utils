import re
from pathlib import Path
from typing import Any

DATA = Path(__file__).resolve().parents[2] / "tests" / "data" / "show_interfaces.txt"

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
def parse_interfaces(text: str) -> dict[str, dict[str, Any]]:
    interfaces: dict[str, dict[str, Any]] = {}
    current: dict[str, Any] | None = None

    for line in text.splitlines():
        if not line.strip():
            continue

        if not line[0].isspace():              # header line
            m = HEADER_RE.match(line)
            if m:
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
                current = None                 # unknown header: ignore its details
            continue

        if current is None:                    # detail line with no owner
            continue

        d = DESC_RE.match(line)
        if d:
            current["description"] = d["description"]

        for key, rx in INT_FIELDS.items():
            f = rx.search(line)
            if f:
                current[key] = int(f.group(1))

    return interfaces
if __name__ == "__main__":
    expected = {
        "GigabitEthernet0/1": 
        {
            "status": "up",
            "protocol": "up",
            "description": "UPLINK-TO-CORE",
            "mtu": 1500,
            "bandwidth_kbit": 1000000,
            "input_errors": 0,
            "delay": 10,
        },
        "GigabitEthernet0/2": 
        {
            "status": "administratively down",
            "protocol": "down",
            "description": "SPARE-PORT",
            "mtu": 1500,
            "bandwidth_kbit": 1000000,
            "input_errors": 0,
            "delay": 10,
        },
        "GigabitEthernet0/3": 
            {
                "status": "down",
                "protocol": "down",
                "description": "LAB-SERVER-02",
                "mtu": 1500,
                "bandwidth_kbit": 100000,
                "input_errors": 0,
                "delay": 100,
            },
        "TenGigabitEthernet1/0/1": 
            {
                "status": "up",
                "protocol": "up",
                "description": None,
                "mtu": 9000,
                "bandwidth_kbit": 10000000,
                "input_errors": 42,
                "delay": 10,
            }
    }
    text = DATA.read_text()
    result = parse_interfaces(text)

    if result == expected:
        print("OK: parser matches expected")
    else:
        for name in sorted(set(expected) | set(result)):
            if result.get(name) != expected.get(name):
                print(f"MISMATCH {name}")
                print("  expected:", expected.get(name))
                print("  got:     ", result.get(name))
