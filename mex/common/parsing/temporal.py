# This module contains code ported from the following projects, all licensed under
# the BSD 3-Clause License:
#
# - pandas: pandas/_libs/tslibs/parsing.pyx and np_datetime.pyx
#   Copyright (c) 2008-2011, AQR Capital Management, LLC, Lambda Foundry, Inc. and
#   PyData Development Team. All rights reserved.
#   Copyright (c) 2011-2026, Open source contributors.
#
# - NumPy datetime parsing, as vendored by pandas in
#   pandas/_libs/src/vendored/numpy/datetime/np_datetime_strings.c
#   Copyright (c) 2005-2023, NumPy Developers. All rights reserved.
#   Copyright (c) 2011 by Enthought, Inc.
#   Copyright (c) 2016, PyData Development Team. All rights reserved.
#
# - xstrtod, as included in pandas (pandas/_libs/src/parser/tokenizer.c)
#   Copyright (C) 2002 Michael Ringgaard. All rights reserved.
#   Modifications by Warren Weckesser (2011) and Richard T Guy (2013).
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Parsing of temporal entity strings into timezone-aware datetimes and resolutions.

Behaves like pandas' `parse_datetime_string_with_reso` with `freq=None,
dayfirst=False, yearfirst=True` (as of pandas 3.0.6) followed by localizing naive
results to "CET". The vendored numpy ISO 8601 parser and pandas' `xstrtod` are ported
byte-by-byte to keep their exact quirks; branches unreachable with these arguments
and resolutions that are no valid `TemporalEntityPrecision` are pruned.
"""

import re
import time
from datetime import UTC, datetime, timedelta, timezone, tzinfo
from decimal import InvalidOperation
from math import inf
from typing import Literal

from dateutil.parser import DEFAULTPARSER
from dateutil.tz import tzoffset, tzutc
from pytz import BaseTzInfo
from pytz import timezone as pytz_timezone

Resolution = Literal["year", "month", "day", "hour", "minute", "second", "microsecond"]
IsoUnit = Resolution | Literal["nanosecond"]  # internal marker for >6 fraction digits

CET = pytz_timezone("CET")  # default assumed timezone
DEFAULT_DATETIME = datetime(1, 1, 1)  # noqa: DTZ001
NOT_DATELIKE_STRINGS = {"a", "A", "m", "M", "p", "P", "t", "T"}
NAT_STRINGS = {"NaT", "nat", "NAT", "nan", "NaN", "NAN"}
DIGITS = b"0123456789"
SPACES = b" \t\n\v\f\r"
DELIMITERS = b" /-.\0"  # C `strchr` also matches the terminating NUL
YMD_SEPARATORS = b"-./\\ "
DAYS_PER_MONTH = (
    (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31),
    (31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31),
)
SUBSECOND_PATTERN = re.compile(r"\d:\d{2}:\d{2}\.(?P<frac>\d+)")
NANOSECOND_BOUNDS = (  # fractions of a second in attoseconds
    (1677, 9, 21, 0, 12, 43, 145224193 * 10**9),
    (2262, 4, 11, 23, 47, 16, 854775807 * 10**9),
)
INT64_NANOSECOND_MINIMUM = (  # utc datetime and remaining nanoseconds
    datetime(1677, 9, 21, 0, 12, 43, 145224),  # noqa: DTZ001
    192,
)
DATEUTIL_ATTRIBUTES: tuple[Resolution, ...] = (
    "year",
    "month",
    "day",
    "hour",
    "minute",
    "second",
    "microsecond",
)


def _strtod(buf: bytes) -> tuple[float | None, int]:  # noqa: C901, PLR0912
    """Port of pandas' `xstrtod`, returns the number (None on error) and end index."""
    s, i = buf + b"\0", 0
    while s[i] in SPACES:
        i += 1
    negative = s[i] == ord("-")
    if s[i] in b"+-":
        i += 1
    number, exponent, num_digits, num_decimals = 0.0, 0, 0, 0
    while s[i] in DIGITS:
        number, i, num_digits = number * 10.0 + (s[i] - 48), i + 1, num_digits + 1
    if s[i] == ord("."):
        i += 1
        while num_digits < 17 and s[i] in DIGITS:  # noqa: PLR2004
            number, i, num_digits = number * 10.0 + (s[i] - 48), i + 1, num_digits + 1
            num_decimals += 1
        if num_digits >= 17:  # noqa: PLR2004
            while s[i] in DIGITS:
                i += 1
        exponent -= num_decimals
    if num_digits == 0:
        return None, i
    if negative:
        number = -number
    if s[i] in b"eE":
        i += 1
        negative = s[i] == ord("-")
        if s[i] in b"+-":
            i += 1
        power, num_digits = 0, 0
        while num_digits < 8 and s[i] in DIGITS:  # noqa: PLR2004
            power, i, num_digits = power * 10 + (s[i] - 48), i + 1, num_digits + 1
        exponent += -power if negative else power
        if num_digits == 0:
            i -= 1
    if not -1021 <= exponent <= 1024:  # noqa: PLR2004
        return None, i
    p10, power = 10.0, abs(exponent)
    while power:
        if power & 1:
            number = number / p10 if exponent < 0 else number * p10
        power >>= 1
        p10 *= p10
    if number == inf:
        return None, i
    while s[i] in SPACES:
        i += 1
    return number, i


def _looks_like_datetime(value: str, buf: bytes) -> bool:
    """Port of `_does_string_look_like_datetime`."""
    if not buf or buf[0] == ord("0"):
        return True
    if value in NOT_DATELIKE_STRINGS:
        return False
    number, end = _strtod(buf)
    if number is not None and end == len(buf):
        return number >= 1000  # noqa: PLR2004
    return True


def _parse_iso_time(  # noqa: C901, PLR0911, PLR0912
    s: bytes, i: int, n: int, parts: list[int]
) -> tuple[int, IsoUnit] | None:
    """Parse `H[H][[:]MM[[:]SS[.fffffffff...]]]` into parts, return index and unit."""
    if s[i] not in DIGITS:
        return None
    parts[3], i = s[i] - 48, i + 1
    two_digit_hour = s[i] in DIGITS
    if two_digit_hour:
        parts[3], i = parts[3] * 10 + s[i] - 48, i + 1
        if parts[3] >= 24:  # noqa: PLR2004
            return None
    if i == n:
        return (i, "hour") if two_digit_hour else None
    has_sep = s[i] == ord(":")
    if has_sep:
        i += 1
        if i == n or s[i] not in DIGITS:
            return None
    elif s[i] not in DIGITS:
        return (i, "hour") if two_digit_hour else None
    time_units: tuple[tuple[int, Resolution], ...] = ((4, "minute"), (5, "second"))
    for part, unit in time_units:
        parts[part], i = s[i] - 48, i + 1
        if s[i] in DIGITS:
            parts[part], i = parts[part] * 10 + s[i] - 48, i + 1
            if parts[part] >= 60:  # noqa: PLR2004
                return None
        elif not has_sep:
            return None
        if unit == "minute":
            if i == n:
                return i, unit
            if has_sep and s[i] == ord(":"):
                i += 1
                if i == n or s[i] not in DIGITS:
                    return None
            elif has_sep or s[i] not in DIGITS:
                return i, unit
    if i == n or s[i] != ord("."):
        return i, "second"
    start = i = i + 1  # up to 18 fractional digits, everything past 6 is truncated
    while i < n and i - start < 18 and s[i] in DIGITS:  # noqa: PLR2004
        i += 1
    parts[6] = int(s[start:i].ljust(18, b"0"))
    # more than 6 digits make pandas return a `Timestamp`, see `_localize_timestamp`
    return i, "microsecond" if i - start <= 6 else "nanosecond"  # noqa: PLR2004


def _parse_iso_8601(  # noqa: C901, PLR0911, PLR0912, PLR0915
    buf: bytes,
) -> tuple[list[int], IsoUnit, int | None] | None:
    """Port of pandas' `parse_iso_8601_datetime` in inference mode.

    Returns the datetime parts (with attoseconds as the last part), the unit and the
    timezone offset in minutes, or None.
    """
    s, n, i = buf + b"\0", len(buf), 0
    parts = [0, 1, 1, 0, 0, 0, 0]
    while i < n and s[i] in SPACES:
        i += 1
    if s[i] == ord("-"):
        i += 1
    if i == n:
        return None
    if n - i >= 4 and all(c in DIGITS for c in s[i : i + 4]):  # noqa: PLR2004
        parts[0], i = int(s[i : i + 4]), i + 4
    if buf[:1] == b"-":
        parts[0] = -parts[0]
    leap = parts[0] & 3 == 0 and (parts[0] % 100 != 0 or parts[0] % 400 == 0)
    if i == n:
        return parts, "year", None
    sep = None
    if s[i] not in DIGITS:
        if s[i] not in YMD_SEPARATORS:
            return None
        sep, i = s[i], i + 1
        if i == n or s[i] not in DIGITS:
            return None
    for part in (1, 2):
        if s[i] not in DIGITS:
            return None
        parts[part], i = s[i] - 48, i + 1
        if s[i] in DIGITS:
            parts[part], i = parts[part] * 10 + s[i] - 48, i + 1
        elif sep is None:
            return None
        if part == 1:
            if not 1 <= parts[1] <= 12:  # noqa: PLR2004
                return None
            if i == n:
                return (parts, "month", None) if sep is not None else None
            if sep is not None:
                if s[i] != sep or i == n - 1:
                    return None
                i += 1
    if not 1 <= parts[2] <= DAYS_PER_MONTH[leap][parts[1] - 1]:
        return None
    if i == n:
        return parts, "day", None
    if s[i] not in b"T " or i == n - 1:
        return None
    if (time_result := _parse_iso_time(s, i + 1, n, parts)) is None:
        return None
    i, unit = time_result
    offset = None
    while i < n and s[i] in SPACES:
        i += 1
    if i < n and s[i] == ord("Z"):
        offset, i = 0, i + 1
    elif i < n and s[i] in b"+-":
        sign, i = -1 if s[i] == ord("-") else 1, i + 1
        offset = 0
        for factor, limit in ((60, 24), (1, 60)):  # hours, then optional minutes
            if factor == 1:
                if i == n:
                    break
                if s[i] == ord(":"):
                    i += 1
            width = (s[i] in DIGITS) + (s[i] in DIGITS and s[i + 1] in DIGITS)
            if not width or (value := int(s[i : i + width])) >= limit:
                return None
            offset, i = offset + sign * factor * value, i + width
    while i < n and s[i] in SPACES:
        i += 1
    return (parts, unit, offset) if i == n else None


def localize(value: datetime, tz: tzinfo) -> datetime:
    """Attach the given timezone to a naive datetime.

    For pytz zones, `datetime.replace(tzinfo=tz)` would pick the zone's first offset
    in history (e.g. LMT +00:18 for "CET"), so we let pytz resolve the actual offset.
    Ambiguous and non-existent times are resolved to daylight saving time.
    """
    if isinstance(tz, BaseTzInfo):
        return tz.localize(value, is_dst=True)
    return value.replace(tzinfo=tz)


def _localize_timestamp(plain: datetime, nanosecond: int) -> datetime:
    """Mimic `pandas.Timestamp.replace(tzinfo=CET)` for nanosecond timestamps.

    Pandas raises if the localized result underflows int64 nanoseconds.
    """
    localized = localize(plain, CET)
    utc = (localized.astimezone(UTC).replace(tzinfo=None), nanosecond)
    if utc < INT64_NANOSECOND_MINIMUM:  # CET offsets are positive, so no maximum
        msg = "Python int too large to convert to C long"
        raise OverflowError(msg)
    return localized


def _to_datetime(parts: list[int], tz: tzinfo | None) -> datetime:
    """Convert datetime parts with attoseconds into a datetime with microseconds."""
    year, month, day, hour, minute, second, attoseconds = parts
    return datetime(
        year, month, day, hour, minute, second, attoseconds // 10**12, tzinfo=tz
    )


def _check_nanosecond_bounds(parts: list[int], offset: int | None) -> None:
    """Raise like `pandas.Timestamp` for values that do not fit into int64 nanos."""
    stamp = "{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(*parts)
    if not NANOSECOND_BOUNDS[0] <= tuple(parts) <= NANOSECOND_BOUNDS[1]:
        msg = f"Out of bounds nanosecond timestamp: {stamp}"
        raise ValueError(msg)
    if offset:
        utc = _to_datetime(parts, None) - timedelta(minutes=offset)
        utc_parts = (*utc.timetuple()[:6], parts[6] // 10**9 * 10**9)
        if utc_parts > NANOSECOND_BOUNDS[1]:
            msg = f"Converting {stamp} overflows past 2262-04-11 23:47:16.854775807"
            raise ValueError(msg)
        if utc_parts < NANOSECOND_BOUNDS[0]:
            msg = f"Converting {stamp} underflows past 1677-09-21 00:12:43.145224193"
            raise ValueError(msg)


def _parse_delimited_date(buf: bytes) -> tuple[datetime, Resolution] | None:
    """Port of `_parse_delimited_date` for `MM/DD/YYYY`, `DD/MM/YYYY` and `MM/YYYY`."""
    n, day, can_swap = len(buf), b"1", True
    unit: Resolution = "day"
    if n == 10 and buf[2] in DELIMITERS and buf[5] in DELIMITERS:  # noqa: PLR2004
        month, day, year = buf[0:2], buf[3:5], buf[6:10]
    elif n == 9 and buf[1] in DELIMITERS and buf[4] in DELIMITERS:  # noqa: PLR2004
        month, day, year = buf[0:1], buf[2:4], buf[5:9]
    elif n == 9 and buf[2] in DELIMITERS and buf[4] in DELIMITERS:  # noqa: PLR2004
        month, day, year = buf[0:2], buf[3:4], buf[5:9]
    elif n == 8 and buf[1] in DELIMITERS and buf[3] in DELIMITERS:  # noqa: PLR2004
        month, day, year = buf[0:1], buf[2:3], buf[4:8]
    elif n == 7 and buf[2] in DELIMITERS and buf[2] != ord("."):  # noqa: PLR2004
        month, year, can_swap, unit = buf[0:2], buf[3:7], False, "month"
    else:
        return None
    if not (month.isdigit() and day.isdigit() and year.isdigit()) or int(year) < 1000:  # noqa: PLR2004
        return None
    m, d = int(month), int(day)
    if 1 <= m <= 31 and 1 <= d <= 31 and (m <= 12 or d <= 12):  # noqa: PLR2004
        if m > 12 and can_swap:  # noqa: PLR2004
            m, d = d, m
        return datetime(int(year), m, d), unit  # noqa: DTZ001
    msg = f"Invalid date specified ({m}/{d})"
    raise ValueError(msg)


def _reject_quarter(value: str) -> None:
    """Port of the quarter branch of `_parse_dateabbr_string`, e.g. `2Q05`, `2005Q1`.

    Quarters are no valid precision, so instead of returning them, we raise the same
    error that `TemporalEntityPrecision("quarter")` would.
    """
    buf = value.encode()
    n, i = len(buf), value.find("Q", 1, 6)  # pandas mixes up char and byte lengths
    if i == 1 and (n in (4, 6) or (n in (5, 7) and value[2] == "-")):
        quarter, year, century = buf[0], value[-2:] if n < 6 else value[-4:], n < 6  # noqa: PLR2004
    elif i in (2, 3) and (n == 4 or (n == 5 and value[i - 1] == "-")):  # noqa: PLR2004
        quarter, year, century = buf[-1], value[:2], True
    elif i in (4, 5) and (n == 6 or (n == 7 and value[i - 1] == "-")):  # noqa: PLR2004
        quarter, year, century = buf[-1], value[:4], False
    else:
        return
    try:
        parsed_year = int(year) + 2000 * century
    except ValueError:
        return
    if quarter not in b"1234":
        msg = (
            "Incorrect quarterly string is given, quarter must be "
            f"between 1 and 4: {value}"
        )
        raise ValueError(msg)
    if 1 <= parsed_year <= 9999:  # noqa: PLR2004
        msg = "'quarter' is not a valid TemporalEntityPrecision"
        raise ValueError(msg)


def _parse_dateabbr_string(value: str) -> tuple[datetime, Resolution] | None:
    """Port of `_parse_dateabbr_string`, e.g. `2000`, `2Q2005`, `MAY 2005`."""
    value = value.upper()
    if len(value) == 4:  # noqa: PLR2004
        try:
            return DEFAULT_DATETIME.replace(year=int(value)), "year"
        except ValueError:
            pass
    if 4 <= len(value) <= 7:  # noqa: PLR2004
        _reject_quarter(value)
    for pattern in ("%Y-%m", "%b %Y", "%b-%Y"):
        try:
            return datetime.strptime(value, pattern), "month"  # noqa: DTZ007
        except ValueError:
            pass
    return None


def _dateutil_parse(value: str) -> tuple[datetime, Resolution]:  # noqa: C901, PLR0912
    """Port of pandas' `dateutil_parse` wrapper, which also detects the resolution."""
    try:
        result, _ = DEFAULTPARSER._parse(value, dayfirst=False, yearfirst=True)  # type: ignore[attr-defined]  # noqa: SLF001
    except InvalidOperation:
        result = None
    if result is None:
        msg = f"Unknown datetime string format, unable to parse: {value}"
        raise ValueError(msg)
    replace = {
        attribute: getattr(result, attribute)
        for attribute in DATEUTIL_ATTRIBUTES
        if getattr(result, attribute) is not None
    }
    if not replace:
        msg = f"Unable to parse datetime string: {value}"
        raise ValueError(msg)
    resolution = next(a for a in reversed(DATEUTIL_ATTRIBUTES) if a in replace)
    if (
        resolution == "microsecond"
        and replace["microsecond"] % 1000 == 0
        and not SUBSECOND_PATTERN.search(value)
    ):
        resolution = "second"
    try:
        parsed = DEFAULT_DATETIME.replace(**replace)
    except ValueError as error:
        msg = f"{error}: {value}"
        raise ValueError(msg) from error
    except OverflowError as error:
        msg = f'Parsing "{value}" to datetime overflows'
        raise ValueError(msg) from error
    if result.weekday is not None and not result.day:
        msg = "Parsing datetimes with weekday but no day information is not supported"
        raise ValueError(msg)
    if result.tzname and result.tzname in time.tzname:
        if result.tzname != "UTC":
            msg = (
                f"Parsing '{result.tzname}' as tzlocal (dependent on system timezone) "
                "is no longer supported. Pass the 'tz' "
                "keyword or call tz_localize after construction instead"
            )
            raise ValueError(msg)
        parsed = parsed.replace(tzinfo=UTC)
    elif result.tzoffset == 0:
        parsed = parsed.replace(tzinfo=tzutc())
    elif result.tzoffset:
        parsed = parsed.replace(tzinfo=tzoffset(result.tzname, result.tzoffset))
        try:
            parsed.utcoffset()
        except ValueError:
            msg = (
                f'Parsed string "{value}" gives an invalid tzoffset, which must '
                "be between -timedelta(hours=24) and timedelta(hours=24)"
            )
            raise ValueError(msg) from None
    elif result.tzname is not None:
        msg = (
            f'Parsed string "{value}" included an un-recognized timezone '
            f'"{result.tzname}".'
        )
        raise ValueError(msg)
    return parsed, resolution


def parse_datetime_string_with_resolution(
    value: str,
) -> tuple[datetime, Resolution]:
    """Parse a datetime string and detect its resolution, pandas-style.

    Equivalent to pandas' `parse_datetime_string_with_reso` with `freq=None,
    dayfirst=False, yearfirst=True`, followed by localizing naive results to "CET".
    Except that pandas' `DateParseError`s are plain `ValueError`s, nanosecond
    timestamps are truncated to microseconds and resolutions are coarsened to valid
    `TemporalEntityPrecision` values: quarters raise, milli- and nanoseconds are
    reported as microseconds.

    Args:
        value: String to parse

    Raises:
        ValueError: If the string cannot be parsed
        OverflowError: If localizing a nanosecond timestamp overflows

    Returns:
        Tuple of timezone-aware datetime and resolution
    """
    parsed, resolution = _parse_datetime_string(value)
    if parsed.tzinfo is None:
        parsed = localize(parsed, CET)
    return parsed, resolution


def _parse_datetime_string(value: str) -> tuple[datetime, Resolution]:
    """Parse a datetime string into a naive or aware datetime and its resolution."""
    buf = value.encode()
    if not _looks_like_datetime(value, buf):
        msg = f'Given date string "{value}" not likely a datetime'
        raise ValueError(msg)
    if iso := _parse_iso_8601(buf):
        parts, unit, offset = iso
        if unit != "nanosecond":
            tz = None if offset is None else timezone(timedelta(minutes=offset))
            return _to_datetime(parts, tz), unit
        _check_nanosecond_bounds(parts, offset)
        if offset is not None:
            tz = timezone(timedelta(minutes=offset))
            return _to_datetime(parts, tz), "microsecond"
        nanosecond = parts[6] // 10**9 % 1000
        return _localize_timestamp(_to_datetime(parts, None), nanosecond), "microsecond"
    if delimited := _parse_delimited_date(buf):
        return delimited
    if value in NAT_STRINGS:
        msg = "NaTType does not support astimezone"
        raise ValueError(msg)
    if abbreviated := _parse_dateabbr_string(value):
        return abbreviated
    return _dateutil_parse(value)
