"""A specific representation of a dataset."""

from typing import Annotated, ClassVar, Literal

from pydantic import Field, computed_field

from mex.common.models.base import BaseModel
from mex.common.models.extracted_data import ExtractedData
from mex.common.models.merged_item import MergedItem
from mex.common.models.rules import AdditiveRule, PreventiveRule, SubtractiveRule
from mex.common.types import (
    AccessRestriction,
    ExtractedDistributionIdentifier,
    License,
    Link,
    MergedAccessPlatformIdentifier,
    MergedDistributionIdentifier,
    MergedPrimarySourceIdentifier,
    MIMEType,
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


class _OptionalValues(_Stem):
    accessService: MergedAccessPlatformIdentifier | None = None
    license: (
        Annotated[License, Field(examples=["https://mex.rki.de/item/license-1"])] | None
    ) = None
    mediaType: (
        Annotated[
            MIMEType,
            Field(
                examples=["https://mex.rki.de/item/mime-type-1"],
            ),
        ]
        | None
    ) = None
    modified: YearMonthDayTime | YearMonthDay | YearMonth | Year | None = None


class _RequiredValues(_Stem):
    accessRestriction: Annotated[
        AccessRestriction,
        Field(examples=["https://mex.rki.de/item/access-restriction-1"]),
    ]
    issued: YearMonthDayTime | YearMonthDay | YearMonth | Year
    title: Annotated[
        str,
        Field(
            examples=["theNameOfTheFile"],
            min_length=1,
        ),
    ]


class _SparseValues(_Stem):
    accessRestriction: (
        Annotated[
            AccessRestriction,
            Field(examples=["https://mex.rki.de/item/access-restriction-1"]),
        ]
        | None
    ) = None
    issued: YearMonthDayTime | YearMonthDay | YearMonth | Year | None = None
    title: (
        Annotated[
            str,
            Field(
                examples=["theNameOfTheFile"],
                min_length=1,
            ),
        ]
        | None
    ) = None


class _VariadicValues(_Stem):
    accessRestriction: list[
        Annotated[
            AccessRestriction,
            Field(examples=["https://mex.rki.de/item/access-restriction-1"]),
        ]
    ] = []
    issued: list[YearMonthDayTime | YearMonthDay | YearMonth | Year] = []
    title: list[
        Annotated[
            str,
            Field(
                examples=["theNameOfTheFile"],
                min_length=1,
            ),
        ]
    ] = []


class BaseDistribution(_OptionalLists, _OptionalValues, _RequiredValues):
    """All fields for a valid distribution except for provenance."""


class ExtractedDistribution(BaseDistribution, ExtractedData):
    """An automatically extracted metadata set describing a distribution."""

    entityType: Annotated[
        Literal["ExtractedDistribution"], Field(alias="$type", frozen=True)
    ] = "ExtractedDistribution"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def identifier(self) -> ExtractedDistributionIdentifier:
        """Return the computed identifier for this extracted data item."""
        return self._get_identifier(ExtractedDistributionIdentifier)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def stableTargetId(self) -> MergedDistributionIdentifier:  # noqa: N802
        """Return the computed stableTargetId for this extracted data item."""
        return self._get_stable_target_id(MergedDistributionIdentifier)


class MergedDistribution(BaseDistribution, MergedItem):
    """The result of merging all extracted data and rules for a distribution."""

    entityType: Annotated[
        Literal["MergedDistribution"], Field(alias="$type", frozen=True)
    ] = "MergedDistribution"
    identifier: Annotated[MergedDistributionIdentifier, Field(frozen=True)]


class AdditiveDistribution(
    _OptionalLists, _OptionalValues, _SparseValues, AdditiveRule
):
    """Rule to add values to merged distribution items."""

    entityType: Annotated[
        Literal["AdditiveDistribution"], Field(alias="$type", frozen=True)
    ] = "AdditiveDistribution"


class SubtractiveDistribution(_OptionalLists, _VariadicValues, SubtractiveRule):
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
