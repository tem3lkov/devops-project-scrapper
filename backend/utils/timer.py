import time
from typing import Optional

class Elapsed:
    _start: float
    _elapsed: Optional[float] = None

    # called when the context manager is entered
    def __enter__(self) -> "Elapsed":
        self._start = time.perf_counter()
        return self

    # called when the context manager is exited
    def __exit__(self, *_exc) -> None:
        self._elapsed = time.perf_counter() - self._start

    # called when the object is called
    def __call__(self) -> float:
        now = time.perf_counter()
        return round(
            (self._elapsed if self._elapsed is not None else now - self._start), 3
        )

def elapsed() -> Elapsed:    
    return Elapsed()
