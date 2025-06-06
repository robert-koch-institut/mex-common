"""A defined piece or collection of information."""

from typing import Annotated, ClassVar, Literal

from pydantic import AfterValidator, Field, computed_field

from mex.common.models.base.extracted_data import ExtractedData
from mex.common.models.base.filter import BaseFilter, FilterField
from mex.common.models.base.mapping import BaseMapping, MappingField
from mex.common.models.base.merged_item import MergedItem
from mex.common.models.base.model import BaseModel
from mex.common.models.base.preview_item import PreviewItem
from mex.common.models.base.rules import (
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
    Identifier,
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

ConformsToStr = Annotated[str, Field(examples=["FHIR", "LOINC", "SNOMED", "ICD-10"])]
DoiStr = Annotated[
    str,
    Field(
        pattern="^https?://(?:dx\\.)?doi\\.org/[0-9]{2}\\.[0-9]{4,9}[-_.;()/:A-Za-z0-9]{0,256}$",
        examples=[
            "https://doi.org/10.1007/978-1-0716-2441-8_7",
            "https://doi.org/10.2807/1560-7917.ES.2022.27.46.2200849",
            "https://doi.org/10.3389/fmicb.2022.868887",
            "http://dx.doi.org/10.25646/5147",
            "https://doi.org/10.1016/j.vaccine.2022.11.065",
        ],
    ),
]
LoincIdStr = Annotated[
    str,
    Field(
        pattern="^https://loinc\\.org/[-A-Za-z0-9]{2,64}$",
        examples=[
            "https://loinc.org/95209-3",
            "https://loinc.org/LA26211-5",
            "https://loinc.org/96766-1",
        ],
        json_schema_extra={"format": "uri"},
    ),
]
MeshIdStr = Annotated[
    str,
    Field(
        pattern="^http://id\\.nlm\\.nih\\.gov/mesh/[A-Z0-9]{2,64}$",
        examples=[
            "http://id.nlm.nih.gov/mesh/D001604",
            "http://id.nlm.nih.gov/mesh/T025130",
            "http://id.nlm.nih.gov/mesh/D007717",
        ],
        json_schema_extra={"format": "uri"},
    ),
]
TemporalStr = Annotated[
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
AnyContactIdentifier = Annotated[
    MergedOrganizationalUnitIdentifier
    | MergedPersonIdentifier
    | MergedContactPointIdentifier,
    AfterValidator(Identifier),
]
MaxTypicalAgeInt = Annotated[int, Field(examples=["99", "21"])]
MinTypicalAgeInt = Annotated[int, Field(examples=["0", "18"])]


class _Stem(BaseModel):
    stemType: ClassVar[Annotated[Literal["Resource"], Field(frozen=True)]] = "Resource"


class _OptionalLists(_Stem):
    accessPlatform: list[MergedAccessPlatformIdentifier] = []
    alternativeTitle: list[Text] = []
    anonymizationPseudonymization: list[AnonymizationPseudonymization] = []
    conformsTo: list[ConformsToStr] = []
    contributingUnit: list[MergedOrganizationalUnitIdentifier] = []
    contributor: list[MergedPersonIdentifier] = []
    creator: list[MergedPersonIdentifier] = []
    description: list[Text] = []
    distribution: list[MergedDistributionIdentifier] = []
    documentation: list[Link] = []
    externalPartner: list[MergedOrganizationIdentifier] = []
    hasLegalBasis: list[Text] = []
    hasPurpose: list[Text] = []
    icd10code: list[str] = []
    instrumentToolOrApparatus: list[Text] = []
    isPartOf: list[MergedResourceIdentifier] = []
    keyword: list[Text] = []
    language: list[Language] = []
    loincId: list[LoincIdStr] = []
    meshId: list[MeshIdStr] = []
    method: list[Text] = []
    methodDescription: list[Text] = []
    populationCoverage: list[Text] = []
    provenance: list[Text] = []
    publication: list[MergedBibliographicResourceIdentifier] = []
    publisher: list[MergedOrganizationIdentifier] = []
    qualityInformation: list[Text] = []
    resourceCreationMethod: list[ResourceCreationMethod] = []
    resourceTypeGeneral: list[ResourceTypeGeneral] = []
    resourceTypeSpecific: list[Text] = []
    rights: list[Text] = []
    spatial: list[Text] = []
    stateOfDataProcessing: list[DataProcessingState] = []


class _RequiredLists(_Stem):
    contact: Annotated[list[AnyContactIdentifier], Field(min_length=1)]
    theme: Annotated[list[Theme], Field(min_length=1)]
    title: Annotated[list[Text], Field(min_length=1)]
    unitInCharge: Annotated[
        list[MergedOrganizationalUnitIdentifier], Field(min_length=1)
    ]


class _SparseLists(_Stem):
    contact: list[AnyContactIdentifier] = []
    theme: list[Theme] = []
    title: list[Text] = []
    unitInCharge: list[MergedOrganizationalUnitIdentifier] = []


class _OptionalValues(_Stem):
    accrualPeriodicity: Frequency | None = None
    created: YearMonthDayTime | YearMonthDay | YearMonth | Year | None = None
    doi: DoiStr | None = None
    hasPersonalData: PersonalData | None = None
    license: License | None = None
    maxTypicalAge: MaxTypicalAgeInt | None = None
    minTypicalAge: MinTypicalAgeInt | None = None
    modified: YearMonthDayTime | YearMonthDay | YearMonth | Year | None = None
    sizeOfDataBasis: str | None = None
    temporal: (
        YearMonthDayTime | YearMonthDay | YearMonth | Year | TemporalStr | None
    ) = None
    wasGeneratedBy: MergedActivityIdentifier | None = None


class _RequiredValues(_Stem):
    accessRestriction: AccessRestriction


class _SparseValues(_Stem):
    accessRestriction: AccessRestriction | None = None


class _VariadicValues(_Stem):
    accessRestriction: list[AccessRestriction] = []
    accrualPeriodicity: list[Frequency] = []
    created: list[YearMonthDayTime | YearMonthDay | YearMonth | Year] = []
    doi: list[DoiStr] = []
    hasPersonalData: list[PersonalData] = []
    license: list[License] = []
    maxTypicalAge: list[MaxTypicalAgeInt] = []
    minTypicalAge: list[MinTypicalAgeInt] = []
    modified: list[YearMonthDayTime | YearMonthDay | YearMonth | Year] = []
    sizeOfDataBasis: list[str] = []
    temporal: list[
        YearMonthDayTime | YearMonthDay | YearMonth | Year | TemporalStr
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
        """Return the computed identifier for this extracted item."""
        return self._get_identifier(ExtractedResourceIdentifier)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def stableTargetId(self) -> MergedResourceIdentifier:  # noqa: N802
        """Return the computed stableTargetId for this extracted item."""
        return self._get_stable_target_id(MergedResourceIdentifier)


class MergedResource(BaseResource, MergedItem):
    """The result of merging all extracted items and rules for a resource."""

    entityType: Annotated[
        Literal["MergedResource"], Field(alias="$type", frozen=True)
    ] = "MergedResource"
    identifier: Annotated[MergedResourceIdentifier, Field(frozen=True)]


class PreviewResource(
    _OptionalLists, _SparseLists, _OptionalValues, _SparseValues, PreviewItem
):
    """Preview for merging all extracted items and rules for a resource."""

    entityType: Annotated[
        Literal["PreviewResource"], Field(alias="$type", frozen=True)
    ] = "PreviewResource"
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
    doi: list[MergedPrimarySourceIdentifier] = []
    creator: list[MergedPrimarySourceIdentifier] = []
    description: list[MergedPrimarySourceIdentifier] = []
    distribution: list[MergedPrimarySourceIdentifier] = []
    documentation: list[MergedPrimarySourceIdentifier] = []
    externalPartner: list[MergedPrimarySourceIdentifier] = []
    hasLegalBasis: list[MergedPrimarySourceIdentifier] = []
    hasPurpose: list[MergedPrimarySourceIdentifier] = []
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
    provenance: list[MergedPrimarySourceIdentifier] = []
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


class _BaseRuleSet(_Stem, RuleSet):
    additive: AdditiveResource = AdditiveResource()
    subtractive: SubtractiveResource = SubtractiveResource()
    preventive: PreventiveResource = PreventiveResource()


class ResourceRuleSetRequest(_BaseRuleSet):
    """Set of rules to create or update a resource item."""

    entityType: Annotated[
        Literal["ResourceRuleSetRequest"], Field(alias="$type", frozen=True)
    ] = "ResourceRuleSetRequest"


class ResourceRuleSetResponse(_BaseRuleSet):
    """Set of rules to retrieve a resource item."""

    entityType: Annotated[
        Literal["ResourceRuleSetResponse"], Field(alias="$type", frozen=True)
    ] = "ResourceRuleSetResponse"
    stableTargetId: MergedResourceIdentifier


class ResourceMapping(_Stem, BaseMapping):
    """Mapping for describing a resource transformation."""

    entityType: Annotated[
        Literal["ResourceMapping"], Field(alias="$type", frozen=True)
    ] = "ResourceMapping"
    hadPrimarySource: Annotated[
        list[MappingField[MergedPrimarySourceIdentifier]], Field(min_length=1)
    ]
    identifierInPrimarySource: Annotated[list[MappingField[str]], Field(min_length=1)]
    accessRestriction: Annotated[
        list[MappingField[AccessRestriction]], Field(min_length=1)
    ]
    accrualPeriodicity: list[MappingField[Frequency | None]] = []
    created: list[
        MappingField[YearMonthDayTime | YearMonthDay | YearMonth | Year | None]
    ] = []
    doi: list[MappingField[DoiStr | None]] = []
    hasPersonalData: list[MappingField[PersonalData | None]] = []
    license: list[MappingField[License | None]] = []
    maxTypicalAge: list[MappingField[MaxTypicalAgeInt | None]] = []
    minTypicalAge: list[MappingField[MinTypicalAgeInt | None]] = []
    modified: list[
        MappingField[YearMonthDayTime | YearMonthDay | YearMonth | Year | None]
    ] = []
    sizeOfDataBasis: list[MappingField[str | None]] = []
    temporal: list[
        MappingField[
            YearMonthDayTime | YearMonthDay | YearMonth | Year | TemporalStr | None
        ]
    ] = []
    wasGeneratedBy: list[MappingField[MergedActivityIdentifier | None]] = []
    contact: Annotated[
        list[MappingField[list[AnyContactIdentifier]]],
        Field(min_length=1),
    ]
    theme: Annotated[list[MappingField[list[Theme]]], Field(min_length=1)]
    title: Annotated[list[MappingField[list[Text]]], Field(min_length=1)]
    unitInCharge: Annotated[
        list[MappingField[list[MergedOrganizationalUnitIdentifier]]],
        Field(min_length=1),
    ]
    accessPlatform: list[MappingField[list[MergedAccessPlatformIdentifier]]] = []
    alternativeTitle: list[MappingField[list[Text]]] = []
    anonymizationPseudonymization: list[
        MappingField[list[AnonymizationPseudonymization]]
    ] = []
    conformsTo: list[MappingField[list[ConformsToStr]]] = []
    contributingUnit: list[MappingField[list[MergedOrganizationalUnitIdentifier]]] = []
    contributor: list[MappingField[list[MergedPersonIdentifier]]] = []
    creator: list[MappingField[list[MergedPersonIdentifier]]] = []
    description: list[MappingField[list[Text]]] = []
    distribution: list[MappingField[list[MergedDistributionIdentifier]]] = []
    documentation: list[MappingField[list[Link]]] = []
    externalPartner: list[MappingField[list[MergedOrganizationIdentifier]]] = []
    hasLegalBasis: list[MappingField[list[Text]]] = []
    hasPurpose: list[MappingField[list[Text]]] = []
    icd10code: list[MappingField[list[str]]] = []
    instrumentToolOrApparatus: list[MappingField[list[Text]]] = []
    isPartOf: list[MappingField[list[MergedResourceIdentifier]]] = []
    keyword: list[MappingField[list[Text]]] = []
    language: list[MappingField[list[Language]]] = []
    loincId: list[MappingField[list[LoincIdStr]]] = []
    meshId: list[MappingField[list[MeshIdStr]]] = []
    method: list[MappingField[list[Text]]] = []
    methodDescription: list[MappingField[list[Text]]] = []
    populationCoverage: list[MappingField[list[Text]]] = []
    provenance: list[MappingField[list[Text]]] = []
    publication: list[MappingField[list[MergedBibliographicResourceIdentifier]]] = []
    publisher: list[MappingField[list[MergedOrganizationIdentifier]]] = []
    qualityInformation: list[MappingField[list[Text]]] = []
    resourceCreationMethod: list[MappingField[list[ResourceCreationMethod]]] = []
    resourceTypeGeneral: list[MappingField[list[ResourceTypeGeneral]]] = []
    resourceTypeSpecific: list[MappingField[list[Text]]] = []
    rights: list[MappingField[list[Text]]] = []
    spatial: list[MappingField[list[Text]]] = []
    stateOfDataProcessing: list[MappingField[list[DataProcessingState]]] = []


class ResourceFilter(_Stem, BaseFilter):
    """Class for defining filter rules for resource items."""

    entityType: Annotated[
        Literal["ResourceFilter"], Field(alias="$type", frozen=True)
    ] = "ResourceFilter"
    fields: Annotated[list[FilterField], Field(title="fields")] = []
