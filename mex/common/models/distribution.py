from typing import Annotated, ClassVar, Literal

from pydantic import Field, computed_field

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
    ExtractedDistributionIdentifier,
    License,
    Link,
    MergedAccessPlatformIdentifier,
    MergedDistributionIdentifier,
    MergedPrimarySourceIdentifier,
    MIMEType,
    Text,
    Year,
    YearMonth,
    YearMonthDay,
    YearMonthDayTime,
)


class _Stem(BaseModel):
    stemType: ClassVar[Annotated[Literal["Distribution"], Field(frozen=True)]] = (
        "Distribution"
    )


class _OptionalLists(_Stem):
    accessURL: Annotated[
        list[Link],
        Field(
            description=(
                "A URL of the resource that gives access to a distribution of the "
                "dataset. E.g. landing page, feed, SPARQL endpoint "
                "([DCAT, 2020-02-04](https://www.w3.org/TR/2020/"
                "REC-vocab-dcat-2-20200204/))."
            ),
            json_schema_extra={"sameAs": ["http://www.w3.org/ns/dcat#accessURL"]},
        ),
    ] = []
    downloadURL: Annotated[
        list[Link],
        Field(
            description=(
                "The URL of the downloadable file in a given format. E.g. CSV file "
                "or RDF file. The format is indicated by the distribution's "
                "`dcat:mediaType` ([DCAT, 2020-02-04](https://www.w3.org/TR/2020/"
                "REC-vocab-dcat-2-20200204/))."
            ),
            json_schema_extra={"sameAs": ["http://www.w3.org/ns/dcat#downloadURL"]},
        ),
    ] = []


class _RequiredLists(_Stem):
    title: Annotated[
        list[Text],
        Field(
            description="The name of the distribution.",
            min_length=1,
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/title"]},
        ),
    ]


class _SparseLists(_Stem):
    title: Annotated[
        list[Text],
        Field(
            description="The name of the distribution.",
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/title"]},
        ),
    ] = []


class _OptionalValues(_Stem):
    accessService: Annotated[
        MergedAccessPlatformIdentifier | None,
        Field(
            description=(
                "A data service that gives access to the distribution of the "
                "dataset ([DCAT, 2020-02-04](https://www.w3.org/TR/2020/"
                "REC-vocab-dcat-2-20200204/))."
            ),
            json_schema_extra={"sameAs": ["http://www.w3.org/ns/dcat#accessService"]},
        ),
    ] = None
    license: Annotated[
        License | None,
        Field(
            description=(
                "A legal document giving official permission to do something with "
                "the resource ([DCT, 2020-01-20](http://dublincore.org/"
                "specifications/dublin-core/dcmi-terms/2020-01-20/))."
            ),
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/license"]},
        ),
    ] = None
    mediaType: Annotated[
        MIMEType | None,
        Field(
            description=(
                "The media type of the distribution as defined by "
                "[IANA media types](https://www.iana.org/assignments/media-types/) "
                "([DCAT, 2020-02-04](https://www.w3.org/TR/2020/"
                "REC-vocab-dcat-2-20200204/))."
            ),
            json_schema_extra={
                "sameAs": [
                    "http://www.w3.org/ns/dcat#mediaType",
                    "http://purl.org/dc/terms/format",
                ]
            },
        ),
    ] = None
    modified: Annotated[
        YearMonthDayTime | YearMonthDay | YearMonth | Year | None,
        Field(
            description=(
                "Date on which the resource was changed ([DCT, 2020-01-20]"
                "(http://dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/))."
            ),
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/modified"]},
        ),
    ] = None


class _RequiredValues(_Stem):
    accessRestriction: Annotated[
        AccessRestriction,
        Field(
            description="Indicates how access to the distribution is restricted.",
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/accessRights"]},
        ),
    ]
    issued: Annotated[
        YearMonthDayTime | YearMonthDay | YearMonth | Year,
        Field(
            description=(
                "Date of formal issuance of the resource ([DCT, 2020-01-20]"
                "(http://dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/))."
            ),
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/issued"]},
        ),
    ]


class _SparseValues(_Stem):
    accessRestriction: Annotated[
        AccessRestriction | None,
        Field(
            description="Indicates how access to the distribution is restricted.",
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/accessRights"]},
        ),
    ] = None
    issued: Annotated[
        YearMonthDayTime | YearMonthDay | YearMonth | Year | None,
        Field(
            description=(
                "Date of formal issuance of the resource ([DCT, 2020-01-20]"
                "(http://dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/))."
            ),
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/issued"]},
        ),
    ] = None


class _VariadicValues(_Stem):
    accessRestriction: Annotated[
        list[AccessRestriction],
        Field(
            description="Indicates how access to the distribution is restricted.",
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/accessRights"]},
        ),
    ] = []
    accessService: Annotated[
        list[MergedAccessPlatformIdentifier],
        Field(
            description=(
                "A data service that gives access to the distribution of the "
                "dataset ([DCAT, 2020-02-04](https://www.w3.org/TR/2020/"
                "REC-vocab-dcat-2-20200204/))."
            ),
            json_schema_extra={"sameAs": ["http://www.w3.org/ns/dcat#accessService"]},
        ),
    ] = []
    issued: Annotated[
        list[YearMonthDayTime | YearMonthDay | YearMonth | Year],
        Field(
            description=(
                "Date of formal issuance of the resource ([DCT, 2020-01-20]"
                "(http://dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/))."
            ),
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/issued"]},
        ),
    ] = []
    license: Annotated[
        list[License],
        Field(
            description=(
                "A legal document giving official permission to do something with "
                "the resource ([DCT, 2020-01-20](http://dublincore.org/"
                "specifications/dublin-core/dcmi-terms/2020-01-20/))."
            ),
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/license"]},
        ),
    ] = []
    mediaType: Annotated[
        list[MIMEType],
        Field(
            description=(
                "The media type of the distribution as defined by "
                "[IANA media types](https://www.iana.org/assignments/media-types/) "
                "([DCAT, 2020-02-04](https://www.w3.org/TR/2020/"
                "REC-vocab-dcat-2-20200204/))."
            ),
            json_schema_extra={
                "sameAs": [
                    "http://www.w3.org/ns/dcat#mediaType",
                    "http://purl.org/dc/terms/format",
                ]
            },
        ),
    ] = []
    modified: Annotated[
        list[YearMonthDayTime | YearMonthDay | YearMonth | Year],
        Field(
            description=(
                "Date on which the resource was changed ([DCT, 2020-01-20]"
                "(http://dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/))."
            ),
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/modified"]},
        ),
    ] = []


class BaseDistribution(
    _OptionalLists,
    _RequiredLists,
    _OptionalValues,
    _RequiredValues,
    json_schema_extra={
        "description": (
            "A specific representation of a dataset. A dataset might be available in "
            "multiple serializations that may differ in various ways, including "
            "natural language, media-type or format, schematic organization, temporal "
            "and spatial resolution, level of detail or profiles (which might specify "
            "any or all of the above) ([DCAT, 2020-02-04]"
            "(https://www.w3.org/TR/2020/REC-vocab-dcat-2-20200204/))."
        ),
        "sameAs": ["http://www.w3.org/ns/dcat#Distribution"],
    },
):
    """All fields for a valid distribution except for provenance."""


class ExtractedDistribution(BaseDistribution, ExtractedData):
    """An automatically extracted metadata set describing a distribution."""

    entityType: Annotated[
        Literal["ExtractedDistribution"], Field(alias="$type", frozen=True)
    ] = "ExtractedDistribution"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def identifier(
        self,
    ) -> Annotated[
        ExtractedDistributionIdentifier,
        Field(
            json_schema_extra={"sameAs": ["http://purl.org/dc/elements/1.1/identifier"]}
        ),
    ]:
        """An unambiguous reference to the resource within a given context."""
        return self._get_identifier(ExtractedDistributionIdentifier)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def stableTargetId(self) -> MergedDistributionIdentifier:  # noqa: N802
        """The identifier of the merged item that this extracted item belongs to."""
        return self._get_stable_target_id(MergedDistributionIdentifier)


class MergedDistribution(BaseDistribution, MergedItem):
    """The result of merging all extracted items and rules for a distribution."""

    entityType: Annotated[
        Literal["MergedDistribution"], Field(alias="$type", frozen=True)
    ] = "MergedDistribution"
    identifier: Annotated[
        MergedDistributionIdentifier,
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


class PreviewDistribution(
    _OptionalLists, _SparseLists, _OptionalValues, _SparseValues, PreviewItem
):
    """Preview for merging all extracted items and rules for a distribution."""

    entityType: Annotated[
        Literal["PreviewDistribution"], Field(alias="$type", frozen=True)
    ] = "PreviewDistribution"
    identifier: Annotated[
        MergedDistributionIdentifier,
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


class AdditiveDistribution(
    _OptionalLists, _SparseLists, _OptionalValues, _SparseValues, AdditiveRule
):
    """Rule to add values to merged distribution items."""

    entityType: Annotated[
        Literal["AdditiveDistribution"], Field(alias="$type", frozen=True)
    ] = "AdditiveDistribution"


class SubtractiveDistribution(
    _OptionalLists, _SparseLists, _VariadicValues, SubtractiveRule
):
    """Rule to subtract values from merged distribution items."""

    entityType: Annotated[
        Literal["SubtractiveDistribution"], Field(alias="$type", frozen=True)
    ] = "SubtractiveDistribution"


class PreventiveDistribution(_Stem, PreventiveRule):
    """Rule to prevent primary sources for fields of merged distribution items."""

    entityType: Annotated[
        Literal["PreventiveDistribution"], Field(alias="$type", frozen=True)
    ] = "PreventiveDistribution"
    accessRestriction: list[MergedPrimarySourceIdentifier] = []
    accessService: list[MergedPrimarySourceIdentifier] = []
    accessURL: list[MergedPrimarySourceIdentifier] = []
    downloadURL: list[MergedPrimarySourceIdentifier] = []
    issued: list[MergedPrimarySourceIdentifier] = []
    license: list[MergedPrimarySourceIdentifier] = []
    mediaType: list[MergedPrimarySourceIdentifier] = []
    modified: list[MergedPrimarySourceIdentifier] = []
    title: list[MergedPrimarySourceIdentifier] = []


class _BaseRuleSet(_Stem, RuleSet):
    """Base class for sets of rules for a distribution item."""

    additive: AdditiveDistribution = AdditiveDistribution()
    subtractive: SubtractiveDistribution = SubtractiveDistribution()
    preventive: PreventiveDistribution = PreventiveDistribution()


class DistributionRuleSetRequest(_BaseRuleSet):
    """Set of rules to create or update a distribution item."""

    entityType: Annotated[
        Literal["DistributionRuleSetRequest"], Field(alias="$type", frozen=True)
    ] = "DistributionRuleSetRequest"


class DistributionRuleSetResponse(_BaseRuleSet):
    """Set of rules to retrieve a distribution item."""

    entityType: Annotated[
        Literal["DistributionRuleSetResponse"], Field(alias="$type", frozen=True)
    ] = "DistributionRuleSetResponse"
    stableTargetId: MergedAccessPlatformIdentifier


class DistributionMapping(_Stem, BaseMapping):
    """Mapping for describing a distribution transformation."""

    entityType: Annotated[
        Literal["DistributionMapping"], Field(alias="$type", frozen=True)
    ] = "DistributionMapping"
    accessRestriction: Annotated[
        list[MappingField[AccessRestriction]], Field(min_length=1)
    ]
    issued: Annotated[
        list[MappingField[YearMonthDayTime | YearMonthDay | YearMonth | Year]],
        Field(min_length=1),
    ]
    accessService: list[MappingField[MergedAccessPlatformIdentifier | None]] = []
    license: list[MappingField[License | None]] = []
    mediaType: list[MappingField[MIMEType | None]] = []
    modified: list[
        MappingField[YearMonthDayTime | YearMonthDay | YearMonth | Year | None]
    ] = []
    title: Annotated[list[MappingField[list[Text]]], Field(min_length=1)]
    accessURL: list[MappingField[list[Link]]] = []
    downloadURL: list[MappingField[list[Link]]] = []


class DistributionFilter(_Stem, BaseFilter):
    """Class for defining filter rules for distribution items."""

    entityType: Annotated[
        Literal["DistributionFilter"], Field(alias="$type", frozen=True)
    ] = "DistributionFilter"
    fields: Annotated[list[FilterField], Field(title="fields")] = []
