from typing import Annotated, Literal

from pydantic import Field

from mex.common.models.base import BaseModel
from mex.common.models.extracted_data import ExtractedData
from mex.common.models.merged_item import MergedItem
from mex.common.types import (
    ExtractedOrganizationIdentifier,
    MergedOrganizationIdentifier,
    Text,
)


class BaseOrganization(BaseModel):
    """Represents a collection of people organized together.

    This can be any community or other social, commercial or political structure.
    """

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
    officialName: Annotated[list[Text], Field(min_length=1)]
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


class ExtractedOrganization(BaseOrganization, ExtractedData):
    """An automatically extracted metadata set describing an organization."""

    entityType: Annotated[
        Literal["ExtractedOrganization"], Field(alias="$type", frozen=True)
    ] = "ExtractedOrganization"
    identifier: Annotated[ExtractedOrganizationIdentifier, Field(frozen=True)]
    stableTargetId: MergedOrganizationIdentifier


class MergedOrganization(BaseOrganization, MergedItem):
    """The result of merging all extracted data and rules for an organization."""

    entityType: Annotated[
        Literal["MergedOrganization"], Field(alias="$type", frozen=True)
    ] = "MergedOrganization"
    identifier: Annotated[MergedOrganizationIdentifier, Field(frozen=True)]
