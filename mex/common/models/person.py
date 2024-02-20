from typing import Annotated, Literal

from pydantic import Field

from mex.common.models.base import BaseModel
from mex.common.models.extracted_data import ExtractedData
from mex.common.models.merged_item import MergedItem
from mex.common.types import (
    Email,
    ExtractedPersonIdentifier,
    MergedOrganizationalUnitIdentifier,
    MergedOrganizationIdentifier,
    MergedPersonIdentifier,
)


class BasePerson(BaseModel):
    """A person related to a source and/or resource, i.e. a project leader."""

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


class ExtractedPerson(BasePerson, ExtractedData):
    """An automatically extracted metadata set describing a person."""

    entityType: Literal["ExtractedPerson"] = Field(
        "ExtractedPerson", alias="$type", frozen=True
    )
    identifier: Annotated[ExtractedPersonIdentifier, Field(frozen=True)]
    stableTargetId: MergedPersonIdentifier


class MergedPerson(BasePerson, MergedItem):
    """The result of merging all extracted data and rules for a person."""

    entityType: Literal["MergedPerson"] = Field(
        "MergedPerson", alias="$type", frozen=True
    )
    identifier: Annotated[MergedPersonIdentifier, Field(frozen=True)]
