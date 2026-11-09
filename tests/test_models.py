from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from netutil.models import BgpNeighbor, Interface
from netutil.parser import parse_interfaces

DATA = Path(__file__).parent / "data" / "show_interfaces.txt"


def good_interface() -> dict[str, Any]:
    return {
        "status": "up",
        "protocol": "up",
        "description": None,
        "mtu": 1500,
        "bandwidth_kbit": 1000000,
        "input_errors": 0,
        "delay": 10,
    }


def good_neighbor() -> dict[str, Any]:
    return {"neighbor_ip": "192.0.2.1", "remote_as": 65001, "state": "Idle"}


def test_interface_from_parser_output() -> None:
    parsed = parse_interfaces(DATA.read_text(encoding="utf-8"))
    iface = Interface(**parsed["GigabitEthernet0/1"])
    assert iface.description == "UPLINK-TO-CORE"
    assert iface.mtu == 1500


def test_all_sample_interfaces_are_valid() -> None:
    parsed = parse_interfaces(DATA.read_text(encoding="utf-8"))
    models = {name: Interface(**rec) for name, rec in parsed.items()}
    assert len(models) == 4


def test_missing_description_is_none() -> None:
    parsed = parse_interfaces(DATA.read_text(encoding="utf-8"))
    assert Interface(**parsed["TenGigabitEthernet1/0/1"]).description is None


def test_unknown_status_rejected() -> None:
    with pytest.raises(ValidationError):
        Interface.model_validate(good_interface() | {"status": "flapping"})


def test_zero_mtu_rejected() -> None:
    with pytest.raises(ValidationError) as exc:
        Interface.model_validate(good_interface() | {"mtu": 0})
    assert exc.value.errors()[0]["loc"] == ("mtu",)


def test_all_problems_reported_together() -> None:
    with pytest.raises(ValidationError) as exc:
        Interface.model_validate(good_interface() | {"status": "x", "mtu": 0})
    assert exc.value.error_count() == 2


def test_valid_bgp_neighbor() -> None:
    n = BgpNeighbor.model_validate(
        good_neighbor() | {"state": "Established", "uptime": "1d02h", "prefixes_received": 12}
    )
    assert n.state == "Established"


def test_bgp_optional_fields_default_to_none() -> None:
    n = BgpNeighbor.model_validate(good_neighbor())
    assert n.uptime is None
    assert n.prefixes_received is None


def test_bgp_bad_state_rejected() -> None:
    with pytest.raises(ValidationError):
        BgpNeighbor.model_validate(good_neighbor() | {"state": "Broken"})


def test_bgp_bad_ip_rejected() -> None:
    with pytest.raises(ValidationError):
        BgpNeighbor.model_validate(good_neighbor() | {"neighbor_ip": "not-an-ip"})


def test_bgp_asn_out_of_range_rejected() -> None:
    with pytest.raises(ValidationError):
        BgpNeighbor.model_validate(good_neighbor() | {"remote_as": 0})
    with pytest.raises(ValidationError):
        BgpNeighbor.model_validate(good_neighbor() | {"remote_as": 4294967296})
