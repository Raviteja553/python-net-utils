"""Tests for the command-line entry point."""

import pytest

from net_utils import __version__
from net_utils.cli import main


def test_main_prints_version_and_returns_zero(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == 0
    assert f"net-utils {__version__}" in capsys.readouterr().out


def test_version_flag_exits_cleanly(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["--version"])
    assert excinfo.value.code == 0
    assert __version__ in capsys.readouterr().out
