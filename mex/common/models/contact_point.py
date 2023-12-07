from typing import Annotated

from pydantic import Field

from mex.common.models.base import MExModel
from mex.common.models.extracted_data import ExtractedData
from mex.common.models.merged_item import MergedItem
from mex.common.types import ContactPointID, Email


class BaseContactPoint(MExModel):
    """A contact point - for example, an interdepartmental project."""

    stableTargetId: ContactPointID
    email: list[
        Annotated[
            Email,
            Field(
                examples=["info@rki.de"],
            ),
        ]
    ] = Field(
        ...,
        min_length=1,
    )


class ExtractedContactPoint(BaseContactPoint, ExtractedData):
    """An automatically extracted metadata set describing a contact point."""


class MergedContactPoint(BaseContactPoint, MergedItem):
    """The result of merging all extracted data and rules for a contact point."""
