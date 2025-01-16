from typing import Any

from mex.common.exceptions import EmptySearchResultError, FoundMoreThanOneError
from mex.common.orcid.connector import OrcidConnector
from mex.common.orcid.models.person import OrcidRecord
from mex.common.orcid.transform import map_orcid_data_to_orcid_record


def get_data_by_id(orcid_id: str) -> dict[str, Any]:
    """Retrieve data by UNIQUE ORCID ID.

    Args:
        orcid_id: Uniqe identifier in ORCID system.

    Returns:
        Personal data of the single matching id.
    """
    orcidapi = OrcidConnector.get()
    # or endpoint = f"{orcid_id}/person"
    endpoint = f"{orcid_id}/record"
    return dict(orcidapi.request(method="GET", endpoint=endpoint))


def get_data_by_name(
    given_names: str = "*",
    family_name: str = "*",
    **filters: str,
) -> dict[str, Any]:
    """Get ORCID record of a single person for the given filters.

    Args:
        given_names: Given name of a person, defaults to non-null
        family_name: Surname of a person, defaults to non-null
        **filters: Key-value pairs representing ORCID search filters.

    Raises:
        EmptySearchResultError
        FoundMoreThanOneError

    Returns:
        Orcid data of the single matching person by name.
    """
    orcidapi = OrcidConnector.get()
    if given_names:
        filters["given-names"] = given_names
    if family_name:
        filters["family-name"] = family_name
    search_response = orcidapi.fetch(filters=filters)
    num_found = search_response.get("num-found", 0)
    if num_found == 0:
        msg = f"Cannot find orcid person for filters {filters}'"
        raise EmptySearchResultError(msg)
    if num_found > 1:
        msg = f"Found multiple orcid persons for filters {filters}'"
        raise FoundMoreThanOneError(msg)

    orcid_id = search_response["result"][0]["orcid-identifier"]["path"]
    return get_data_by_id(orcid_id)


def get_orcid_record_by_name(
    given_names: str = "*", family_name: str = "*"
) -> OrcidRecord:
    """Returns Orcidrecord of a single person for the given filters.

    Args:
        given_names: Given name of a person, defaults to non-null
        family_name: Surname of a person, defaults to non-null
        **filters: Key-value pairs representing ORCID search filters.

    Raises:
        EmptySearchResultError
        FoundMoreThanOneError

    Returns:
        Orcidrecord of the matching person by name.
    """
    orcid_data = get_data_by_name(given_names=given_names, family_name=family_name)
    return map_orcid_data_to_orcid_record(orcid_data)


def get_orcid_record_by_id(orcid_id: str) -> OrcidRecord:
    """Returns Orcidrecord by UNIQUE ORCID ID.

    Args:
        orcid_id: Uniqe identifier in ORCID system.

    Returns:
        Orcidrecord of the matching id.
    """
    orcid_data = get_data_by_id(orcid_id=orcid_id)
    return map_orcid_data_to_orcid_record(orcid_data)
