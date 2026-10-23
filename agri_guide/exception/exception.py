import sys
from typing import Any


class AgriGuideException(Exception):
    """Custom exception class to wrap lower-level errors with context."""

    def __init__(self, message: str, error: Exception | None = None) -> None:
        super().__init__(message)
        self.error = error

    def __str__(self) -> str:  # pragma: no cover - trivial
        base = super().__str__()
        if self.error is not None:
            return f"{base} (caused by {repr(self.error)})"
        return base








