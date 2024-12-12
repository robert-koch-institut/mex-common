from typing import Any

from mex.common.exceptions import EmptySearchResultError, FoundMoreThanOneError
from mex.common.orcid.connector import OrcidConnector


def get_person_by_id(orcid_id: str) -> dict[str, Any]:
    """Retrieve personal details by UNIQUE ORCID ID.

    Args:
        orcid_id: Uniqe identifier in ORCID system.

    Returns:
        Personal metadata of the single matching ORCID person.
    """
    orcidapi = OrcidConnector.get()
    if orcidapi.check_orcid_id_exists(orcid_id):
        # or endpoint = f"{orcid_id}/person"
        endpoint = f"{orcid_id}/record"
        return dict(orcidapi.request(method="GET", endpoint=endpoint))
    return {"result": None, "num-found": 0}


def get_person_by_name(
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
        Personal metadata of the single matching ORCID person.
    """
    orcidapi = OrcidConnector.get()
    if given_names:
        filters["given-names"] = given_names
    if family_name:
        filters["family-name"] = family_name
    search_response = orcidapi.fetch(orcidapi.build_query(filters))
    num_found = search_response.get("num-found", 0)
    if num_found == 0:
        msg = f"Cannot find orcid person for filters {filters}'"
        raise EmptySearchResultError(msg)
    if num_found > 1:
        msg = f"Found multiple AD persons for filters {filters}'"
        raise FoundMoreThanOneError(msg)

    orcid_id = search_response["result"][0]["orcid-identifier"]["path"]
    return get_person_by_id(orcid_id)
