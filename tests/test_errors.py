import pytest

from netutil.errors import (
    DeviceUnreachableError,
    InputFileError,
    NetutilError,
    ParseError,
    RecordValidationError,
)


def test_all_errors_share_the_base_class() -> None:
    for cls in (InputFileError, ParseError, RecordValidationError, DeviceUnreachableError):
        assert issubclass(cls, NetutilError)


def test_base_class_catches_subclasses() -> None:
    with pytest.raises(NetutilError):
        raise ParseError("bad text")


def test_exit_codes() -> None:
    assert NetutilError.exit_code == 1
    assert InputFileError.exit_code == 3
    assert ParseError.exit_code == 4
    assert RecordValidationError.exit_code == 5
    assert DeviceUnreachableError.exit_code == 6


def test_exit_codes_are_unique() -> None:
    codes = [
        c.exit_code
        for c in (InputFileError, ParseError, RecordValidationError, DeviceUnreachableError)
    ]
    assert len(codes) == len(set(codes))


def test_validation_error_carries_problems() -> None:
    err = RecordValidationError(["a", "b"])
    assert err.problems == ["a", "b"]
    assert "2" in str(err)


def test_device_unreachable_carries_host() -> None:
    err = DeviceUnreachableError("192.0.2.1")
    assert err.host == "192.0.2.1"
    assert "192.0.2.1" in str(err)
