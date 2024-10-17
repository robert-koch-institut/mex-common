from datetime import date, datetime
from typing import Any

import pytest
from pydantic import BaseModel
from pytz import timezone

from mex.common.types import (
    CET,
    UTC,
    TemporalEntity,
    TemporalEntityPrecision,
    Year,
    YearMonth,
    YearMonthDay,
    YearMonthDayTime,
)
from mex.common.types.temporal_entity import YEAR_MONTH_DAY_REGEX


@pytest.mark.parametrize(
    ("args", "kwargs", "message"),
    [
        (
            (datetime.now(tz=UTC),),
            {"tzinfo": UTC},
            "Temporal entity does not accept tzinfo in parsing mode",
        ),
        ((0,) * 10, {}, "Temporal entity takes at most 7 arguments"),
        (
            (1.3, "foo", 42),
            {},
            "Temporal entity takes a single str, date, datetime or TemporalEntity "
            "argument or up to 7 integers",
        ),
    ],
)
def test_temporal_entity_type_errors(
    args: tuple[Any], kwargs: dict[str, Any], message: str
) -> None:
    with pytest.raises(TypeError, match=message):
        TemporalEntity(*args, **kwargs)


@pytest.mark.parametrize(
    ("cls", "args", "kwargs", "error"),
    [
        (
            YearMonthDayTime,
            ("2001-04-24",),
            {},
            "Expected precision level to be one of 'hour', 'minute', 'second', 'microsecond'",
        ),
        (
            YearMonthDay,
            ("1999-02",),
            {},
            "Expected precision level to be 'day'",
        ),
        (
            YearMonth,
            ("1999-02",),
            {"precision": TemporalEntityPrecision.DAY},
            "Expected precision level to be 'month'",
        ),
        (
            YearMonthDay,
            ("2022-02-31",),
            {},
            "day is out of range for month",
        ),
        (
            YearMonthDay,
            ("2023-02-29",),
            {},
            "day is out of range for month",
        ),
        (
            YearMonth,
            ("1987-13",),
            {},
            "month must be in 1..12",
        ),
        (
            YearMonthDayTime,
            ("2018-03-02T12:61:01Z",),
            {},
            "minute must be in 0..59",
        ),
    ],
    ids=[
        "too precise",
        "not precise enough",
        "wrong explicit precision",
        "not a valid day in any year",
        "not a valid leap day",
        "not a valid month",
        "not a valid minute",
    ],
)
def test_temporal_entity_value_errors(
    cls: type[TemporalEntity], args: tuple[Any], kwargs: dict[str, Any], error: str
) -> None:
    with pytest.raises(ValueError, match=error):
        cls(*args, **kwargs)


@pytest.mark.parametrize(
    ("cls", "args", "kwargs", "expected"),
    [
        (TemporalEntity, (), {}, 'TemporalEntity("1970")'),
        (TemporalEntity, (2014,), {}, 'TemporalEntity("2014")'),
        (TemporalEntity, (2009, 12), {}, 'TemporalEntity("2009-12")'),
        (TemporalEntity, (1994, 12, 30), {}, 'TemporalEntity("1994-12-30")'),
        (
            TemporalEntity,
            (1999, 1, 20, 22, 58, 17),
            {},
            'TemporalEntity("1999-01-20T21:58:17Z")',
        ),
        (
            TemporalEntity,
            (1999, 1, 20, 22, 58, 17),
            {"tzinfo": CET},
            'TemporalEntity("1999-01-20T21:58:17Z")',
        ),
        (
            TemporalEntity,
            (1999, 1, 20, 22, 58, 17),
            {"tzinfo": UTC},
            'TemporalEntity("1999-01-20T22:58:17Z")',
        ),
        (
            TemporalEntity,
            ("1994-12-30",),
            {},
            'TemporalEntity("1994-12-30")',
        ),
        (
            TemporalEntity,
            ("1999-01-20T22:58:17Z",),
            {},
            'TemporalEntity("1999-01-20T22:58:17Z")',
        ),
        (
            TemporalEntity,
            ("1999-01-20T22",),
            {},
            'TemporalEntity("1999-01-20T21:00:00Z")',
        ),
        (
            TemporalEntity,
            ("2016-06-10T21:42:24.76073899Z",),
            {},
            'TemporalEntity("2016-06-10T21:42:24Z")',
        ),
        (
            TemporalEntity,
            (date(2020, 3, 22),),
            {},
            'TemporalEntity("2020-03-22")',
        ),
        (
            TemporalEntity,
            (datetime(2020, 3, 22, 14, 30, 58, tzinfo=CET),),
            {},
            'TemporalEntity("2020-03-22T13:30:58Z")',
        ),
        (
            TemporalEntity,
            (
                datetime(
                    2020, 3, 22, 14, 30, 58, tzinfo=timezone("America/Los_Angeles")
                ),
            ),
            {},
            'TemporalEntity("2020-03-22T22:23:58Z")',
        ),
        (
            TemporalEntity,
            (TemporalEntity(2004, 11),),
            {},
            'TemporalEntity("2004-11")',
        ),
        (
            YearMonthDayTime,
            (YearMonthDayTime(2004, 11, 21, 19, 59, tzinfo=UTC),),
            {},
            'YearMonthDayTime("2004-11-21T19:59:00Z")',
        ),
        (
            TemporalEntity,
            (datetime(2004, 11, 19, 00, 00, tzinfo=CET),),
            {"precision": TemporalEntityPrecision.DAY},
            'TemporalEntity("2004-11-19")',
        ),
        (
            Year,
            (datetime(2004, 11, 19, 00, 00, tzinfo=CET),),
            {"precision": TemporalEntityPrecision.YEAR},
            'Year("2004")',
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
        "temporal entity",
        "sub class",
        "temporal entity with precision",
        "sub class with precision",
    ],
)
def test_temporal_entity_parsing(
    cls: type[TemporalEntity], args: tuple[Any], kwargs: dict[str, Any], expected: str
) -> None:
    temporal_entity = cls(*args, **kwargs)
    assert repr(temporal_entity) == expected


def test_temporal_entity_eq() -> None:
    assert TemporalEntity(2004) == TemporalEntity("2004")
    assert TemporalEntity(2004, 11) == TemporalEntity(2004, 11)
    assert TemporalEntity(2004, 11, 2) == "2004-11-02"
    assert TemporalEntity(2020, 3, 22, 14, 30, 58, 0, tzinfo=UTC) == datetime(
        2020, 3, 22, 14, 30, 58, 0, tzinfo=UTC
    )
    assert TemporalEntity(2005) != object()


def test_temporal_entity_gt() -> None:
    assert TemporalEntity(2004) > TemporalEntity("2003")
    assert TemporalEntity(2004, 11) < "2013-10-02"
    assert TemporalEntity(2004, 11) <= TemporalEntity(2004, 12)
    assert TemporalEntity(2020, 3, 22, 14, 30, 58, tzinfo=UTC) >= datetime(
        2020, 3, 22, 14, 29, tzinfo=UTC
    )

    with pytest.raises(NotImplementedError):
        assert TemporalEntity(2005) > object()


def test_temporal_entity_str() -> None:
    assert str(TemporalEntity(2004, 11, 26)) == "2004-11-26"
    assert str(YearMonth(2004, 11)) == "2004-11"
    assert str(YearMonthDay(2004, 11, 26)) == "2004-11-26"
    assert str(YearMonthDayTime(2018, 3, 2, 13, 0, 1)) == "2018-03-02T12:00:01Z"


def test_temporal_entity_repr() -> None:
    assert (
        repr(TemporalEntity(2018, 3, 2, 13, 0, 1))
        == 'TemporalEntity("2018-03-02T12:00:01Z")'
    )
    assert repr(Year("2022")) == 'Year("2022")'
    assert repr(YearMonth("2022-10")) == 'YearMonth("2022-10")'
    assert repr(YearMonthDay("2022-10-03")) == 'YearMonthDay("2022-10-03")'
    assert (
        repr(YearMonthDayTime("2018-03-02T12:00:01Z"))
        == 'YearMonthDayTime("2018-03-02T12:00:01Z")'
    )


class DummyModel(BaseModel):
    birthday: YearMonthDay


def test_temporal_entity_schema() -> None:
    assert DummyModel.model_json_schema() == {
        "properties": {
            "birthday": {
                "examples": ["2014-08-24"],
                "pattern": YEAR_MONTH_DAY_REGEX,
                "title": "YearMonthDay",
                "type": "string",
            }
        },
        "required": ["birthday"],
        "title": "DummyModel",
        "type": "object",
    }


DummyModel.model_json_schema()


def test_temporal_entity_serialization() -> None:
    person = DummyModel.model_validate({"birthday": "24th July 1999"})

    assert person.model_dump_json() == '{"birthday":"1999-07-24"}'
