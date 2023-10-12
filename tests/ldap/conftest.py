from typing import Any, Callable
from unittest.mock import MagicMock, Mock

import pytest
from ldap3 import Connection
from pytest import MonkeyPatch

from mex.common.ldap.connector import LDAPConnector

PagedSearchResults = list[list[dict[str, Any]]]
LDAPMocker = Callable[[PagedSearchResults], None]


SAMPLE_PERSON_ATTRS = dict(
    company=["RKI"],
    department=["XY"],
    departmentNumber=["XY2"],
    displayName=["Sample, Sam"],
    employeeID=["1024"],
    givenName=["Sam"],
    mail=["SampleS@mail.tld"],
    objectGUID=["{00000000-0000-4000-8000-000000000000}"],
    ou=["XY"],
    sAMAccountName=["SampleS"],
    sn=["Sample"],
)

XY_DEPARTMENT_ATTRS = dict(
    mail=["XY@mail.tld"],
    objectGUID=["{00000000-0000-4000-8000-000000000042}"],
    sAMAccountName=["XY"],
)

XY2_DEPARTMENT_ATTRS = dict(
    mail=["XY2@mail.tld"],
    objectGUID=["{00000000-0000-4000-8000-000000000043}"],
    sAMAccountName=["XY2"],
)

XY_FUNC_ACCOUNT_ATTRS = dict(
    mail=["XY@mail.tld"],
    objectGUID=["{00000000-0000-4000-8000-000000000044}"],
    sAMAccountName=["XY"],
)

XY2_FUNC_ACCOUNT_ATTRS = dict(
    mail=["XY2@mail.tld"],
    objectGUID=["{00000000-0000-4000-8000-000000000045}"],
    sAMAccountName=["XY2"],
)


@pytest.fixture
def ldap_mocker(monkeypatch: MonkeyPatch) -> LDAPMocker:
    """Patch the LDAP connector to return `SAMPLE_PERSON_ATTRS` from its connection."""

    def mocker(results: PagedSearchResults) -> None:
        def __init__(self: LDAPConnector) -> None:
            self.connection = MagicMock(spec=Connection, extend=Mock())
            self.connection.extend.standard.paged_search = MagicMock(
                side_effect=[
                    [dict(attributes=e) for e in entries] for entries in results
                ]
            )

        monkeypatch.setattr(LDAPConnector, "__init__", __init__)

    return mocker
