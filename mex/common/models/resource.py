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

ConformsToStr = Annotated[
    str,
    Field(
        examples=[
            "FHIR",
            "LOINC",
            "SNOMED",
            "ICD-10",
        ],
    ),
]
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
        ],
    ),
]
AnyContactIdentifier = Annotated[
    MergedOrganizationalUnitIdentifier
    | MergedPersonIdentifier
    | MergedContactPointIdentifier,
    AfterValidator(Identifier),
]
MaxTypicalAgeInt = Annotated[
    int,
    Field(
        examples=[
            "99",
            "21",
        ]
    ),
]
MinTypicalAgeInt = Annotated[
    int,
    Field(
        examples=[
            "0",
            "18",
        ]
    ),
]


class _Stem(BaseModel):
    stemType: ClassVar[Annotated[Literal["Resource"], Field(frozen=True)]] = "Resource"


class _OptionalLists(_Stem):
    accessPlatform: Annotated[
        list[MergedAccessPlatformIdentifier],
        Field(
            description="A platform from which the resource can be accessed.",
            json_schema_extra={"sameAs": ["http://www.w3.org/ns/dcat#accessService"]},
        ),
    ] = []
    alternativeTitle: Annotated[
        list[Text],
        Field(
            description="An alternative name for the resource.",
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/alternative"]},
        ),
    ] = []
    anonymizationPseudonymization: Annotated[
        list[AnonymizationPseudonymization],
        Field(
            description=(
                "Indicates whether the data has been anonymized and/or pseudonymized."
            )
        ),
    ] = []
    conformsTo: Annotated[
        list[ConformsToStr],
        Field(
            description=(
                "Standards used in the creation, analysis or transmission of the "
                "resource."
            ),
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/conformsTo"]},
        ),
    ] = []
    contributingUnit: Annotated[
        list[MergedOrganizationalUnitIdentifier],
        Field(
            description=(
                "An organizational unit of RKI, that is contributing to the resource."
            ),
            json_schema_extra={
                "subPropertyOf": ["http://purl.org/dc/terms/contributor"]
            },
        ),
    ] = []
    contributor: Annotated[
        list[MergedPersonIdentifier],
        Field(
            description="A person involved in the creation of the resource.",
            json_schema_extra={
                "subPropertyOf": ["http://purl.org/dc/terms/contributor"]
            },
        ),
    ] = []
    creator: Annotated[
        list[MergedPersonIdentifier],
        Field(
            description="A person responsible for making the resource.",
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/creator"]},
        ),
    ] = []
    description: Annotated[
        list[Text],
        Field(
            description="A text describing the nature of the resource.",
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/description"]},
        ),
    ] = []
    distribution: Annotated[
        list[MergedDistributionIdentifier],
        Field(description="An available distribution of the resource"),
    ] = []
    documentation: Annotated[
        list[Link],
        Field(
            description="A link to a document documenting the resource.",
            json_schema_extra={
                "subPropertyOf": ["http://purl.org/dc/terms/isReferencedBy"]
            },
        ),
    ] = []
    externalPartner: Annotated[
        list[MergedOrganizationIdentifier],
        Field(
            description=(
                "An external organization that is somehow involved in the "
                "creation of the resource."
            ),
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/contributor"]},
        ),
    ] = []
    hasLegalBasis: Annotated[
        list[Text],
        Field(
            description=(
                "The legal basis used to justify processing of personal data. "
                "Legal basis (plural: legal bases) are defined by legislations "
                "and regulations, whose applicability is usually restricted to "
                "specific jurisdictions which can be represented using "
                "dpv:hasJurisdiction or dpv:hasLaw. Legal basis can be used "
                "without such declarations, e.g. 'Consent', however their "
                "interpretation will require association with a law, e.g. "
                "'EU GDPR'."
            ),
            json_schema_extra={"sameAs": ["https://w3id.org/dpv#hasLegalBasis"]},
        ),
    ] = []
    hasPurpose: Annotated[
        list[Text],
        Field(
            description=(
                "A free text statement of the purpose of the processing of data "
                "or personal data."
            ),
            json_schema_extra={"sameAs": ["https://w3id.org/dpv#hasPurpose"]},
        ),
    ] = []
    icd10code: Annotated[
        list[str],
        Field(description="A concept from ICD-10."),
    ] = []
    instrumentToolOrApparatus: Annotated[
        list[Text],
        Field(
            description=(
                "Instrument, tool, or apparatus used in the research, analysis, "
                "observation, or processing of the object that is the subject of "
                "this resource."
            ),
        ),
    ] = []
    isPartOf: Annotated[
        list[MergedResourceIdentifier],
        Field(
            description=(
                "A related resource, in which the described resource is "
                "physically or logically included."
            ),
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/isPartOf"]},
        ),
    ] = []
    keyword: Annotated[
        list[Text],
        Field(
            description="A keyword or tag describing the resource.",
            json_schema_extra={"sameAs": ["http://www.w3.org/ns/dcat#keyword"]},
        ),
    ] = []
    language: Annotated[
        list[Language],
        Field(
            description="A language of the resource.",
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/language"]},
        ),
    ] = []
    loincId: Annotated[
        list[LoincIdStr],
        Field(description="A concept from LOINC."),
    ] = []
    meshId: Annotated[
        list[MeshIdStr],
        Field(description="A concept from MeSH."),
    ] = []
    method: Annotated[
        list[Text],
        Field(
            description=(
                "Method used in the research, analysis, observation or "
                "processing of the object that is subject to the resource."
            ),
        ),
    ] = []
    methodDescription: Annotated[
        list[Text],
        Field(
            description=(
                "The description of the method, that was used to research, "
                "analysis, observation or processing of the object that was "
                "subject to the resource."
            ),
            json_schema_extra={
                "subPropertyOf": ["http://purl.org/dc/terms/description"]
            },
        ),
    ] = []
    populationCoverage: Annotated[
        list[Text],
        Field(
            description=(
                "The type of population common to all subjects of the data collection."
            ),
        ),
    ] = []
    provenance: Annotated[
        list[Text],
        Field(
            description=(
                "A statement about the lineage of a Dataset. Information about "
                "how the data was collected, including methodologies, tools, and "
                "protocols used."
            ),
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/provenance"]},
        ),
    ] = []
    publication: Annotated[
        list[MergedBibliographicResourceIdentifier],
        Field(
            description=(
                "A publication that deals with the research, analysis, "
                "observation or processing of the object that was subject to the "
                "resource, e.g. a research paper."
            ),
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/isReferencedBy"]},
        ),
    ] = []
    publisher: Annotated[
        list[MergedOrganizationIdentifier],
        Field(
            description="The entity responsible for making the item available.",
        ),
    ] = []
    qualityInformation: Annotated[
        list[Text],
        Field(
            description="Some information about the quality of the resource.",
            json_schema_extra={
                "sameAs": ["http://www.w3.org/ns/dqv#hasQualityAnnotation"]
            },
        ),
    ] = []
    resourceCreationMethod: Annotated[
        list[ResourceCreationMethod],
        Field(
            description="Method how the resource was created.",
            json_schema_extra={"subPropertyOf": ["http://purl.org/dc/terms/type"]},
        ),
    ] = []
    resourceTypeGeneral: Annotated[
        list[ResourceTypeGeneral],
        Field(
            description="General type of the resource.",
            json_schema_extra={"subPropertyOf": ["http://purl.org/dc/terms/type"]},
        ),
    ] = []
    resourceTypeSpecific: Annotated[
        list[Text],
        Field(
            description=(
                "A term describing the specific nature of the resource. A more "
                "precise term than given by the property 'resourceTypeGeneral'."
            ),
            json_schema_extra={"subPropertyOf": ["http://purl.org/dc/terms/type"]},
        ),
    ] = []
    rights: Annotated[
        list[Text],
        Field(
            description=(
                "Information about rights held in and over the resource as well "
                "as rights about the possibilities of the usage of the resource."
            ),
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/rights"]},
        ),
    ] = []
    spatial: Annotated[
        list[Text],
        Field(
            description="Spatial coverage of the resource.",
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/spatial"]},
        ),
    ] = []
    stateOfDataProcessing: Annotated[
        list[DataProcessingState],
        Field(
            description="The processing state of the data, e.g. raw or aggregated.",
        ),
    ] = []


class _RequiredLists(_Stem):
    contact: Annotated[
        list[AnyContactIdentifier],
        Field(
            description="An agent that serves as a contact for the resource.",
            min_length=1,
            json_schema_extra={"sameAs": ["http://www.w3.org/ns/dcat#contactPoint"]},
        ),
    ]
    theme: Annotated[
        list[Theme],
        Field(
            description=(
                "A main category of the resource. A resource can have multiple themes."
            ),
            min_length=1,
            json_schema_extra={"sameAs": ["http://www.w3.org/ns/dcat#theme"]},
        ),
    ]
    title: Annotated[
        list[Text],
        Field(
            description="The name of the resource.",
            min_length=1,
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/title"]},
        ),
    ]
    unitInCharge: Annotated[
        list[MergedOrganizationalUnitIdentifier],
        Field(
            description=(
                "This property refers to agents who assume responsibility and "
                "accountability for the resource and its appropriate maintenance."
            ),
            min_length=1,
            json_schema_extra={"sameAs": ["http://dcat-ap.de/def/dcatde/maintainer"]},
        ),
    ]


class _SparseLists(_Stem):
    contact: Annotated[
        list[AnyContactIdentifier],
        Field(
            description="An agent that serves as a contact for the resource.",
            json_schema_extra={"sameAs": ["http://www.w3.org/ns/dcat#contactPoint"]},
        ),
    ] = []
    theme: Annotated[
        list[Theme],
        Field(
            description=(
                "A main category of the resource. A resource can have multiple themes."
            ),
            json_schema_extra={"sameAs": ["http://www.w3.org/ns/dcat#theme"]},
        ),
    ] = []
    title: Annotated[
        list[Text],
        Field(
            description="The name of the resource.",
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/title"]},
        ),
    ] = []
    unitInCharge: Annotated[
        list[MergedOrganizationalUnitIdentifier],
        Field(
            description=(
                "This property refers to agents who assume responsibility and "
                "accountability for the resource and its appropriate maintenance."
            ),
            json_schema_extra={"sameAs": ["http://dcat-ap.de/def/dcatde/maintainer"]},
        ),
    ] = []


class _OptionalValues(_Stem):
    accrualPeriodicity: Annotated[
        Frequency | None,
        Field(
            description=("The frequency with which items are added to a collection."),
            json_schema_extra={
                "sameAs": ["http://purl.org/dc/terms/accrualPeriodicity"]
            },
        ),
    ] = None
    created: Annotated[
        YearMonthDayTime | YearMonthDay | YearMonth | Year | None,
        Field(
            description="Date of creation of the resource",
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/created"]},
        ),
    ] = None
    doi: Annotated[
        DoiStr | None,
        Field(description="The Digital Object Identifier (DOI) of the resource."),
    ] = None
    hasPersonalData: Annotated[
        PersonalData | None,
        Field(
            description=(
                "Indicates, if a resource contains data directly or indirectly "
                "associated or related to an individual."
            ),
            json_schema_extra={"sameAs": ["https://w3id.org/dpv#hasPersonalData"]},
        ),
    ] = None
    license: Annotated[
        License | None,
        Field(
            description=(
                "A legal document giving official permission to do something with "
                "the resource."
            ),
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/license"]},
        ),
    ] = None
    maxTypicalAge: Annotated[
        MaxTypicalAgeInt | None,
        Field(
            description=(
                "Specifies the maximum age of the population within the data "
                "collection, expressed in years."
            )
        ),
    ] = None
    minTypicalAge: Annotated[
        MinTypicalAgeInt | None,
        Field(
            description=(
                "Specifies the minimum age of the population within the data "
                "collection, expressed in years."
            )
        ),
    ] = None
    modified: Annotated[
        YearMonthDayTime | YearMonthDay | YearMonth | Year | None,
        Field(
            description="Date on which the resource was changed.",
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/modified"]},
        ),
    ] = None
    sizeOfDataBasis: Annotated[
        str | None,
        Field(
            description=(
                "The size of the underlying data basis, e.g. for studies: the "
                "size of the sample."
            )
        ),
    ] = None
    temporal: Annotated[
        YearMonthDayTime | YearMonthDay | YearMonth | Year | TemporalStr | None,
        Field(
            description="Temporal coverage of the resource.",
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/temporal"]},
        ),
    ] = None
    wasGeneratedBy: Annotated[
        MergedActivityIdentifier | None,
        Field(
            description=(
                "Generation is the completion of production of a new entity by an "
                "activity. This entity did not exist before generation and "
                "becomes available for usage after this generation."
            ),
            json_schema_extra={"sameAs": "http://www.w3.org/ns/prov#wasGeneratedBy"},
        ),
    ] = None


class _RequiredValues(_Stem):
    accessRestriction: Annotated[
        AccessRestriction,
        Field(
            description="Indicates how access to the resource is restricted.",
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/accessRights"]},
        ),
    ]


class _SparseValues(_Stem):
    accessRestriction: Annotated[
        AccessRestriction | None,
        Field(
            description="Indicates how access to the resource is restricted.",
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/accessRights"]},
        ),
    ] = None


class _VariadicValues(_Stem):
    accessRestriction: Annotated[
        list[AccessRestriction],
        Field(
            description="Indicates how access to the resource is restricted.",
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/accessRights"]},
        ),
    ] = []
    accrualPeriodicity: Annotated[
        list[Frequency],
        Field(
            description="The frequency with which items are added to a collection.",
            json_schema_extra={
                "sameAs": ["http://purl.org/dc/terms/accrualPeriodicity"]
            },
        ),
    ] = []
    created: Annotated[
        list[YearMonthDayTime | YearMonthDay | YearMonth | Year],
        Field(
            description="Date of creation of the resource",
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/created"]},
        ),
    ] = []
    doi: Annotated[
        list[DoiStr],
        Field(description="The Digital Object Identifier (DOI) of the resource."),
    ] = []
    hasPersonalData: Annotated[
        list[PersonalData],
        Field(
            description=(
                "Indicates, if a resource contains data directly or indirectly "
                "associated or related to an individual."
            ),
            json_schema_extra={"sameAs": ["https://w3id.org/dpv#hasPersonalData"]},
        ),
    ] = []
    license: Annotated[
        list[License],
        Field(
            description=(
                "A legal document giving official permission to do something with "
                "the resource."
            ),
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/license"]},
        ),
    ] = []
    maxTypicalAge: Annotated[
        list[MaxTypicalAgeInt],
        Field(
            description=(
                "Specifies the maximum age of the population within the data "
                "collection, expressed in years."
            )
        ),
    ] = []
    minTypicalAge: Annotated[
        list[MinTypicalAgeInt],
        Field(
            description=(
                "Specifies the minimum age of the population within the data "
                "collection, expressed in years."
            )
        ),
    ] = []
    modified: Annotated[
        list[YearMonthDayTime | YearMonthDay | YearMonth | Year],
        Field(
            description="Date on which the resource was changed.",
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/modified"]},
        ),
    ] = []
    sizeOfDataBasis: Annotated[
        list[str],
        Field(
            description=(
                "The size of the underlying data basis, e.g. for studies: the "
                "size of the sample."
            )
        ),
    ] = []
    temporal: Annotated[
        list[YearMonthDayTime | YearMonthDay | YearMonth | Year | TemporalStr],
        Field(
            description="Temporal coverage of the resource.",
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/temporal"]},
        ),
    ] = []
    wasGeneratedBy: Annotated[
        list[MergedActivityIdentifier],
        Field(
            description=(
                "Generation is the completion of production of a new entity by an "
                "activity. This entity did not exist before generation and "
                "becomes available for usage after this generation."
            ),
            json_schema_extra={"sameAs": "http://www.w3.org/ns/prov#wasGeneratedBy"},
        ),
    ] = []


class BaseResource(
    _OptionalLists,
    _RequiredLists,
    _OptionalValues,
    _RequiredValues,
    json_schema_extra={
        "description": (
            "A defined piece of information or collection of information on Public "
            "Health, that has been generated as part of a (research) activity at the "
            "RKI or to comply with a (federal) law or regulation that applies to the "
            "RKI."
        ),
        "sameAs": ["http://www.w3.org/ns/dcat#Dataset"],
    },
):
    """All fields for a valid resource except for provenance."""


class ExtractedResource(BaseResource, ExtractedData):
    """An automatically extracted metadata set describing a resource."""

    entityType: Annotated[
        Literal["ExtractedResource"], Field(alias="$type", frozen=True)
    ] = "ExtractedResource"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def identifier(
        self,
    ) -> Annotated[
        ExtractedResourceIdentifier,
        Field(
            json_schema_extra={
                "sameAs": ["http://purl.org/dc/elements/1.1/identifier"]
            },
        ),
    ]:
        """An unambiguous reference to the resource within a given context."""
        return self._get_identifier(ExtractedResourceIdentifier)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def stableTargetId(self) -> MergedResourceIdentifier:  # noqa: N802
        """The identifier of the merged item that this extracted item belongs to."""
        return self._get_stable_target_id(MergedResourceIdentifier)


class MergedResource(BaseResource, MergedItem):
    """The result of merging all extracted items and rules for a resource."""

    entityType: Annotated[
        Literal["MergedResource"], Field(alias="$type", frozen=True)
    ] = "MergedResource"
    identifier: Annotated[
        MergedResourceIdentifier,
        Field(
            json_schema_extra={
                "description": (
                    "An unambiguous reference to the resource within a given context."
                ),
                "readOnly": True,
                "sameAs": ["http://purl.org/dc/elements/1.1/identifier"],
            },
            frozen=True,
        ),
    ]


class PreviewResource(
    _OptionalLists, _SparseLists, _OptionalValues, _SparseValues, PreviewItem
):
    """Preview for merging all extracted items and rules for a resource."""

    entityType: Annotated[
        Literal["PreviewResource"], Field(alias="$type", frozen=True)
    ] = "PreviewResource"
    identifier: Annotated[
        MergedResourceIdentifier,
        Field(
            json_schema_extra={
                "description": (
                    "An unambiguous reference to the resource within a given context."
                ),
                "readOnly": True,
                "sameAs": ["http://purl.org/dc/elements/1.1/identifier"],
            },
            frozen=True,
        ),
    ]


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
    """Base class for sets of rules for a resource item."""

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
