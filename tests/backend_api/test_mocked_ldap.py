import pytest

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.exceptions import EmptySearchResultError, FoundMoreThanOneError
from mex.common.models import ExtractedContactPoint, ExtractedPerson

ALL_PERSON_IDENTIFIERS_IN_PRIMARY_SOURCE = {
    "00000000-0000-4000-8000-000000000001",
    "00000000-0000-4000-8000-000000000002",
    "00000000-0000-4000-8000-000000000003",
}


@pytest.mark.usefixtures("mocked_backend_ldap")
def test_get_persons(frieda_fictitious: ExtractedPerson) -> None:
    connector = BackendApiConnector.get()

    persons = connector.get_persons(surname="Fictitious", given_name="Frieda")
    assert persons.total == len(persons.items) == 1
    assert persons.items[0] == frieda_fictitious

    all_persons = connector.get_persons()
    assert all_persons.total == 3
    assert {
        p.identifierInPrimarySource for p in all_persons.items
    } == ALL_PERSON_IDENTIFIERS_IN_PRIMARY_SOURCE

    missing = connector.get_persons(surname="does-not-exist")
    assert missing.total == 0
    assert missing.items == []


@pytest.mark.usefixtures("mocked_backend_ldap")
def test_get_functional_accounts(contact_point: ExtractedContactPoint) -> None:
    connector = BackendApiConnector.get()

    accounts = connector.get_functional_accounts(mail="contactc@rki.de")
    assert accounts.total == len(accounts.items) == 1
    assert accounts.items[0] == contact_point

    missing = connector.get_functional_accounts(mail="does-not-exist@rki.de")
    assert missing.total == 0
    assert missing.items == []


@pytest.mark.usefixtures("mocked_backend_ldap")
def test_get_person(frieda_fictitious: ExtractedPerson) -> None:
    connector = BackendApiConnector.get()

    person = connector.get_person(employee_id="71")
    assert person == frieda_fictitious

    with pytest.raises(EmptySearchResultError, match="Cannot find AD person"):
        connector.get_person(surname="does-not-exist")

    with pytest.raises(FoundMoreThanOneError, match="Found multiple AD persons"):
        connector.get_person()


@pytest.mark.usefixtures("mocked_backend_ldap")
def test_get_functional_account(contact_point: ExtractedContactPoint) -> None:
    connector = BackendApiConnector.get()

    account = connector.get_functional_account(mail="contactc@rki.de")
    assert account == contact_point

    with pytest.raises(
        EmptySearchResultError, match="Cannot find AD functional account"
    ):
        connector.get_functional_account(mail="does-not-exist@rki.de")
