from pydantic import Field

from mex.common.models import BaseModel


class GivenNames(BaseModel):
    """Model class for given names."""

    given_names: str | None = Field(alias="given-names")
    visibility: str | None = None


class FamilyName(BaseModel):
    """Model class for family name."""

    family_name: str | None = Field(alias="family-name")
    visibility: str | None = None


class OrcidPerson(BaseModel):
    """Model class for ORCID Person."""

    orcid_identifier: str = Field(alias="orcid-identifier")
    email: list[str] | None = Field(alias="email")
    given_names: GivenNames
    family_name: FamilyName

    @staticmethod
    def get_orcid_fields() -> tuple[str, ...]:
        """Return the fields that should be fetched for an ORCID person."""
        return tuple(sorted(OrcidPerson.__annotations__))
