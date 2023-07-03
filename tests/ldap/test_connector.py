import re
from uuid import UUID

import pytest

from mex.common.exceptions import MExError
from mex.common.ldap.connector import LDAPConnector
from tests.ldap.conftest import (
    SAMPLE_PERSON_ATTRS,
    XY2_DEPARTMENT_ATTRS,
    XY_DEPARTMENT_ATTRS,
    LDAPMocker,
    PagedSearchResults,
)


def test_get_persons_mocked(ldap_mocker: LDAPMocker) -> None:
    ldap_mocker([[SAMPLE_PERSON_ATTRS]])
    connector = LDAPConnector.get()
    persons = list(connector.get_persons(surname="Sample", given_name="Kim"))

    assert len(persons) == 1
    assert persons[0].dict(exclude_none=True) == {
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
    "kwargs, pattern",
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
def test_get_persons_ldap(kwargs: dict[str, str], pattern: str) -> None:
    connector = LDAPConnector.get()
    persons = list(connector.get_persons(**kwargs))

    flat_result = ",".join(str(p.objectGUID) for p in persons)
    assert re.match(pattern, flat_result)


def test_get_units_mocked(ldap_mocker: LDAPMocker) -> None:
    ldap_mocker([[XY_DEPARTMENT_ATTRS]])
    connector = LDAPConnector.get()
    units = list(connector.get_units(sAMAccountName="XY"))

    assert len(units) == 1
    assert units[0].dict(exclude_none=True) == {
        "mail": ["XY@mail.tld"],
        "objectGUID": UUID("00000000-0000-4000-8000-000000000042"),
        "sAMAccountName": "XY",
    }


@pytest.mark.parametrize(
    "search_results, error_text",
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
    assert person.dict(exclude_none=True) == expected


@pytest.mark.parametrize(
    "search_results, error_text",
    [
        ([[]], "Cannot find AD unit"),
        ([[XY_DEPARTMENT_ATTRS, XY2_DEPARTMENT_ATTRS]], "Found multiple AD units"),
    ],
)
def test_get_unit_mocked_error(
    ldap_mocker: LDAPMocker, search_results: PagedSearchResults, error_text: str
) -> None:
    ldap_mocker(search_results)
    connector = LDAPConnector.get()
    with pytest.raises(MExError, match=error_text):
        connector.get_unit(sAMAccountName="whatever")


def test_get_unit_mocked(ldap_mocker: LDAPMocker) -> None:
    ldap_mocker([[XY_DEPARTMENT_ATTRS]])
    connector = LDAPConnector.get()

    unit = connector.get_unit(sAMAccountName=XY_DEPARTMENT_ATTRS["sAMAccountName"][0])

    expected = {
        "mail": ["XY@mail.tld"],
        "objectGUID": UUID("00000000-0000-4000-8000-000000000042"),
        "sAMAccountName": "XY",
    }
    assert unit.dict(exclude_none=True) == expected
