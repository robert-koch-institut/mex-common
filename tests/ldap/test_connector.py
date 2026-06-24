import re
from unittest.mock import MagicMock
from uuid import UUID

import pytest
from ldap3.core.exceptions import LDAPSocketSendError
from pytest import MonkeyPatch

from mex.common.exceptions import EmptySearchResultError, FoundMoreThanOneError
from mex.common.ldap.connector import LDAPConnector

# expected results derived from `assets/raw-data/ldap/data.ldif.TEMPLATE`
FRIEDA_FICTITIOUS = {
    "department": "FG99",
    "displayName": "Fictitious, Frieda, Dr.",
    "employeeID": "71",
    "givenName": ["Frieda"],
    "mail": ["fictitiousf@rki.de"],
    "objectGUID": UUID("00000000-0000-4000-8000-000000000003"),
    "sAMAccountName": "FictitiousF",
    "sn": "Fictitious",
}
CONTACT_C = {
    "mail": ["contactc@rki.de"],
    "objectGUID": UUID("00000000-0000-4000-8000-000000000004"),
    "ou": ["Funktion"],
    "sAMAccountName": "ContactC",
}
ALL_PERSON_ACCOUNTS = {"ResolvedR", "FelicitasJ", "FictitiousF"}


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", ""),
        ("Tést@exämple.com", "Tést@exämple.com"),
        ("test*wildcard and spaces", "test*wildcard and spaces"),
        ("bad$chars#(here)!", "bad*chars*here*"),
    ],
)
def test_sanitize_value(value: str, expected: str) -> None:
    assert LDAPConnector._sanitize(value) == expected


@pytest.mark.usefixtures("mocked_ldap")
def test_get_persons() -> None:
    connector = LDAPConnector.get()

    persons = connector.get_persons(surname="Fictitious", given_name="Frieda")
    assert persons.total == len(persons.items) == 1
    assert persons.items[0].model_dump(exclude_defaults=True) == FRIEDA_FICTITIOUS

    all_persons = connector.get_persons()
    assert all_persons.total == 3
    assert {p.sAMAccountName for p in all_persons.items} == ALL_PERSON_ACCOUNTS

    missing = connector.get_persons(surname="does-not-exist")
    assert missing.total == 0
    assert missing.items == []


@pytest.mark.usefixtures("mocked_ldap")
def test_get_functional_accounts() -> None:
    connector = LDAPConnector.get()

    accounts = connector.get_functional_accounts(mail="contactc@rki.de")
    assert accounts.total == len(accounts.items) == 1
    assert accounts.items[0].model_dump(exclude_defaults=True) == CONTACT_C

    missing = connector.get_functional_accounts(mail="does-not-exist@rki.de")
    assert missing.total == 0
    assert missing.items == []


@pytest.mark.usefixtures("mocked_ldap")
def test_get_persons_or_functional_accounts() -> None:
    connector = LDAPConnector.get()

    persons = connector.get_persons_or_functional_accounts(
        query="Fictitious, Frieda, Dr."
    )
    assert persons.total == 1
    assert persons.items[0].model_dump(exclude_defaults=True) == FRIEDA_FICTITIOUS

    accounts = connector.get_persons_or_functional_accounts(query="contactc@rki.de")
    assert accounts.total == 1
    assert accounts.items[0].model_dump(exclude_defaults=True) == CONTACT_C

    everyone = connector.get_persons_or_functional_accounts(query="*")
    assert everyone.total == 4

    missing = connector.get_persons_or_functional_accounts(query="does-not-exist")
    assert missing.total == 0
    assert missing.items == []


@pytest.mark.usefixtures("mocked_ldap")
def test_get_person() -> None:
    connector = LDAPConnector.get()

    person = connector.get_person(employee_id="71")
    assert person.model_dump(exclude_defaults=True) == FRIEDA_FICTITIOUS

    with pytest.raises(EmptySearchResultError, match="Cannot find AD person"):
        connector.get_person(surname="does-not-exist")

    with pytest.raises(FoundMoreThanOneError, match="Found multiple AD persons"):
        connector.get_person()


@pytest.mark.usefixtures("mocked_ldap")
def test_get_functional_account() -> None:
    connector = LDAPConnector.get()

    account = connector.get_functional_account(mail="contactc@rki.de")
    assert account.model_dump(exclude_defaults=True) == CONTACT_C

    with pytest.raises(
        EmptySearchResultError, match="Cannot find AD functional account"
    ):
        connector.get_functional_account(mail="does-not-exist@rki.de")


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
                    "ou": ["Funktion"],
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
    result = connector._fetch("(objectCategory=Person)", 1)
    assert result.raw_items[0] == {
        "sAMAccountName": "foo",
        "objectGUID": "00000000-0000-4000-8000-000000000000",
        "ou": ["Funktion"],
    }
    assert connector._connection is second_connection


def test_pagination(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(LDAPConnector, "_setup_connection", lambda _: None)
    monkeypatch.setattr(
        LDAPConnector,
        "_fetch_all",
        lambda _, __: [{"attributes": {"employeeID": x + 1}} for x in range(1022)],
    )

    connector = LDAPConnector.get()

    with pytest.raises(ValueError, match=re.compile(r">= 0")):
        connector._fetch("(objectCategory=Person)", -1, 100)

    with pytest.raises(ValueError, match="offset exceeds the total number of elements"):
        connector._fetch("(objectCategory=Person)", 100, 1100)

    response = connector._fetch("(objectCategory=Person)", 33, 100)
    assert response.total == 1022
    assert response.raw_items
    assert len(response.raw_items) == 33
    assert response.raw_items[0]["employeeID"] == 101
    assert response.raw_items[-1]["employeeID"] == 133

    response = connector._fetch("(objectCategory=Person)", 33, 1000)
    assert response.total == 1022
    assert response.raw_items
    assert len(response.raw_items) == 22
    assert response.raw_items[0]["employeeID"] == 1001
    assert response.raw_items[-1]["employeeID"] == 1022
