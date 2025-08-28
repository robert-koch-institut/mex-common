from typing import Annotated, Literal

from pydantic import UUID4, Field, TypeAdapter

from mex.common.models import BaseModel
from mex.common.types import Email


class LDAPActor(BaseModel):
    """Model class for generic LDAP accounts."""

    sAMAccountName: str | None = None
    objectGUID: UUID4
    mail: list[Email] = []
    displayName: str | None = None


class LDAPPerson(LDAPActor):
    """Model class for LDAP persons."""

    company: str | None = None
    department: str | None = None
    departmentNumber: str | None = None
    employeeID: str
    givenName: Annotated[list[str], Field(min_length=1)]
    ou: list[str] = []
    sn: str


class LDAPPersonWithQuery(BaseModel):
    """Wrapper bundling LDAPPerson models with the query string that found them."""

    person: LDAPPerson
    query: str


class LDAPFunctionalAccount(LDAPActor):
    """Model class for LDAP functional accounts."""

    ou: list[Literal["Funktion"]]


AnyLDAPActor = LDAPPerson | LDAPFunctionalAccount
LDAPActorTypeAdapter: TypeAdapter[AnyLDAPActor] = TypeAdapter(AnyLDAPActor)
