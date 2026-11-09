import pytest

from netutil.errors import DeviceUnreachableError, NetutilError, ParseError, RecordValidationError


def test_all_errors_share_the_base_class() -> None:
    assert issubclass(ParseError, NetutilError)
    assert issubclass(RecordValidationError, NetutilError)
    assert issubclass(DeviceUnreachableError, NetutilError)


def test_base_class_catches_subclasses() -> None:
    with pytest.raises(NetutilError):
        raise ParseError("bad text")


def test_validation_failure_carries_problems() -> None:
    with pytest.raises(NetutilError) as exc:
        raise RecordValidationError(["a", "b"])
    err = exc.value
    assert isinstance(err, RecordValidationError)
    assert err.problems == ["a", "b"]
    assert "2" in str(err)


def test_device_unreachable_carries_host() -> None:
    err = DeviceUnreachableError("192.0.2.1")
    assert err.host == "192.0.2.1"
    assert "192.0.2.1" in str(err)
