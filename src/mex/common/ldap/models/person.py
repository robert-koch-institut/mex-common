from typing import Annotated

from pydantic import Field

from mex.common.ldap.models.actor import LDAPActor
from mex.common.models import BaseModel


class LDAPPerson(LDAPActor):
    """Model class for LDAP persons."""

    company: str | None = None
    department: str | None = None
    departmentNumber: str | None = None
    displayName: str | None = None
    employeeID: str
    givenName: Annotated[list[str], Field(min_length=1)]
    ou: list[str] = []
    sn: str

    @classmethod
    def get_ldap_fields(cls) -> tuple[str, ...]:
        """Return the fields that should be fetched from LDAP."""
        return tuple(sorted(cls.model_fields))


class LDAPPersonWithQuery(BaseModel):
    """Wrapper bundling LDAPPerson models with the query string that found them."""

    person: LDAPPerson
    query: str
