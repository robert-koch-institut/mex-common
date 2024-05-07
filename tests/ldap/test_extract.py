from uuid import UUID

from mex.common.identity import get_provider
from mex.common.ldap.extract import _get_merged_ids_by_attribute
from mex.common.ldap.models.person import LDAPPerson
from mex.common.models import ExtractedPrimarySource
from mex.common.testing import Joker


def test_get_merged_ids_by_attribute(
    extracted_primary_sources: dict[str, ExtractedPrimarySource],
) -> None:
    persons = [
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
    ldap_primary_source = extracted_primary_sources["ldap"]
    provider = get_provider()
    provider.assign(ldap_primary_source.stableTargetId, str(persons[0].objectGUID))
    merged_ids_by_attribute = _get_merged_ids_by_attribute(
        "sn",
        persons,
        ldap_primary_source,
    )
    assert merged_ids_by_attribute == {"Has Identity": [Joker()]}
