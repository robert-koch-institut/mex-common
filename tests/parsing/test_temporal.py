from datetime import UTC, datetime, timedelta
from decimal import InvalidOperation

import pytest
from dateutil.parser import parser
from dateutil.tz import tzoffset

from mex.common.parsing.temporal import (
    _looks_like_datetime,
    _parse_dateabbr_string,
    _parse_iso_8601,
    parse_datetime_string_with_resolution,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", True),
        ("0.5", True),
        ("a", False),
        ("T", False),
        ("999", False),
        ("1000", True),
        (" 999.99 ", False),
        ("-5000", False),
        ("1e3", True),
        ("1E2", False),
        ("1e", True),
        ("1e+", True),
        ("12345678901234567890e-16", True),
        ("12345678901234567890e-17", False),
        ("1" + "0" * 30 + ".5e-28", False),  # decimals dropped after 17 digits
        ("9e308", True),
        ("1e-2000", True),
        ("1e2000", True),
        ("-1e300e", True),
        ("2020-01-01", True),
    ],
)
def test_looks_like_datetime(value: str, expected: bool) -> None:  # noqa: FBT001
    assert _looks_like_datetime(value, value.encode()) is expected


@pytest.mark.parametrize(
    ("value", "expected", "resolution"),
    [
        ("2020", "2020-01-01T00:00:00+01:00", "year"),
        ("2020-05", "2020-05-01T00:00:00+02:00", "month"),
        ("2020-5-7", "2020-05-07T00:00:00+02:00", "day"),
        ("2020\\05\\07", "2020-05-07T00:00:00+02:00", "day"),
        ("20200507", "2020-05-07T00:00:00+02:00", "day"),
        ("2020-02-29", "2020-02-29T00:00:00+01:00", "day"),
        ("2020-05-07T10", "2020-05-07T10:00:00+02:00", "hour"),
        ("2020-05-07T10Z", "2020-05-07T10:00:00+00:00", "hour"),
        ("2020-05-07 10:30", "2020-05-07T10:30:00+02:00", "minute"),
        ("2020-05-07T1030", "2020-05-07T10:30:00+02:00", "minute"),
        ("2020-05-07T10:3", "2020-05-07T10:03:00+02:00", "minute"),
        ("2020-05-07T10:30Z", "2020-05-07T10:30:00+00:00", "minute"),
        ("2020-05-07T10:30:15", "2020-05-07T10:30:15+02:00", "second"),
        ("2020-05-07T103015", "2020-05-07T10:30:15+02:00", "second"),
        ("2020-05-07T10:30:15.1", "2020-05-07T10:30:15.100000+02:00", "microsecond"),
        ("2020-05-07T10:30:15.1234", "2020-05-07T10:30:15.123400+02:00", "microsecond"),
        (
            "2020-05-07T10:30:15.123456789",
            "2020-05-07T10:30:15.123456+02:00",
            "microsecond",
        ),
        (
            "2020-05-07T10:30:15.123456789012345678",
            "2020-05-07T10:30:15.123456+02:00",
            "microsecond",
        ),
        (
            "2262-04-11T22:47:16.854775807-01:00",
            "2262-04-11T22:47:16.854775-01:00",
            "microsecond",
        ),
        (" 2020-05-07T10:30:15+01:30 ", "2020-05-07T10:30:15+01:30", "second"),
        ("2020-05-07T10:30:15 -5", "2020-05-07T10:30:15-05:00", "second"),
        ("05/07/2020", "2020-05-07T00:00:00+02:00", "day"),
        ("13/07/2020", "2020-07-13T00:00:00+02:00", "day"),
        ("5.7.2020", "2020-05-07T00:00:00+02:00", "day"),
        ("5-07-2020", "2020-05-07T00:00:00+02:00", "day"),
        ("05 7 2020", "2020-05-07T00:00:00+02:00", "day"),
        ("05-2020", "2020-05-01T00:00:00+02:00", "month"),
        ("May 2005", "2005-05-01T00:00:00+02:00", "month"),
        ("may-2005", "2005-05-01T00:00:00+02:00", "month"),
        ("May 7 2020", "2020-05-07T00:00:00+02:00", "day"),
        ("7th of May 2020 10:30", "2020-05-07T10:30:00+02:00", "minute"),
        ("10:30", "0001-01-01T10:30:00+00:18", "minute"),
        ("May 7 2020 10:30:15.000", "2020-05-07T10:30:15+02:00", "microsecond"),
        (
            "May 7 2020 10:30:15.120000",
            "2020-05-07T10:30:15.120000+02:00",
            "microsecond",
        ),
        (
            "May 7 2020 10:30:15.1200000",
            "2020-05-07T10:30:15.120000+02:00",
            "microsecond",
        ),
        (
            "May 7 2020 10:30:15.123456",
            "2020-05-07T10:30:15.123456+02:00",
            "microsecond",
        ),
        ("May 7 2020 10:30:15", "2020-05-07T10:30:15+02:00", "second"),
        ("May 7 2020 10:30 Z", "2020-05-07T10:30:00+00:00", "minute"),
        ("May 7 2020 10:30 +0130", "2020-05-07T10:30:00+01:30", "minute"),
    ],
)
def test_parse_datetime_string_with_resolution(
    value: str, expected: str, resolution: str
) -> None:
    parsed, parsed_resolution = parse_datetime_string_with_resolution(value)
    assert isinstance(parsed, datetime)
    assert parsed.isoformat() == expected
    assert parsed_resolution == resolution


def test_parse_datetime_string_with_resolution_dateutil_tzoffset() -> None:
    parsed, _ = parse_datetime_string_with_resolution("May 7 2020 10:30 GMT+3")
    assert parsed.tzinfo == tzoffset(None, -10800)


@pytest.mark.parametrize(
    ("value", "error"),
    [
        ("999", 'Given date string "999" not likely a datetime'),
        ("-2020", 'Given date string "-2020" not likely a datetime'),
        ("a", 'Given date string "a" not likely a datetime'),
        ("", "Unable to parse datetime string: "),
        ("foo", "Unknown datetime string format, unable to parse: foo"),
        ("NaT", "NaTType does not support astimezone"),
        ("nan", "NaTType does not support astimezone"),
        ("13/13/2020", r"Invalid date specified \(13/13\)"),
        (
            "5Q2005",
            "Incorrect quarterly string is given, quarter must be between 1 and 4: 5Q2005",
        ),
        (
            "05-QX",
            "Incorrect quarterly string is given, quarter must be between 1 and 4: 05-QX",
        ),
        ("2Q2005", "'quarter' is not a valid TemporalEntityPrecision"),
        ("2q-2005", "'quarter' is not a valid TemporalEntityPrecision"),
        ("1Q05", "'quarter' is not a valid TemporalEntityPrecision"),
        ("05Q3", "'quarter' is not a valid TemporalEntityPrecision"),
        ("05-Q3", "'quarter' is not a valid TemporalEntityPrecision"),
        ("2005Q4", "'quarter' is not a valid TemporalEntityPrecision"),
        ("2005-Q4", "'quarter' is not a valid TemporalEntityPrecision"),
        ("0000-01-01", r"(year 0 is out of range)|(year must be in 1\.\.9999, not 0)"),
        (
            "0000-01-01T00:00:00.000000001",
            "Out of bounds nanosecond timestamp: 0-01-01 00:00:00",
        ),
        (
            "1500-01-01T00:00:00.000000001",
            "Out of bounds nanosecond timestamp: 1500-01-01 00:00:00",
        ),
        (
            "2262-04-11T23:47:16.8547758070001",
            "Out of bounds nanosecond timestamp: 2262-04-11 23:47:16",
        ),
        (
            "2262-04-11T23:47:16.854775807-01:00",
            "Converting 2262-04-11 23:47:16 overflows past 2262-04-11 23:47:16.854775807",
        ),
        (
            "1677-09-21T00:12:43.145224193+01:00",
            "Converting 1677-09-21 00:12:43 underflows past 1677-09-21 00:12:43.145224193",
        ),
        (
            "Monday 10:30",
            "Parsing datetimes with weekday but no day information is not supported",
        ),
        ("08335394550", 'Parsing "08335394550" to datetime overflows'),
        (
            "May 7 2020 10:30 FOO",
            'Parsed string "May 7 2020 10:30 FOO" included an un-recognized timezone "FOO".',
        ),
        (
            "May 7 2020 10:30 +2400",
            r'Parsed string "May 7 2020 10:30 \+2400" gives an invalid tzoffset',
        ),
        ("\ud800", "surrogates not allowed"),
    ],
)
def test_parse_datetime_string_with_resolution_error(value: str, error: str) -> None:
    with pytest.raises(ValueError, match=error):
        parse_datetime_string_with_resolution(value)


def test_parse_datetime_string_with_resolution_day_out_of_range() -> None:
    with pytest.raises(ValueError, match=r"day .*range.*: May 32 2020 10:30$"):
        parse_datetime_string_with_resolution("May 32 2020 10:30")


def test_parse_datetime_string_with_resolution_local_timezone(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("time.tzset", lambda: None)  # strptime would reset tzname
    monkeypatch.setattr("time.tzname", ("CET", "CEST"))
    with pytest.raises(ValueError, match="Parsing 'CET' as tzlocal"):
        parse_datetime_string_with_resolution("May 7 2020 10:30 CET")

    monkeypatch.setattr("time.tzname", ("UTC", "UTC"))
    parsed, _ = parse_datetime_string_with_resolution("May 7 2020 10:30 UTC")
    assert parsed.tzinfo is UTC


def test_parse_datetime_string_with_resolution_invalid_operation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _parse(*_: object, **__: object) -> None:
        raise InvalidOperation

    monkeypatch.setattr(parser, "_parse", _parse)
    with pytest.raises(ValueError, match="Unknown datetime string format"):
        parse_datetime_string_with_resolution("May 7 2020")


@pytest.mark.parametrize(
    "value",
    [
        "-",
        "2020-13",
        "202001",
        "2020-02-30",
        "2020-01/01",
        "2020-01-",
        "2020-01-01X",
        "2020-01-01T",
        "2020-01-01Tx",
        "2020-01-01T1",
        "2020-01-01T25",
        "2020-01-01T1Z",
        "2020-01-01T10:",
        "2020-01-01T10:61",
        "2020-01-01T103",
        "2020-01-01T10:30:",
        "2020-01-01T10:30:61",
        "2020-01-01T10305",
        "2020-01-01T10:30+",
        "2020-01-01T10:30+25",
        "2020-01-01T10:30+01:",
        "2020-01-01T10:30 x",
    ],
)
def test_parse_iso_8601_rejected(value: str) -> None:
    assert _parse_iso_8601(value.encode()) is None


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("-2020-01-01", ([-2020, 1, 1, 0, 0, 0, 0], "day", None)),
        ("2020-01-01T10:30+0130", ([2020, 1, 1, 10, 30, 0, 0], "minute", 90)),
        ("2020-01-01T10:30+01:3", ([2020, 1, 1, 10, 30, 0, 0], "minute", 63)),
        ("2020-01-01T10:30-1:30 ", ([2020, 1, 1, 10, 30, 0, 0], "minute", -90)),
    ],
)
def test_parse_iso_8601_quirks(
    value: str, expected: tuple[list[int], str, int | None]
) -> None:
    assert _parse_iso_8601(value.encode()) == expected


@pytest.mark.parametrize("value", ["ABCD", "XXQ1", "1Q1X", "0000Q1"])
def test_parse_dateabbr_string_rejected(value: str) -> None:
    assert _parse_dateabbr_string(value) is None


@pytest.mark.parametrize(
    ("value", "offset"),
    [
        # naive datetimes are localized to CET or CEST
        ("2020-01-07T10:30:15.123456789", timedelta(hours=1)),
        ("2020-07-07T10:30:15.123456789", timedelta(hours=2)),
        # non-existent and ambiguous times are resolved to daylight saving time
        ("2020-03-29T02:30:00.000000001", timedelta(hours=2)),
        ("2020-10-25T02:30:00.000000001", timedelta(hours=2)),
        # all other naive datetimes are localized the same way
        ("2020-07-07T10:30:15.123456", timedelta(hours=2)),
        ("May 7 2020 10:30:15.1234567", timedelta(hours=2)),
        ("2020-01-07", timedelta(hours=1)),
        # before time zones were introduced, local mean time is used
        ("10:30", timedelta(minutes=18)),
        # localizing within int64 nanosecond bounds works
        ("1677-09-21T00:30:43.145224192", timedelta(minutes=18)),
        ("2262-04-11T23:47:16.854775807", timedelta(hours=1)),
        # explicit offsets are kept
        ("2020-07-07T10:30:15.123456789Z", timedelta(0)),
        ("2020-07-07T10:30:15.123456789+05:00", timedelta(hours=5)),
    ],
)
def test_parse_datetime_string_with_resolution_localization(
    value: str, offset: timedelta
) -> None:
    parsed, _ = parse_datetime_string_with_resolution(value)
    assert parsed.utcoffset() == offset


@pytest.mark.parametrize(
    "value",
    ["1677-09-21T00:30:43.145224191", "1677-09-21T00:12:43.145224193"],
)
def test_parse_datetime_string_with_resolution_localization_overflow(
    value: str,
) -> None:
    with pytest.raises(OverflowError, match="Python int too large to convert"):
        parse_datetime_string_with_resolution(value)
