from pydantic import Field

from mex.common.models.extracted_data import ExtractedData
from mex.common.types import (
    ContactPointID,
    Link,
    OrganizationalUnitID,
    PersonID,
    PrimarySourceID,
    Text,
)


class ExtractedPrimarySource(ExtractedData):
    """Model class definition for extracted primary source."""

    stableTargetId: PrimarySourceID
    alternativeTitle: list[Text] = []
    contact: list[OrganizationalUnitID | PersonID | ContactPointID] = []
    description: list[Text] = []
    documentation: list[Link] = []
    locatedAt: list[Link] = []
    title: list[Text] = []
    unitInCharge: list[OrganizationalUnitID] = []
    version: str | None = Field(
        None,
        examples=["v1", "2023-01-16", "Schema 9"],
    )
