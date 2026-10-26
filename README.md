# Python Net Utils
# python-net-utils

Small, typed network automation helpers: parsers, an API client and config rendering.

**Lab project, not production.**

## Purpose

Practice repo for the Week 3 to 7 exercises. Everything here is built against sample data
or emulated devices. Nothing comes from a work network.

## Layout

```
pyproject.toml     project metadata plus ruff, mypy, pytest and coverage config
src/netutil/     the importable package (src layout)
tests/             pytest tests
```

Install name is `python-net-utils`; import name is `netutil`.

## How to run

```
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

ruff check .
ruff format --check .
mypy
pytest --cov
neutil --version
```

## What it proves

Typed Python, tests, linting and a clean PR workflow.

## Limits

Early skeleton. No device access yet.

## Cost and teardown

None. Delete the `.venv` folder to clean up.

## Lessons learned
