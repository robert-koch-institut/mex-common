from collections.abc import Callable, Iterable

from mex.common.models import ExtractedData, ExtractedPrimarySource
from mex.common.types import MergedOrganizationIdentifier, MergedPrimarySourceIdentifier
from mex.common.wikidata.extract import search_organization_by_label
from mex.common.wikidata.transform import (
    transform_wikidata_organization_to_extracted_organization,
)


class _QueryCache(dict[str, MergedOrganizationIdentifier]):
    primary_source_and_load_function: tuple[
        MergedPrimarySourceIdentifier | None, int | None
    ] = (None, None)


_ORGANIZATION_BY_QUERY_CACHE: _QueryCache = _QueryCache()


def get_merged_organization_id_by_query_with_extract_transform_and_load(
    query_string: str,
    wikidata_primary_source: ExtractedPrimarySource,
    load_function: Callable[[Iterable[ExtractedData]], None],
) -> MergedOrganizationIdentifier | None:
    """Get stableTargetId of an organization matching the query string.

    Search wikidata for organization, transform it into an ExtractedOrganization and
      load it using the provided load_function.

    Args:
         query_string: query string to search in wikidata
         wikidata_primary_source: wikidata primary source
         load_function: function to pass ExtractedOrganization to

    Returns:
         ExtractedOrganization stableTargetId if one matching organization is found in
           Wikidata lookup.
         None if multiple matches / no organization is found
    """
    primary_source_and_load_function = (
        wikidata_primary_source.stableTargetId,
        id(load_function),
    )
    if (
        _ORGANIZATION_BY_QUERY_CACHE.primary_source_and_load_function
        != primary_source_and_load_function
    ):
        _ORGANIZATION_BY_QUERY_CACHE.primary_source_and_load_function = (
            primary_source_and_load_function
        )
        _ORGANIZATION_BY_QUERY_CACHE.clear()
    elif organization_id := _ORGANIZATION_BY_QUERY_CACHE.get(query_string):
        return organization_id

    found_organization = search_organization_by_label(query_string)

    if found_organization is None:
        return None

    extracted_organization = transform_wikidata_organization_to_extracted_organization(
        found_organization, wikidata_primary_source
    )

    if extracted_organization is None:
        return None

    load_function([extracted_organization])

    _ORGANIZATION_BY_QUERY_CACHE[query_string] = extracted_organization.stableTargetId

    return extracted_organization.stableTargetId
