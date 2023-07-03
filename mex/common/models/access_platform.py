from pydantic import Field

from mex.common.models.extracted_data import ExtractedData
from mex.common.types import (
    AccessPlatformID,
    ContactPointID,
    Link,
    OrganizationalUnitID,
    PersonID,
    Text,
    VocabularyEnum,
)


class TechnicalAccessibility(VocabularyEnum):
    """Technical accessibility within RKI and outside of RKI."""

    __vocabulary__ = "technical-accessibility"


class APIType(VocabularyEnum):
    """Technical standard or style of a network API."""

    __vocabulary__ = "api-type"


class ExtractedAccessPlatform(ExtractedData):
    """A way of physically accessing the Resource for re-use."""

    stableTargetId: AccessPlatformID
    alternativeTitle: list[Text] = []
    contact: list[OrganizationalUnitID | PersonID | ContactPointID] = []
    description: list[Text] = []
    endpointDescription: Link | None = None
    endpointType: APIType | None = Field(
        None, examples=["https://mex.rki.de/concept/api-type-1"]
    )
    endpointURL: Link | None = None
    landingPage: list[Link] = []
    technicalAccessibility: TechnicalAccessibility = Field(
        ..., examples=["https://mex.rki.de/concept/technical-accessibility-1"]
    )
    title: list[Text] = []
    unitInCharge: list[OrganizationalUnitID] = []
