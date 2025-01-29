from typing import Annotated, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class MappingRule(BaseModel, Generic[T], extra="forbid"):
    """Generic mapping rule model."""

    forValues: Annotated[list[str] | None, Field(title="forValues")] = None
    setValues: Annotated[list[T] | None, Field(title="setValues")] = None
    rule: Annotated[str | None, Field(title="rule")] = None


class MappingField(BaseModel, Generic[T], extra="forbid"):
    """Generic mapping field model."""

    fieldInPrimarySource: Annotated[str | None, Field(title="fieldInPrimarySource")] = (
        None
    )
    locationInPrimarySource: Annotated[
        str | None, Field(title="locationInPrimarySource")
    ] = None
    examplesInPrimarySource: Annotated[
        list[str] | None, Field(title="examplesInPrimarySource")
    ] = None
    mappingRules: Annotated[
        list[MappingRule[T]], Field(min_length=1, title="mappingRules")
    ]
    comment: Annotated[str | None, Field(title="comment")] = None


class BaseMapping(BaseModel, extra="forbid"):
    """Base class for mapping implementations."""
