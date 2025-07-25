from copy import deepcopy
from datetime import date, datetime, tzinfo
from enum import Enum
from functools import total_ordering
from itertools import zip_longest
from typing import Any, Literal, Union, cast, overload

from pandas._libs.tslibs import parsing
from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler, json_schema
from pydantic_core import core_schema
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
YEAR_MONTH_DAY_TIME_REGEX = r"^[0-9]{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12][0-9]|3[01])T(?:[0-1][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]Z$"  # noqa: E501
YEAR_MONTH_DAY_REGEX = r"^[0-9]{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12][0-9]|3[01])$"
YEAR_MONTH_REGEX = r"^[0-9]{4}-(?:0[1-9]|1[0-2])$"
YEAR_REGEX = r"^[0-9]{4}$"
MAX_DATETIME_ARGUMENTS = 7


@total_ordering
class TemporalEntity:
    """Custom temporal entity with precision detection and timezone normalization."""

    __slots__ = ("date_time", "precision")

    precision: TemporalEntityPrecision
    date_time: datetime
    STR_SCHEMA_PATTERN = r".*"
    ALLOWED_PRECISION_LEVELS = list(TemporalEntityPrecision.__members__.values())
    JSON_SCHEMA_CONFIG: dict[str, str | list[str]] = {
        "examples": [
            "2011",
            "2019-03",
            "2014-08-24",
            "2022-09-30T20:48:35Z",
        ]
    }

    @overload
    def __init__(
        self,
        *args: Union[str, date, datetime, "TemporalEntity"],
        precision: TemporalEntityPrecision | None = None,
        tzinfo: Literal[None] = None,
    ) -> None: ...  # pragma: no cover

    @overload
    def __init__(
        self,
        *args: int,
        precision: TemporalEntityPrecision | None = None,
        tzinfo: tzinfo | None = None,
    ) -> None: ...  # pragma: no cover

    def __init__(  # noqa: PLR0912
        self,
        *args: Union[int, str, date, datetime, "TemporalEntity"],
        precision: TemporalEntityPrecision | None = None,
        tzinfo: tzinfo | None = None,
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
        if len(args) > MAX_DATETIME_ARGUMENTS:
            msg = (
                f"Temporal entity takes at most {MAX_DATETIME_ARGUMENTS} arguments "
                f"({len(args)} given)"
            )
            raise TypeError(msg)

        if len(args) == 1 and isinstance(
            args[0], str | date | datetime | TemporalEntity
        ):
            if tzinfo:
                msg = "Temporal entity does not accept tzinfo in parsing mode"
                raise TypeError(msg)
            if isinstance(args[0], TemporalEntity):
                date_time, parsed_precision = self._parse_temporal_entity(args[0])
            elif isinstance(args[0], datetime):
                date_time, parsed_precision = self._parse_datetime(args[0])
            elif isinstance(args[0], date):
                date_time, parsed_precision = self._parse_date(args[0])
            else:
                date_time, parsed_precision = self._parse_string(args[0])
        elif all(isinstance(a, int) for a in args):
            args = cast("tuple[int, ...]", args)
            date_time, parsed_precision = self._parse_integers(*args, tzinfo=tzinfo)
        else:
            msg = (
                "Temporal entity takes a single str, date, datetime or "
                "TemporalEntity argument or up to 7 integers"
            )
            raise TypeError(msg)

        if precision:
            self._validate_precision(precision)
        else:
            self._validate_precision(parsed_precision)
            precision = parsed_precision

        if precision in TIME_PRECISIONS:
            date_time = date_time.astimezone(UTC)
        else:
            date_time = date_time.replace(tzinfo=None)

        self.date_time = date_time
        self.precision = precision

    @classmethod
    def _validate_precision(cls, precision: TemporalEntityPrecision) -> None:
        """Confirm that the temporal entity can handle the given precision.

        Args:
            precision: a temporal entity precision

        Raises:
            ValueError: If the given precision is not covered by the temporal entity.
        """
        if precision not in cls.ALLOWED_PRECISION_LEVELS:
            allowed_precision_str = str(
                [p.value for p in cls.ALLOWED_PRECISION_LEVELS]
            )[1:-1]
            if len(cls.ALLOWED_PRECISION_LEVELS) == 1:
                error_str = f"Expected precision level to be {allowed_precision_str}"
            else:
                error_str = (
                    f"Expected precision level to be one of {allowed_precision_str}"
                )
            raise ValueError(error_str)

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,  # noqa: ANN401
        handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        """Modify the core schema to add validation and serialization rules."""
        return core_schema.json_or_python_schema(
            json_schema=core_schema.chain_schema(
                [
                    core_schema.str_schema(pattern=cls.STR_SCHEMA_PATTERN),
                    core_schema.no_info_plain_validator_function(cls),
                ]
            ),
            python_schema=core_schema.chain_schema(
                [
                    core_schema.is_instance_schema(cls | date | str | TemporalEntity),
                    core_schema.no_info_plain_validator_function(cls),
                ]
            ),
            serialization=core_schema.to_string_ser_schema(when_used="unless-none"),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema_: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> json_schema.JsonSchemaValue:
        """Modify the json schema to add a title, examples and an optional format."""
        json_schema_ = handler(core_schema_)
        json_schema_["title"] = cls.__name__
        json_schema_.update(cls.JSON_SCHEMA_CONFIG)
        return json_schema_

    @staticmethod
    def _parse_integers(
        *args: int, tzinfo: tzinfo | None = None
    ) -> tuple[datetime, TemporalEntityPrecision]:
        """Parse 0-7 integer arguments into a timestamp and deduct the precision."""
        if tzinfo is None:
            tzinfo = CET
        padded = tuple(a or d for a, d in zip_longest(args, (1970, 1, 1, 0, 0, 0, 0)))
        date_time = datetime(*padded, tzinfo=tzinfo)  # type: ignore[arg-type,misc]
        precision = TEMPORAL_ENTITY_PRECISIONS_BY_ARG_LENGTH[len(args)]
        return date_time, precision

    @staticmethod
    def _parse_temporal_entity(
        value: "TemporalEntity",
    ) -> tuple[datetime, TemporalEntityPrecision]:
        """Parse a temporal entity into a new one by copying its attributes."""
        return deepcopy(value.date_time), value.precision

    @staticmethod
    def _parse_string(value: str) -> tuple[datetime, TemporalEntityPrecision]:
        """Parse a string containing a temporal entity using pandas' tslibs."""
        try:
            parsed, precision = parsing.parse_datetime_string_with_reso(  # type: ignore[attr-defined]
                str(value), freq=None, dayfirst=False, yearfirst=True
            )
        except parsing.DateParseError as error:
            raise ValueError(*error.args) from error
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=CET)
        if precision in ("millisecond", "nanosecond"):
            precision = TemporalEntityPrecision.MICROSECOND.value
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
        return (
            datetime(value.year, value.month, value.day, tzinfo=CET),
            TemporalEntityPrecision.DAY,
        )

    def __eq__(self, other: object) -> bool:
        """Return whether the given other value is the same as this one."""
        try:
            other_temporal = TemporalEntity(other)  # type: ignore[call-overload]
        except TypeError:
            return False
        return bool(
            self.date_time == other_temporal.date_time
            and self.precision == other_temporal.precision
        )

    def __gt__(self, other: object) -> bool:
        """Return whether the given other value is the greater than this one."""
        try:
            other_temporal = TemporalEntity(other)  # type: ignore[call-overload]
        except TypeError:
            raise NotImplementedError from None
        return bool(self.date_time > other_temporal.date_time)

    def __hash__(self) -> int:
        """Return the hash for this object."""
        return hash((self.date_time, self.precision))

    def __str__(self) -> str:
        """Render temporal entity with format fitting for its precision."""
        return self.date_time.strftime(
            TEMPORAL_ENTITY_FORMATS_BY_PRECISION[self.precision]
        )

    def __repr__(self) -> str:
        """Overwrite the default representation."""
        return f'{self.__class__.__name__}("{self}")'


class Year(TemporalEntity):
    """Parser for temporal entities with year-precision."""

    STR_SCHEMA_PATTERN = YEAR_REGEX
    ALLOWED_PRECISION_LEVELS = [TemporalEntityPrecision.YEAR]
    JSON_SCHEMA_CONFIG = {"examples": ["2024"]}


class YearMonth(TemporalEntity):
    """Parser for temporal entities with month-precision."""

    STR_SCHEMA_PATTERN = YEAR_MONTH_REGEX
    ALLOWED_PRECISION_LEVELS = [TemporalEntityPrecision.MONTH]
    JSON_SCHEMA_CONFIG = {"examples": ["2019-03"]}


class YearMonthDay(TemporalEntity):
    """Parser for temporal entities with day-precision."""

    STR_SCHEMA_PATTERN = YEAR_MONTH_DAY_REGEX
    ALLOWED_PRECISION_LEVELS = [TemporalEntityPrecision.DAY]
    JSON_SCHEMA_CONFIG = {"examples": ["2014-08-24"]}


class YearMonthDayTime(TemporalEntity):
    """Parser for temporal entities with time-precision."""

    STR_SCHEMA_PATTERN = YEAR_MONTH_DAY_TIME_REGEX
    ALLOWED_PRECISION_LEVELS = TIME_PRECISIONS
    JSON_SCHEMA_CONFIG = {"examples": ["2022-09-30T20:48:35Z"]}


TEMPORAL_ENTITY_CLASSES_BY_PRECISION: dict[
    TemporalEntityPrecision, type[Year | YearMonth | YearMonthDay | YearMonthDayTime]
] = {
    TemporalEntityPrecision.YEAR: Year,
    TemporalEntityPrecision.MONTH: YearMonth,
    TemporalEntityPrecision.DAY: YearMonthDay,
    TemporalEntityPrecision.HOUR: YearMonthDayTime,
    TemporalEntityPrecision.MINUTE: YearMonthDayTime,
    TemporalEntityPrecision.SECOND: YearMonthDayTime,
    TemporalEntityPrecision.MICROSECOND: YearMonthDayTime,
}
