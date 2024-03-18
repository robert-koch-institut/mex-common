import logging
import logging.config
from collections.abc import Callable, Generator
from datetime import datetime
from functools import wraps
from typing import Any, TypeVar

import click

YieldT = TypeVar("YieldT")

LOGGING_CONFIG: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(message)s",
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
    func: Callable[..., Generator[YieldT, None, None]]
) -> Callable[..., Generator[YieldT, None, None]]:
    """Watch the output of a generator function and log the yielded items.

    Args:
        func: Generator function that yields strings, models or exceptions
            (It will use the objects `__str__()` method to print it out.)

    Returns:
        Decorated function that logs all yielded items
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Generator[YieldT, None, None]:
        fname = func.__name__.replace("_", " ")
        for item in func(*args, **kwargs):
            echo(f"[{fname}] {item}")
            yield item

    return wrapper


def get_ts(ts: datetime | None = None) -> str:
    """Get a styled timestamp tag for prefixing log messages."""
    return click.style(f"[{ts or datetime.now()}]", fg="bright_yellow")


def echo(text: str | bytes, ts: datetime | None = None, **styles: Any) -> None:
    """Echo the given text with the given styles and the current timestamp prefix.

    Args:
        text: Text to print to the console
        ts: Timestamp to print as prefix, defaults to `now()`
        styles: Keyword parameters to be passed to `click.style`
    """
    logger.info(f"{get_ts(ts)} {click.style(text, **styles)}")
