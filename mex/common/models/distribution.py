"""A specific representation of a dataset."""

from typing import Annotated, Literal

from pydantic import Field

from mex.common.models.base import BaseModel
from mex.common.models.extracted_data import ExtractedData
from mex.common.models.merged_item import MergedItem
from mex.common.models.rule_set import (
    AdditiveRule,
    SubtractiveRule,
    create_blocking_rule,
)
from mex.common.types import (
    AccessRestriction,
    ExtractedDistributionIdentifier,
    License,
    Link,
    MergedAccessPlatformIdentifier,
    MergedDistributionIdentifier,
    MergedOrganizationIdentifier,
    MergedPersonIdentifier,
    MIMEType,
    YearMonth,
    YearMonthDay,
    YearMonthDayTime,
)


class SparseDistribution(BaseModel):
    """Distribution model where all fields are optional."""

    accessService: MergedAccessPlatformIdentifier | None = None
    accessRestriction: Annotated[
        AccessRestriction,
        Field(examples=["https://mex.rki.de/item/access-restriction-1"]),
    ]
    accessURL: Link | None = None
    author: list[MergedPersonIdentifier] = []
    contactPerson: list[MergedPersonIdentifier] = []
    dataCurator: list[MergedPersonIdentifier] = []
    dataManager: list[MergedPersonIdentifier] = []
    downloadURL: Link | None = None
    issued: YearMonthDayTime | YearMonthDay | YearMonth | None = None
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
    modified: YearMonthDayTime | YearMonthDay | YearMonth | None = None
    otherContributor: list[MergedPersonIdentifier] = []
    projectLeader: list[MergedPersonIdentifier] = []
    projectManager: list[MergedPersonIdentifier] = []
    publisher: list[MergedOrganizationIdentifier]
    researcher: list[MergedPersonIdentifier] = []
    title: Annotated[
        str,
        Field(examples=["theNameOfTheFile"]),
    ]


class BaseDistribution(SparseDistribution):
    """Distribution model where some fields may be required."""

    issued: YearMonthDayTime | YearMonthDay | YearMonth
    publisher: Annotated[list[MergedOrganizationIdentifier], Field(min_length=1)]
    title: Annotated[
        str,
        Field(
            examples=["theNameOfTheFile"],
            min_length=1,
        ),
    ]


class ExtractedDistribution(BaseDistribution, ExtractedData):
    """An automatically extracted metadata set describing a distribution."""

    entityType: Annotated[
        Literal["ExtractedDistribution"], Field(alias="$type", frozen=True)
    ] = "ExtractedDistribution"
    identifier: Annotated[ExtractedDistributionIdentifier, Field(frozen=True)]
    stableTargetId: MergedDistributionIdentifier


class MergedDistribution(BaseDistribution, MergedItem):
    """The result of merging all extracted data and rules for a distribution."""

    entityType: Annotated[
        Literal["MergedDistribution"], Field(alias="$type", frozen=True)
    ] = "MergedDistribution"
    identifier: Annotated[MergedDistributionIdentifier, Field(frozen=True)]


class AdditiveDistribution(SparseDistribution, AdditiveRule):
    """Rule to add values to merged distribution items."""

    entityType: Annotated[
        Literal["AdditiveDistribution"], Field(alias="$type", frozen=True)
    ] = "AdditiveDistribution"


class SubtractiveDistribution(SparseDistribution, SubtractiveRule):
    """Rule to subtract values from merged distribution items."""

    entityType: Annotated[
        Literal["SubtractiveDistribution"], Field(alias="$type", frozen=True)
    ] = "SubtractiveDistribution"


PreventiveDistribution = create_blocking_rule(
    Literal["PreventiveDistribution"],
    SparseDistribution,
    "Rule to block primary sources for fields of merged distribution items.",
)
