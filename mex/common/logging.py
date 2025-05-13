import logging
import logging.config
from collections.abc import Callable, Generator
from functools import wraps
from typing import Any, ParamSpec, TypeVar

import click

_YieldT = TypeVar("_YieldT")

LOGGING_CONFIG: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": f"{click.style('%(asctime)s', fg='bright_yellow')}"
            " - mex - %(message)s",
        }
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "mex": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": True,
        }
    },
}
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("mex")
echo = logger.info  # `echo` is deprecated, use the logger directly instead

P = ParamSpec("P")


def watch(
    log_interval: int = 10000,
) -> Callable[
    [Callable[P, Generator[_YieldT, None, None]]],
    Callable[P, Generator[_YieldT, None, None]],
]:
    """Watch the output of a generator function and log the yielded items.

    Args:
        func: Generator function that yields strings, models or exceptions
            (It will use the objects `__str__()` method to print it out.)
        log_interval: integer determining the interval length between loggings

    Returns:
        Decorated function that logs all yielded items
    """

    def decorator(
        func: Callable[P, Generator[_YieldT, None, None]],
    ) -> Callable[P, Generator[_YieldT, None, None]]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Generator[_YieldT, None, None]:  # noqa: ANN401
            for i, item in enumerate(func(*args, **kwargs)):
                if i % log_interval == 0:
                    logger.info("%s - %s - %s", i, func.__name__, item)
                yield item

        return wrapper

    return decorator
