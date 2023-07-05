from pydantic import Field

from mex.common.models.base import BaseModel
from mex.common.models.extracted_data import ExtractedData
from mex.common.models.merged_item import MergedItem
from mex.common.types import ContactPointID, Email


class BaseContactPoint(BaseModel):
    """A contact point - for example, an interdepartmental project."""

    stableTargetId: ContactPointID
    email: list[Email] = Field(
        ...,
        examples=["info@rki.de"],
        min_items=1,
    )


class ExtractedContactPoint(BaseContactPoint, ExtractedData):
    """An automatically extracted metadata set describing a contact point."""


class MergedContactPoint(BaseContactPoint, MergedItem):
    """The result of merging all extracted data and rules for a contact point."""
