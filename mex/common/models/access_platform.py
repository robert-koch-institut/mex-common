"""A way of physically accessing the Resource for re-use."""

from typing import Annotated, ClassVar, Literal

from pydantic import AfterValidator, Field, computed_field

from mex.common.models.base.extracted_data import ExtractedData
from mex.common.models.base.merged_item import MergedItem
from mex.common.models.base.model import BaseModel
from mex.common.models.base.rules import (
    AdditiveRule,
    PreventiveRule,
    RuleSet,
    SubtractiveRule,
)
from mex.common.types import (
    APIType,
    ExtractedAccessPlatformIdentifier,
    Identifier,
    Link,
    MergedAccessPlatformIdentifier,
    MergedContactPointIdentifier,
    MergedOrganizationalUnitIdentifier,
    MergedPersonIdentifier,
    MergedPrimarySourceIdentifier,
    TechnicalAccessibility,
    Text,
)


class _Stem(BaseModel):
    stemType: ClassVar[Annotated[Literal["AccessPlatform"], Field(frozen=True)]] = (
        "AccessPlatform"
    )


class _OptionalLists(_Stem):
    alternativeTitle: list[Text] = []
    contact: list[
        Annotated[
            MergedOrganizationalUnitIdentifier
            | MergedPersonIdentifier
            | MergedContactPointIdentifier,
            AfterValidator(Identifier),
        ]
    ] = []
    description: list[Text] = []
    landingPage: list[Link] = []
    title: list[Text] = []
    unitInCharge: list[MergedOrganizationalUnitIdentifier] = []


class _OptionalValues(_Stem):
    endpointDescription: Link | None = None
    endpointType: APIType | None = None
    endpointURL: Link | None = None


class _RequiredValues(_Stem):
    technicalAccessibility: TechnicalAccessibility


class _SparseValues(_Stem):
    technicalAccessibility: TechnicalAccessibility | None = None


class _VariadicValues(_Stem):
    endpointDescription: list[Link] = []
    endpointType: list[APIType] = []
    endpointURL: list[Link] = []
    technicalAccessibility: list[TechnicalAccessibility] = []


class BaseAccessPlatform(_OptionalLists, _OptionalValues, _RequiredValues):
    """All fields for a valid access platform except for provenance."""


class ExtractedAccessPlatform(BaseAccessPlatform, ExtractedData):
    """An automatically extracted metadata item describing an access platform."""

    entityType: Annotated[
        Literal["ExtractedAccessPlatform"], Field(alias="$type", frozen=True)
    ] = "ExtractedAccessPlatform"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def identifier(self) -> ExtractedAccessPlatformIdentifier:
        """Return the computed identifier for this extracted data item."""
        return self._get_identifier(ExtractedAccessPlatformIdentifier)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def stableTargetId(self) -> MergedAccessPlatformIdentifier:  # noqa: N802
        """Return the computed stableTargetId for this extracted data item."""
        return self._get_stable_target_id(MergedAccessPlatformIdentifier)


class MergedAccessPlatform(BaseAccessPlatform, MergedItem):
    """The result of merging all extracted data and rules for an access platform."""

    entityType: Annotated[
        Literal["MergedAccessPlatform"], Field(alias="$type", frozen=True)
    ] = "MergedAccessPlatform"
    identifier: Annotated[MergedAccessPlatformIdentifier, Field(frozen=True)]


class AdditiveAccessPlatform(
    _OptionalLists, _OptionalValues, _SparseValues, AdditiveRule
):
    """Rule to add values to merged access platform items."""

    entityType: Annotated[
        Literal["AdditiveAccessPlatform"], Field(alias="$type", frozen=True)
    ] = "AdditiveAccessPlatform"


class SubtractiveAccessPlatform(_OptionalLists, _VariadicValues, SubtractiveRule):
    """Rule to subtract values from merged access platform items."""

    entityType: Annotated[
        Literal["SubtractiveAccessPlatform"], Field(alias="$type", frozen=True)
    ] = "SubtractiveAccessPlatform"


class PreventiveAccessPlatform(_Stem, PreventiveRule):
    """Rule to prevent primary sources for fields of merged access platform items."""

    entityType: Annotated[
        Literal["PreventiveAccessPlatform"], Field(alias="$type", frozen=True)
    ] = "PreventiveAccessPlatform"
    alternativeTitle: list[MergedPrimarySourceIdentifier] = []
    contact: list[MergedPrimarySourceIdentifier] = []
    description: list[MergedPrimarySourceIdentifier] = []
    endpointDescription: list[MergedPrimarySourceIdentifier] = []
    endpointType: list[MergedPrimarySourceIdentifier] = []
    endpointURL: list[MergedPrimarySourceIdentifier] = []
    landingPage: list[MergedPrimarySourceIdentifier] = []
    technicalAccessibility: list[MergedPrimarySourceIdentifier] = []
    title: list[MergedPrimarySourceIdentifier] = []
    unitInCharge: list[MergedPrimarySourceIdentifier] = []


class _BaseRuleSet(_Stem, RuleSet):
    additive: AdditiveAccessPlatform
    subtractive: SubtractiveAccessPlatform
    preventive: PreventiveAccessPlatform


class AccessPlatformRuleSetRequest(_BaseRuleSet):
    """Set of rules to create or update an access platform item."""

    entityType: Annotated[
        Literal["AccessPlatformRuleSetRequest"], Field(alias="$type", frozen=True)
    ] = "AccessPlatformRuleSetRequest"


class AccessPlatformRuleSetResponse(_BaseRuleSet):
    """Set of rules to retrieve an access platform item."""

    entityType: Annotated[
        Literal["AccessPlatformRuleSetResponse"], Field(alias="$type", frozen=True)
    ] = "AccessPlatformRuleSetResponse"
    stableTargetId: MergedAccessPlatformIdentifier
