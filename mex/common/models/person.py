"""A person related to a source and/or resource, i.e. a project leader."""

from typing import Annotated, ClassVar, Literal

from pydantic import Field, computed_field

from mex.common.models.base.extracted_data import ExtractedData
from mex.common.models.base.merged_item import MergedItem, PreviewItem
from mex.common.models.base.model import BaseModel
from mex.common.models.base.rules import (
    AdditiveRule,
    PreventiveRule,
    RuleSet,
    SubtractiveRule,
)
from mex.common.types import (
    Email,
    ExtractedPersonIdentifier,
    MergedOrganizationalUnitIdentifier,
    MergedOrganizationIdentifier,
    MergedPersonIdentifier,
    MergedPrimarySourceIdentifier,
)


class _Stem(BaseModel):
    stemType: ClassVar[Annotated[Literal["Person"], Field(frozen=True)]] = "Person"


class _OptionalLists(_Stem):
    affiliation: list[MergedOrganizationIdentifier] = []
    email: list[Email] = []
    familyName: list[
        Annotated[
            str,
            Field(
                examples=["Patapoutian", "Skłodowska-Curie", "Muta Maathai"],
            ),
        ]
    ] = []
    fullName: list[
        Annotated[
            str,
            Field(
                examples=["Juturna Felicitás", "M. Berhanu", "Keone Seong-Hyeon"],
            ),
        ]
    ] = []
    givenName: list[
        Annotated[
            str,
            Field(
                examples=["Romāns", "Marie Salomea", "May-Britt"],
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
    memberOf: list[MergedOrganizationalUnitIdentifier] = []
    orcidId: list[
        Annotated[
            str,
            Field(
                pattern=r"^https://orcid\.org/[-X0-9]{9,21}$",
                examples=["https://orcid.org/0000-0002-9079-593X"],
                json_schema_extra={"format": "uri"},
            ),
        ],
    ] = []


class BasePerson(_OptionalLists):
    """All fields for a valid person except for provenance."""


class ExtractedPerson(BasePerson, ExtractedData):
    """An automatically extracted metadata set describing a person."""

    entityType: Annotated[
        Literal["ExtractedPerson"], Field(alias="$type", frozen=True)
    ] = "ExtractedPerson"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def identifier(self) -> ExtractedPersonIdentifier:
        """Return the computed identifier for this extracted data item."""
        return self._get_identifier(ExtractedPersonIdentifier)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def stableTargetId(self) -> MergedPersonIdentifier:  # noqa: N802
        """Return the computed stableTargetId for this extracted data item."""
        return self._get_stable_target_id(MergedPersonIdentifier)


class MergedPerson(BasePerson, MergedItem):
    """The result of merging all extracted data and rules for a person."""

    entityType: Annotated[
        Literal["MergedPerson"], Field(alias="$type", frozen=True)
    ] = "MergedPerson"
    identifier: Annotated[MergedPersonIdentifier, Field(frozen=True)]


class PreviewPerson(_OptionalLists, PreviewItem):
    """Preview for merging all extracted data and rules for a person."""

    entityType: Annotated[
        Literal["PreviewPerson"], Field(alias="$type", frozen=True)
    ] = "PreviewPerson"
    identifier: Annotated[MergedPersonIdentifier, Field(frozen=True)]


class AdditivePerson(_OptionalLists, AdditiveRule):
    """Rule to add values to merged person items."""

    entityType: Annotated[
        Literal["AdditivePerson"], Field(alias="$type", frozen=True)
    ] = "AdditivePerson"


class SubtractivePerson(_OptionalLists, SubtractiveRule):
    """Rule to subtract values from merged person items."""

    entityType: Annotated[
        Literal["SubtractivePerson"], Field(alias="$type", frozen=True)
    ] = "SubtractivePerson"


class PreventivePerson(_Stem, PreventiveRule):
    """Rule to prevent primary sources for fields of merged person items."""

    entityType: Annotated[
        Literal["PreventivePerson"], Field(alias="$type", frozen=True)
    ] = "PreventivePerson"
    affiliation: list[MergedPrimarySourceIdentifier] = []
    email: list[MergedPrimarySourceIdentifier] = []
    familyName: list[MergedPrimarySourceIdentifier] = []
    fullName: list[MergedPrimarySourceIdentifier] = []
    givenName: list[MergedPrimarySourceIdentifier] = []
    isniId: list[MergedPrimarySourceIdentifier] = []
    memberOf: list[MergedPrimarySourceIdentifier] = []
    orcidId: list[MergedPrimarySourceIdentifier] = []


class _BaseRuleSet(_Stem, RuleSet):
    additive: AdditivePerson = AdditivePerson()
    subtractive: SubtractivePerson = SubtractivePerson()
    preventive: PreventivePerson = PreventivePerson()


class PersonRuleSetRequest(_BaseRuleSet):
    """Set of rules to create or update a person item."""

    entityType: Annotated[
        Literal["PersonRuleSetRequest"], Field(alias="$type", frozen=True)
    ] = "PersonRuleSetRequest"


class PersonRuleSetResponse(_BaseRuleSet):
    """Set of rules to retrieve a person item."""

    entityType: Annotated[
        Literal["PersonRuleSetResponse"], Field(alias="$type", frozen=True)
    ] = "PersonRuleSetResponse"
    stableTargetId: MergedPersonIdentifier
