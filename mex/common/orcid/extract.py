from functools import lru_cache
from typing import Any

from mex.common.exceptions import EmptySearchResultError, FoundMoreThanOneError
from mex.common.models import PaginatedItemsContainer
from mex.common.orcid.connector import OrcidConnector
from mex.common.orcid.models import OrcidRecord


@lru_cache(maxsize=128)
def get_orcid_record_by_id(orcid_id: str) -> OrcidRecord:
    """Get a single orcid record by id.

    Args:
        orcid_id: Unique identifier in ORCID system.

    Returns:
        Orcid record of the single matching id.
    """
    connector = OrcidConnector.get()
    return connector.get_record_by_id(orcid_id)


def get_orcid_record_by_name(
    given_names: str | None = None,
    family_name: str | None = None,
    given_and_family_names: str | None = None,
    filters: dict[str, Any] | None = None,
) -> OrcidRecord:
    """Get OrcidRecord of a single person for the given filters.

    Args:
        given_names: Optional given name of a person.
        family_name: Optional surname of a person.
        given_and_family_names: Optional full name of a person.
        filters: Key-value pairs representing ORCID search filters.

    Raises:
        EmptySearchResultError
        FoundMoreThanOneError

    Returns:
        OrcidRecord of the matching person by name.
    """
    connector = OrcidConnector.get()
    orcid_response = connector.search_records_by_name(
        given_names=given_names,
        family_name=family_name,
        given_and_family_names=given_and_family_names,
        filters=filters,
        skip=0,
        limit=1,
    )
    if orcid_response.num_found == 0:
        msg = "Cannot find orcid person for filters."
        raise EmptySearchResultError(msg)
    if orcid_response.num_found > 1:
        msg = f"Found multiple orcid persons for filters: {orcid_response.num_found}"
        raise FoundMoreThanOneError(msg)
    return get_orcid_record_by_id(
        orcid_response.result[0].orcid_identifier.path,
    )


def search_records_by_name(  # noqa: PLR0913
    given_names: str | None = None,
    family_name: str | None = None,
    given_and_family_names: str | None = None,
    filters: dict[str, Any] | None = None,
    skip: int = 0,
    limit: int = 10,
) -> PaginatedItemsContainer[OrcidRecord]:
    """Get all Orcid records for the given filters.

    Args:
        given_names: Optional given name of a person.
        family_name: Optional surname of a person.
        given_and_family_names: Optional full name of a person.
        filters: Key-value pairs representing ORCID search filters.
        skip: How many items to skip for pagination.
        limit: How many items to return in one page.

    Returns:
        Paginated container of orcid records.
    """
    connector = OrcidConnector.get()
    response = connector.search_records_by_name(
        given_names=given_names,
        family_name=family_name,
        given_and_family_names=given_and_family_names,
        filters=filters,
        skip=skip,
        limit=limit,
    )
    items = [
        get_orcid_record_by_id(
            item.orcid_identifier.path,
        )
        for item in response.result
    ]
    return PaginatedItemsContainer[OrcidRecord](items=items, total=response.num_found)
