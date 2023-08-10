from pydantic import UUID4

from mex.common.models import BaseModel
from mex.common.types import Email


class LDAPActor(BaseModel):
    """Model class for generic LDAP accounts."""

    sAMAccountName: str | None = None
    objectGUID: UUID4
    mail: list[Email] = []

    @staticmethod
    def get_ldap_fields() -> tuple[str, ...]:
        """Return the fields that should be fetched from LDAP."""
        return tuple(sorted(LDAPActor.__fields__))
