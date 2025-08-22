import re
from typing import Any
from unittest.mock import MagicMock
from uuid import UUID

import pytest
from ldap3.core.exceptions import LDAPSocketSendError
from pytest import MonkeyPatch

from mex.common.exceptions import MExError
from mex.common.ldap.connector import LDAPConnector
from mex.common.ldap.models import LDAPActor
from tests.ldap.conftest import (
    SAMPLE_PERSON_ATTRS,
    XY2_FUNC_ACCOUNT_ATTRS,
    XY_FUNC_ACCOUNT_ATTRS,
    LDAPMocker,
    PagedSearchResults,
)


def test_get_persons_mocked(ldap_mocker: LDAPMocker) -> None:
    ldap_mocker([[SAMPLE_PERSON_ATTRS]])
    connector = LDAPConnector.get()
    persons = list(connector.get_persons(surname="Sample", given_name="Kim"))

    assert len(persons) == 1
    assert persons[0].model_dump(exclude_none=True) == {
        "company": "RKI",
        "department": "XY",
        "departmentNumber": "XY2",
        "displayName": "Sample, Sam",
        "employeeID": "1024",
        "givenName": ["Sam"],
        "mail": ["SampleS@mail.tld"],
        "objectGUID": UUID(int=0, version=4),
        "ou": ["XY"],
        "sAMAccountName": "SampleS",
        "sn": "Sample",
    }


@pytest.mark.parametrize(
    ("kwargs", "pattern"),
    [
        ({"surname": "müller"}, r".{37,}"),  # needs more than one guid to pass
        ({"surname": "nobody-has-this-name"}, r""),  # only empty list passes
    ],
    ids=[
        "common_surname",
        "nonexistent_person",
    ],
)
@pytest.mark.integration
def test_get_persons_ldap(kwargs: dict[str, Any], pattern: str) -> None:
    connector = LDAPConnector.get()
    persons = list(connector.get_persons(**kwargs))

    flat_result = ",".join(str(p.objectGUID) for p in persons)
    assert re.match(pattern, flat_result)


@pytest.mark.parametrize(
    ("kwargs", "pattern"),
    [
        ({"mail": "mex@rki.de"}, r".{36}"),  # exactly one guid
        ({"mail": "non-existent@function.xyz"}, r"^$"),  # empty result
    ],
    ids=[
        "mex_functional_account",
        "nonexistent_functional_account",
    ],
)
@pytest.mark.integration
def test_get_functional_accounts_ldap(kwargs: dict[str, Any], pattern: str) -> None:
    connector = LDAPConnector.get()
    functional_accounts = list(connector.get_functional_accounts(**kwargs))

    flat_result = ",".join(str(p.objectGUID) for p in functional_accounts)
    assert re.match(pattern, flat_result)


def test_get_functional_accounts_mocked(ldap_mocker: LDAPMocker) -> None:
    ldap_mocker([[XY_FUNC_ACCOUNT_ATTRS]])
    connector = LDAPConnector.get()
    functional_accounts = list(connector.get_functional_accounts(sAMAccountName="XY"))

    assert len(functional_accounts) == 1
    assert functional_accounts[0].model_dump(exclude_none=True) == {
        "mail": ["XY@mail.tld"],
        "objectGUID": UUID("00000000-0000-4000-8000-000000000044"),
        "sAMAccountName": "XY",
    }


@pytest.mark.parametrize(
    ("search_results", "error_text"),
    [
        ([[]], "Cannot find AD person"),
        ([[SAMPLE_PERSON_ATTRS, SAMPLE_PERSON_ATTRS]], "Found multiple AD persons"),
    ],
)
def test_get_person_mocked_error(
    ldap_mocker: LDAPMocker, search_results: PagedSearchResults, error_text: str
) -> None:
    ldap_mocker(search_results)
    connector = LDAPConnector.get()
    with pytest.raises(MExError, match=error_text):
        connector.get_person(objectGUID="whatever")


def test_get_person_mocked(ldap_mocker: LDAPMocker) -> None:
    ldap_mocker([[SAMPLE_PERSON_ATTRS]])
    connector = LDAPConnector.get()

    person = connector.get_person(objectGUID=SAMPLE_PERSON_ATTRS["objectGUID"][0])

    expected = {
        "company": "RKI",
        "department": "XY",
        "departmentNumber": "XY2",
        "displayName": "Sample, Sam",
        "employeeID": "1024",
        "givenName": ["Sam"],
        "mail": ["SampleS@mail.tld"],
        "objectGUID": UUID("00000000-0000-4000-8000-000000000000"),
        "ou": ["XY"],
        "sAMAccountName": "SampleS",
        "sn": "Sample",
    }
    assert person.model_dump(exclude_none=True) == expected


@pytest.mark.parametrize(
    ("search_results", "error_text"),
    [
        ([[]], "Cannot find AD functional account"),
        (
            [[XY_FUNC_ACCOUNT_ATTRS, XY2_FUNC_ACCOUNT_ATTRS]],
            "Found multiple AD functional accounts",
        ),
    ],
)
def test_get_functional_account_mocked_error(
    ldap_mocker: LDAPMocker, search_results: PagedSearchResults, error_text: str
) -> None:
    ldap_mocker(search_results)
    connector = LDAPConnector.get()
    with pytest.raises(MExError, match=error_text):
        connector.get_functional_account(sAMAccountName="whatever")


def test_functional_account_mocked(ldap_mocker: LDAPMocker) -> None:
    ldap_mocker([[XY_FUNC_ACCOUNT_ATTRS]])
    connector = LDAPConnector.get()

    unit = connector.get_functional_account(
        sAMAccountName=XY_FUNC_ACCOUNT_ATTRS["sAMAccountName"][0]
    )

    expected = {
        "mail": ["XY@mail.tld"],
        "objectGUID": UUID("00000000-0000-4000-8000-000000000044"),
        "sAMAccountName": "XY",
    }
    assert unit.model_dump(exclude_none=True) == expected


def test_fetch_backoff_reconnect(monkeypatch: MonkeyPatch) -> None:
    # first connection raises ldap error
    first_connection = MagicMock(name="conn1")
    first_connection.extend.standard.paged_search = MagicMock(
        side_effect=LDAPSocketSendError("Simulated error")
    )
    # second connection returns valid content
    second_connection: MagicMock = MagicMock(name="conn2")
    second_connection.extend.standard.paged_search = MagicMock(
        return_value=[
            {
                "attributes": {
                    "sAMAccountName": "foo",
                    "objectGUID": "00000000-0000-4000-8000-000000000000",
                }
            }
        ]
    )

    monkeypatch.setattr(
        LDAPConnector,
        "_setup_connection",
        MagicMock(side_effect=[first_connection, second_connection]),
    )
    connector = LDAPConnector.get()
    assert connector._connection is first_connection
    result = connector._fetch(LDAPActor)
    assert result[0].model_dump(exclude_defaults=True) == {
        "sAMAccountName": "foo",
        "objectGUID": UUID("00000000-0000-4000-8000-000000000000"),
    }
    assert connector._connection is second_connection
