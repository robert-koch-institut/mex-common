from uuid import UUID

import pytest

from mex.common.identity import get_provider
from mex.common.ldap.extract import (
    get_merged_ids_by_employee_ids,
    get_merged_ids_by_query_string,
)
from mex.common.ldap.models import LDAPPerson, LDAPPersonWithQuery
from mex.common.models import ExtractedPrimarySource
from mex.common.types import Identifier


@pytest.fixture
def ldap_primary_source(
    extracted_primary_sources: dict[str, ExtractedPrimarySource],
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
        mail=["annaWithIdentity@example.com", "annaWithIdentity@test.com"],
        sn="Has Identity",
    )
    provider = get_provider()
    provider.assign(ldap_primary_source.stableTargetId, str(person.objectGUID))
    return person


@pytest.fixture
def ldap_person_with_identity_with_query(
    ldap_person_with_identity: LDAPPerson,
) -> LDAPPersonWithQuery:
    return LDAPPersonWithQuery(person=ldap_person_with_identity, query="foo")


@pytest.fixture
def ldap_person_without_identity() -> LDAPPerson:
    return LDAPPerson(
        objectGUID=UUID(int=2, version=4),
        employeeID="2",
        givenName=["Berta"],
        mail=["bertaWithoutIdentity@example.com"],
        sn="Without Identity",
    )


@pytest.fixture
def ldap_person_without_identity_with_query(
    ldap_person_without_identity: LDAPPerson,
) -> LDAPPersonWithQuery:
    return LDAPPersonWithQuery(person=ldap_person_without_identity, query="foo")


@pytest.fixture
def ldap_persons(
    ldap_person_with_identity: LDAPPerson, ldap_person_without_identity: LDAPPerson
) -> list[LDAPPerson]:
    return [
        ldap_person_with_identity,
        ldap_person_without_identity,
    ]


@pytest.fixture
def ldap_persons_with_query(
    ldap_person_with_identity_with_query: LDAPPersonWithQuery,
    ldap_person_without_identity_with_query: LDAPPersonWithQuery,
) -> list[LDAPPersonWithQuery]:
    return [
        ldap_person_with_identity_with_query,
        ldap_person_without_identity_with_query,
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


def test_get_merged_ids_by_query_string(
    ldap_person_with_identity_with_query: LDAPPersonWithQuery,
    ldap_persons_with_query: list[LDAPPersonWithQuery],
    ldap_primary_source: ExtractedPrimarySource,
    merged_id_of_person_with_identity: Identifier,
) -> None:
    expected = {
        ldap_person_with_identity_with_query.query: [merged_id_of_person_with_identity]
    }
    merged_ids_by_query_string = get_merged_ids_by_query_string(
        ldap_persons_with_query, ldap_primary_source
    )
    assert merged_ids_by_query_string == expected
