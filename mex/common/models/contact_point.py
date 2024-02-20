from typing import Annotated, Literal

from pydantic import Field

from mex.common.models.base import BaseModel
from mex.common.models.extracted_data import ExtractedData
from mex.common.models.merged_item import MergedItem
from mex.common.types import ContactPointID, Email


class BaseContactPoint(BaseModel):
    """A contact point - for example, an interdepartmental project."""

    email: Annotated[list[Email], Field(min_length=1)]


class ExtractedContactPoint(BaseContactPoint, ExtractedData):
    """An automatically extracted metadata set describing a contact point."""

    entityType: Literal["ExtractedContactPoint"] = Field(
        "ExtractedContactPoint", alias="$type", frozen=True
    )
    stableTargetId: ContactPointID


class MergedContactPoint(BaseContactPoint, MergedItem):
    """The result of merging all extracted data and rules for a contact point."""

    entityType: Literal["MergedContactPoint"] = Field(
        "MergedContactPoint", alias="$type", frozen=True
    )
