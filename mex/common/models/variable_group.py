from pydantic import Field

from mex.common.models.extracted_data import ExtractedData
from mex.common.types import ResourceID, Text, VariableGroupID


class ExtractedVariableGroup(ExtractedData):
    """An extracted variable group."""

    stableTargetId: VariableGroupID
    containedBy: list[ResourceID] = Field(..., min_items=1)
    label: list[Text] = Field(..., min_items=1)
