import json
from pathlib import Path

import pytest

from netutil import __version__
from netutil.cli import main

DATA = Path(__file__).parent / "data" / "show_interfaces.txt"


def test_version_flag(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert f"net-utils {__version__}" in capsys.readouterr().out


def test_no_command_is_usage_error() -> None:
    with pytest.raises(SystemExit) as exc:
        main([])
    assert exc.value.code == 2


def test_parse_requires_input() -> None:
    with pytest.raises(SystemExit) as exc:
        main(["parse"])
    assert exc.value.code == 2


def test_parse_valid_file(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["parse", "--input", str(DATA)]) == 0
    data = json.loads(capsys.readouterr().out)
    assert len(data) == 4
    assert data["TenGigabitEthernet1/0/1"]["description"] is None


def test_parse_missing_file(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    assert main(["parse", "--input", str(tmp_path / "nope.txt")]) == 2
    assert capsys.readouterr().out == ""  # no data on stdout


def test_parse_directory(tmp_path: Path) -> None:
    assert main(["parse", "--input", str(tmp_path)]) == 2


def test_parse_binary_file(tmp_path: Path) -> None:
    bad = tmp_path / "blob.bin"
    bad.write_bytes(b"\xff\xfe\x00\x80")
    assert main(["parse", "--input", str(bad)]) == 2


def test_parse_wrong_content(tmp_path: Path) -> None:
    f = tmp_path / "other.txt"
    f.write_text("hello world\n", encoding="utf-8")
    assert main(["parse", "--input", str(f)]) == 2
