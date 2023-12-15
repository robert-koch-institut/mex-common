from datetime import date, datetime
from typing import Any

import pytest

from mex.common.types import CET, UTC, Timestamp


@pytest.mark.parametrize(
    ("args", "kwargs", "message"),
    [
        (
            (datetime.now(),),
            {"tzinfo": UTC},
            "Timestamp does not accept tzinfo in parsing mode",
        ),
        ((0,) * 10, {}, "Timestamp takes at most 7 arguments"),
        (
            (1.3, "foo", 42),
            {},
            "Timestamp takes a single str, date, datetime or Timestamp argument or up to 7 integers",
        ),
    ],
)
def test_timestamp_parsing_errors(
    args: tuple[Any], kwargs: dict[str, Any], message: str
) -> None:
    with pytest.raises(TypeError, match=message):
        Timestamp(*args, **kwargs)


@pytest.mark.parametrize(
    ("value", "message"),
    [(object(), "Cannot parse <class 'object'> as Timestamp")],
)
def test_timestamp_validation_errors(value: Any, message: str) -> None:
    with pytest.raises(TypeError, match=message):
        Timestamp.validate(value)


@pytest.mark.parametrize(
    ("args", "kwargs", "expected"),
    [
        ((), {}, "1970"),
        ((2014,), {}, "2014"),
        ((2009, 12), {}, "2009-12"),
        ((1994, 12, 30), {}, "1994-12-30"),
        ((1999, 1, 20, 22, 58, 17), {}, "1999-01-20T21:58:17Z"),
        ((1999, 1, 20, 22, 58, 17), {"tzinfo": CET}, "1999-01-20T21:58:17Z"),
        ((1999, 1, 20, 22, 58, 17), {"tzinfo": UTC}, "1999-01-20T22:58:17Z"),
        (("1994-12-30",), {}, "1994-12-30"),
        (
            ("1999-01-20T22:58:17Z",),
            {},
            "1999-01-20T22:58:17Z",
        ),
        (
            ("1999-01-20T22",),
            {},
            "1999-01-20T21:00:00Z",
        ),
        (
            (date(2020, 3, 22),),
            {},
            "2020-03-22",
        ),
        (
            (datetime(2020, 3, 22, 14, 30, 58),),
            {},
            "2020-03-22T13:30:58Z",
        ),
        (
            (Timestamp(2004, 11),),
            {},
            "2004-11",
        ),
    ],
    ids=[
        "empty",
        "year",
        "month",
        "day",
        "time",
        "cet time",
        "utc time",
        "date string",
        "time string",
        "padded time",
        "date",
        "datetime",
        "timestamp",
    ],
)
def test_timestamp_parsing(
    args: tuple[Any], kwargs: dict[str, Any], expected: str
) -> None:
    timestamp = Timestamp(*args, **kwargs)
    assert str(timestamp) == expected
