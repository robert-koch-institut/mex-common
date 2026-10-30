import re
from datetime import date, datetime, timedelta, timezone, tzinfo
from decimal import InvalidOperation
from enum import Enum
from functools import total_ordering
from itertools import zip_longest
from typing import Annotated, Any, NoReturn, Self, Union, cast, overload

from dateutil.parser import parser, parserinfo
from pydantic import (
    GetCoreSchemaHandler,
    GetJsonSchemaHandler,
    ValidationInfo,
    ValidatorFunctionWrapHandler,
    WrapValidator,
    json_schema,
)
from pydantic_core import core_schema
from pytz import BaseTzInfo
from pytz import timezone as pytz_timezone


class TemporalEntityPrecision(Enum):
    """Precision levels that are allowed for temporal entity fields."""

    YEAR = "year"
    MONTH = "month"
    DAY = "day"
    SECOND = "second"


TEMPORAL_ENTITY_FORMATS_BY_PRECISION = {
    TemporalEntityPrecision.YEAR: r"%Y",
    TemporalEntityPrecision.MONTH: r"%Y-%m",
    TemporalEntityPrecision.DAY: r"%Y-%m-%d",
    TemporalEntityPrecision.SECOND: r"%Y-%m-%dT%H:%M:%SZ",
}

TEMPORAL_ENTITY_PRECISIONS_BY_ARG_LENGTH = (
    TemporalEntityPrecision.YEAR,
    TemporalEntityPrecision.YEAR,
    TemporalEntityPrecision.MONTH,
    TemporalEntityPrecision.DAY,
    TemporalEntityPrecision.SECOND,
    TemporalEntityPrecision.SECOND,
    TemporalEntityPrecision.SECOND,
    TemporalEntityPrecision.SECOND,
)

TEMPORAL_ENTITY_PRECISIONS_BY_FIELD = {
    "year": TemporalEntityPrecision.YEAR,
    "month": TemporalEntityPrecision.MONTH,
    "day": TemporalEntityPrecision.DAY,
    "hour": TemporalEntityPrecision.SECOND,
    "minute": TemporalEntityPrecision.SECOND,
    "second": TemporalEntityPrecision.SECOND,
}

CET = pytz_timezone("CET")  # default assumed timezone
UTC = pytz_timezone("UTC")  # required output timezone
YEAR_MONTH_DAY_TIME_REGEX = r"^[0-9]{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12][0-9]|3[01])T(?:[0-1][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]Z$"  # noqa: E501
YEAR_MONTH_DAY_REGEX = r"^[0-9]{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12][0-9]|3[01])$"
YEAR_MONTH_REGEX = r"^[0-9]{4}-(?:0[1-9]|1[0-2])$"
YEAR_REGEX = r"^[0-9]{4}$"
MAX_DATETIME_ARGUMENTS = 7


ISO_8601_PATTERN = re.compile(
    r"(?P<year>\d{4})"
    r"(?:-(?P<month>\d{2})"
    r"(?:-(?P<day>\d{2})"
    r"(?:[T ](?P<hour>\d{2})"
    r"(?::(?P<minute>\d{2})"
    r"(?::(?P<second>\d{2})"
    r"(?:[.,]\d+)?)?)?"  # fractions of seconds are ignored
    r"\s*(?P<offset>Z|[+-]\d{2}(?::?\d{2})?)?)?)?)?"
)
GERMAN_DATE_PATTERN = re.compile(
    r"(?:(?P<day>\d{1,2})\.\s*)?(?P<month>\d{1,2})\.\s*(?P<year>\d{4}|\d{2})"
)
GERMAN_MONTHS = [
    ("Januar", "Jänner"),
    ("Februar",),
    ("Mär", "Mrz", "März", "Maerz"),
    ("April",),
    ("Mai",),
    ("Juni",),
    ("Juli",),
    ("August",),
    ("September",),
    ("Okt", "Oktober"),
    ("November",),
    ("Dez", "Dezember"),
]


class BilingualParserInfo(parserinfo):
    """Dateutil parser info that knows English and German month names."""

    MONTHS = [
        (*english, *german)
        for english, german in zip(parserinfo.MONTHS, GERMAN_MONTHS, strict=True)
    ]


DATEUTIL_PARSER = parser(BilingualParserInfo())  # month-first, then day, then year


def _localize(value: datetime, tz: tzinfo) -> datetime:
    """Attach the given timezone to a naive datetime.

    For pytz zones, `datetime.replace(tzinfo=tz)` would pick the zone's first offset
    in history (e.g. LMT +00:18 for "CET"), so we let pytz resolve the actual offset.
    Ambiguous and non-existent times are resolved to daylight saving time.
    """
    if isinstance(tz, BaseTzInfo):
        return tz.localize(value, is_dst=True)
    return value.replace(tzinfo=tz)


def _parse_offset(offset: str) -> tzinfo:
    """Parse an ISO 8601 offset like `Z`, `+02`, `-0130` or `+01:30`."""
    if offset == "Z":
        return UTC
    hours, minutes = int(offset[1:3]), int(offset[-2:]) if len(offset) > 3 else 0  # noqa: PLR2004
    sign = -1 if offset[0] == "-" else 1
    return timezone(sign * timedelta(hours=hours, minutes=minutes))


def _parse_iso_8601(match: re.Match[str]) -> tuple[dict[str, int], tzinfo | None]:
    """Convert a match of the ISO 8601 pattern into fields and timezone."""
    groups = {key: value for key, value in match.groupdict().items() if value}
    offset = groups.pop("offset", None)
    fields = {key: int(value) for key, value in groups.items()}
    return fields, None if offset is None else _parse_offset(offset)


def _parse_german_date(match: re.Match[str]) -> tuple[dict[str, int], None] | None:
    """Convert a match of the German date pattern into fields, if it is plausible."""
    day, month, year = match.group("day", "month", "year")
    if day is None and len(year) == 2:  # noqa: PLR2004
        return None  # too ambiguous, e.g. `12.20` could just be a number
    fields = {
        "year": DATEUTIL_PARSER.info.convertyear(int(year)),
        "month": int(month),
    }
    if day is not None:
        fields["day"] = int(day)
    return fields, None


def _parse_with_dateutil(value: str) -> tuple[dict[str, int], tzinfo | None]:
    """Parse a free-form string with dateutil and return the fields it found."""
    if value.startswith(("-", "+")):  # dateutil would silently drop the sign
        msg = f"Unable to parse datetime string with leading sign: {value}"
        raise ValueError(msg)
    try:
        # private method, but unlike `parse` it tells us which fields were found
        result, _ = DATEUTIL_PARSER._parse(value)  # type: ignore[attr-defined]  # noqa: SLF001
    except (InvalidOperation, OverflowError) as error:
        msg = f"Unknown datetime string format, unable to parse: {value}"
        raise ValueError(msg) from error
    if result is None:
        msg = f"Unknown datetime string format, unable to parse: {value}"
        raise ValueError(msg)
    fields = {
        field: getattr(result, field)
        for field in TEMPORAL_ENTITY_PRECISIONS_BY_FIELD
        if getattr(result, field) is not None
    }
    if fields.get("year", 0) < 1000:  # noqa: PLR2004
        msg = f"Unable to parse datetime string without four-digit year: {value}"
        raise ValueError(msg)
    if result.tzoffset is not None:
        return fields, timezone(timedelta(seconds=result.tzoffset))
    if result.tzname is not None:
        msg = f'Unknown timezone "{result.tzname}" in datetime string: {value}'
        raise ValueError(msg)
    return fields, None


def _parse_string(value: str) -> tuple[datetime, TemporalEntityPrecision]:
    """Parse a string into a timezone-aware datetime and detect its precision.

    Supported formats, tried in this order:

    - ISO 8601, e.g. `2020`, `2020-05`, `2020-05-07`, `2020-05-07T10:30:15+02:00`
    - German numeric dates, always day-first, e.g. `7.5.2020`, `07.05.20`, `05.2020`
    - Anything `dateutil` understands, with English and German month names,
      e.g. `05/07/2020`, `May 7 2020`, `7th of May 2020 10:30`, `4. März '08`

    Times are parsed with second precision, fractions of seconds are discarded.
    Results without explicit timezone are localized to "CET", i.e. CET or CEST.

    Args:
        value: String to parse

    Raises:
        ValueError: If the string cannot be parsed

    Returns:
        Tuple of timezone-aware datetime and precision
    """
    value = value.strip()
    if match := ISO_8601_PATTERN.fullmatch(value):
        fields, tz = _parse_iso_8601(match)
    elif (match := GERMAN_DATE_PATTERN.fullmatch(value)) and (
        german := _parse_german_date(match)
    ):
        fields, tz = german
    else:
        fields, tz = _parse_with_dateutil(value)
    finest = [f for f in TEMPORAL_ENTITY_PRECISIONS_BY_FIELD if f in fields][-1]
    try:
        parsed = datetime(**{"month": 1, "day": 1, **fields}, tzinfo=tz)
    except (ValueError, OverflowError) as error:
        msg = f"{error}: {value}"
        raise ValueError(msg) from error
    if tz is None:
        parsed = _localize(parsed, CET)
    return parsed, TEMPORAL_ENTITY_PRECISIONS_BY_FIELD[finest]


def _parse_arguments(
    args: tuple[Union[int, str, date, "TemporalEntity"], ...],
    tz: tzinfo | None,
) -> tuple[datetime, TemporalEntityPrecision]:
    """Parse temporal entity arguments into a datetime and the detected precision."""
    if len(args) > MAX_DATETIME_ARGUMENTS:
        msg = (
            f"Temporal entity takes at most {MAX_DATETIME_ARGUMENTS} arguments "
            f"({len(args)} given)"
        )
        raise TypeError(msg)
    if len(args) == 1 and isinstance(args[0], str | date | TemporalEntity):
        if tz:
            msg = "Temporal entity does not accept tzinfo in parsing mode"
            raise TypeError(msg)
        match args[0]:
            case TemporalEntity() as entity:
                return entity.date_time, entity.precision
            case datetime() as value:
                return value, TemporalEntityPrecision.SECOND
            case date() as value:
                day = datetime(value.year, value.month, value.day)  # noqa: DTZ001
                return day, TemporalEntityPrecision.DAY
            case value:
                return _parse_string(value)
    if all(isinstance(arg, int) for arg in args):
        padded = [a or d for a, d in zip_longest(args, (1970, 1, 1, 0, 0, 0, 0))]
        date_time = _localize(datetime(*padded), tz or CET)  # type: ignore[arg-type]  # noqa: DTZ001
        return date_time, TEMPORAL_ENTITY_PRECISIONS_BY_ARG_LENGTH[len(args)]
    msg = (
        "Temporal entity takes a single str, date, datetime or "
        "TemporalEntity argument or up to 7 integers"
    )
    raise TypeError(msg)


def _truncate(value: datetime, precision: TemporalEntityPrecision) -> datetime:
    """Cut off everything finer than the precision and normalize the timezone.

    Times are converted to UTC, dates are kept as naive wall-clock dates.
    Naive values are assumed to be in CET.
    """
    if value.tzinfo is None:
        value = _localize(value, CET)
    if precision is TemporalEntityPrecision.SECOND:
        return value.astimezone(UTC).replace(microsecond=0)
    month = 1 if precision is TemporalEntityPrecision.YEAR else value.month
    day = value.day if precision is TemporalEntityPrecision.DAY else 1
    return datetime(value.year, month, day)  # noqa: DTZ001


@total_ordering
class TemporalEntity:
    """Immutable temporal entity with precision detection and timezone normalization.

    Instantiating `TemporalEntity` itself returns an instance of the subclass that
    matches the detected precision, e.g. `TemporalEntity("2020")` gives `Year("2020")`.
    """

    __slots__ = ("date_time", "precision")

    precision: TemporalEntityPrecision
    date_time: datetime
    STR_SCHEMA_PATTERN = r".*"
    ALLOWED_PRECISION_LEVELS = list(TemporalEntityPrecision)
    JSON_SCHEMA_CONFIG: dict[str, str | list[str]] = {
        "examples": [
            "2011",
            "2019-03",
            "2014-08-24",
            "2022-09-30T20:48:35Z",
        ]
    }

    @overload
    def __new__(
        cls,
        *args: Union[str, date, datetime, "TemporalEntity"],
        precision: TemporalEntityPrecision | None = None,
        tzinfo: None = None,
    ) -> Self: ...  # pragma: no cover

    @overload
    def __new__(
        cls,
        *args: int,
        precision: TemporalEntityPrecision | None = None,
        tzinfo: tzinfo | None = None,
    ) -> Self: ...  # pragma: no cover

    def __new__(
        cls,
        *args: Union[int, str, date, datetime, "TemporalEntity"],
        precision: TemporalEntityPrecision | None = None,
        tzinfo: tzinfo | None = None,
    ) -> Self:
        """Create a new temporal entity instance.

        Can parse strings, dates, datetimes, other temporal entity objects
        or 0-7 integers for (year, month, day, hour, minute, second, ms).

        For any argument, a precision level is derived, unless one is given.
        Values are truncated to their precision, i.e. microseconds are discarded.
        When a time component is given, `tzinfo` keyword with timezone information is
        accepted. When no timezone is given, "CET" is assumed.
        Times are converted to "UTC".

        Examples:
            TemporalEntity("May 2005")
            TemporalEntity("2002-04-01T23:59")
            TemporalEntity(2009, 1)
            TemporalEntity(date(2009, 9, 30))
            TemporalEntity(timezone("CET").localize(datetime(2009, 9, 30, 23, 59, 5)))
            TemporalEntity(2009, 9, 30, 23, 59, 5, tzinfo=timezone("CET"))
            TemporalEntity(TemporalEntity(2000))
        """
        date_time, parsed_precision = _parse_arguments(args, tzinfo)
        precision = precision or parsed_precision
        target: type[TemporalEntity] = TEMPORAL_ENTITY_CLASSES_BY_PRECISION[precision]
        if cls is not TemporalEntity:
            cls._validate_precision(precision)
            target = cls
        instance = object.__new__(target)
        object.__setattr__(instance, "date_time", _truncate(date_time, precision))
        object.__setattr__(instance, "precision", precision)
        return cast("Self", instance)

    @classmethod
    def _validate_precision(cls, precision: TemporalEntityPrecision) -> None:
        """Confirm that the temporal entity can handle the given precision.

        Args:
            precision: a temporal entity precision

        Raises:
            ValueError: If the given precision is not covered by the temporal entity.
        """
        if precision not in cls.ALLOWED_PRECISION_LEVELS:
            allowed = " or ".join(repr(p.value) for p in cls.ALLOWED_PRECISION_LEVELS)
            msg = f"Expected precision level to be {allowed}"
            raise ValueError(msg)

    @classmethod
    def _validate(cls, value: Union[str, date, "TemporalEntity"]) -> Self:
        """Return the given value if it is already valid, otherwise parse it."""
        return value if isinstance(value, cls) else cls(value)

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
                    core_schema.is_instance_schema(str | date | TemporalEntity),
                    core_schema.no_info_plain_validator_function(cls._validate),
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

    def __setattr__(self, name: str, value: object) -> NoReturn:
        """Prevent changes, temporal entities are immutable."""
        msg = f"{type(self).__name__} is immutable"
        raise AttributeError(msg)

    def __delattr__(self, name: str) -> NoReturn:
        """Prevent changes, temporal entities are immutable."""
        msg = f"{type(self).__name__} is immutable"
        raise AttributeError(msg)

    def __copy__(self) -> Self:
        """Return this instance, since temporal entities are immutable."""
        return self

    def __deepcopy__(self, memo: dict[int, object]) -> Self:
        """Return this instance, since temporal entities are immutable."""
        return self

    def __reduce__(self) -> tuple[type[Self], tuple[str]]:
        """Pickle temporal entities by their string representation."""
        return type(self), (str(self),)

    def _sort_key(self) -> tuple[datetime, int]:
        """Return the start of the entity in UTC and its precision for ordering."""
        start = self.date_time
        if start.tzinfo is None:
            start = _localize(start, CET)
        return start, list(TemporalEntityPrecision).index(self.precision)

    def __eq__(self, other: object) -> bool:
        """Return whether the given other value is the same as this one."""
        if not isinstance(other, TemporalEntity):
            return NotImplemented
        return (self.date_time, self.precision) == (other.date_time, other.precision)

    def __lt__(self, other: object) -> bool:
        """Return whether this entity starts before the other, or is less precise."""
        if not isinstance(other, TemporalEntity):
            return NotImplemented
        return self._sort_key() < other._sort_key()

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

    __slots__ = ()

    STR_SCHEMA_PATTERN = YEAR_REGEX
    ALLOWED_PRECISION_LEVELS = [TemporalEntityPrecision.YEAR]
    JSON_SCHEMA_CONFIG = {"examples": ["2024"]}


class YearMonth(TemporalEntity):
    """Parser for temporal entities with month-precision."""

    __slots__ = ()

    STR_SCHEMA_PATTERN = YEAR_MONTH_REGEX
    ALLOWED_PRECISION_LEVELS = [TemporalEntityPrecision.MONTH]
    JSON_SCHEMA_CONFIG = {"examples": ["2019-03"]}


class YearMonthDay(TemporalEntity):
    """Parser for temporal entities with day-precision."""

    __slots__ = ()

    STR_SCHEMA_PATTERN = YEAR_MONTH_DAY_REGEX
    ALLOWED_PRECISION_LEVELS = [TemporalEntityPrecision.DAY]
    JSON_SCHEMA_CONFIG = {"examples": ["2014-08-24"]}


class YearMonthDayTime(TemporalEntity):
    """Parser for temporal entities with second-precision."""

    __slots__ = ()

    STR_SCHEMA_PATTERN = YEAR_MONTH_DAY_TIME_REGEX
    ALLOWED_PRECISION_LEVELS = [TemporalEntityPrecision.SECOND]
    JSON_SCHEMA_CONFIG = {"examples": ["2022-09-30T20:48:35Z"]}


TEMPORAL_ENTITY_CLASSES_BY_PRECISION: dict[
    TemporalEntityPrecision, type[Year | YearMonth | YearMonthDay | YearMonthDayTime]
] = {
    TemporalEntityPrecision.YEAR: Year,
    TemporalEntityPrecision.MONTH: YearMonth,
    TemporalEntityPrecision.DAY: YearMonthDay,
    TemporalEntityPrecision.SECOND: YearMonthDayTime,
}


def _validate_temporal_entity_union(
    value: Any,  # noqa: ANN401
    handler: ValidatorFunctionWrapHandler,
    info: ValidationInfo,
) -> Any:  # noqa: ANN401
    """Parse python input once, instead of once per member of the union.

    JSON input is still validated by the union, i.e. it needs to be in ISO format.
    """
    if info.mode == "python" and isinstance(value, str | date | TemporalEntity):
        return TemporalEntity._validate(value)  # noqa: SLF001
    return handler(value)


TemporalEntityUnion = Annotated[
    YearMonthDayTime | YearMonthDay | YearMonth | Year,
    WrapValidator(_validate_temporal_entity_union),
]
