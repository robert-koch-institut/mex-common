from typing import Any

from requests.exceptions import ReadTimeout


class MExError(Exception):
    """Base class for generic exceptions."""

    def __str__(self) -> str:
        """Format this exception as a string for logging."""
        args = ", ".join(str(a) for a in self.args) or "N/A"
        return f"{self.__class__.__name__}: {args}"


class EmptySearchResultError(MExError):
    """Empty search result."""


class FoundMoreThanOneError(MExError):
    """Found more than one."""


class MergingError(MExError):
    """Creating a merged item from extracted items and rules failed."""


class TimedReadTimeout(ReadTimeout):
    """Read time out exception with a seconds attribute."""

    seconds: float

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize exception with timeout `seconds`."""
        self.seconds = kwargs.pop("seconds", 0.0)
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        """Return a shortened representation."""
        args = ", ".join(str(a) for a in self.args) or "N/A"
        return f"{self.__class__.__name__}: {args} (seconds elapsed={self.seconds:.3f})"
