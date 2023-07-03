from pydantic import Field

from mex.common.models.extracted_data import ExtractedData
from mex.common.types import Email, Link, OrganizationalUnitID, OrganizationID, Text


class ExtractedOrganizationalUnit(ExtractedData):
    """Model class definition for organizational units."""

    stableTargetId: OrganizationalUnitID
    alternativeName: list[Text] = []
    email: list[Email] = Field(
        [],
        examples=["info@rki.de"],
    )
    name: list[Text] = Field(..., min_items=1)
    parentUnit: OrganizationalUnitID | None = None
    shortName: list[Text] = []
    unitOf: list[OrganizationID] = []
    website: list[Link] = []
