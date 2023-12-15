import json
import re
from enum import Enum
from functools import cache
from pathlib import PurePath
from typing import Any
from uuid import UUID

from pydantic import AnyUrl, SecretStr
from pydantic import BaseModel as PydanticModel

from mex.common.types import Timestamp
from mex.common.types.path import PathWrapper


class MExEncoder(json.JSONEncoder):
    """Custom JSON encoder that can handle pydantic models, enums and UUIDs."""

    def default(self, obj: Any) -> Any:
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
        if isinstance(obj, Timestamp):
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
