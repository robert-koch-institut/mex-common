from typing import Annotated

from pydantic import Field

from mex.common.models.base import BaseModel
from mex.common.models.extracted_data import ExtractedData
from mex.common.models.merged_item import MergedItem
from mex.common.types import Email, OrganizationalUnitID, OrganizationID, PersonID


class BasePerson(BaseModel):
    """A person related to a source and/or resource, i.e. a project leader."""

    stableTargetId: PersonID
    affiliation: list[OrganizationID] = []
    email: list[
        Annotated[
            Email,
            Field(
                examples=["info@rki.de"],
            ),
        ]
    ] = []
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
                examples=["Anna Schmidt", "P. Meier", "Wolf Maria Hermann"],
            ),
        ]
    ]
    givenName: list[
        Annotated[
            str,
            Field(
                examples=["Wangari", "Marie Salomea", "May-Britt"],
            ),
        ]
    ] = []
    isniId: list[
        Annotated[
            str,
            Field(
                pattern=r"^https://isni\.org/isni/[X0-9]{16}$",
                examples=["https://isni.org/isni/0000000109403744"],
            ),
        ]
    ] = []
    memberOf: list[OrganizationalUnitID] = []
    orcidId: list[
        Annotated[
            str,
            Field(
                pattern=r"^https://orcid\.org/[-X0-9]{9,21}$",
                examples=["https://orcid.org/0000-0002-9079-593X"],
            ),
        ],
    ] = []


class ExtractedPerson(BasePerson, ExtractedData):
    """An automatically extracted metadata set describing a person."""


class MergedPerson(BasePerson, MergedItem):
    """The result of merging all extracted data and rules for a person."""
