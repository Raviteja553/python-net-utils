from pathlib import Path

import pytest

from netutil.errors import InputFileError, ParseError, RecordValidationError
from netutil.service import load_interfaces

DATA = Path(__file__).parent / "data" / "show_interfaces.txt"

BLOCK = """GigabitEthernet0/1 is up, line protocol is up (connected)
  Description: TEST-LINK
  MTU {mtu} bytes, BW 1000000 Kbit/sec, DLY 10 usec,
     0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored
"""


def test_valid_file_returns_models() -> None:
    result = load_interfaces(DATA)
    assert len(result) == 4
    assert result["GigabitEthernet0/1"].mtu == 1500
    assert result["TenGigabitEthernet1/0/1"].description is None


def test_missing_file(tmp_path: Path) -> None:
    with pytest.raises(InputFileError):
        load_interfaces(tmp_path / "nope.txt")


def test_directory(tmp_path: Path) -> None:
    with pytest.raises(InputFileError):
        load_interfaces(tmp_path)


def test_binary_file(tmp_path: Path) -> None:
    f = tmp_path / "blob.bin"
    f.write_bytes(b"\xff\xfe\x00\x80")
    with pytest.raises(InputFileError):
        load_interfaces(f)


def test_wrong_content(tmp_path: Path) -> None:
    f = tmp_path / "other.txt"
    f.write_text("hello world\n", encoding="utf-8")
    with pytest.raises(ParseError):
        load_interfaces(f)


def test_invalid_record_reports_problem(tmp_path: Path) -> None:
    f = tmp_path / "bad.txt"
    f.write_text(BLOCK.format(mtu=0), encoding="utf-8")
    with pytest.raises(RecordValidationError) as exc:
        load_interfaces(f)
    assert any("GigabitEthernet0/1: mtu" in p for p in exc.value.problems)


def test_cause_is_kept(tmp_path: Path) -> None:
    with pytest.raises(InputFileError) as exc:
        load_interfaces(tmp_path / "nope.txt")
    assert isinstance(exc.value.__cause__, FileNotFoundError)
