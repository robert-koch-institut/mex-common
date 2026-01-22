from mex.common.ldap.helpers import get_ldap_units_for_employee_ids
from tests.ldap.conftest import SAMPLE_PERSON_ATTRS, LDAPMocker


def test_get_ldap_units_for_employee_ids(ldap_mocker: LDAPMocker) -> None:
    ldap_mocker(
        [
            [SAMPLE_PERSON_ATTRS],  # valid
            [],  # EmptySearchResultError
            [SAMPLE_PERSON_ATTRS, SAMPLE_PERSON_ATTRS],  # FoundMoreThanOneError
        ]
    )

    units = get_ldap_units_for_employee_ids(employee_ids=["1024", "9999", "8888"])

    assert units == {"XY2"}
