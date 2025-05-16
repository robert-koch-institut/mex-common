import time
from typing import Any, Self

from requests.exceptions import RequestException


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


class TimedRequestException(RequestException):
    """Timed request exception with a seconds attribute."""

    seconds: float

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        """Initialize exception with timeout `seconds`."""
        self.seconds = kwargs.pop("seconds", 0.0)
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        """Return a shortened representation."""
        args = (
            ", ".join(str(a) for a in self.args)
            or (self.response and self.response.status_code)
            or "N/A"
        )
        return f"{args} (seconds elapsed={self.seconds:.3f})"

    @classmethod
    def create(cls, exc: RequestException, t0: float) -> Self:
        """Create a new timed error from an upstream exception and start time."""
        return cls(
            *exc.args,
            response=exc.response,
            request=exc.request,
            seconds=time.perf_counter() - t0,
        )


class TimedReadTimeout(TimedRequestException):
    """The server did not send any data in the allotted amount of time."""


class TimedTooManyRequests(TimedRequestException):
    """Client sent too many requests in a given time."""


class TimedServerError(TimedRequestException):
    """The server encountered an error or is incapable of responding."""
