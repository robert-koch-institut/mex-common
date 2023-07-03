from pydantic import Field

from mex.common.models.extracted_data import ExtractedData
from mex.common.types import OrganizationID, Text


class ExtractedOrganization(ExtractedData):
    """Model class definition for extracted organizations."""

    stableTargetId: OrganizationID
    alternativeName: list[Text] = []
    geprisId: list[str] = Field(
        [],
        examples=["https://gepris.dfg.de/gepris/institution/10179"],
        regex=r"^https://gepris\.dfg\.de/gepris/institution/[0-9]{1,64}$",
    )
    gndId: list[str] = Field(
        [],
        examples=["https://d-nb.info/gnd/17690-4"],
        regex=r"^https://d\-nb\.info/gnd/[-X0-9]{3,10}$",
    )
    isniId: list[str] = Field(
        [],
        examples=["https://isni.org/isni/0000000109403744"],
        regex=r"^https://isni\.org/isni/[X0-9]{16}$",
    )
    officialName: list[Text] = Field(..., min_items=1)
    rorId: list[str] = Field(
        [],
        examples=["https://ror.org/01k5qnb77"],
        regex=r"^https://ror\.org/[a-z0-9]{9}$",
    )
    shortName: list[Text] = []
    viafId: list[str] = Field(
        [],
        examples=["https://viaf.org/viaf/123556639"],
        regex=r"^https://viaf\.org/viaf/[0-9]{2,22}$",
    )
    wikidataId: str | None = Field(
        None,
        examples=["http://www.wikidata.org/entity/Q679041"],
        regex=r"^https://www\.wikidata\.org/entity/[PQ0-9]{2,64}$",
    )
