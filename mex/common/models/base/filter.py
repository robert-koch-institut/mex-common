from typing import Annotated

from pydantic import BaseModel, Field


class FilterRule(BaseModel, extra="forbid"):
    """Entity filter rule model."""

    forValues: Annotated[list[str] | None, Field(title="forValues")] = None
    rule: Annotated[str | None, Field(title="rule")] = None


class FilterField(BaseModel, extra="forbid"):
    """Entity filter field model."""

    fieldInPrimarySource: Annotated[str | None, Field(title="fieldInPrimarySource")] = (
        None
    )
    locationInPrimarySource: Annotated[
        str | None, Field(title="locationInPrimarySource")
    ] = None
    examplesInPrimarySource: Annotated[
        list[str] | None, Field(title="examplesInPrimarySource")
    ] = None
    mappingRules: Annotated[list[FilterRule], Field(min_length=1, title="mappingRules")]
    comment: Annotated[str | None, Field(title="comment")] = None


class BaseFilter(BaseModel, extra="forbid"):
    """Base class for filter implementations."""
