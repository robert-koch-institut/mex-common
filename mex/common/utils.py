import re
from functools import cache
from itertools import zip_longest
from random import random
from time import sleep
from typing import Container, Iterable, Iterator, Optional, TypeVar

T = TypeVar("T")


def contains_any(base: Container[T], tokens: Iterable[T]) -> bool:
    """Check if a given base contains any of the given tokens."""
    for token in tokens:
        if token in base:
            return True
    return False


def any_contains_any(
    bases: Iterable[Optional[Container[T]]], tokens: Iterable[T]
) -> bool:
    """Check if any of the given bases contains any of the given tokens."""
    for base in bases:
        if base is None:
            continue
        for token in tokens:
            if token in base:
                return True
    return False


@cache
def normalize(string: str) -> str:
    """Normalize the given string to lowercase, numerals and single spaces."""
    return " ".join(re.sub(r"[^a-z0-9]", " ", string.lower()).split())


def grouper(chunk_size: int, iterable: Iterable[T]) -> Iterator[Iterable[Optional[T]]]:
    """Collect data into fixed-length chunks or blocks."""
    # https://docs.python.org/3.9/library/itertools.html#itertools-recipes
    args = [iter(iterable)] * chunk_size
    return zip_longest(*args, fillvalue=None)


def jitter_sleep(min_seconds: float, jitter_seconds: float) -> None:
    """Sleep a random amount of seconds within the given parameters.

    Args:
        min_seconds: The minimum time to sleep
        jitter_seconds: The variable sleep time added to the minimum
    """
    sleep(min_seconds + random() * jitter_seconds)  # nosec
