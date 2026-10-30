import pickle
from copy import copy, deepcopy
from datetime import date, datetime, timedelta, timezone
from decimal import InvalidOperation
from typing import Any

import pytest
from pydantic import BaseModel, ValidationError
from pytz import timezone as pytz_timezone

from mex.common.types import (
    UTC,
    TemporalEntity,
    TemporalEntityPrecision,
    TemporalEntityUnion,
    Year,
    YearMonth,
    YearMonthDay,
    YearMonthDayTime,
)
from mex.common.types.temporal_entity import (
    CET,
    DATEUTIL_PARSER,
    YEAR_MONTH_DAY_REGEX,
    _localize,
    _parse_string,
)

CET_tz = pytz_timezone("Europe/Berlin")
PST_tz = pytz_timezone("America/Los_Angeles")


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
            (
                "Temporal entity takes a single str, date, datetime or TemporalEntity "
                "argument or up to 7 integers"
            ),
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
            "Expected precision level to be 'second'",
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
            (
                r"(day is out of range for month)|"
                # python 3.14+ gives us a better error message:
                r"(day 31 must be in range 1\.\.28 for month 2 in year 2022: 2022-02-31)"
            ),
        ),
        (
            YearMonthDay,
            ("2023-02-29",),
            {},
            (
                r"(day is out of range for month)|"
                # python 3.14+ gives us a better error message:
                r"(day 29 must be in range 1\.\.28 for month 2 in year 2023: 2023-02-29)"
            ),
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
        (TemporalEntity, (), {}, 'Year("1970")'),
        (TemporalEntity, (2014,), {}, 'Year("2014")'),
        (TemporalEntity, (2009, 12), {}, 'YearMonth("2009-12")'),
        (TemporalEntity, (1994, 12, 30), {}, 'YearMonthDay("1994-12-30")'),
        (
            TemporalEntity,
            (1994, 12, 30, 10),
            {},
            'YearMonthDayTime("1994-12-30T09:00:00Z")',
        ),
        (
            TemporalEntity,
            (CET_tz.localize(datetime(1999, 1, 20, 22, 58, 17)),),  # noqa: DTZ001
            {},
            'YearMonthDayTime("1999-01-20T21:58:17Z")',
        ),
        (
            TemporalEntity,
            (datetime(1999, 1, 20, 22, 58, 17, tzinfo=UTC),),
            {},
            'YearMonthDayTime("1999-01-20T22:58:17Z")',
        ),
        (
            TemporalEntity,
            ("1994-12-30",),
            {},
            'YearMonthDay("1994-12-30")',
        ),
        (
            TemporalEntity,
            ("1999-01-20T22:58:17Z",),
            {},
            'YearMonthDayTime("1999-01-20T22:58:17Z")',
        ),
        (
            TemporalEntity,
            ("1999-01-20T22",),
            {},
            'YearMonthDayTime("1999-01-20T21:00:00Z")',
        ),
        (
            TemporalEntity,
            ("2016-06-10T21:42:24.76073899Z",),
            {},
            'YearMonthDayTime("2016-06-10T21:42:24Z")',
        ),
        (
            TemporalEntity,
            (date(2020, 3, 22),),
            {},
            'YearMonthDay("2020-03-22")',
        ),
        (
            TemporalEntity,
            (CET_tz.localize(datetime(2020, 3, 22, 14, 30, 58)),),  # noqa: DTZ001
            {},
            'YearMonthDayTime("2020-03-22T13:30:58Z")',
        ),
        (
            TemporalEntity,
            (PST_tz.localize(datetime(2020, 3, 22, 14, 30, 58)),),  # noqa: DTZ001
            {},
            'YearMonthDayTime("2020-03-22T21:30:58Z")',
        ),
        (
            TemporalEntity,
            (TemporalEntity(2004, 11),),
            {},
            'YearMonth("2004-11")',
        ),
        (
            YearMonthDayTime,
            (YearMonthDayTime(2004, 11, 21, 19, 59, tzinfo=UTC),),
            {},
            'YearMonthDayTime("2004-11-21T19:59:00Z")',
        ),
        (
            TemporalEntity,
            (CET_tz.localize(datetime(2004, 11, 19, 0, 0)),),  # noqa: DTZ001
            {"precision": TemporalEntityPrecision.DAY},
            'YearMonthDay("2004-11-19")',
        ),
        (
            Year,
            (CET_tz.localize(datetime(2004, 11, 19, 0, 0)),),  # noqa: DTZ001
            {"precision": TemporalEntityPrecision.YEAR},
            'Year("2004")',
        ),
        (
            TemporalEntity,
            ("2004-11-19",),
            {"precision": TemporalEntityPrecision.SECOND},
            'YearMonthDayTime("2004-11-18T23:00:00Z")',
        ),
    ],
    ids=[
        "empty",
        "year",
        "month",
        "day",
        "hour",
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
        "finer precision",
    ],
)
def test_temporal_entity_parsing(
    cls: type[TemporalEntity], args: tuple[Any], kwargs: dict[str, Any], expected: str
) -> None:
    temporal_entity = cls(*args, **kwargs)
    assert repr(temporal_entity) == expected


@pytest.mark.parametrize(
    ("value", "precision", "expected"),
    [
        (
            datetime(2020, 5, 7, 23, 30, 15, 123456),  # noqa: DTZ001
            TemporalEntityPrecision.SECOND,
            datetime(2020, 5, 7, 21, 30, 15, tzinfo=UTC),
        ),
        (
            datetime(2020, 5, 7, 23, 30, 15, 123456),  # noqa: DTZ001
            TemporalEntityPrecision.DAY,
            datetime(2020, 5, 7),  # noqa: DTZ001
        ),
        (
            datetime(2020, 5, 7, 23, 30),  # noqa: DTZ001
            TemporalEntityPrecision.MONTH,
            datetime(2020, 5, 1),  # noqa: DTZ001
        ),
        (
            datetime(2020, 5, 7, 23, 30),  # noqa: DTZ001
            TemporalEntityPrecision.YEAR,
            datetime(2020, 1, 1),  # noqa: DTZ001
        ),
    ],
)
def test_temporal_entity_truncates_to_precision(
    value: datetime, precision: TemporalEntityPrecision, expected: datetime
) -> None:
    temporal_entity = TemporalEntity(value, precision=precision)
    assert temporal_entity.date_time == expected
    assert temporal_entity == TemporalEntity(str(temporal_entity))


@pytest.mark.parametrize(
    "value",
    ["2020", "2020-05", "2020-05-07", "2020-05-07T10", "2020-05-07T10:30:15.123456"],
)
def test_temporal_entity_round_trip(value: str) -> None:
    temporal_entity = TemporalEntity(value)
    assert TemporalEntity(str(temporal_entity)) == temporal_entity


def test_temporal_entity_eq() -> None:
    assert TemporalEntity(2004) == TemporalEntity("2004")
    assert TemporalEntity(2004) == Year(2004)
    assert TemporalEntity(2004, 11) == TemporalEntity(2004, 11)
    assert TemporalEntity(2004, 11, 2) != "2004-11-02"
    assert TemporalEntity(2004) != YearMonth(2004, 1)
    assert TemporalEntity(2020, 3, 22, 14, 30, 58, tzinfo=UTC) != datetime(
        2020, 3, 22, 14, 30, 58, tzinfo=UTC
    )
    assert TemporalEntity(2005) != object()


def test_temporal_entity_hash() -> None:
    assert len({Year(2004), TemporalEntity("2004"), YearMonth(2004, 1)}) == 2


def test_temporal_entity_ordering() -> None:
    assert TemporalEntity(2004) > TemporalEntity("2003")
    assert TemporalEntity(2004, 11) <= TemporalEntity(2004, 12)
    assert Year(2020) < YearMonthDayTime(2020, 1, 1, 1, tzinfo=UTC)
    assert sorted(
        [
            YearMonthDayTime(2021, 1, 1, 0),
            Year(2021),
            YearMonthDay(2020, 12, 31),
            YearMonth(2021, 1),
        ]
    ) == [
        YearMonthDay(2020, 12, 31),
        Year(2021),
        YearMonth(2021, 1),
        YearMonthDayTime(2021, 1, 1, 0),
    ]

    with pytest.raises(TypeError, match="not supported"):
        assert TemporalEntity(2005) > "2004"


def test_temporal_entity_immutable() -> None:
    temporal_entity = Year(2004)

    with pytest.raises(AttributeError, match="Year is immutable"):
        temporal_entity.precision = TemporalEntityPrecision.DAY
    with pytest.raises(AttributeError, match="Year is immutable"):
        del temporal_entity.date_time

    assert copy(temporal_entity) is temporal_entity
    assert deepcopy(temporal_entity) is temporal_entity
    assert pickle.loads(pickle.dumps(temporal_entity)) == temporal_entity  # noqa: S301


def test_temporal_entity_str() -> None:
    assert str(TemporalEntity(2004, 11, 26)) == "2004-11-26"
    assert str(YearMonth(2004, 11)) == "2004-11"
    assert str(YearMonthDay(2004, 11, 26)) == "2004-11-26"
    assert str(YearMonthDayTime(2018, 3, 2, 13, 0, 1)) == "2018-03-02T12:00:01Z"


def test_temporal_entity_repr() -> None:
    assert (
        repr(TemporalEntity(2018, 3, 2, 13, 0, 1, tzinfo=UTC))
        == 'YearMonthDayTime("2018-03-02T13:00:01Z")'
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


def test_temporal_entity_serialization() -> None:
    person = DummyModel.model_validate({"birthday": "24th July 1999"})

    assert person.model_dump_json() == '{"birthday":"1999-07-24"}'


class DummyUnionModel(BaseModel):
    dates: list[TemporalEntityUnion] = []


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("2020", Year(2020)),
        ("May 2020", YearMonth(2020, 5)),
        (date(2020, 5, 7), YearMonthDay(2020, 5, 7)),
        ("2020-05-07T10:00:00Z", YearMonthDayTime(2020, 5, 7, 10, tzinfo=UTC)),
        (YearMonth(2020, 5), YearMonth(2020, 5)),
    ],
)
def test_temporal_entity_union_validate_python(
    value: object, expected: TemporalEntity
) -> None:
    model = DummyUnionModel.model_validate({"dates": [value]})
    assert model.dates == [expected]
    assert type(model.dates[0]) is type(expected)


def test_temporal_entity_union_parses_once(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def counting_parse(value: str) -> Any:  # noqa: ANN401
        calls.append(value)
        return _parse_string(value)

    monkeypatch.setattr(
        "mex.common.types.temporal_entity._parse_string", counting_parse
    )
    DummyUnionModel.model_validate({"dates": ["2020"]})
    assert calls == ["2020"]


def test_temporal_entity_union_validate_python_error() -> None:
    with pytest.raises(ValidationError) as exc_info:
        DummyUnionModel.model_validate({"dates": ["foo"]})
    assert exc_info.value.error_count() == 1
    assert "Unknown datetime string format" in str(exc_info.value)


def test_temporal_entity_union_validate_json() -> None:
    model = DummyUnionModel.model_validate_json('{"dates": ["2020", "2020-05-07"]}')
    assert model.dates == [Year(2020), YearMonthDay(2020, 5, 7)]

    with pytest.raises(ValidationError, match="String should match pattern"):
        DummyUnionModel.model_validate_json('{"dates": ["May 2020"]}')


def test_temporal_entity_union_schema() -> None:
    schema = DummyUnionModel.model_json_schema()["properties"]["dates"]["items"]
    assert [option["title"] for option in schema["anyOf"]] == [
        "YearMonthDayTime",
        "YearMonthDay",
        "YearMonth",
        "Year",
    ]


@pytest.mark.parametrize(
    ("args", "kwargs", "expected"),
    [
        (("2020-01-07T10:00",), {}, "2020-01-07T09:00:00Z"),
        (("2020-07-07T10:00",), {}, "2020-07-07T08:00:00Z"),
        ((2020, 1, 7, 10, 0), {}, "2020-01-07T09:00:00Z"),
        ((2020, 7, 7, 10, 0), {}, "2020-07-07T08:00:00Z"),
        ((2020, 7, 7, 10, 0), {"tzinfo": pytz_timezone("CET")}, "2020-07-07T08:00:00Z"),
        ((datetime(2020, 1, 7, 10, 0),), {}, "2020-01-07T09:00:00Z"),  # noqa: DTZ001
        ((datetime(2020, 7, 7, 10, 0),), {}, "2020-07-07T08:00:00Z"),  # noqa: DTZ001
    ],
    ids=[
        "winter string",
        "summer string",
        "winter integers",
        "summer integers",
        "summer integers with pytz tzinfo",
        "winter datetime",
        "summer datetime",
    ],
)
def test_temporal_entity_localizes_to_cet(
    args: tuple[Any, ...], kwargs: dict[str, Any], expected: str
) -> None:
    assert str(TemporalEntity(*args, **kwargs)) == expected


@pytest.mark.parametrize(
    ("value", "expected", "resolution"),
    [
        # ISO 8601
        ("2020", "2020-01-01T00:00:00+01:00", "year"),
        ("2020-05", "2020-05-01T00:00:00+02:00", "month"),
        ("2020-05-07", "2020-05-07T00:00:00+02:00", "day"),
        ("2020-02-29", "2020-02-29T00:00:00+01:00", "day"),
        ("2020-05-07T10", "2020-05-07T10:00:00+02:00", "second"),
        ("2020-05-07T10Z", "2020-05-07T10:00:00+00:00", "second"),
        ("2020-05-07 10:30", "2020-05-07T10:30:00+02:00", "second"),
        ("2020-05-07T10:30+01", "2020-05-07T10:30:00+01:00", "second"),
        ("2020-05-07T10:30-0130", "2020-05-07T10:30:00-01:30", "second"),
        ("2020-05-07T10:30:15", "2020-05-07T10:30:15+02:00", "second"),
        ("2020-05-07T10:30:15.1", "2020-05-07T10:30:15+02:00", "second"),
        ("2020-05-07T10:30:15,1234", "2020-05-07T10:30:15+02:00", "second"),
        (
            "2020-05-07T10:30:15.123456789",
            "2020-05-07T10:30:15+02:00",
            "second",
        ),
        (
            " 2020-05-07T10:30:15.000Z ",
            "2020-05-07T10:30:15+00:00",
            "second",
        ),
        ("2020-05-07T10:30:15 +01:30", "2020-05-07T10:30:15+01:30", "second"),
        # German numeric dates
        ("5.7.2020", "2020-07-05T00:00:00+02:00", "day"),
        ("05.07.2020", "2020-07-05T00:00:00+02:00", "day"),
        ("5. 7. 2020", "2020-07-05T00:00:00+02:00", "day"),
        ("05.07.20", "2020-07-05T00:00:00+02:00", "day"),
        ("05.07.99", "1999-07-05T00:00:00+02:00", "day"),
        ("07.2020", "2020-07-01T00:00:00+02:00", "month"),
        # free-form via dateutil
        ("20200507", "2020-05-07T00:00:00+02:00", "day"),
        ("2020-05-07T1030", "2020-05-07T10:30:00+02:00", "second"),
        ("2020-05-07T10:30:15 -5", "2020-05-07T10:30:15-05:00", "second"),
        ("2020/05/07", "2020-05-07T00:00:00+02:00", "day"),
        ("05/07/2020", "2020-05-07T00:00:00+02:00", "day"),
        ("13/07/2020", "2020-07-13T00:00:00+02:00", "day"),
        ("05-2020", "2020-05-01T00:00:00+02:00", "month"),
        ("May 2005", "2005-05-01T00:00:00+02:00", "month"),
        ("may-2005", "2005-05-01T00:00:00+02:00", "month"),
        ("Jan 1 1990", "1990-01-01T00:00:00+01:00", "day"),
        ("7 May 08", "2008-05-07T00:00:00+02:00", "day"),
        ("7th of May 2020 10:30", "2020-05-07T10:30:00+02:00", "second"),
        ("May 7 2020 10:30:15", "2020-05-07T10:30:15+02:00", "second"),
        ("May 7 2020 10:30:15.000", "2020-05-07T10:30:15+02:00", "second"),
        (
            "May 7 2020 10:30:15.123456",
            "2020-05-07T10:30:15+02:00",
            "second",
        ),
        ("May 7 2020 10:30 Z", "2020-05-07T10:30:00+00:00", "second"),
        ("May 7 2020 10:30 UTC", "2020-05-07T10:30:00+00:00", "second"),
        ("May 7 2020 10:30 +0130", "2020-05-07T10:30:00+01:30", "second"),
        ("May 7 2020 10:30 GMT+3", "2020-05-07T10:30:00-03:00", "second"),  # POSIX
        # German month names
        ("4. März '08", "2008-03-04T00:00:00+01:00", "day"),
        ("4. Mär. 2008", "2008-03-04T00:00:00+01:00", "day"),
        ("4. Maerz 2008", "2008-03-04T00:00:00+01:00", "day"),
        ("März 2008", "2008-03-01T00:00:00+01:00", "month"),
        ("Mai 2008", "2008-05-01T00:00:00+02:00", "month"),
        ("1. Okt. 2008", "2008-10-01T00:00:00+02:00", "day"),
        ("24. Dezember 2008", "2008-12-24T00:00:00+01:00", "day"),
    ],
)
def test_parse_string(value: str, expected: str, resolution: str) -> None:
    parsed, precision = _parse_string(value)
    assert parsed.isoformat() == expected
    assert precision.value == resolution


@pytest.mark.parametrize(
    ("value", "error"),
    [
        ("", "without four-digit year: $"),
        ("999", "without four-digit year: 999"),
        ("12.20", "without four-digit year: 12.20"),
        ("10:30", "without four-digit year: 10:30"),
        ("Monday 10:30", "without four-digit year: Monday 10:30"),
        ("-2020", "with leading sign: -2020"),
        ("-2020-01-01", "with leading sign: -2020-01-01"),
        ("+5000", r"with leading sign: \+5000"),
        ("foo", "Unknown datetime string format, unable to parse: foo"),
        ("NaT", "Unknown datetime string format, unable to parse: NaT"),
        ("2Q2005", "Unknown datetime string format, unable to parse: 2Q2005"),
        (
            "31.12.2020 (31.08.2021)",
            r"Unknown datetime string format, unable to parse: 31\.12\.2020 \(",
        ),
        ("0000-01-01", r"year (0 is out of range|must be in 1\.\.9999, not 0)"),
        ("2020-13", "month must be in 1..12, not 13: 2020-13"),
        ("2020-02-30", "day 30 must be in range 1..29 .*: 2020-02-30"),
        ("2020-05-07T24", "hour must be in 0..23.*: 2020-05-07T24"),
        ("31.02.2020", r"day 31 must be in range 1..29 .*: 31\.02\.2020"),
        ("13/13/2020", "month must be in 1..12, not 13: 13/13/2020"),
        ("May 32 2020", "day 32 must be in range 1..31 .*: May 32 2020"),
        ("08335394550", "08335394550"),
        ("2020-05-07T10:30+24", "offset must be a timedelta strictly between"),
        ("May 7 2020 10:30 +2400", "offset must be a timedelta strictly between"),
        ("May 7 2020 10:30 CEST", 'Unknown timezone "CEST" in datetime string'),
    ],
)
def test_parse_string_error(value: str, error: str) -> None:
    with pytest.raises(ValueError, match=error):
        _parse_string(value)


def test_parse_string_invalid_operation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _parse(*_: object, **__: object) -> None:
        raise InvalidOperation

    monkeypatch.setattr(DATEUTIL_PARSER, "_parse", _parse)
    with pytest.raises(ValueError, match="Unknown datetime string format"):
        _parse_string("May 7 2020")


@pytest.mark.parametrize(
    ("value", "offset"),
    [
        # naive datetimes are localized to CET or CEST
        ("2020-01-07T10:30", timedelta(hours=1)),
        ("2020-07-07T10:30", timedelta(hours=2)),
        ("7.1.2020", timedelta(hours=1)),
        ("Jul 7 2020", timedelta(hours=2)),
        # non-existent and ambiguous times are resolved to daylight saving time
        ("2020-03-29T02:30", timedelta(hours=2)),
        ("2020-10-25T02:30", timedelta(hours=2)),
        # explicit offsets are kept
        ("2020-07-07T10:30Z", timedelta(0)),
        ("2020-07-07T10:30+05:00", timedelta(hours=5)),
    ],
)
def test_parse_string_localization(value: str, offset: timedelta) -> None:
    parsed, _ = _parse_string(value)
    assert parsed.utcoffset() == offset


@pytest.mark.parametrize(
    ("tz", "expected"),
    [
        (CET, "2020-07-07T10:30:00+02:00"),
        (pytz_timezone("Europe/London"), "2020-07-07T10:30:00+01:00"),
        (UTC, "2020-07-07T10:30:00+00:00"),
        (timezone(timedelta(hours=-3)), "2020-07-07T10:30:00-03:00"),
    ],
)
def test_localize(tz: timezone, expected: str) -> None:
    assert _localize(datetime(2020, 7, 7, 10, 30), tz).isoformat() == expected  # noqa: DTZ001
