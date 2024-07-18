import logging
import logging.config
from collections.abc import Callable, Generator
from functools import wraps
from typing import Any, TypeVar

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


def watch(
    func: Callable[..., Generator[_YieldT, None, None]],
) -> Callable[..., Generator[_YieldT, None, None]]:
    """Watch the output of a generator function and log the yielded items.

    Args:
        func: Generator function that yields strings, models or exceptions
            (It will use the objects `__str__()` method to print it out.)

    Returns:
        Decorated function that logs all yielded items
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Generator[_YieldT, None, None]:
        fname = func.__name__
        for item in func(*args, **kwargs):
            echo(f"{fname} - {item}")
            yield item

    return wrapper


def echo(text: str | bytes, **styles: Any) -> None:
    """Echo the given text with the given styles and the current timestamp prefix.

    Args:
        text: Text to print to the console
        styles: Keyword parameters to be passed to `click.style`
    """
    logger.info(text)
