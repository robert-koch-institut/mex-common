from collections.abc import Generator

from mex.common.exceptions import EmptySearchResultError
from mex.common.orcid.connector import OrcidConnector
from mex.common.orcid.models.person import OrcidRecord
from mex.common.orcid.transform import map_orcid_data_to_orcid_record


def get_orcid_record_by_name(
    given_names: str = "*", family_name: str = "*", given_and_family_names: str = "*"
) -> OrcidRecord:
    """Returns Orcidrecord of a single person for the given filters.

    Args:
        given_names: Given name of a person, defaults to non-null
        family_name: Surname of a person, defaults to non-null
        given_and_family_names: Name of a person, default non-null

    Raises:
        EmptySearchResultError
        FoundMoreThanOneError

    Returns:
        Orcidrecord of the matching person by name.
    """
    orcid_data = OrcidConnector.get().get_data_by_name(
        given_names=given_names,
        family_name=family_name,
        given_and_family_names=given_and_family_names,
    )
    return map_orcid_data_to_orcid_record(orcid_data)


def get_orcid_record_by_id(orcid_id: str) -> OrcidRecord:
    """Returns Orcidrecord by UNIQUE ORCID ID.

    Args:
        orcid_id: Unique identifier in ORCID system.

    Returns:
        Orcidrecord of the matching id.
    """
    orcid_data = OrcidConnector.get().get_data_by_id(orcid_id=orcid_id)
    return map_orcid_data_to_orcid_record(orcid_data)


def get_orcid_records_by_given_or_family_name(
    given_names: str = "*", family_name: str = "*"
) -> Generator[OrcidRecord, None, None]:
    """Returns a generator of OrcidRecord objects matching the given filters.

    Args:
        given_names: Given name of a person, defaults to '*'.
        family_name: Surname of a person, defaults to '*'.

    Raises:
        EmptySearchResultError

    Yields:
        OrcidRecord: ORCID records matching the search filters.
    """
    filters = {"given-and-family-names": f"{given_names} {family_name}"}
    orcidapi = OrcidConnector.get()

    search_response = orcidapi.fetch(filters=filters)
    num_found = search_response.get("num-found", 0)

    if num_found == 0:
        raise EmptySearchResultError

    for record in search_response.get("result", []):
        orcid_data = orcidapi.get_data_by_id(record["orcid-identifier"]["path"])
        yield map_orcid_data_to_orcid_record(orcid_data)
