from collections.abc import Callable

from mex.common.exceptions import TimedRequestException


def bounded_backoff(
    min_time: float, max_time: float
) -> Callable[[TimedRequestException], int | float]:
    """Get a function to calculate a bounded backoff time."""

    def wrapped(error: TimedRequestException) -> int | float:
        return min(max(error.seconds, min_time), max_time)

    return wrapped
