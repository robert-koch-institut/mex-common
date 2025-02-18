from typing import Annotated, Generic, TypeVar

from pydantic import BaseModel, Field

_ValueT = TypeVar("_ValueT")
_MappingRuleT = TypeVar("_MappingRuleT")


class MappingRule(BaseModel, Generic[_ValueT], extra="forbid"):
    """Generic mapping rule model."""

    forValues: Annotated[list[str] | None, Field(title="forValues")] = None
    setValues: Annotated[_ValueT | None, Field(title="setValues")] = None
    rule: Annotated[str | None, Field(title="rule")] = None


class MappingField(BaseModel, Generic[_MappingRuleT], extra="forbid"):
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
        list[MappingRule[_MappingRuleT]], Field(min_length=1, title="mappingRules")
    ]
    comment: Annotated[str | None, Field(title="comment")] = None


class BaseMapping(BaseModel, extra="forbid"):
    """Base class for mapping implementations."""
