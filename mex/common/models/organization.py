"""Represents a collection of people organized together.

This can be any community or other social, commercial or political structure.
"""

from typing import Annotated, ClassVar, Literal

from pydantic import Field, computed_field

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
    ExtractedOrganizationIdentifier,
    MergedOrganizationIdentifier,
    MergedPrimarySourceIdentifier,
    Text,
)


class _Stem(BaseModel):
    stemType: ClassVar[Annotated[Literal["Organization"], Field(frozen=True)]] = (
        "Organization"
    )


class _OptionalLists(_Stem):
    alternativeName: list[Text] = []
    geprisId: list[
        Annotated[
            str,
            Field(
                pattern=r"^https://gepris\.dfg\.de/gepris/institution/[0-9]{1,64}$",
                examples=["https://gepris.dfg.de/gepris/institution/10179"],
                json_schema_extra={"format": "uri"},
            ),
        ]
    ] = []
    gndId: list[
        Annotated[
            str,
            Field(
                pattern=r"^https://d\-nb\.info/gnd/[-X0-9]{3,10}$",
                examples=["https://d-nb.info/gnd/17690-4"],
                json_schema_extra={"format": "uri"},
            ),
        ]
    ] = []
    isniId: list[
        Annotated[
            str,
            Field(
                pattern=r"^https://isni\.org/isni/[X0-9]{16}$",
                examples=["https://isni.org/isni/0000000109403744"],
                json_schema_extra={"format": "uri"},
            ),
        ]
    ] = []
    rorId: list[
        Annotated[
            str,
            Field(
                pattern=r"^https://ror\.org/[a-z0-9]{9}$",
                examples=["https://ror.org/01k5qnb77"],
                json_schema_extra={"format": "uri"},
            ),
        ]
    ] = []
    shortName: list[Text] = []
    viafId: list[
        Annotated[
            str,
            Field(
                pattern=r"^https://viaf\.org/viaf/[0-9]{2,22}$",
                examples=["https://viaf.org/viaf/123556639"],
                json_schema_extra={"format": "uri"},
            ),
        ]
    ] = []
    wikidataId: list[
        Annotated[
            str,
            Field(
                examples=["http://www.wikidata.org/entity/Q679041"],
                pattern=r"^https://www\.wikidata\.org/entity/[PQ0-9]{2,64}$",
                json_schema_extra={"format": "uri"},
            ),
        ]
    ] = []


class _RequiredLists(_Stem):
    officialName: Annotated[list[Text], Field(min_length=1)]


class _SparseLists(_Stem):
    officialName: list[Text] = []


class BaseOrganization(_OptionalLists, _RequiredLists):
    """All fields for a valid organization except for provenance."""


class ExtractedOrganization(BaseOrganization, ExtractedData):
    """An automatically extracted metadata set describing an organization."""

    entityType: Annotated[
        Literal["ExtractedOrganization"], Field(alias="$type", frozen=True)
    ] = "ExtractedOrganization"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def identifier(self) -> ExtractedOrganizationIdentifier:
        """Return the computed identifier for this extracted item."""
        return self._get_identifier(ExtractedOrganizationIdentifier)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def stableTargetId(self) -> MergedOrganizationIdentifier:  # noqa: N802
        """Return the computed stableTargetId for this extracted item."""
        return self._get_stable_target_id(MergedOrganizationIdentifier)


class MergedOrganization(BaseOrganization, MergedItem):
    """The result of merging all extracted items and rules for an organization."""

    entityType: Annotated[
        Literal["MergedOrganization"], Field(alias="$type", frozen=True)
    ] = "MergedOrganization"
    identifier: Annotated[MergedOrganizationIdentifier, Field(frozen=True)]


class PreviewOrganization(_OptionalLists, _SparseLists, PreviewItem):
    """Preview for merging all extracted items and rules for an organization."""

    entityType: Annotated[
        Literal["PreviewOrganization"], Field(alias="$type", frozen=True)
    ] = "PreviewOrganization"
    identifier: Annotated[MergedOrganizationIdentifier, Field(frozen=True)]


class AdditiveOrganization(_OptionalLists, _SparseLists, AdditiveRule):
    """Rule to add values to merged organization items."""

    entityType: Annotated[
        Literal["AdditiveOrganization"], Field(alias="$type", frozen=True)
    ] = "AdditiveOrganization"


class SubtractiveOrganization(_OptionalLists, _SparseLists, SubtractiveRule):
    """Rule to subtract values from merged organization items."""

    entityType: Annotated[
        Literal["SubtractiveOrganization"], Field(alias="$type", frozen=True)
    ] = "SubtractiveOrganization"


class PreventiveOrganization(_Stem, PreventiveRule):
    """Rule to prevent primary sources for fields of merged organization items."""

    entityType: Annotated[
        Literal["PreventiveOrganization"], Field(alias="$type", frozen=True)
    ] = "PreventiveOrganization"
    alternativeName: list[MergedPrimarySourceIdentifier] = []
    geprisId: list[MergedPrimarySourceIdentifier] = []
    gndId: list[MergedPrimarySourceIdentifier] = []
    isniId: list[MergedPrimarySourceIdentifier] = []
    officialName: list[MergedPrimarySourceIdentifier] = []
    rorId: list[MergedPrimarySourceIdentifier] = []
    shortName: list[MergedPrimarySourceIdentifier] = []
    viafId: list[MergedPrimarySourceIdentifier] = []
    wikidataId: list[MergedPrimarySourceIdentifier] = []


class _BaseRuleSet(_Stem, RuleSet):
    additive: AdditiveOrganization = AdditiveOrganization()
    subtractive: SubtractiveOrganization = SubtractiveOrganization()
    preventive: PreventiveOrganization = PreventiveOrganization()


class OrganizationRuleSetRequest(_BaseRuleSet):
    """Set of rules to create or update an organization item."""

    entityType: Annotated[
        Literal["OrganizationRuleSetRequest"], Field(alias="$type", frozen=True)
    ] = "OrganizationRuleSetRequest"


class OrganizationRuleSetResponse(_BaseRuleSet):
    """Set of rules to retrieve an organization item."""

    entityType: Annotated[
        Literal["OrganizationRuleSetResponse"], Field(alias="$type", frozen=True)
    ] = "OrganizationRuleSetResponse"
    stableTargetId: MergedOrganizationIdentifier
