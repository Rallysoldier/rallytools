from __future__ import annotations
import time
from functools import wraps
from typing import Callable, TypeVar, ParamSpec

P = ParamSpec("P")
T = TypeVar("T")

class Timer:
    """Simple context manager for timing code blocks."""
    def __init__(self) -> None:
        self._start: float | None = None
        self.elapsed: float = 0.0

    def __enter__(self) -> "Timer":
        self._start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._start is not None:
            self.elapsed = time.perf_counter() - self._start

def timeit(fn: Callable[P, T]) -> Callable[P, T]:
    """Decorator that measures function runtime and attaches `.last_runtime` on the function."""
    @wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        start = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            wrapper.last_runtime = time.perf_counter() - start  # type: ignore[attr-defined]
    wrapper.last_runtime = 0.0  # type: ignore[attr-defined]
    return wrapper
