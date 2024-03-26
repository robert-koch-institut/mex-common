"""The grouping of variables according to a certain aspect."""

from typing import Annotated, Literal

from pydantic import Field

from mex.common.models.base import BaseModel
from mex.common.models.extracted_data import ExtractedData
from mex.common.models.merged_item import MergedItem
from mex.common.types import (
    ExtractedVariableGroupIdentifier,
    MergedResourceIdentifier,
    MergedVariableGroupIdentifier,
    Text,
)


class BaseVariableGroup(BaseModel):
    """The grouping of variables according to a certain aspect."""

    containedBy: Annotated[list[MergedResourceIdentifier], Field(min_length=1)]
    label: Annotated[list[Text], Field(min_length=1)]


class ExtractedVariableGroup(BaseVariableGroup, ExtractedData):
    """An automatically extracted metadata set describing a variable group."""

    entityType: Annotated[
        Literal["ExtractedVariableGroup"], Field(alias="$type", frozen=True)
    ] = "ExtractedVariableGroup"
    identifier: Annotated[ExtractedVariableGroupIdentifier, Field(frozen=True)]
    stableTargetId: MergedVariableGroupIdentifier


class MergedVariableGroup(BaseVariableGroup, MergedItem):
    """The result of merging all extracted data and rules for a variable group."""

    entityType: Annotated[
        Literal["MergedVariableGroup"], Field(alias="$type", frozen=True)
    ] = "MergedVariableGroup"
    identifier: Annotated[MergedVariableGroupIdentifier, Field(frozen=True)]
