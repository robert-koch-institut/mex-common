"""A specific representation of a dataset."""

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
    accessURL: list[Link] = []
    downloadURL: list[Link] = []


class _RequiredLists(_Stem):
    title: Annotated[list[Text], Field(min_length=1)]


class _SparseLists(_Stem):
    title: list[Text] = []


class _OptionalValues(_Stem):
    accessService: MergedAccessPlatformIdentifier | None = None
    license: License | None = None
    mediaType: MIMEType | None = None
    modified: YearMonthDayTime | YearMonthDay | YearMonth | Year | None = None


class _RequiredValues(_Stem):
    accessRestriction: AccessRestriction
    issued: YearMonthDayTime | YearMonthDay | YearMonth | Year


class _SparseValues(_Stem):
    accessRestriction: AccessRestriction | None = None
    issued: YearMonthDayTime | YearMonthDay | YearMonth | Year | None = None


class _VariadicValues(_Stem):
    accessRestriction: list[AccessRestriction] = []
    accessService: list[MergedAccessPlatformIdentifier] = []
    issued: list[YearMonthDayTime | YearMonthDay | YearMonth | Year] = []
    license: list[License] = []
    mediaType: list[MIMEType] = []
    modified: list[YearMonthDayTime | YearMonthDay | YearMonth | Year] = []


class BaseDistribution(
    _OptionalLists, _RequiredLists, _OptionalValues, _RequiredValues
):
    """All fields for a valid distribution except for provenance."""


class ExtractedDistribution(BaseDistribution, ExtractedData):
    """An automatically extracted metadata set describing a distribution."""

    entityType: Annotated[
        Literal["ExtractedDistribution"], Field(alias="$type", frozen=True)
    ] = "ExtractedDistribution"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def identifier(self) -> ExtractedDistributionIdentifier:
        """Return the computed identifier for this extracted item."""
        return self._get_identifier(ExtractedDistributionIdentifier)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def stableTargetId(self) -> MergedDistributionIdentifier:  # noqa: N802
        """Return the computed stableTargetId for this extracted item."""
        return self._get_stable_target_id(MergedDistributionIdentifier)


class MergedDistribution(BaseDistribution, MergedItem):
    """The result of merging all extracted items and rules for a distribution."""

    entityType: Annotated[
        Literal["MergedDistribution"], Field(alias="$type", frozen=True)
    ] = "MergedDistribution"
    identifier: Annotated[MergedDistributionIdentifier, Field(frozen=True)]


class PreviewDistribution(
    _OptionalLists, _SparseLists, _OptionalValues, _SparseValues, PreviewItem
):
    """Preview for merging all extracted items and rules for a distribution."""

    entityType: Annotated[
        Literal["PreviewDistribution"], Field(alias="$type", frozen=True)
    ] = "PreviewDistribution"
    identifier: Annotated[MergedDistributionIdentifier, Field(frozen=True)]


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
        Literal["DistributionRuleSetRequest"], Field(alias="$type", frozen=True)
    ] = "DistributionRuleSetRequest"
    stableTargetId: MergedAccessPlatformIdentifier


class DistributionMapping(_Stem, BaseMapping):
    """Mapping for describing a distribution transformation."""

    entityType: Annotated[
        Literal["DistributionMapping"], Field(alias="$type", frozen=True)
    ] = "DistributionMapping"
    hadPrimarySource: Annotated[
        list[MappingField[MergedPrimarySourceIdentifier]], Field(min_length=1)
    ]
    identifierInPrimarySource: Annotated[list[MappingField[str]], Field(min_length=1)]
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
