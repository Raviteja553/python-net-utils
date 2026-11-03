import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "interface_parse.py"
DATA = ROOT / "tests" / "data" / "show_interfaces.txt"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603  (fixed args, our own script)
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=ROOT,
        check=False,
    )


def test_valid_file_prints_json() -> None:
    r = run(str(DATA))
    assert r.returncode == 0
    assert len(json.loads(r.stdout)) == 4


def test_missing_file_exits_2() -> None:
    r = run("nope.txt")
    assert r.returncode == 2
    assert r.stdout == ""


def test_no_arguments_exits_2() -> None:
    r = run()
    assert r.returncode == 2
    assert "usage" in r.stderr


def test_two_arguments_exits_2() -> None:
    assert run("a", "b").returncode == 2
