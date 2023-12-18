from datetime import date, datetime
from typing import Any

import pytest
from pytz import timezone

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
            ("2016-06-10T21:42:24.76073899Z",),
            {},
            "2016-06-10T21:42:24Z",
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
            (
                datetime(
                    2020, 3, 22, 14, 30, 58, tzinfo=timezone("America/Los_Angeles")
                ),
            ),
            {},
            "2020-03-22T22:23:58Z",
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
        "nano seconds",
        "date",
        "datetime",
        "pacific time",
        "timestamp",
    ],
)
def test_timestamp_parsing(
    args: tuple[Any], kwargs: dict[str, Any], expected: str
) -> None:
    timestamp = Timestamp(*args, **kwargs)
    assert str(timestamp) == expected


def test_timestamp_eq() -> None:
    assert Timestamp(2004) == Timestamp("2004")
    assert Timestamp(2004, 11) == Timestamp(2004, 11)
    assert Timestamp(2004, 11, 2) == "2004-11-02"
    assert Timestamp(2020, 3, 22, 14, 30, 58, 0) == datetime(2020, 3, 22, 14, 30, 58, 0)
    assert Timestamp(2005) != object()


def test_timestamp_gt() -> None:
    assert Timestamp(2004) > Timestamp("2003")
    assert Timestamp(2004, 11) < "2013-10-02"
    assert Timestamp(2004, 11) <= Timestamp(2004, 12)
    assert Timestamp(2020, 3, 22, 14, 30, 58) >= datetime(2020, 3, 22, 14, 29)

    with pytest.raises(NotImplementedError):
        assert Timestamp(2005) > object()


def test_timestamp_str() -> None:
    assert str(Timestamp(2004, 11, 26)) == "2004-11-26"


def test_timestamp_repr() -> None:
    assert repr(Timestamp(2018, 3, 2, 13, 0, 1)) == 'Timestamp("2018-03-02T12:00:01Z")'
