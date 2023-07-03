from pydantic import NoneStr

from mex.common.ldap.models.actor import LDAPActor


class LDAPUnit(LDAPActor):
    """Model class for LDAP organizational units."""

    parent_label: NoneStr = None
