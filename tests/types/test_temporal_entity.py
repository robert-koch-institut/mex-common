from datetime import date, datetime
from typing import Any

import pytest
from pandas._libs.tslibs.parsing import DateParseError
from pytz import timezone

from mex.common.types import (
    CET,
    UTC,
    TemporalEntity,
    TemporalEntityPrecision,
    YearMonth,
    YearMonthDay,
    YearMonthDayTime,
)


@pytest.mark.parametrize(
    ("args", "kwargs", "message"),
    [
        (
            (datetime.now(),),
            {"tzinfo": UTC},
            "Temporal entity does not accept tzinfo in parsing mode",
        ),
        ((0,) * 10, {}, "Temporal entity takes at most 7 arguments"),
        (
            (1.3, "foo", 42),
            {},
            "Temporal entity takes a single str, date, datetime or TemporalEntity argument or up to 7 integers",
        ),
    ],
)
def test_timestamp_parsing_errors(
    args: tuple[Any], kwargs: dict[str, Any], message: str
) -> None:
    with pytest.raises(TypeError, match=message):
        TemporalEntity(*args, **kwargs)


@pytest.mark.parametrize(
    ("value", "message"),
    [(object(), "Cannot parse <class 'object'> as TemporalEntity")],
)
def test_timestamp_validation_errors(value: Any, message: str) -> None:
    with pytest.raises(TypeError, match=message):
        TemporalEntity.validate(value)


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
            (TemporalEntity(2004, 11),),
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
    timestamp = TemporalEntity(*args, **kwargs)
    assert str(timestamp) == expected


def test_timestamp_eq() -> None:
    assert TemporalEntity(2004) == TemporalEntity("2004")
    assert TemporalEntity(2004, 11) == TemporalEntity(2004, 11)
    assert TemporalEntity(2004, 11, 2) == "2004-11-02"
    assert TemporalEntity(2020, 3, 22, 14, 30, 58, 0) == datetime(
        2020, 3, 22, 14, 30, 58, 0
    )
    assert TemporalEntity(2005) != object()


def test_timestamp_gt() -> None:
    assert TemporalEntity(2004) > TemporalEntity("2003")
    assert TemporalEntity(2004, 11) < "2013-10-02"
    assert TemporalEntity(2004, 11) <= TemporalEntity(2004, 12)
    assert TemporalEntity(2020, 3, 22, 14, 30, 58) >= datetime(2020, 3, 22, 14, 29)

    with pytest.raises(NotImplementedError):
        assert TemporalEntity(2005) > object()


def test_timestamp_str() -> None:
    assert str(TemporalEntity(2004, 11, 26)) == "2004-11-26"
    assert str(YearMonth(2004, 11)) == "2004-11"
    assert str(YearMonthDay(2004, 11, 26)) == "2004-11-26"
    assert str(YearMonthDayTime(2018, 3, 2, 13, 0, 1)) == "2018-03-02T12:00:01Z"


def test_timestamp_repr() -> None:
    assert (
        repr(TemporalEntity(2018, 3, 2, 13, 0, 1))
        == 'TemporalEntity("2018-03-02T12:00:01Z")'
    )

    assert repr(YearMonth("2022")) == 'YearMonth("2022")'

    assert repr(YearMonthDay("2022-10-03")) == 'YearMonthDay("2022-10-03")'

    assert (
        repr(YearMonthDayTime("2018-03-02T12:00:01Z"))
        == 'YearMonthDayTime("2018-03-02T12:00:01Z")'
    )


def test_invalid_temporal_resolution_throws_error() -> None:
    with pytest.raises(
        ValueError,
        match="Expected precision level to be one of "
        "'hour', 'minute', 'second', 'microsecond'",
    ):
        YearMonthDayTime("2001-04-24")

    with pytest.raises(ValueError, match="Expected precision level to be 'day'"):
        YearMonthDay("1999-02")

    with pytest.raises(
        ValueError, match="Expected precision level to be one of " "'year', 'month'"
    ):
        YearMonth("1999-02-02")


def test_invalid_dates_throw_error() -> None:
    with pytest.raises(DateParseError):
        YearMonthDay("2022-02-31")

    with pytest.raises(DateParseError):
        YearMonthDay("2023-02-29")  # not a leap year

    with pytest.raises(DateParseError):
        YearMonth("1987-13")

    with pytest.raises(DateParseError):
        YearMonthDayTime("2018-03-02T12:61:01Z")


def test_apply_precision() -> None:
    temporal_entity = TemporalEntity(date(2022, 12, 25))
    temporal_entity.apply_precision(TemporalEntityPrecision.DAY)

    assert temporal_entity.date_time == datetime(2022, 12, 25, 0, 0)
    assert temporal_entity.precision == TemporalEntityPrecision.DAY
