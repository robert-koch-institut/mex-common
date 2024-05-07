from uuid import UUID

import pytest

from mex.common.identity import get_provider
from mex.common.ldap.extract import (
    _get_merged_ids_by_attribute,
    get_merged_ids_by_employee_ids,
)
from mex.common.ldap.models.person import LDAPPerson
from mex.common.models import ExtractedPrimarySource
from mex.common.types import Identifier


@pytest.fixture
def ldap_primary_source(
    extracted_primary_sources: dict[str, ExtractedPrimarySource]
) -> ExtractedPrimarySource:
    return extracted_primary_sources["ldap"]


@pytest.fixture
def ldap_person_with_identity(
    ldap_primary_source: ExtractedPrimarySource,
) -> LDAPPerson:
    person = LDAPPerson(
        objectGUID=UUID(int=1, version=4),
        employeeID="1",
        givenName=["Anna"],
        sn="Has Identity",
    )
    provider = get_provider()
    provider.assign(ldap_primary_source.stableTargetId, str(person.objectGUID))
    return person


@pytest.fixture
def ldap_person_without_identity() -> LDAPPerson:
    return LDAPPerson(
        objectGUID=UUID(int=2, version=4),
        employeeID="2",
        givenName=["Berta"],
        sn="Without Identity",
    )


@pytest.fixture
def ldap_persons(
    ldap_person_with_identity: LDAPPerson, ldap_person_without_identity: LDAPPerson
) -> list[LDAPPerson]:
    return [
        ldap_person_with_identity,
        ldap_person_without_identity,
    ]


@pytest.fixture
def merged_id_of_person_with_identity(
    ldap_person_with_identity: LDAPPerson,
    ldap_primary_source: ExtractedPrimarySource,
) -> Identifier:
    provider = get_provider()
    identities = provider.fetch(
        had_primary_source=ldap_primary_source.stableTargetId,
        identifier_in_primary_source=str(ldap_person_with_identity.objectGUID),
    )
    return identities[0].stableTargetId


def test_get_merged_ids_by_attribute(
    ldap_persons: list[LDAPPerson],
    ldap_primary_source: ExtractedPrimarySource,
    merged_id_of_person_with_identity: Identifier,
) -> None:
    merged_ids_by_attribute = _get_merged_ids_by_attribute(
        "sn",
        ldap_persons,
        ldap_primary_source,
    )
    assert merged_ids_by_attribute == {
        "Has Identity": [merged_id_of_person_with_identity]
    }

    with pytest.raises(RuntimeError):
        _get_merged_ids_by_attribute(
            "foo",
            ldap_persons,
            ldap_primary_source,
        )


def test_get_merged_ids_by_employee_ids(
    ldap_persons: list[LDAPPerson],
    ldap_primary_source: ExtractedPrimarySource,
    merged_id_of_person_with_identity: Identifier,
    ldap_person_with_identity: LDAPPerson,
) -> None:
    expected = {
        ldap_person_with_identity.employeeID: [merged_id_of_person_with_identity]
    }
    merged_ids_by_employee_ids = get_merged_ids_by_employee_ids(
        ldap_persons, ldap_primary_source
    )
    assert merged_ids_by_employee_ids == expected
