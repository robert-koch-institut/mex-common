import json
import time
from collections.abc import Iterable
from typing import Annotated, Any

import pytest

from mex.common.utils import (
    any_contains_any,
    contains_any,
    get_inner_types,
    grouper,
    jitter_sleep,
)


@pytest.mark.parametrize(
    ("base", "tokens", "expected"),
    [
        ("foo", (), False),
        ("i have foo in it", ("foo", "bar", "batz"), True),
        ("i have none of the tokens ", ("foo", "bar", "batz"), False),
        ((1, 2, 3), (0, 2, 4), True),
    ],
    ids=["empty", "hit", "miss", "numbers"],
)
def test_contains_any(base: Any, tokens: Iterable[Any], expected: bool) -> None:
    assert contains_any(base, tokens) == expected


@pytest.mark.parametrize(
    ("base", "tokens", "expected"),
    [
        (["foo", None], (), False),
        (["i have foo in it", "i dont"], ("foo", "bar", "batz"), True),
        (["i have none of the tokens", "me neither"], ("foo", "bar", "batz"), False),
        (json.loads("[null, [1, 2], [], [3]]"), (0, 2, 4), True),
    ],
    ids=["empty", "hit", "miss", "numbers"],
)
def test_any_contains_any(base: Any, tokens: Iterable[Any], expected: bool) -> None:
    assert any_contains_any(base, tokens) == expected


@pytest.mark.parametrize(
    ("annotation", "expected_types"),
    (
        (str, [str]),
        (None, [type(None)]),
        (str | None, [str, type(None)]),
        (list[str] | None, [str, type(None)]),
        (list[str | int | list[str]], [str, int, str]),
        (Annotated[str | int, "This is a string or integer"], [str, int]),
    ),
)
def test_get_inner_types(annotation: Any, expected_types: list[type]) -> None:
    assert list(get_inner_types(annotation)) == expected_types


def test_grouper() -> None:
    groups = grouper(4, "ABCDEFGHIJ")
    joined = ["".join(c or "-" for c in g) for g in groups]
    assert joined == ["ABCD", "EFGH", "IJ--"]


def test_jitter_sleep() -> None:
    t0 = time.monotonic()
    jitter_sleep(0.1, 0.2)
    t1 = time.monotonic()
    time_slept = t1 - t0

    assert 0.1 < time_slept < 0.3  # giving 100ms of courtesy to pytest
