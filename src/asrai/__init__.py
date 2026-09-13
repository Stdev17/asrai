"""asrai: first-pass art direction for game assets."""
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("asrai")
except PackageNotFoundError:  # checkout without install
    __version__ = "0.0.0+local"
