from pydantic import Field

from mex.common.models.base import BaseModel
from mex.common.models.extracted_data import ExtractedData
from mex.common.models.merged_item import MergedItem
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


class BaseAccessPlatform(BaseModel):
    """A way of physically accessing the Resource for re-use."""

    stableTargetId: AccessPlatformID
    alternativeTitle: list[Text] = []
    contact: list[OrganizationalUnitID | PersonID | ContactPointID] = []
    description: list[Text] = []
    endpointDescription: Link | None = None
    endpointType: APIType | None = Field(
        None, examples=["https://mex.rki.de/item/api-type-1"]
    )
    endpointURL: Link | None = None
    landingPage: list[Link] = []
    technicalAccessibility: TechnicalAccessibility = Field(
        ..., examples=["https://mex.rki.de/item/technical-accessibility-1"]
    )
    title: list[Text] = []
    unitInCharge: list[OrganizationalUnitID] = []


class ExtractedAccessPlatform(BaseAccessPlatform, ExtractedData):
    """An automatically extracted metadata set describing an access platform."""


class MergedAccessPlatform(BaseAccessPlatform, MergedItem):
    """The result of merging all extracted data and rules for an access platform."""
