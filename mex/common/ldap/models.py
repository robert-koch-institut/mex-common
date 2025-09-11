from typing import Final, Literal, get_args

from pydantic import UUID4, TypeAdapter

from mex.common.models import BaseModel
from mex.common.types import Email


class LDAPActor(BaseModel):
    """Model class for generic LDAP accounts."""

    objectGUID: UUID4
    sAMAccountName: str | None = None
    mail: list[Email] = []


class LDAPPerson(LDAPActor):
    """Model class for LDAP persons."""

    employeeID: str
    givenName: list[str]
    sn: str
    company: str | None = None
    department: str | None = None
    departmentNumber: str | None = None
    displayName: str | None = None
    ou: list[str] = []


class LDAPPersonWithQuery(BaseModel):
    """Wrapper bundling LDAPPerson models with the query string that found them."""

    person: LDAPPerson
    query: str


class LDAPFunctionalAccount(LDAPActor):
    """Model class for LDAP functional accounts."""

    ou: list[Literal["Funktion"]]


AnyLDAPActor = LDAPPerson | LDAPFunctionalAccount
LDAP_MODEL_CLASSES: Final[list[type[AnyLDAPActor]]] = list(get_args(AnyLDAPActor))
AnyLDAPActorsTypeAdapter: TypeAdapter[list[AnyLDAPActor]] = TypeAdapter(
    list[AnyLDAPActor]
)
LDAPFunctionalAccountsTypeAdapter: TypeAdapter[list[LDAPFunctionalAccount]] = (
    TypeAdapter(list[LDAPFunctionalAccount])
)
LDAPPersonsTypeAdapter: TypeAdapter[list[LDAPPerson]] = TypeAdapter(list[LDAPPerson])
