"""A person related to a source and/or resource, i.e. a project leader."""

from typing import Annotated, Literal

from pydantic import Field

from mex.common.models.base import BaseModel
from mex.common.models.extracted_data import ExtractedData
from mex.common.models.merged_item import MergedItem
from mex.common.models.rule_set import AdditiveRule, PreventiveRule, SubtractiveRule
from mex.common.types import (
    Email,
    ExtractedPersonIdentifier,
    MergedOrganizationalUnitIdentifier,
    MergedOrganizationIdentifier,
    MergedPersonIdentifier,
    MergedPrimarySourceIdentifier,
)


class _OptionalLists(BaseModel):
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
    identifier: Annotated[ExtractedPersonIdentifier, Field(frozen=True)]
    stableTargetId: MergedPersonIdentifier


class MergedPerson(BasePerson, MergedItem):
    """The result of merging all extracted data and rules for a person."""

    entityType: Annotated[
        Literal["MergedPerson"], Field(alias="$type", frozen=True)
    ] = "MergedPerson"
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


class PreventivePerson(PreventiveRule):
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
