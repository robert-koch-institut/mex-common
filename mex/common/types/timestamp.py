from copy import deepcopy
from datetime import date, datetime, tzinfo
from enum import Enum
from functools import total_ordering
from itertools import zip_longest
from typing import Any, Literal, Optional, Type, Union, cast, overload

from pandas._libs.tslibs import parsing
from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema, core_schema
from pytz import timezone


class TimestampPrecision(Enum):
    """Precision levels that are allowed for timestamp fields."""

    YEAR = "year"
    MONTH = "month"
    DAY = "day"
    HOUR = "hour"
    MINUTE = "minute"
    SECOND = "second"
    MICROSECOND = "microsecond"


TIMESTAMP_FORMATS_BY_PRECISION = {
    TimestampPrecision.YEAR: r"%Y",
    TimestampPrecision.MONTH: r"%Y-%m",
    TimestampPrecision.DAY: r"%Y-%m-%d",
    TimestampPrecision.HOUR: r"%Y-%m-%dT%H:%M:%SZ",
    TimestampPrecision.MINUTE: r"%Y-%m-%dT%H:%M:%SZ",
    TimestampPrecision.SECOND: r"%Y-%m-%dT%H:%M:%SZ",
    TimestampPrecision.MICROSECOND: r"%Y-%m-%dT%H:%M:%SZ",
}

TIMESTAMP_PRECISIONS_BY_ARG_LENGTH = {
    0: TimestampPrecision.YEAR,
    1: TimestampPrecision.YEAR,
    2: TimestampPrecision.MONTH,
    3: TimestampPrecision.DAY,
    4: TimestampPrecision.HOUR,
    5: TimestampPrecision.MINUTE,
    6: TimestampPrecision.SECOND,
    7: TimestampPrecision.MICROSECOND,
}

TIME_PRECISIONS = [
    TimestampPrecision.HOUR,
    TimestampPrecision.MINUTE,
    TimestampPrecision.SECOND,
    TimestampPrecision.MICROSECOND,
]

CET = timezone("CET")  # default assumed timezone
UTC = timezone("UTC")  # required output timezone
TIMESTAMP_REGEX = r"^\d{4}(-\d{2}(-\d{2}(T\d{2}:\d{2}:\d{2}Z)?)?)?$"


@total_ordering
class Timestamp:
    """Custom timestamp with precision detection and timezone normalization."""

    __slots__ = ("precision", "date_time")

    precision: TimestampPrecision
    date_time: datetime

    @overload
    def __init__(
        self,
        *args: Union[str, date, datetime, "Timestamp"],
        tzinfo: Literal[None] = None,
    ) -> None: ...  # pragma: no cover

    @overload
    def __init__(
        self,
        *args: int,
        tzinfo: Optional[tzinfo] = None,
    ) -> None: ...  # pragma: no cover

    def __init__(
        self,
        *args: Union[int, str, date, datetime, "Timestamp"],
        tzinfo: Optional[tzinfo] = None,
    ) -> None:
        """Create a new timestamp instance.

        Can parse strings, dates, datetimes, other timestamp objects
        or 0-7 integers for (year, month, day, hour, minute, second, ms).

        For any argument, a precision level is derived.
        When a time component is given, `tzinfo` keyword with timezone information is
        accepted. When no timezone is given, "CET" is assumed.
        If the timezone is not "UTC", the datetime is converted to "UTC".

        Examples:
            Timestamp("May 2005")
            Timestamp("2002-04-01T23:59")
            Timestamp(2009, 1)
            Timestamp(date(2009, 9, 30))
            Timestamp(datetime(2009, 9, 30, 23, 59, 5, tzinfo=timezone("CET")))
            Timestamp(2009, 9, 30, 23, 59, 5, tzinfo=timezone("CET"))
            Timestamp(Timestamp(2000))
        """
        if len(args) > 7:
            raise TypeError(f"Timestamp takes at most 7 arguments ({len(args)} given)")

        if len(args) == 1 and isinstance(args[0], (str, date, datetime, Timestamp)):
            if tzinfo:
                raise TypeError("Timestamp does not accept tzinfo in parsing mode")
            if isinstance(args[0], Timestamp):
                date_time, precision = self._parse_timestamp(args[0])
            elif isinstance(args[0], datetime):
                date_time, precision = self._parse_datetime(args[0])
            elif isinstance(args[0], date):
                date_time, precision = self._parse_date(args[0])
            else:
                date_time, precision = self._parse_string(args[0])
        elif all(isinstance(a, int) for a in args):
            args = cast(tuple[int, ...], args)
            date_time, precision = self._parse_args(*args, tzinfo=tzinfo)
        else:
            raise TypeError(
                "Timestamp takes a single str, date, datetime or Timestamp argument "
                "or up to 7 integers"
            )

        if precision in TIME_PRECISIONS:
            date_time = date_time.astimezone(UTC)

        self.date_time = date_time
        self.precision = precision

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source: Type[Any], _handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        """Mutate the field schema for timestamps."""
        from_str_schema = core_schema.chain_schema(
            [
                core_schema.str_schema(pattern=TIMESTAMP_REGEX),
                core_schema.no_info_plain_validator_function(
                    cls.validate,
                ),
            ]
        )
        from_anything_schema = core_schema.chain_schema(
            [
                core_schema.no_info_plain_validator_function(cls.validate),
                core_schema.is_instance_schema(Timestamp),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_str_schema,
            python_schema=from_anything_schema,
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema_: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """Modify the schema to add the class name as title and examples."""
        json_schema = handler(core_schema_)
        json_schema["title"] = cls.__name__
        json_schema["format"] = "date-time"
        json_schema["examples"] = [
            "2011",
            "2019-03",
            "2014-08-24",
            "2022-09-30T20:48:35Z",
        ]
        return json_schema

    @classmethod
    def validate(cls, value: Any) -> "Timestamp":
        """Parse any value and try to convert it into a timestamp."""
        if isinstance(value, (cls, date, str)):
            return cls(value)
        raise TypeError(f"Cannot parse {type(value)} as {cls.__name__}")

    @staticmethod
    def _parse_args(
        *args: int, tzinfo: Optional[tzinfo] = None
    ) -> tuple[datetime, TimestampPrecision]:
        """Parse 0-7 integer arguments into a timestamp and deduct the precision."""
        if tzinfo is None:
            tzinfo = CET
        padded = tuple(a or d for a, d in zip_longest(args, (1970, 1, 1, 0, 0, 0, 0)))
        date_time = datetime(*padded, tzinfo=tzinfo)  # type: ignore
        precision = TIMESTAMP_PRECISIONS_BY_ARG_LENGTH[len(args)]
        return date_time, precision

    @staticmethod
    def _parse_timestamp(value: "Timestamp") -> tuple[datetime, TimestampPrecision]:
        """Parse a timestamp into a new timestamp by copying its attributes."""
        return deepcopy(value.date_time), value.precision

    @staticmethod
    def _parse_string(value: str) -> tuple[datetime, TimestampPrecision]:
        """Parse a string containing a timestamp using pandas' tslibs."""
        parsed, precision = parsing.parse_datetime_string_with_reso(  # type: ignore[attr-defined]
            str(value), freq=None, dayfirst=False, yearfirst=True
        )
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=CET)
        if precision in ("millisecond", "nanosecond"):
            precision = "microsecond"
        return parsed, TimestampPrecision(precision)

    @staticmethod
    def _parse_datetime(
        value: datetime,
    ) -> tuple[datetime, TimestampPrecision]:
        """Parse a datetime and assume the precision is microseconds."""
        if value.tzinfo is None:
            value = value.replace(tzinfo=CET)
        return deepcopy(value), TimestampPrecision.MICROSECOND

    @staticmethod
    def _parse_date(
        value: date,
    ) -> tuple[datetime, TimestampPrecision]:
        """Parse a date and assume the precision is days."""
        return datetime(value.year, value.month, value.day), TimestampPrecision.DAY

    def __eq__(self, other: Any) -> bool:
        """Return wether the given other value is the same as this timestamp."""
        try:
            other = self.validate(other)
        except TypeError:
            return False
        return bool(
            self.date_time == other.date_time and self.precision == other.precision
        )

    def __gt__(self, other: Any) -> bool:
        """Return wether the given other value is the greater than this timestamp."""
        try:
            other = self.validate(other)
        except TypeError:
            raise NotImplementedError()
        return bool(self.date_time > other.date_time)

    def __str__(self) -> str:
        """Render timestamp with format fitting for its precision."""
        return self.date_time.strftime(TIMESTAMP_FORMATS_BY_PRECISION[self.precision])

    def __repr__(self) -> str:
        """Render a presentation showing this is not just a datetime."""
        return f'{self.__class__.__name__}("{self}")'
