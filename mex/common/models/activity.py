"""The context a resource was generated in.

This may be a project, an area of work or an administrative procedure.
"""

from typing import Annotated, ClassVar, Literal

from pydantic import AfterValidator, Field, computed_field

from mex.common.models.base.extracted_data import ExtractedData
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
    ActivityType,
    ExtractedActivityIdentifier,
    Identifier,
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
    activityType: list[ActivityType] = []
    alternativeTitle: list[Text] = []
    documentation: list[Link] = []
    end: list[YearMonthDay | YearMonth | Year] = []
    externalAssociate: list[
        Annotated[
            MergedOrganizationIdentifier | MergedPersonIdentifier,
            AfterValidator(Identifier),
        ]
    ] = []
    funderOrCommissioner: list[MergedOrganizationIdentifier] = []
    fundingProgram: list[str] = []
    involvedPerson: list[MergedPersonIdentifier] = []
    involvedUnit: list[MergedOrganizationalUnitIdentifier] = []
    isPartOfActivity: list[MergedActivityIdentifier] = []
    publication: list[MergedBibliographicResourceIdentifier] = []
    shortName: list[Text] = []
    start: list[YearMonthDay | YearMonth | Year] = []
    succeeds: list[MergedActivityIdentifier] = []
    theme: list[Theme] = []
    website: list[Link] = []


class _RequiredLists(_Stem):
    contact: Annotated[
        list[
            Annotated[
                MergedOrganizationalUnitIdentifier
                | MergedPersonIdentifier
                | MergedContactPointIdentifier,
                AfterValidator(Identifier),
            ]
        ],
        Field(min_length=1),
    ]
    responsibleUnit: Annotated[
        list[MergedOrganizationalUnitIdentifier], Field(min_length=1)
    ]
    title: Annotated[list[Text], Field(min_length=1)]


class _SparseLists(_Stem):
    contact: list[
        Annotated[
            MergedOrganizationalUnitIdentifier
            | MergedPersonIdentifier
            | MergedContactPointIdentifier,
            AfterValidator(Identifier),
        ]
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
        """Return the computed identifier for this extracted item."""
        return self._get_identifier(ExtractedActivityIdentifier)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def stableTargetId(self) -> MergedActivityIdentifier:  # noqa: N802
        """Return the computed stableTargetId for this extracted item."""
        return self._get_stable_target_id(MergedActivityIdentifier)


class MergedActivity(BaseActivity, MergedItem):
    """The result of merging all extracted items and rules for an activity."""

    entityType: Annotated[
        Literal["MergedActivity"], Field(alias="$type", frozen=True)
    ] = "MergedActivity"
    identifier: Annotated[MergedActivityIdentifier, Field(frozen=True)]


class PreviewActivity(_OptionalLists, _SparseLists, PreviewItem):
    """Preview for merging all extracted items and rules for an activity."""

    entityType: Annotated[
        Literal["PreviewActivity"], Field(alias="$type", frozen=True)
    ] = "PreviewActivity"
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


class _BaseRuleSet(_Stem, RuleSet):
    additive: AdditiveActivity = AdditiveActivity()
    subtractive: SubtractiveActivity = SubtractiveActivity()
    preventive: PreventiveActivity = PreventiveActivity()


class ActivityRuleSetRequest(_BaseRuleSet):
    """Set of rules to create or update an activity item."""

    entityType: Annotated[
        Literal["ActivityRuleSetRequest"], Field(alias="$type", frozen=True)
    ] = "ActivityRuleSetRequest"


class ActivityRuleSetResponse(_BaseRuleSet):
    """Set of rules to retrieve an activity item."""

    entityType: Annotated[
        Literal["ActivityRuleSetResponse"], Field(alias="$type", frozen=True)
    ] = "ActivityRuleSetResponse"
    stableTargetId: MergedActivityIdentifier
