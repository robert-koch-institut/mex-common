from mex.common.ldap.models.actor import LDAPActor


class LDAPUnit(LDAPActor):
    """Model class for LDAP organizational units."""

    parent_label: str | None = None
