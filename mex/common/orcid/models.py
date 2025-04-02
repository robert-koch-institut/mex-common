from pydantic import Field

from mex.common.models import BaseModel


class OrcidIdentifier(BaseModel):
    """Model class for OrcidID."""

    path: str
    uri: str


class OrcidEmail(BaseModel):
    """Model class for Orcid email."""

    email: list[str]


class OrcidEmails(BaseModel):
    """Model class for Orcid emails."""

    email: list[OrcidEmail]


class OrcidFamilyName(BaseModel):
    """Model class for orcid family names."""

    value: str


class OrcidGivenNames(BaseModel):
    """Model class for Orcid given names."""

    value: str


class OrcidName(BaseModel):
    """Model class for Orcid name."""

    family_name: OrcidFamilyName | None = Field(alias="family-name")
    given_names: OrcidGivenNames | None = Field(alias="given-names")
    visibility: str


class OrcidPerson(BaseModel):
    """Model class for Orcid person."""

    emails: OrcidEmails
    name: OrcidName


class OrcidRecord(BaseModel):
    """Model class for Orcid record."""

    orcid_identifier: OrcidIdentifier = Field(alias="orcid-identifier")
    person: OrcidPerson


class OrcidSearchItem(BaseModel):
    """Model class for a single search result item."""

    orcid_identifier: OrcidIdentifier = Field(alias="orcid-identifier")


class OrcidSearchResponse(BaseModel):
    """Model class for a search response."""

    num_found: int = Field(alias="num-found")
    result: list[OrcidSearchItem]
