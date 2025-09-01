"""Top-level package for rallytools."""
from .log import get_logger, setup_logging
from .io import read_text, write_text, read_json, write_json
from .time import timeit, Timer

__all__ = [
    "get_logger",
    "setup_logging",
    "read_text",
    "write_text",
    "read_json",
    "write_json",
    "timeit",
    "Timer",
]

__version__ = "0.1.0"
