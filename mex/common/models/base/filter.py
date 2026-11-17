from typing import Annotated

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field

from mex.common.models.base.model import BaseModel


class FilterRule(PydanticBaseModel, extra="forbid"):
    """A single filter rule to apply."""

    forValues: Annotated[list[str] | None, Field(title="forValues")] = None
    rule: Annotated[str | None, Field(title="rule")] = None


class FilterField(PydanticBaseModel, extra="forbid"):
    """Filter definition for one field in the primary source."""

    fieldInPrimarySource: Annotated[str | None, Field(title="fieldInPrimarySource")] = (
        None
    )
    locationInPrimarySource: Annotated[
        str | None, Field(title="locationInPrimarySource")
    ] = None
    examplesInPrimarySource: Annotated[
        list[str] | None, Field(title="examplesInPrimarySource")
    ] = None
    filterRules: Annotated[list[FilterRule], Field(min_length=1, title="filterRules")]
    comment: Annotated[str | None, Field(title="comment")] = None


class BaseFilter(BaseModel, extra="forbid"):
    """Base class for filter implementations."""
