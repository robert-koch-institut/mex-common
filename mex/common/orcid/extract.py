from typing import Any

from mex.common.orcid.connector import OrcidConnector


def get_person_by_id(string_id: str) -> dict[str, Any]:
    """Get personal metadata by orcid id."""
    connector = OrcidConnector.get()
    return connector.get_personal_metadata_by_id(string_id)


def get_persons_by_name(
    surname: str = "*",
    given_name: str = "*",
    **filters: str,
) -> dict[str, Any]:
    """Get all orcid persons matching the filters.

    Args:
        given_name: Given name of a person, defaults to non-null.
        surname: Surname of a person, defaults to non-null.
        **filters: Additional filters.

    Returns:
        Generator for LDAP persons.
    """
    connector = OrcidConnector.get()
    return connector.get_personal_metadata_by_name(surname, given_name, **filters)
