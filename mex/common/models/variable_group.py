from pydantic import Field

from mex.common.models.base import MExModel
from mex.common.models.extracted_data import ExtractedData
from mex.common.models.merged_item import MergedItem
from mex.common.types import ResourceID, Text, VariableGroupID


class BaseVariableGroup(MExModel):
    """The grouping of variables according to a certain aspect."""

    stableTargetId: VariableGroupID
    containedBy: list[ResourceID] = Field(..., min_length=1)
    label: list[Text] = Field(..., min_length=1)


class ExtractedVariableGroup(BaseVariableGroup, ExtractedData):
    """An automatically extracted metadata set describing a variable group."""


class MergedVariableGroup(BaseVariableGroup, MergedItem):
    """The result of merging all extracted data and rules for a variable group."""
