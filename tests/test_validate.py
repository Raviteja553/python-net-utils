from typing import Any

from netutil.validate import validate_records


def good() -> dict[str, Any]:
    return {
        "status": "up",
        "protocol": "up",
        "description": None,
        "mtu": 1500,
        "bandwidth_kbit": 1000000,
        "input_errors": 0,
        "delay": 10,
    }


def test_valid_record_has_no_problems() -> None:
    assert validate_records({"Gi0/1": good()}) == []


def test_empty_input_is_a_problem() -> None:
    assert validate_records({}) == ["no interfaces found"]


def test_unknown_status() -> None:
    rec = good() | {"status": "flapping"}
    problems = validate_records({"Gi0/1": rec})
    assert problems == ["Gi0/1: unknown status 'flapping'"]


def test_missing_mtu_and_negative_errors() -> None:
    rec = good() | {"mtu": None, "input_errors": -1}
    problems = validate_records({"Gi0/1": rec})
    assert len(problems) == 2
    assert any("mtu" in p for p in problems)
    assert any("input_errors" in p for p in problems)


def test_description_may_be_none_but_not_a_number() -> None:
    assert validate_records({"Gi0/1": good() | {"description": None}}) == []
    assert len(validate_records({"Gi0/1": good() | {"description": 5}})) == 1


def test_bool_is_not_an_int() -> None:
    assert len(validate_records({"Gi0/1": good() | {"mtu": True}})) == 1


def test_all_problems_reported_not_just_first() -> None:
    rec = good() | {"status": "x", "protocol": "y", "mtu": 0}
    assert len(validate_records({"Gi0/1": rec})) == 3
