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
    WorkflowRule,
)
from mex.common.types import (
    ExtractedResourceSeriesIdentifier,
    Frequency,
    Identifier,
    Link,
    MergedAccessPlatformIdentifier,
    MergedContactPointIdentifier,
    MergedOrganizationalUnitIdentifier,
    MergedOrganizationIdentifier,
    MergedPersonIdentifier,
    MergedPrimarySourceIdentifier,
    MergedResourceSeriesIdentifier,
    Text,
    Year,
    YearMonth,
    YearMonthDay,
    YearMonthDayTime,
)

AnyContactIdentifier = Annotated[
    MergedOrganizationalUnitIdentifier
    | MergedPersonIdentifier
    | MergedContactPointIdentifier,
    AfterValidator(Identifier),
]


class _Stem(BaseModel):
    stemType: ClassVar[Annotated[Literal["ResourceSeries"], Field(frozen=True)]] = (
        "ResourceSeries"
    )


class _OptionalLists(_Stem):
    accessPlatform: Annotated[
        list[MergedAccessPlatformIdentifier],
        Field(
            description="A platform from which the resource series can be accessed.",
            json_schema_extra={
                "closeMatch": ["http://www.w3.org/ns/dcat#accessService"]
            },
        ),
    ] = []
    alternativeTitle: Annotated[
        list[Text],
        Field(
            description="An alternative name for the resource series.",
            json_schema_extra={"closeMatch": ["http://purl.org/dc/terms/alternative"]},
        ),
    ] = []
    contact: Annotated[
        list[AnyContactIdentifier],
        Field(
            description="An agent that serves as a contact for the resource series.",
            json_schema_extra={
                "closeMatch": ["http://www.w3.org/ns/dcat#contactPoint"]
            },
        ),
    ] = []
    documentation: Annotated[
        list[Link],
        Field(
            description="A link to a document documenting the resource series.",
            json_schema_extra={
                "closeMatch": ["http://purl.org/dc/terms/isReferencedBy"]
            },
        ),
    ] = []
    end: Annotated[
        list[YearMonthDayTime | YearMonthDay | YearMonth | Year],
        Field(
            description="End date of the temporal coverage of the resource series.",
            json_schema_extra={"closeMatch": ["http://www.w3.org/ns/dcat#endDate"]},
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
            json_schema_extra={"closeMatch": ["https://w3id.org/dpv#hasLegalBasis"]},
        ),
    ] = []
    keyword: Annotated[
        list[Text],
        Field(
            description="A keyword or tag describing the resource series.",
            json_schema_extra={"closeMatch": ["http://www.w3.org/ns/dcat#keyword"]},
        ),
    ] = []
    publisher: Annotated[
        list[MergedOrganizationIdentifier],
        Field(
            description="The entity responsible for making the item available.",
        ),
    ] = []
    spatial: Annotated[
        list[Text],
        Field(
            description="Spatial coverage of the resource series.",
            json_schema_extra={"closeMatch": ["http://purl.org/dc/terms/spatial"]},
        ),
    ] = []
    start: Annotated[
        list[YearMonthDayTime | YearMonthDay | YearMonth | Year],
        Field(
            description="Start date of the temporal coverage of the resource series.",
            json_schema_extra={"closeMatch": ["http://www.w3.org/ns/dcat#startDate"]},
        ),
    ] = []


class _RequiredLists(_Stem):
    description: Annotated[
        list[Text],
        Field(
            description="A text describing the nature of the resource series.",
            min_length=1,
            json_schema_extra={"closeMatch": ["http://purl.org/dc/terms/description"]},
        ),
    ]
    title: Annotated[
        list[Text],
        Field(
            description="The name of the resource series.",
            min_length=1,
            json_schema_extra={"closeMatch": ["http://purl.org/dc/terms/title"]},
        ),
    ]


class _SparseLists(_Stem):
    description: Annotated[
        list[Text],
        Field(
            description="A text describing the nature of the resource series.",
            json_schema_extra={"closeMatch": ["http://purl.org/dc/terms/description"]},
        ),
    ] = []
    title: Annotated[
        list[Text],
        Field(
            description="The name of the resource series.",
            json_schema_extra={"closeMatch": ["http://purl.org/dc/terms/title"]},
        ),
    ] = []


class _OptionalValues(_Stem):
    accrualPeriodicity: Annotated[
        Frequency | None,
        Field(
            description="The frequency with which items are added to a collection.",
            json_schema_extra={
                "closeMatch": ["http://purl.org/dc/terms/accrualPeriodicity"]
            },
        ),
    ] = None


class _VariadicValues(_Stem):
    accrualPeriodicity: Annotated[
        list[Frequency],
        Field(
            description="The frequency with which items are added to a collection.",
            json_schema_extra={
                "closeMatch": ["http://purl.org/dc/terms/accrualPeriodicity"]
            },
        ),
    ] = []


class BaseResourceSeries(
    _OptionalLists,
    _RequiredLists,
    _OptionalValues,
    json_schema_extra={
        "description": (
            "A collection of resources that are published separately, but share "
            "some characteristics that group them."
        ),
        "closeMatch": ["http://healthdataportal.eu/ns/health#DatasetSeries"],
    },
):
    """All fields for a valid resource."""


class ExtractedResourceSeries(BaseResourceSeries, ExtractedData):
    """An automatically extracted metadata set describing a resource series."""

    entityType: Annotated[
        Literal["ExtractedResourceSeries"], Field(alias="$type", frozen=True)
    ] = "ExtractedResourceSeries"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def identifier(  # noqa: D102
        self,
    ) -> Annotated[
        ExtractedResourceSeriesIdentifier,
        Field(
            description=(
                "An unambiguous reference to the resource within a given "
                "context. Persistent identifiers should be provided as HTTP URIs "
                "([DCT, 2020-01-20](http://dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/))."
            ),
            json_schema_extra={
                "closeMatch": ["http://purl.org/dc/elements/1.1/identifier"]
            },
        ),
    ]:
        return self._get_identifier(ExtractedResourceSeriesIdentifier)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def stableTargetId(  # noqa: D102, N802
        self,
    ) -> Annotated[
        MergedResourceSeriesIdentifier,
        Field(
            description=(
                "The identifier of the merged item that this extracted item belongs to."
            )
        ),
    ]:
        return self._get_stable_target_id(MergedResourceSeriesIdentifier)


class MergedResourceSeries(BaseResourceSeries, MergedItem):
    """The result of merging all extracted items and rules for a resource series."""

    entityType: Annotated[
        Literal["MergedResourceSeries"], Field(alias="$type", frozen=True)
    ] = "MergedResourceSeries"
    identifier: Annotated[
        MergedResourceSeriesIdentifier,
        Field(
            json_schema_extra={
                "description": (
                    "An unambiguous reference to the resource within a given "
                    "context. Persistent identifiers should be provided as HTTP URIs "
                    "([DCT, 2020-01-20](http://dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/))."
                ),
                "readOnly": True,
                "closeMatch": ["http://purl.org/dc/elements/1.1/identifier"],
            },
            frozen=True,
        ),
    ]
    supersededBy: Annotated[
        MergedResourceSeriesIdentifier | None,
        Field(
            json_schema_extra={
                "description": (
                    "A merged item which is the preferred duplicate, because it "
                    "replaces, consolidates or otherwise makes the current merged item "
                    "obsolete."
                ),
            }
        ),
    ] = None


class PreviewResourceSeries(_OptionalLists, _SparseLists, _VariadicValues, PreviewItem):
    """Preview for merging all extracted items and rules for a resource series."""

    entityType: Annotated[
        Literal["PreviewResourceSeries"], Field(alias="$type", frozen=True)
    ] = "PreviewResourceSeries"
    identifier: Annotated[
        MergedResourceSeriesIdentifier,
        Field(
            json_schema_extra={
                "description": (
                    "An unambiguous reference to the resource within a given "
                    "context. Persistent identifiers should be provided as HTTP URIs "
                    "([DCT, 2020-01-20](http://dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/))."
                ),
                "readOnly": True,
                "closeMatch": ["http://purl.org/dc/elements/1.1/identifier"],
            },
            frozen=True,
        ),
    ]
    supersededBy: Annotated[
        MergedResourceSeriesIdentifier | None,
        Field(
            json_schema_extra={
                "description": (
                    "A merged item which is the preferred duplicate, because it "
                    "replaces, consolidates or otherwise makes the current merged item "
                    "obsolete."
                ),
            }
        ),
    ] = None


class AdditiveResourceSeries(
    _OptionalLists, _SparseLists, _OptionalValues, AdditiveRule
):
    """Rule to add values to merged resource series items."""

    entityType: Annotated[
        Literal["AdditiveResourceSeries"], Field(alias="$type", frozen=True)
    ] = "AdditiveResourceSeries"
    supersededBy: Annotated[
        MergedResourceSeriesIdentifier | None,
        Field(
            json_schema_extra={
                "description": (
                    "A merged item which is the preferred duplicate, because it "
                    "replaces, consolidates or otherwise makes the current merged item "
                    "obsolete."
                ),
            }
        ),
    ] = None


class SubtractiveResourceSeries(
    _OptionalLists, _SparseLists, _VariadicValues, SubtractiveRule
):
    """Rule to subtract values from merged resource series items."""

    entityType: Annotated[
        Literal["SubtractiveResourceSeries"], Field(alias="$type", frozen=True)
    ] = "SubtractiveResourceSeries"


class PreventiveResourceSeries(_Stem, PreventiveRule):
    """Rule to prevent primary sources for fields of merged resource series items."""

    entityType: Annotated[
        Literal["PreventiveResourceSeries"], Field(alias="$type", frozen=True)
    ] = "PreventiveResourceSeries"
    accessPlatform: list[MergedPrimarySourceIdentifier] = []
    accrualPeriodicity: list[MergedPrimarySourceIdentifier] = []
    alternativeTitle: list[MergedPrimarySourceIdentifier] = []
    contact: list[MergedPrimarySourceIdentifier] = []
    description: list[MergedPrimarySourceIdentifier] = []
    documentation: list[MergedPrimarySourceIdentifier] = []
    end: list[MergedPrimarySourceIdentifier] = []
    hasLegalBasis: list[MergedPrimarySourceIdentifier] = []
    keyword: list[MergedPrimarySourceIdentifier] = []
    publisher: list[MergedPrimarySourceIdentifier] = []
    spatial: list[MergedPrimarySourceIdentifier] = []
    start: list[MergedPrimarySourceIdentifier] = []
    title: list[MergedPrimarySourceIdentifier] = []


class WorkflowResourceSeries(_Stem, WorkflowRule):
    """Rule to prevent publishing of merged resource series items."""

    entityType: Annotated[
        Literal["WorkflowResourceSeries"], Field(alias="$type", frozen=True)
    ] = "WorkflowResourceSeries"


class _BaseRuleSet(_Stem, RuleSet):
    """Base class for sets of rules for a resource series item."""

    additive: AdditiveResourceSeries = AdditiveResourceSeries()
    subtractive: SubtractiveResourceSeries = SubtractiveResourceSeries()
    preventive: PreventiveResourceSeries = PreventiveResourceSeries()
    workflow: WorkflowResourceSeries = WorkflowResourceSeries()


class ResourceSeriesRuleSetRequest(_BaseRuleSet):
    """Set of rules to create or update a resource series item."""

    entityType: Annotated[
        Literal["ResourceSeriesRuleSetRequest"], Field(alias="$type", frozen=True)
    ] = "ResourceSeriesRuleSetRequest"


class ResourceSeriesRuleSetResponse(_BaseRuleSet):
    """Set of rules to retrieve a resource series item."""

    entityType: Annotated[
        Literal["ResourceSeriesRuleSetResponse"], Field(alias="$type", frozen=True)
    ] = "ResourceSeriesRuleSetResponse"
    stableTargetId: MergedResourceSeriesIdentifier


class ResourceSeriesMapping(_Stem, BaseMapping):
    """Mapping for describing a resource series transformation."""

    entityType: Annotated[
        Literal["ResourceSeriesMapping"], Field(alias="$type", frozen=True)
    ] = "ResourceSeriesMapping"
    accrualPeriodicity: list[MappingField[Frequency | None]] = []
    contact: list[MappingField[list[AnyContactIdentifier]]] = []
    title: Annotated[list[MappingField[list[Text]]], Field(min_length=1)]
    accessPlatform: list[MappingField[list[MergedAccessPlatformIdentifier]]] = []
    alternativeTitle: list[MappingField[list[Text]]] = []
    description: Annotated[list[MappingField[list[Text]]], Field(min_length=1)]
    documentation: list[MappingField[list[Link]]] = []
    end: list[MappingField[YearMonthDayTime | YearMonthDay | YearMonth | Year]] = []
    hasLegalBasis: list[MappingField[list[Text]]] = []
    keyword: list[MappingField[list[Text]]] = []
    publisher: list[MappingField[list[MergedOrganizationIdentifier]]] = []
    spatial: list[MappingField[list[Text]]] = []
    start: list[MappingField[YearMonthDayTime | YearMonthDay | YearMonth | Year]] = []


class ResourceSeriesFilter(_Stem, BaseFilter):
    """Class for defining filter rules for resource series items."""

    entityType: Annotated[
        Literal["ResourceSeriesFilter"], Field(alias="$type", frozen=True)
    ] = "ResourceSeriesFilter"
    fields: Annotated[list[FilterField], Field(title="fields")] = []
