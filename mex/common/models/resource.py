from typing import Annotated, Literal

from pydantic import Field

from mex.common.models.base import BaseModel
from mex.common.models.extracted_data import ExtractedData
from mex.common.models.merged_item import MergedItem
from mex.common.types import (
    AccessRestriction,
    AnonymizationPseudonymization,
    DataProcessingState,
    ExtractedResourceIdentifier,
    Frequency,
    Language,
    License,
    Link,
    MergedAccessPlatformIdentifier,
    MergedActivityIdentifier,
    MergedContactPointIdentifier,
    MergedDistributionIdentifier,
    MergedOrganizationalUnitIdentifier,
    MergedOrganizationIdentifier,
    MergedPersonIdentifier,
    MergedResourceIdentifier,
    ResourceTypeGeneral,
    Text,
    Theme,
    YearMonth,
    YearMonthDay,
    YearMonthDayTime,
)


class BaseResource(BaseModel):
    """A defined piece or collection of information."""

    accessPlatform: list[MergedAccessPlatformIdentifier] = []
    accessRestriction: Annotated[
        AccessRestriction,
        Field(
            examples=["https://mex.rki.de/item/access-restriction-1"],
        ),
    ]
    accrualPeriodicity: (
        Annotated[Frequency, Field(examples=["https://mex.rki.de/item/frequency-1"])]
        | None
    ) = None
    alternativeTitle: list[Text] = []
    anonymizationPseudonymization: list[
        Annotated[
            AnonymizationPseudonymization,
            Field(
                examples=["https://mex.rki.de/item/anonymization-pseudonymization-1"]
            ),
        ]
    ] = []
    contact: Annotated[
        list[
            MergedOrganizationalUnitIdentifier
            | MergedPersonIdentifier
            | MergedContactPointIdentifier
        ],
        Field(min_length=1),
    ]
    contributingUnit: list[MergedOrganizationalUnitIdentifier] = []
    contributor: list[MergedPersonIdentifier] = []
    created: YearMonthDayTime | YearMonthDay | YearMonth | None = None
    creator: list[MergedPersonIdentifier] = []
    description: list[Text] = []
    distribution: list[MergedDistributionIdentifier] = []
    documentation: list[Link] = []
    externalPartner: list[MergedOrganizationIdentifier] = []
    icd10code: list[str] = []
    instrumentToolOrApparatus: list[Text] = []
    isPartOf: list[MergedResourceIdentifier] = []
    keyword: list[Text] = []
    language: list[
        Annotated[Language, Field(examples=["https://mex.rki.de/item/language-1"])]
    ] = []
    license: (
        Annotated[License, Field(examples=["https://mex.rki.de/item/license-1"])] | None
    ) = None
    loincId: list[str] = []
    meshId: list[
        Annotated[
            str,
            Field(
                pattern=r"^http://id\.nlm\.nih\.gov/mesh/[A-Z0-9]{2,64}$",
                examples=["http://id.nlm.nih.gov/mesh/D001604"],
                json_schema_extra={"format": "uri"},
            ),
        ]
    ] = []
    method: list[Text] = []
    methodDescription: list[Text] = []
    modified: YearMonthDayTime | YearMonthDay | YearMonth | None = None
    publication: list[Link] = []
    publisher: list[MergedOrganizationIdentifier] = []
    qualityInformation: list[Text] = []
    resourceTypeGeneral: list[
        Annotated[
            ResourceTypeGeneral,
            Field(
                examples=["https://mex.rki.de/item/resource-type-general-1"],
            ),
        ]
    ] = []
    resourceTypeSpecific: list[Text] = []
    rights: list[Text] = []
    sizeOfDataBasis: str | None = None
    spatial: list[Text] = []
    stateOfDataProcessing: list[
        Annotated[
            DataProcessingState,
            Field(
                examples=["https://mex.rki.de/item/data-processing-state-1"],
            ),
        ]
    ] = []
    temporal: (
        YearMonthDayTime
        | YearMonthDay
        | YearMonth
        | Annotated[
            str,
            Field(
                examples=[
                    "2022-01 bis 2022-03",
                    "Sommer 2023",
                    "nach 2013",
                    "1998-2008",
                ]
            ),
        ]
        | None
    ) = None
    theme: Annotated[
        list[Annotated[Theme, Field(examples=["https://mex.rki.de/item/theme-1"])]],
        Field(min_length=1),
    ]
    title: Annotated[list[Text], Field(min_length=1)]
    unitInCharge: Annotated[
        list[MergedOrganizationalUnitIdentifier], Field(min_length=1)
    ]
    wasGeneratedBy: MergedActivityIdentifier | None = None


class ExtractedResource(BaseResource, ExtractedData):
    """An automatically extracted metadata set describing a resource."""

    entityType: Annotated[
        Literal["ExtractedResource"], Field(alias="$type", frozen=True)
    ] = "ExtractedResource"
    identifier: Annotated[ExtractedResourceIdentifier, Field(frozen=True)]
    stableTargetId: MergedResourceIdentifier


class MergedResource(BaseResource, MergedItem):
    """The result of merging all extracted data and rules for a resource."""

    entityType: Annotated[
        Literal["MergedResource"], Field(alias="$type", frozen=True)
    ] = "MergedResource"
    identifier: Annotated[MergedResourceIdentifier, Field(frozen=True)]
