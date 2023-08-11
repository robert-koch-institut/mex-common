from pydantic import Field

from mex.common.models.base import BaseModel
from mex.common.models.extracted_data import ExtractedData
from mex.common.models.merged_item import MergedItem
from mex.common.types import OrganizationID, Text


class BaseOrganization(BaseModel):
    """Represents a collection of people organized together.

    This can be any community or other social, commercial or political structure.
    """

    stableTargetId: OrganizationID
    alternativeName: list[Text] = []
    geprisId: list[str] = Field(
        [],
        examples=["https://gepris.dfg.de/gepris/institution/10179"],
        pattern=r"^https://gepris\.dfg\.de/gepris/institution/[0-9]{1,64}$",
    )
    gndId: list[str] = Field(
        [],
        examples=["https://d-nb.info/gnd/17690-4"],
        pattern=r"^https://d\-nb\.info/gnd/[-X0-9]{3,10}$",
    )
    isniId: list[str] = Field(
        [],
        examples=["https://isni.org/isni/0000000109403744"],
        pattern=r"^https://isni\.org/isni/[X0-9]{16}$",
    )
    officialName: list[Text] = Field(..., min_length=1)
    rorId: list[str] = Field(
        [],
        examples=["https://ror.org/01k5qnb77"],
        pattern=r"^https://ror\.org/[a-z0-9]{9}$",
    )
    shortName: list[Text] = []
    viafId: list[str] = Field(
        [],
        examples=["https://viaf.org/viaf/123556639"],
        pattern=r"^https://viaf\.org/viaf/[0-9]{2,22}$",
    )
    wikidataId: str | None = Field(
        None,
        examples=["http://www.wikidata.org/entity/Q679041"],
        pattern=r"^https://www\.wikidata\.org/entity/[PQ0-9]{2,64}$",
    )


class ExtractedOrganization(BaseOrganization, ExtractedData):
    """An automatically extracted metadata set describing an organization."""


class MergedOrganization(BaseOrganization, MergedItem):
    """The result of merging all extracted data and rules for an organization."""
