"""The context a resource was generated in.

This may be a project, an area of work or an administrative procedure.
"""

from typing import Annotated, ClassVar, Literal

from pydantic import Field, computed_field

from mex.common.models.base import BaseModel
from mex.common.models.extracted_data import ExtractedData
from mex.common.models.merged_item import MergedItem
from mex.common.models.rules import (
    AdditiveRule,
    PreventiveRule,
    SubtractiveRule,
)
from mex.common.types import (
    ActivityType,
    ExtractedActivityIdentifier,
    Link,
    MergedActivityIdentifier,
    MergedBibliographicResourceIdentifier,
    MergedContactPointIdentifier,
    MergedOrganizationalUnitIdentifier,
    MergedOrganizationIdentifier,
    MergedPersonIdentifier,
    MergedPrimarySourceIdentifier,
    Text,
    Theme,
    Year,
    YearMonth,
    YearMonthDay,
)


class _Stem(BaseModel):
    stemType: ClassVar[Annotated[Literal["Activity"], Field(frozen=True)]] = "Activity"


class _OptionalLists(_Stem):
    abstract: list[Text] = []
    activityType: list[
        Annotated[
            ActivityType, Field(examples=["https://mex.rki.de/item/activity-type-1"])
        ]
    ] = []
    alternativeTitle: list[Text] = []
    documentation: list[Link] = []
    end: list[YearMonthDay | YearMonth | Year] = []
    externalAssociate: list[MergedOrganizationIdentifier | MergedPersonIdentifier] = []
    funderOrCommissioner: list[MergedOrganizationIdentifier] = []
    fundingProgram: list[str] = []
    involvedPerson: list[MergedPersonIdentifier] = []
    involvedUnit: list[MergedOrganizationalUnitIdentifier] = []
    isPartOfActivity: list[MergedActivityIdentifier] = []
    publication: list[MergedBibliographicResourceIdentifier] = []
    shortName: list[Text] = []
    start: list[YearMonthDay | YearMonth | Year] = []
    succeeds: list[MergedActivityIdentifier] = []
    theme: list[
        Annotated[Theme, Field(examples=["https://mex.rki.de/item/theme-1"])]
    ] = []
    website: list[Link] = []


class _RequiredLists(_Stem):
    contact: Annotated[
        list[
            MergedOrganizationalUnitIdentifier
            | MergedPersonIdentifier
            | MergedContactPointIdentifier,
        ],
        Field(min_length=1),
    ]
    responsibleUnit: Annotated[
        list[MergedOrganizationalUnitIdentifier], Field(min_length=1)
    ]
    title: Annotated[list[Text], Field(min_length=1)]


class _SparseLists(_Stem):
    contact: list[
        MergedOrganizationalUnitIdentifier
        | MergedPersonIdentifier
        | MergedContactPointIdentifier,
    ] = []
    responsibleUnit: list[MergedOrganizationalUnitIdentifier] = []
    title: list[Text] = []


class BaseActivity(_OptionalLists, _RequiredLists):
    """All fields for a valid activity except for provenance."""


class ExtractedActivity(BaseActivity, ExtractedData):
    """An automatically extracted metadata set describing an activity."""

    entityType: Annotated[
        Literal["ExtractedActivity"], Field(alias="$type", frozen=True)
    ] = "ExtractedActivity"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def identifier(self) -> ExtractedActivityIdentifier:
        """Return the computed identifier for this extracted data item."""
        return self._get_identifier(ExtractedActivityIdentifier)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def stableTargetId(self) -> MergedActivityIdentifier:  # noqa: N802
        """Return the computed stableTargetId for this extracted data item."""
        return self._get_stable_target_id(MergedActivityIdentifier)


class MergedActivity(BaseActivity, MergedItem):
    """The result of merging all extracted data and rules for an activity."""

    entityType: Annotated[
        Literal["MergedActivity"], Field(alias="$type", frozen=True)
    ] = "MergedActivity"
    identifier: Annotated[MergedActivityIdentifier, Field(frozen=True)]


class AdditiveActivity(_OptionalLists, _SparseLists, AdditiveRule):
    """Rule to add values to merged activity items."""

    entityType: Annotated[
        Literal["AdditiveActivity"], Field(alias="$type", frozen=True)
    ] = "AdditiveActivity"


class SubtractiveActivity(_OptionalLists, _SparseLists, SubtractiveRule):
    """Rule to subtract values from merged activity items."""

    entityType: Annotated[
        Literal["SubtractiveActivity"], Field(alias="$type", frozen=True)
    ] = "SubtractiveActivity"


class PreventiveActivity(_Stem, PreventiveRule):
    """Rule to prevent primary sources for fields of merged activity items."""

    entityType: Annotated[
        Literal["PreventiveActivity"], Field(alias="$type", frozen=True)
    ] = "PreventiveActivity"
    abstract: list[MergedPrimarySourceIdentifier] = []
    activityType: list[MergedPrimarySourceIdentifier] = []
    alternativeTitle: list[MergedPrimarySourceIdentifier] = []
    contact: list[MergedPrimarySourceIdentifier] = []
    documentation: list[MergedPrimarySourceIdentifier] = []
    end: list[MergedPrimarySourceIdentifier] = []
    externalAssociate: list[MergedPrimarySourceIdentifier] = []
    funderOrCommissioner: list[MergedPrimarySourceIdentifier] = []
    fundingProgram: list[MergedPrimarySourceIdentifier] = []
    involvedPerson: list[MergedPrimarySourceIdentifier] = []
    involvedUnit: list[MergedPrimarySourceIdentifier] = []
    isPartOfActivity: list[MergedPrimarySourceIdentifier] = []
    publication: list[MergedPrimarySourceIdentifier] = []
    responsibleUnit: list[MergedPrimarySourceIdentifier] = []
    shortName: list[MergedPrimarySourceIdentifier] = []
    start: list[MergedPrimarySourceIdentifier] = []
    succeeds: list[MergedPrimarySourceIdentifier] = []
    theme: list[MergedPrimarySourceIdentifier] = []
    title: list[MergedPrimarySourceIdentifier] = []
    website: list[MergedPrimarySourceIdentifier] = []
