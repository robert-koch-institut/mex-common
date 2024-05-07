import pytest

from mex.common.ldap.extract import _get_merged_ids_by_attribute
from mex.common.ldap.models.person import LDAPPerson
from mex.common.models import ExtractedPrimarySource
from mex.common.types import MergedPersonIdentifier


@pytest.mark.parametrize(
    ("attribute", "expected"), [("sAMAccountName", {})], ids=["person not found"]
)
def test_get_merged_ids_by_attribute(
    attribute: str,
    expected: dict[str, list[MergedPersonIdentifier]],
    extracted_primary_sources: dict[str, ExtractedPrimarySource],
) -> None:
    merged_ids_by_attribute = _get_merged_ids_by_attribute(
        attribute,
        [
            LDAPPerson(
                objectGUID="3f5a722d-e7c1-4c7c-ac40-23ce7753ce40",
                employeeID="foo",
                givenName=["Anna"],
                sn="bar",
            )
        ],
        extracted_primary_sources["ldap"],
    )
    assert merged_ids_by_attribute == expected
