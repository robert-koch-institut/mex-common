from pydantic import Field

from mex.common.models.extracted_data import ExtractedData
from mex.common.types import ContactPointID, Email


class ExtractedContactPoint(ExtractedData):
    """An extracted contact point."""

    stableTargetId: ContactPointID
    email: list[Email] = Field(
        ...,
        examples=["info@rki.de"],
        min_items=1,
    )
