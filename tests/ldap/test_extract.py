from uuid import UUID

import pytest

from mex.common.identity import get_provider
from mex.common.ldap.extract import (
    _get_merged_ids_by_attribute,
    get_merged_ids_by_employee_ids,
)
from mex.common.ldap.models.person import LDAPPerson
from mex.common.models import ExtractedPrimarySource
from mex.common.testing import Joker


@pytest.fixture
def ldap_primary_source(
    extracted_primary_sources: dict[str, ExtractedPrimarySource]
) -> ExtractedPrimarySource:
    return extracted_primary_sources["ldap"]


@pytest.fixture
def ldap_persons() -> list[LDAPPerson]:
    return [
        LDAPPerson(
            objectGUID=UUID(int=1, version=4),
            employeeID="1",
            givenName=["Anna"],
            sn="Has Identity",
        ),
        LDAPPerson(
            objectGUID=UUID(int=2, version=4),
            employeeID="2",
            givenName=["Berta"],
            sn="Without Identity",
        ),
    ]


def test_get_merged_ids_by_attribute(
    ldap_persons: list[LDAPPerson],
    ldap_primary_source: ExtractedPrimarySource,
) -> None:
    provider = get_provider()
    provider.assign(ldap_primary_source.stableTargetId, str(ldap_persons[0].objectGUID))
    merged_ids_by_attribute = _get_merged_ids_by_attribute(
        "sn",
        ldap_persons,
        ldap_primary_source,
    )
    assert merged_ids_by_attribute == {"Has Identity": [Joker()]}

    with pytest.raises(RuntimeError):
        _get_merged_ids_by_attribute(
            "foo",
            ldap_persons,
            ldap_primary_source,
        )


def test_get_merged_ids_by_employee_ids(
    ldap_persons: list[LDAPPerson], ldap_primary_source: ExtractedPrimarySource
) -> None:
    get_merged_ids_by_employee_ids(ldap_persons, ldap_primary_source)
