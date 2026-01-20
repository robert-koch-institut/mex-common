from collections.abc import Iterable

from mex.common.exceptions import EmptySearchResultError, FoundMoreThanOneError
from mex.common.ldap.connector import LDAPConnector


def get_ldap_units_for_employee_ids(
    employee_ids: Iterable[str],
) -> set[str]:
    """Return organizational unit strings for given employee IDs using LDAP."""
    ldap = LDAPConnector.get()
    units: set[str] = set()

    for employee_id in employee_ids:
        try:
            person = ldap.get_person(employee_id=employee_id)
        except EmptySearchResultError:
            continue
        except FoundMoreThanOneError:
            continue

        if person.departmentNumber:
            units.add(person.departmentNumber)

    return units
