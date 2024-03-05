from typing import Annotated, Literal

from pydantic import Field

from mex.common.models.base import BaseModel
from mex.common.models.extracted_data import ExtractedData
from mex.common.models.merged_item import MergedItem
from mex.common.types import (
    Email,
    ExtractedContactPointIdentifier,
    MergedContactPointIdentifier,
)


class BaseContactPoint(BaseModel):
    """A contact point - for example, an interdepartmental project."""

    email: Annotated[list[Email], Field(min_length=1)]


class ExtractedContactPoint(BaseContactPoint, ExtractedData):
    """An automatically extracted metadata set describing a contact point."""

    entityType: Annotated[
        Literal["ExtractedContactPoint"], Field(alias="$type", frozen=True)
    ] = "ExtractedContactPoint"
    identifier: Annotated[ExtractedContactPointIdentifier, Field(frozen=True)]
    stableTargetId: MergedContactPointIdentifier


class MergedContactPoint(BaseContactPoint, MergedItem):
    """The result of merging all extracted data and rules for a contact point."""

    entityType: Annotated[
        Literal["MergedContactPoint"], Field(alias="$type", frozen=True)
    ] = "MergedContactPoint"
    identifier: Annotated[MergedContactPointIdentifier, Field(frozen=True)]
