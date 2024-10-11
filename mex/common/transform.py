import json
import re
from collections.abc import Iterable
from enum import Enum
from functools import cache
from pathlib import PurePath
from typing import Any
from uuid import UUID

from pydantic import AnyUrl, SecretStr
from pydantic import BaseModel as PydanticModel

from mex.common.types import PathWrapper, TemporalEntity


class MExEncoder(json.JSONEncoder):
    """Custom JSON encoder that can handle pydantic models, enums and UUIDs."""

    def default(self, obj: Any) -> Any:  # noqa: PLR0911
        """Implement custom serialization rules."""
        if isinstance(obj, PydanticModel):
            return obj.model_dump()
        if isinstance(obj, AnyUrl):
            return str(obj)
        if isinstance(obj, SecretStr):
            return obj.get_secret_value()
        if isinstance(obj, Enum):
            return obj.value
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, TemporalEntity):
            return str(obj)
        if isinstance(obj, PurePath):
            return obj.as_posix()
        if isinstance(obj, PathWrapper):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


@cache
def snake_to_dromedary(string: str) -> str:
    """Convert the given string from `snake_case` into `dromedaryCase`."""
    if len(tokens := re.split(r"_", string)) > 1:
        return "".join(
            word.capitalize() if index else word.lower()
            for index, word in enumerate(tokens)
        )
    return string


@cache
def dromedary_to_snake(string: str) -> str:
    """Convert the given string from `dromedaryCase` into `snake_case`."""
    return "_".join(
        word.lower()
        for word in re.split(r"([A-Z]+(?![a-z])|[a-z]+|[A-Z][a-z]+)", string)
        if word.strip("_")
    )


@cache
def dromedary_to_kebab(string: str) -> str:
    """Convert the given string from `dromedaryCase` into `kebab-case`."""
    return "-".join(
        word.lower()
        for word in re.split(r"([A-Z]+(?![a-z])|[a-z]+|[A-Z][a-z]+)", string)
        if word.strip("-")
    )


@cache
def kebab_to_camel(string: str) -> str:
    """Convert the given string from `kebab-case` into `CamelCase`."""
    if len(tokens := re.split(r"\-+", string)) > 1:
        return "".join(word.title() for word in tokens)
    return string[:1].upper() + string[1:]


def ensure_prefix(string_like: Any, prefix: Any) -> str:
    """Return a string with the given prefix prepended if it is not present yet.

    If `string_like` already starts with the prefix, return a stringified copy.
    This method is the inverse of `str.removeprefix`.
    """
    string = str(string_like)
    prefix = str(prefix)
    if string.startswith(prefix):
        return string
    return f"{prefix}{string}"


def ensure_postfix(string_like: Any, postfix: Any) -> str:
    """Return a string with the given postfix appended if it is not present yet.

    If `string_like` already ends with the postfix, return a stringified copy.
    This method is the inverse of `str.removepostfix`.
    """
    string = str(string_like)
    postfix = str(postfix)
    if string.endswith(postfix):
        return string
    return f"{string}{postfix}"


def to_key_and_values(dct: dict[str, Any]) -> Iterable[tuple[str, list[Any]]]:
    """Return an iterable of dictionary items where the values are always lists."""
    for key, value in dct.items():
        if value is None:
            list_of_values = []
        elif isinstance(value, list):
            list_of_values = value
        else:
            list_of_values = [value]
        yield key, list_of_values
