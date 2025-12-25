import time
from typing import Optional


class Elapsed:
    _start: float
    _elapsed: Optional[float] = None

    def __enter__(self) -> "Elapsed":
        """Called when the context manager is entered."""
        self._start = time.perf_counter()
        return self

    def __exit__(self, *_exc) -> None:
        """Called when the context manager is exited."""
        self._elapsed = time.perf_counter() - self._start

    def __call__(self) -> float:
        """Return the elapsed time in seconds (rounded to 3 decimals)."""
        now = time.perf_counter()
        duration = self._elapsed if self._elapsed is not None else now - self._start
        return round(duration, 3)


def elapsed() -> Elapsed:
    return Elapsed()
