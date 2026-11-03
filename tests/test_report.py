from netutil.report import BUCKETS, status_summary


def rec(status: str, protocol: str) -> dict[str, str]:
    return {"status": status, "protocol": protocol}


def test_one_interface_per_bucket() -> None:
    data = {
        "Gi0/1": rec("up", "up"),
        "Gi0/2": rec("administratively down", "down"),
        "Gi0/3": rec("down", "down"),
        "Gi0/4": rec("up", "down"),
    }
    assert status_summary(data) == {
        "healthy": ["Gi0/1"],
        "admin_down": ["Gi0/2"],
        "down": ["Gi0/3"],
        "suspicious": ["Gi0/4"],
    }


def test_empty_input_has_all_buckets() -> None:
    assert status_summary({}) == {bucket: [] for bucket in BUCKETS}


def test_names_are_sorted() -> None:
    data = {"Gi0/9": rec("up", "up"), "Gi0/10": rec("up", "up"), "Gi0/1": rec("up", "up")}
    assert status_summary(data)["healthy"] == ["Gi0/1", "Gi0/10", "Gi0/9"]


def test_missing_fields_are_suspicious() -> None:
    assert status_summary({"Gi0/1": {}})["suspicious"] == ["Gi0/1"]
