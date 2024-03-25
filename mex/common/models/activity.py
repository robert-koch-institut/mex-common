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
    ActivityType,
    ExtractedActivityIdentifier,
    Link,
    MergedActivityIdentifier,
    MergedContactPointIdentifier,
    MergedOrganizationalUnitIdentifier,
    MergedOrganizationIdentifier,
    MergedPersonIdentifier,
    Text,
    Theme,
    Timestamp,
)


class SparseActivity(BaseModel):
    """Activity model where all fields are optional."""

    abstract: list[Text] = []
    activityType: list[
        Annotated[
            ActivityType, Field(examples=["https://mex.rki.de/item/activity-type-1"])
        ]
    ] = []
    alternativeTitle: list[Text] = []
    contact: list[
        MergedOrganizationalUnitIdentifier
        | MergedPersonIdentifier
        | MergedContactPointIdentifier,
    ] = []
    documentation: list[Link] = []
    end: list[
        Annotated[Timestamp, Field(examples=["2024-01-17", "2024", "2024-01"])]
    ] = []
    externalAssociate: list[MergedOrganizationIdentifier | MergedPersonIdentifier] = []
    funderOrCommissioner: list[MergedOrganizationIdentifier] = []
    fundingProgram: list[str] = []
    involvedPerson: list[MergedPersonIdentifier] = []
    involvedUnit: list[MergedOrganizationalUnitIdentifier] = []
    isPartOfActivity: list[MergedActivityIdentifier] = []
    publication: list[Link] = []
    responsibleUnit: list[MergedOrganizationalUnitIdentifier] = []
    shortName: list[Text] = []
    start: list[
        Annotated[Timestamp, Field(examples=["2023-01-16", "2023", "2023-02"])]
    ] = []
    succeeds: list[MergedActivityIdentifier] = []
    theme: list[
        Annotated[Theme, Field(examples=["https://mex.rki.de/item/theme-1"])]
    ] = []
    title: list[Text] = []
    website: list[Link] = []


class BaseActivity(SparseActivity):
    """The context a resource was generated in.

    This may be a project, an area of work or an administrative procedure.
    """

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


class ExtractedActivity(BaseActivity, ExtractedData):
    """An automatically extracted metadata set describing an activity."""

    entityType: Annotated[
        Literal["ExtractedActivity"], Field(alias="$type", frozen=True)
    ] = "ExtractedActivity"
    identifier: Annotated[ExtractedActivityIdentifier, Field(frozen=True)]
    stableTargetId: MergedActivityIdentifier


class MergedActivity(BaseActivity, MergedItem):
    """The result of merging all extracted data and rules for an activity."""

    entityType: Annotated[
        Literal["MergedActivity"], Field(alias="$type", frozen=True)
    ] = "MergedActivity"
    identifier: Annotated[MergedActivityIdentifier, Field(frozen=True)]


class AdditiveActivity(SparseActivity, AdditiveRule):
    """Rule to add values to merged activity items."""

    entityType: Annotated[
        Literal["AdditiveActivity"], Field(alias="$type", frozen=True)
    ] = "AdditiveActivity"


class SubtractiveActivity(SparseActivity, SubtractiveRule):
    """Rule to subtract values from merged activity items."""

    entityType: Annotated[
        Literal["SubtractiveActivity"], Field(alias="$type", frozen=True)
    ] = "SubtractiveActivity"


BlockingActivity = create_blocking_rule(
    Literal["BlockingActivity"],
    SparseActivity,
    "Rule to block primary sources for fields of merged activity items.",
)
