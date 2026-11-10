"""Load, parse and validate interface data, raising typed errors on failure."""

from __future__ import annotations

from pathlib import Path

from pydantic import ValidationError

from netutil.errors import InputFileError, ParseError, RecordValidationError
from netutil.models import Interface
from netutil.parser import parse_interfaces, read_text_file


def _read(path: Path) -> str:
    try:
        return read_text_file(path)
    except UnicodeDecodeError as exc:
        raise InputFileError(f"{path} is not a UTF-8 text file") from exc
    except OSError as exc:
        # Covers missing file, permission denied, and a directory passed as a file.
        raise InputFileError(f"cannot read {path}: {exc.strerror or exc}") from exc


def _problems(name: str, exc: ValidationError) -> list[str]:
    """Turn a pydantic error into readable 'Gi0/1: mtu: message' strings."""
    out: list[str] = []
    for err in exc.errors():
        field = ".".join(str(part) for part in err["loc"])
        out.append(f"{name}: {field}: {err['msg']}")
    return out


def load_interfaces(path: Path) -> dict[str, Interface]:
    """Read PATH and return validated interfaces.

    Raises InputFileError, ParseError or RecordValidationError.
    """
    raw = parse_interfaces(_read(path))
    if not raw:
        raise ParseError(f"no interfaces found in {path}")

    interfaces: dict[str, Interface] = {}
    problems: list[str] = []
    for name, record in raw.items():
        try:
            interfaces[name] = Interface.model_validate(record)
        except ValidationError as exc:
            problems.extend(_problems(name, exc))

    if problems:
        raise RecordValidationError(problems)
    return interfaces
