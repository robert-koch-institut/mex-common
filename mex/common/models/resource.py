from typing import Annotated

from pydantic import Field

from mex.common.models.base import BaseModel
from mex.common.models.extracted_data import ExtractedData
from mex.common.models.merged_item import MergedItem
from mex.common.types import (
    AccessPlatformID,
    AccessRestriction,
    ActivityID,
    ContactPointID,
    DistributionID,
    Link,
    OrganizationalUnitID,
    OrganizationID,
    PersonID,
    ResourceID,
    Text,
    Theme,
    Timestamp,
    VocabularyEnum,
)


class ResourceTypeGeneral(VocabularyEnum):
    """The general type of a resource."""

    __vocabulary__ = "resource-type-general"


class AnonymizationPseudonymization(VocabularyEnum):
    """Whether the resource is anonymized/pseudonymized."""

    __vocabulary__ = "anonymization-pseudonymization"


class DataProcessingState(VocabularyEnum):
    """Type for state of data processing."""

    __vocabulary__ = "data-processing-state"


class Frequency(VocabularyEnum):
    """Frequency type."""

    __vocabulary__ = "frequency"


class License(VocabularyEnum):
    """License type."""

    __vocabulary__ = "license"


class BaseResource(BaseModel):
    """A defined piece or collection of information."""

    stableTargetId: ResourceID
    accessPlatform: list[AccessPlatformID] = []
    accessRestriction: AccessRestriction = Field(
        ...,
        examples=["https://mex.rki.de/item/access-restriction-1"],
    )
    accrualPeriodicity: Frequency | None = Field(
        None, examples=["https://mex.rki.de/item/frequency-1"]
    )
    alternativeTitle: list[Text] = []
    anonymizationPseudonymization: list[AnonymizationPseudonymization] = Field(
        [], examples=["https://mex.rki.de/item/anonymization-pseudonymization-1"]
    )
    contact: list[OrganizationalUnitID | PersonID | ContactPointID] = Field(
        ..., min_length=1
    )
    contributingUnit: list[OrganizationalUnitID] = []
    contributor: list[PersonID] = []
    created: list[Timestamp] = []
    creator: list[PersonID] = []
    description: list[Text] = []
    distribution: list[DistributionID] = []
    documentation: list[Link] = []
    externalPartner: list[OrganizationID] = []
    icd10code: list[str] = []
    instrumentToolOrApparatus: list[Text] = []
    isPartOf: list[ResourceID] = []
    keyword: list[Text] = []
    language: list[str] = Field([], enum=["de", "en"])
    license: list[License] = Field(
        [],
        examples=["https://mex.rki.de/item/license-1"],
    )
    loincId: list[str] = []
    meshId: list[
        Annotated[
            str, Field(pattern=r"^https://id\.nlm\.nih\.gov/mesh/[A-Z0-9]{2,64}$")
        ]
    ] = []
    method: list[Text] = []
    methodDescription: list[Text] = []
    modified: list[Timestamp] = []
    publication: list[Link] = []
    publisher: list[OrganizationID] = []
    qualityInformation: list[Text] = []
    resourceTypeGeneral: list[ResourceTypeGeneral] = Field(
        [],
        examples=["https://mex.rki.de/item/resource-type-general-1"],
    )
    resourceTypeSpecific: list[Text] = []
    rights: list[Text] = []
    sizeOfDataBasis: str | None = None
    spatial: list[Text] = []
    stateOfDataProcessing: DataProcessingState | None = Field(
        None, examples=["https://mex.rki.de/item/data-processing-state-1"]
    )
    temporal: list[Timestamp | str] = []
    theme: list[Theme] = Field(
        ..., min_length=1, examples=["https://mex.rki.de/item/theme-1"]
    )
    title: list[Text] = Field(..., min_length=1)
    unitInCharge: list[OrganizationalUnitID] = Field(..., min_length=1)
    wasGeneratedBy: ActivityID | None = None


class ExtractedResource(BaseResource, ExtractedData):
    """An automatically extracted metadata set describing a resource."""


class MergedResource(BaseResource, MergedItem):
    """The result of merging all extracted data and rules for a resource."""
