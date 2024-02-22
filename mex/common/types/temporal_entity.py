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


class TemporalEntityPrecision(Enum):
    """Precision levels that are allowed for temporal entity fields."""

    YEAR = "year"
    MONTH = "month"
    DAY = "day"
    HOUR = "hour"
    MINUTE = "minute"
    SECOND = "second"
    MICROSECOND = "microsecond"


TEMPORAL_ENTITY_FORMATS_BY_PRECISION = {
    TemporalEntityPrecision.YEAR: r"%Y",
    TemporalEntityPrecision.MONTH: r"%Y-%m",
    TemporalEntityPrecision.DAY: r"%Y-%m-%d",
    TemporalEntityPrecision.HOUR: r"%Y-%m-%dT%H:%M:%SZ",
    TemporalEntityPrecision.MINUTE: r"%Y-%m-%dT%H:%M:%SZ",
    TemporalEntityPrecision.SECOND: r"%Y-%m-%dT%H:%M:%SZ",
    TemporalEntityPrecision.MICROSECOND: r"%Y-%m-%dT%H:%M:%SZ",
}

TEMPORAL_ENTITY_PRECISIONS_BY_ARG_LENGTH = {
    0: TemporalEntityPrecision.YEAR,
    1: TemporalEntityPrecision.YEAR,
    2: TemporalEntityPrecision.MONTH,
    3: TemporalEntityPrecision.DAY,
    4: TemporalEntityPrecision.HOUR,
    5: TemporalEntityPrecision.MINUTE,
    6: TemporalEntityPrecision.SECOND,
    7: TemporalEntityPrecision.MICROSECOND,
}

TIME_PRECISIONS = [
    TemporalEntityPrecision.HOUR,
    TemporalEntityPrecision.MINUTE,
    TemporalEntityPrecision.SECOND,
    TemporalEntityPrecision.MICROSECOND,
]

CET = timezone("CET")  # default assumed timezone
UTC = timezone("UTC")  # required output timezone
TEMPORAL_ENTITY_REGEX = (
    r"^\d{4}(-\d{2}(-\d{2}(T\d{2}:\d{2}:\d{2}Z)?)?)?$"  # optional resolution
)
TIMESTAMP_REGEX = r"^[1-9]\\d{3}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z$"
DATE_REGEX = r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$"
YEAR_MONTH_REGEX = r"^(?:\d{4}|(?:\d{4}-(?:0[1-9]|1[0-2])))$"


@total_ordering
class TemporalEntity:
    """Custom temporal entity with precision detection and timezone normalization."""

    __slots__ = ("precision", "date_time")

    precision: TemporalEntityPrecision
    date_time: datetime

    @overload
    def __init__(
        self,
        *args: Union[str, date, datetime, "TemporalEntity"],
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
        *args: Union[int, str, date, datetime, "TemporalEntity"],
        tzinfo: Optional[tzinfo] = None,
    ) -> None:
        """Create a new temporal entity instance.

        Can parse strings, dates, datetimes, other temporal entity objects
        or 0-7 integers for (year, month, day, hour, minute, second, ms).

        For any argument, a precision level is derived.
        When a time component is given, `tzinfo` keyword with timezone information is
        accepted. When no timezone is given, "CET" is assumed.
        If the timezone is not "UTC", the datetime is converted to "UTC".

        Examples:
            TemporalEntity("May 2005")
            TemporalEntity("2002-04-01T23:59")
            TemporalEntity(2009, 1)
            TemporalEntity(date(2009, 9, 30))
            TemporalEntity(datetime(2009, 9, 30, 23, 59, 5, tzinfo=timezone("CET")))
            TemporalEntity(2009, 9, 30, 23, 59, 5, tzinfo=timezone("CET"))
            TemporalEntity(TemporalEntity(2000))
        """
        if len(args) > 7:
            raise TypeError(
                f"Temporal entity takes at most 7 arguments ({len(args)} given)"
            )

        if len(args) == 1 and isinstance(
            args[0], (str, date, datetime, TemporalEntity)
        ):
            if tzinfo:
                raise TypeError(
                    "Temporal entity does not accept tzinfo in parsing mode"
                )
            if isinstance(args[0], TemporalEntity):
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
                "Temporal entity takes a single str, date, datetime or "
                "TemporalEntity argument or up to 7 integers"
            )

        if precision in TIME_PRECISIONS:
            date_time = date_time.astimezone(UTC)

        self.date_time = date_time
        self.precision = precision

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source: Type[Any], _handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        """Mutate the field schema for temporal entity."""
        from_str_schema = core_schema.chain_schema(
            [
                core_schema.str_schema(pattern=TEMPORAL_ENTITY_REGEX),
                core_schema.no_info_plain_validator_function(
                    cls.validate,
                ),
            ]
        )
        from_anything_schema = core_schema.chain_schema(
            [
                core_schema.no_info_plain_validator_function(cls.validate),
                core_schema.is_instance_schema(TemporalEntity),
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
        json_schema["examples"] = [
            "2011",
            "2019-03",
            "2014-08-24",
            "2022-09-30T20:48:35Z",
        ]
        return json_schema

    @classmethod
    def validate(cls, value: Any) -> "TemporalEntity":
        """Parse any value and try to convert it into a temporal entity."""
        if isinstance(value, (cls, date, str, TemporalEntity)):
            return cls(value)
        raise TypeError(f"Cannot parse {type(value)} as {cls.__name__}")

    @staticmethod
    def _parse_args(
        *args: int, tzinfo: Optional[tzinfo] = None
    ) -> tuple[datetime, TemporalEntityPrecision]:
        """Parse 0-7 integer arguments into a timestamp and deduct the precision."""
        if tzinfo is None:
            tzinfo = CET
        padded = tuple(a or d for a, d in zip_longest(args, (1970, 1, 1, 0, 0, 0, 0)))
        date_time = datetime(*padded, tzinfo=tzinfo)  # type: ignore
        precision = TEMPORAL_ENTITY_PRECISIONS_BY_ARG_LENGTH[len(args)]
        return date_time, precision

    @staticmethod
    def _parse_timestamp(
        value: "TemporalEntity",
    ) -> tuple[datetime, TemporalEntityPrecision]:
        """Parse a temporal entity into a new one by copying its attributes."""
        return deepcopy(value.date_time), value.precision

    @staticmethod
    def _parse_string(value: str) -> tuple[datetime, TemporalEntityPrecision]:
        """Parse a string containing a temporal entity using pandas' tslibs."""
        parsed, precision = parsing.parse_datetime_string_with_reso(  # type: ignore[attr-defined]
            str(value), freq=None, dayfirst=False, yearfirst=True
        )
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=CET)
        if precision in ("millisecond", "nanosecond"):
            precision = "microsecond"
        return parsed, TemporalEntityPrecision(precision)

    @staticmethod
    def _parse_datetime(
        value: datetime,
    ) -> tuple[datetime, TemporalEntityPrecision]:
        """Parse a datetime and assume the precision is microseconds."""
        if value.tzinfo is None:
            value = value.replace(tzinfo=CET)
        return deepcopy(value), TemporalEntityPrecision.MICROSECOND

    @staticmethod
    def _parse_date(
        value: date,
    ) -> tuple[datetime, TemporalEntityPrecision]:
        """Parse a date and assume the precision is days."""
        return datetime(value.year, value.month, value.day), TemporalEntityPrecision.DAY

    def __eq__(self, other: Any) -> bool:
        """Return whether the given other value is the same as this one."""
        try:
            other = self.validate(other)
        except TypeError:
            return False
        return bool(
            self.date_time == other.date_time and self.precision == other.precision
        )

    def __gt__(self, other: Any) -> bool:
        """Return whether the given other value is the greater than this one."""
        try:
            other = self.validate(other)
        except TypeError:
            raise NotImplementedError()
        return bool(self.date_time > other.date_time)

    def __str__(self) -> str:
        """Render temporal entity with format fitting for its precision."""
        return self.date_time.strftime(
            TEMPORAL_ENTITY_FORMATS_BY_PRECISION[self.precision]
        )

    def __repr__(self) -> str:
        """Render a presentation showing this is not just a datetime."""
        return f'{self.__class__.__name__}("{self}")'


class YearMonth(TemporalEntity):
    """Partial date pattern that accepts yyyy or yyyy-MM format."""

    def __init__(
        self,
        *args: Union[int, str, date, datetime, "TemporalEntity"],
        tzinfo: Optional[tzinfo] = None,
    ) -> None:
        """Validate for precision (year or month) after initialization."""
        super().__init__(*args, tzinfo=tzinfo)  # type: ignore
        if self.precision not in (
            TemporalEntityPrecision.YEAR,
            TemporalEntityPrecision.MONTH,
        ):
            raise ValueError("Expected precision level 'YEAR' or 'MONTH'")

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source: Type[Any], _handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        """Mutate the field schema for year-month pattern."""
        from_str_schema = core_schema.chain_schema(
            [
                core_schema.str_schema(pattern=YEAR_MONTH_REGEX),
                core_schema.no_info_plain_validator_function(
                    cls.validate,
                ),
            ]
        )

        from_anything_schema = core_schema.chain_schema(
            [
                core_schema.no_info_plain_validator_function(cls.validate),
                core_schema.is_instance_schema(YearMonth),
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
        json_schema = super().__get_pydantic_json_schema__(core_schema_, handler)
        json_schema["examples"] = ["2011", "2019-03"]
        return json_schema


class YearMonthDay(TemporalEntity):
    """Date pattern that accepts only yyyy-MM-dd format."""

    def __init__(
        self,
        *args: Union[int, str, date, datetime, "YearMonthDay"],
        tzinfo: Optional[tzinfo] = None,
    ) -> None:
        """Validate for day precision after initialization."""
        super().__init__(*args, tzinfo=tzinfo)  # type: ignore
        if self.precision != TemporalEntityPrecision.DAY:
            raise ValueError("Expected precision level 'DAY'")

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema_: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """Modify the schema to add the class name as title and examples."""
        json_schema = super().__get_pydantic_json_schema__(core_schema_, handler)
        json_schema["examples"] = ["2014-08-24"]
        json_schema["format"] = "date"
        return json_schema

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source: Type[Any], _handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        """Mutate the field schema for date pattern."""
        from_str_schema = core_schema.chain_schema(
            [
                core_schema.str_schema(pattern=DATE_REGEX),
                core_schema.no_info_plain_validator_function(
                    cls.validate,
                ),
            ]
        )

        from_anything_schema = core_schema.chain_schema(
            [
                core_schema.no_info_plain_validator_function(cls.validate),
                core_schema.is_instance_schema(YearMonthDay),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_str_schema,
            python_schema=from_anything_schema,
        )


class YearMonthDayTime(TemporalEntity):
    """Date pattern that accepts only yyyy-MM-dd HH:mm:ss format."""

    def __init__(
        self,
        *args: Union[int, str, date, datetime, "YearMonthDayTime"],
        tzinfo: Optional[tzinfo] = None,
    ) -> None:
        """Validate for timestamp (up to seconds) precision after initialization."""
        super().__init__(*args, tzinfo=tzinfo)  # type: ignore
        if self.precision not in TIME_PRECISIONS:
            raise ValueError("Expected time-based precision level")

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema_: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """Modify the schema to add the class name as title and examples."""
        json_schema = super().__get_pydantic_json_schema__(core_schema_, handler)
        json_schema["examples"] = ["2022-09-30T20:48:35Z"]
        json_schema["format"] = "date-time"
        return json_schema

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source: Type[Any], _handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        """Mutate the field schema for timestamp pattern."""
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
                core_schema.is_instance_schema(YearMonthDayTime),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_str_schema,
            python_schema=from_anything_schema,
        )
