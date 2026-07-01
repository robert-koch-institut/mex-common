import pytest
from ldap3.core.exceptions import LDAPSocketOpenError

from mex.common.ldap.connector import LDAPConnector

SAMPLE_PERSON_ATTRS = {
    "company": ["RKI"],
    "department": ["XY"],
    "departmentNumber": ["XY2"],
    "displayName": ["Sample, Sam"],
    "employeeID": ["1024"],
    "givenName": ["Sam"],
    "mail": ["SampleS@mail.tld"],
    "objectGUID": ["{00000000-0000-4000-8000-000000000000}"],
    "ou": ["XY"],
    "sAMAccountName": ["SampleS"],
    "sn": ["Sample"],
}


@pytest.fixture(autouse=True)
def skip_ldap_integration_tests_on_connection_error(
    is_integration_test: bool,  # noqa: FBT001
) -> None:
    if is_integration_test:
        try:
            LDAPConnector.get()
        except LDAPSocketOpenError:
            pytest.skip("LDAP unavailable")
