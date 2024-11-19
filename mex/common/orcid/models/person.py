from pydantic import Field

from mex.common.models import BaseModel


class Value(BaseModel):
    """Model class for value objects in ORCID data."""

    value: str | None = None


class DateValue(BaseModel):
    """Model class for date values."""

    value: int | None = None


class Name(BaseModel):
    """Model class for name details."""

    created_date: DateValue | None = Field(alias="created-date")
    last_modified_date: DateValue | None = Field(alias="last-modified-date")
    given_names: Value | None = Field(alias="given-names")
    family_name: Value | None = Field(alias="family-name")
    credit_name: Value | None = Field(alias="credit-name")
    source: Value | None = None
    visibility: str | None = None
    path: str | None = None


class OtherNames(BaseModel):
    """Model class for other names."""

    last_modified_date: DateValue | None = Field(alias="last-modified-date")
    other_name: list[Value] = []
    path: str | None = None


'''class ResearcherUrls(BaseModel):
    """Model class for representing researcher URLs."""
    last_modified_date: DateValue | None = Field(alias="last-modified-date")
    researcher_url: list[Value] = []
    path: str | None = None'''


class Emails(BaseModel):
    """Model class for representing emails."""

    last_modified_date: DateValue | None = Field(alias="last-modified-date")
    email: list[Value] = []
    path: str | None = None


'''class Addresses(BaseModel):
    """Model class for representing addresses."""
    last_modified_date: DateValue | None = Field(alias="last-modified-date")
    address: list[Value] = []
    path: str | None = None'''

'''class Keywords(BaseModel):
    """Model class for representing keywords."""
    last_modified_date: DateValue | None = Field(alias="last-modified-date")
    keyword: list[Value] = []
    path: str | None = None'''


class ExternalIdentifiers(BaseModel):
    """Model class for representing external identifiers."""

    last_modified_date: DateValue | None = Field(alias="last-modified-date")
    external_identifier: list[Value] = Field(alias="external-identifier")
    path: str | None = None


class OrcidPerson(BaseModel):
    """Model class for an ORCID person."""

    last_modified_date: DateValue | None = Field(alias="last-modified-date")
    name: Name
    other_names: OtherNames = Field(alias="other-names")
    biography: Value | None = None
    # researcher_urls: ResearcherUrls = Field(alias="researcher-urls")  # noqa: ERA001
    emails: Emails
    # addresses: Addresses  # noqa: ERA001
    # keywords: Keywords  # noqa: ERA001
    external_identifiers: ExternalIdentifiers = Field(alias="external-identifiers")
    path: str | None = None
