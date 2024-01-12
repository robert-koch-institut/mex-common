from typing import Annotated, Literal

from pydantic import Field

from mex.common.models.base import BaseModel
from mex.common.models.extracted_data import ExtractedData
from mex.common.models.merged_item import MergedItem
from mex.common.types import ResourceID, Text, VariableGroupID


class BaseVariableGroup(BaseModel):
    """The grouping of variables according to a certain aspect."""

    stableTargetId: VariableGroupID
    containedBy: Annotated[list[ResourceID], Field(min_length=1)]
    label: Annotated[list[Text], Field(min_length=1)]


class ExtractedVariableGroup(BaseVariableGroup, ExtractedData):
    """An automatically extracted metadata set describing a variable group."""

    entityType: Literal["ExtractedVariableGroup"] = Field(
        "ExtractedVariableGroup", alias="$type", frozen=True
    )


class MergedVariableGroup(BaseVariableGroup, MergedItem):
    """The result of merging all extracted data and rules for a variable group."""

    entityType: Literal["MergedVariableGroup"] = Field(
        "MergedVariableGroup", alias="$type", frozen=True
    )
