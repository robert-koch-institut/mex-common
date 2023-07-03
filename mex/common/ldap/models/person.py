from pydantic import Field, NoneStr

from mex.common.ldap.models.actor import LDAPActor
from mex.common.models.base import BaseModel


class LDAPPerson(LDAPActor):
    """Model class for LDAP persons."""

    company: NoneStr = Field(None)
    department: NoneStr = Field(None)
    departmentNumber: NoneStr = Field(None)
    displayName: NoneStr = Field(None)
    employeeID: str = Field(...)
    givenName: list[str] = Field(..., min_items=1)
    ou: list[str] = Field([])
    sn: str = Field(...)

    @classmethod
    def get_ldap_fields(cls) -> tuple[str, ...]:
        """Return the fields that should be fetched from LDAP."""
        return tuple(sorted(cls.__fields__))


class LDAPPersonWithQuery(BaseModel):
    """Wrapper bundling LDAPPerson models with the query string that found them."""

    person: LDAPPerson
    query: str
