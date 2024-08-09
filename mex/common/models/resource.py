"""A defined piece or collection of information."""

from typing import Annotated, ClassVar, Literal

from pydantic import Field, computed_field

from mex.common.models.base import BaseModel
from mex.common.models.extracted_data import ExtractedData
from mex.common.models.merged_item import MergedItem
from mex.common.models.rules import (
    AdditiveRule,
    PreventiveRule,
    RuleSet,
    SubtractiveRule,
)
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
    MergedBibliographicResourceIdentifier,
    MergedContactPointIdentifier,
    MergedDistributionIdentifier,
    MergedOrganizationalUnitIdentifier,
    MergedOrganizationIdentifier,
    MergedPersonIdentifier,
    MergedPrimarySourceIdentifier,
    MergedResourceIdentifier,
    PersonalData,
    ResourceCreationMethod,
    ResourceTypeGeneral,
    Text,
    Theme,
    Year,
    YearMonth,
    YearMonthDay,
    YearMonthDayTime,
)

LoincIdStr = Annotated[
    str,
    Field(
        examples=["https://loinc.org/95209-3", "https://loinc.org/LA26211-5"],
        pattern=r"^https://loinc.org/([a-zA-z]*)|(([0-9]{5}-[0-9]*))$",
        json_schema_extra={"format": "uri"},
    ),
]


class _Stem(BaseModel):
    stemType: ClassVar[Annotated[Literal["Resource"], Field(frozen=True)]] = "Resource"


class _OptionalLists(_Stem):
    accessPlatform: list[MergedAccessPlatformIdentifier] = []
    alternativeTitle: list[Text] = []
    anonymizationPseudonymization: list[
        Annotated[
            AnonymizationPseudonymization,
            Field(
                examples=["https://mex.rki.de/item/anonymization-pseudonymization-1"]
            ),
        ]
    ] = []
    conformsTo: list[
        Annotated[str, Field(examples=["FHIR", "LOINC", "SNOMED", "ICD-10"])]
    ] = []
    contributingUnit: list[MergedOrganizationalUnitIdentifier] = []
    contributor: list[MergedPersonIdentifier] = []
    creator: list[MergedPersonIdentifier] = []
    description: list[Text] = []
    distribution: list[MergedDistributionIdentifier] = []
    documentation: list[Link] = []
    externalPartner: list[MergedOrganizationIdentifier] = []
    hasLegalBasis: list[Text] = []
    icd10code: list[str] = []
    instrumentToolOrApparatus: list[Text] = []
    isPartOf: list[MergedResourceIdentifier] = []
    keyword: list[Text] = []
    language: list[
        Annotated[Language, Field(examples=["https://mex.rki.de/item/language-1"])]
    ] = []
    loincId: list[LoincIdStr] = []
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
    populationCoverage: list[Text] = []
    publication: list[MergedBibliographicResourceIdentifier] = []
    publisher: list[MergedOrganizationIdentifier] = []
    qualityInformation: list[Text] = []
    resourceCreationMethod: list[
        Annotated[
            ResourceCreationMethod,
            Field(examples=["https://mex.rki.de/item/resource-creation-method-1"]),
        ]
    ] = []
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
    spatial: list[Text] = []
    stateOfDataProcessing: list[
        Annotated[
            DataProcessingState,
            Field(
                examples=["https://mex.rki.de/item/data-processing-state-1"],
            ),
        ]
    ] = []


class _RequiredLists(_Stem):
    contact: Annotated[
        list[
            MergedOrganizationalUnitIdentifier
            | MergedPersonIdentifier
            | MergedContactPointIdentifier
        ],
        Field(min_length=1),
    ]
    theme: Annotated[
        list[Annotated[Theme, Field(examples=["https://mex.rki.de/item/theme-1"])]],
        Field(min_length=1),
    ]
    title: Annotated[list[Text], Field(min_length=1)]
    unitInCharge: Annotated[
        list[MergedOrganizationalUnitIdentifier], Field(min_length=1)
    ]


class _SparseLists(_Stem):
    contact: list[
        MergedOrganizationalUnitIdentifier
        | MergedPersonIdentifier
        | MergedContactPointIdentifier
    ] = []
    theme: list[
        Annotated[Theme, Field(examples=["https://mex.rki.de/item/theme-1"])]
    ] = []
    title: list[Text] = []
    unitInCharge: list[MergedOrganizationalUnitIdentifier] = []


class _OptionalValues(_Stem):
    accrualPeriodicity: (
        Annotated[Frequency, Field(examples=["https://mex.rki.de/item/frequency-1"])]
        | None
    ) = None
    created: YearMonthDayTime | YearMonthDay | YearMonth | Year | None = None
    hasPersonalData: (
        Annotated[
            PersonalData,
            Field(examples=["https://mex.rki.de/item/personal-data-1"]),
        ]
        | None
    ) = None
    license: (
        Annotated[License, Field(examples=["https://mex.rki.de/item/license-1"])] | None
    ) = None
    maxTypicalAge: Annotated[int, Field(examples=["99", "21"])] | None = None
    minTypicalAge: Annotated[int, Field(examples=["0", "18"])] | None = None
    modified: YearMonthDayTime | YearMonthDay | YearMonth | Year | None = None
    sizeOfDataBasis: str | None = None
    temporal: (
        YearMonthDayTime
        | YearMonthDay
        | YearMonth
        | Year
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
    wasGeneratedBy: MergedActivityIdentifier | None = None


class _RequiredValues(_Stem):
    accessRestriction: Annotated[
        AccessRestriction,
        Field(
            examples=["https://mex.rki.de/item/access-restriction-1"],
        ),
    ]


class _SparseValues(_Stem):
    accessRestriction: (
        Annotated[
            AccessRestriction,
            Field(
                examples=["https://mex.rki.de/item/access-restriction-1"],
            ),
        ]
        | None
    ) = None


class _VariadicValues(_Stem):
    accessRestriction: list[
        Annotated[
            AccessRestriction,
            Field(
                examples=["https://mex.rki.de/item/access-restriction-1"],
            ),
        ]
    ] = []
    accrualPeriodicity: list[
        Annotated[Frequency, Field(examples=["https://mex.rki.de/item/frequency-1"])]
    ] = []
    created: list[YearMonthDayTime | YearMonthDay | YearMonth | Year] = []
    hasPersonalData: list[
        Annotated[
            PersonalData,
            Field(examples=["https://mex.rki.de/item/personal-data-1"]),
        ]
    ] = []
    license: list[
        Annotated[License, Field(examples=["https://mex.rki.de/item/license-1"])]
    ] = []
    maxTypicalAge: list[Annotated[int, Field(examples=["99", "21"])]] = []
    minTypicalAge: list[Annotated[int, Field(examples=["0", "18"])]] = []
    modified: list[YearMonthDayTime | YearMonthDay | YearMonth | Year] = []
    sizeOfDataBasis: list[str] = []
    temporal: list[
        YearMonthDayTime
        | YearMonthDay
        | YearMonth
        | Year
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
    ] = []
    wasGeneratedBy: list[MergedActivityIdentifier] = []


class BaseResource(_OptionalLists, _RequiredLists, _OptionalValues, _RequiredValues):
    """All fields for a valid resource except for provenance."""


class ExtractedResource(BaseResource, ExtractedData):
    """An automatically extracted metadata set describing a resource."""

    entityType: Annotated[
        Literal["ExtractedResource"], Field(alias="$type", frozen=True)
    ] = "ExtractedResource"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def identifier(self) -> ExtractedResourceIdentifier:
        """Return the computed identifier for this extracted data item."""
        return self._get_identifier(ExtractedResourceIdentifier)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def stableTargetId(self) -> MergedResourceIdentifier:  # noqa: N802
        """Return the computed stableTargetId for this extracted data item."""
        return self._get_stable_target_id(MergedResourceIdentifier)


class MergedResource(BaseResource, MergedItem):
    """The result of merging all extracted data and rules for a resource."""

    entityType: Annotated[
        Literal["MergedResource"], Field(alias="$type", frozen=True)
    ] = "MergedResource"
    identifier: Annotated[MergedResourceIdentifier, Field(frozen=True)]


class AdditiveResource(
    _OptionalLists, _SparseLists, _OptionalValues, _SparseValues, AdditiveRule
):
    """Rule to add values to merged resource items."""

    entityType: Annotated[
        Literal["AdditiveResource"], Field(alias="$type", frozen=True)
    ] = "AdditiveResource"


class SubtractiveResource(
    _OptionalLists, _SparseLists, _VariadicValues, SubtractiveRule
):
    """Rule to subtract values from merged resource items."""

    entityType: Annotated[
        Literal["SubtractiveResource"], Field(alias="$type", frozen=True)
    ] = "SubtractiveResource"


class PreventiveResource(_Stem, PreventiveRule):
    """Rule to prevent primary sources for fields of merged resource items."""

    entityType: Annotated[
        Literal["PreventiveResource"], Field(alias="$type", frozen=True)
    ] = "PreventiveResource"
    accessPlatform: list[MergedPrimarySourceIdentifier] = []
    accessRestriction: list[MergedPrimarySourceIdentifier] = []
    accrualPeriodicity: list[MergedPrimarySourceIdentifier] = []
    alternativeTitle: list[MergedPrimarySourceIdentifier] = []
    anonymizationPseudonymization: list[MergedPrimarySourceIdentifier] = []
    conformsTo: list[MergedPrimarySourceIdentifier] = []
    contact: list[MergedPrimarySourceIdentifier] = []
    contributingUnit: list[MergedPrimarySourceIdentifier] = []
    contributor: list[MergedPrimarySourceIdentifier] = []
    created: list[MergedPrimarySourceIdentifier] = []
    creator: list[MergedPrimarySourceIdentifier] = []
    description: list[MergedPrimarySourceIdentifier] = []
    distribution: list[MergedPrimarySourceIdentifier] = []
    documentation: list[MergedPrimarySourceIdentifier] = []
    externalPartner: list[MergedPrimarySourceIdentifier] = []
    hasLegalBasis: list[MergedPrimarySourceIdentifier] = []
    hasPersonalData: list[MergedPrimarySourceIdentifier] = []
    icd10code: list[MergedPrimarySourceIdentifier] = []
    instrumentToolOrApparatus: list[MergedPrimarySourceIdentifier] = []
    isPartOf: list[MergedPrimarySourceIdentifier] = []
    keyword: list[MergedPrimarySourceIdentifier] = []
    language: list[MergedPrimarySourceIdentifier] = []
    license: list[MergedPrimarySourceIdentifier] = []
    loincId: list[MergedPrimarySourceIdentifier] = []
    maxTypicalAge: list[MergedPrimarySourceIdentifier] = []
    meshId: list[MergedPrimarySourceIdentifier] = []
    method: list[MergedPrimarySourceIdentifier] = []
    methodDescription: list[MergedPrimarySourceIdentifier] = []
    minTypicalAge: list[MergedPrimarySourceIdentifier] = []
    modified: list[MergedPrimarySourceIdentifier] = []
    populationCoverage: list[MergedPrimarySourceIdentifier] = []
    publication: list[MergedPrimarySourceIdentifier] = []
    publisher: list[MergedPrimarySourceIdentifier] = []
    qualityInformation: list[MergedPrimarySourceIdentifier] = []
    resourceCreationMethod: list[MergedPrimarySourceIdentifier] = []
    resourceTypeGeneral: list[MergedPrimarySourceIdentifier] = []
    resourceTypeSpecific: list[MergedPrimarySourceIdentifier] = []
    rights: list[MergedPrimarySourceIdentifier] = []
    sizeOfDataBasis: list[MergedPrimarySourceIdentifier] = []
    spatial: list[MergedPrimarySourceIdentifier] = []
    stateOfDataProcessing: list[MergedPrimarySourceIdentifier] = []
    temporal: list[MergedPrimarySourceIdentifier] = []
    theme: list[MergedPrimarySourceIdentifier] = []
    title: list[MergedPrimarySourceIdentifier] = []
    unitInCharge: list[MergedPrimarySourceIdentifier] = []
    wasGeneratedBy: list[MergedPrimarySourceIdentifier] = []


class ResourceRuleSet(_Stem, RuleSet):
    """Set of rules to edit a resource item."""

    entityType: Annotated[
        Literal["ResourceRuleSet"], Field(alias="$type", frozen=True)
    ] = "ResourceRuleSet"
    additive: AdditiveResource
    subtractive: SubtractiveResource
    preventive: PreventiveResource
