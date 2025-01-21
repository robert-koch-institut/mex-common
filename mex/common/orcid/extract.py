from mex.common.orcid.connector import get_data_by_id, get_data_by_name
from mex.common.orcid.models.person import OrcidRecord
from mex.common.orcid.transform import map_orcid_data_to_orcid_record


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
