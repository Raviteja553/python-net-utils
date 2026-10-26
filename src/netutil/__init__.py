"""Small, typed network automation helpers. Lab project, not production."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("python-net-utils")  # distribution name, not import name
except PackageNotFoundError:  # running from a source tree that is not installed
    __version__ = "0.0.0"

__all__ = ["__version__"]
