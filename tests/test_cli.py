import json
import subprocess
import sys
from pathlib import Path

import pytest

from netutil import __version__
from netutil.cli import main

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "tests" / "data" / "show_interfaces.txt"

BAD_MTU = """GigabitEthernet0/1 is up, line protocol is up (connected)
  Description: TEST-LINK
  MTU 0 bytes, BW 1000000 Kbit/sec, DLY 10 usec,
     0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored
"""


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


def test_valid_file_exit_0(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["parse", "--input", str(DATA)]) == 0
    data = json.loads(capsys.readouterr().out)
    assert len(data) == 4
    assert data["TenGigabitEthernet1/0/1"]["description"] is None


def test_missing_file_exit_3(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    assert main(["parse", "--input", str(tmp_path / "nope.txt")]) == 3
    out = json.loads(capsys.readouterr().out)
    assert out["ok"] is False
    assert out["error"] == "InputFileError"
    assert out["exit_code"] == 3


def test_directory_exit_3(tmp_path: Path) -> None:
    assert main(["parse", "--input", str(tmp_path)]) == 3


def test_binary_file_exit_3(tmp_path: Path) -> None:
    bad = tmp_path / "blob.bin"
    bad.write_bytes(b"\xff\xfe\x00\x80")
    assert main(["parse", "--input", str(bad)]) == 3


def test_wrong_content_exit_4(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    f = tmp_path / "other.txt"
    f.write_text("hello world\n", encoding="utf-8")
    assert main(["parse", "--input", str(f)]) == 4
    assert json.loads(capsys.readouterr().out)["error"] == "ParseError"


def test_invalid_record_exit_5(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    f = tmp_path / "bad.txt"
    f.write_text(BAD_MTU, encoding="utf-8")
    assert main(["parse", "--input", str(f)]) == 5
    out = json.loads(capsys.readouterr().out)
    assert out["error"] == "RecordValidationError"
    assert any("mtu" in p for p in out["problems"])


def test_subprocess_exit_code_and_stdout(tmp_path: Path) -> None:
    r = subprocess.run(  # noqa: S603
        [sys.executable, "-m", "netutil.cli", "parse", "--input", str(tmp_path / "nope.txt")],
        capture_output=True,
        text=True,
        cwd=ROOT,
        check=False,
    )
    assert r.returncode == 3
    assert json.loads(r.stdout)["error"] == "InputFileError"
    assert json.loads(r.stderr.splitlines()[-1])["level"] == "ERROR"
