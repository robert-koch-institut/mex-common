from functools import cache

from mex.common.models import ExtractedOrganization, ExtractedPrimarySource
from mex.common.wikidata.extract import search_organization_by_label
from mex.common.wikidata.transform import (
    transform_wikidata_organization_to_extracted_organization,
)


@cache
def get_extracted_organization_from_wikidata(
    query_string: str,
    wikidata_primary_source: ExtractedPrimarySource,
) -> ExtractedOrganization | None:
    """Get extracted organization matching the query string.

    Search wikidata for organization and transform it into an ExtractedOrganization.

    Args:
        query_string: query string to search in wikidata
        wikidata_primary_source: wikidata primary source

    Returns:
        ExtractedOrganization if one matching organization is found in
           Wikidata lookup.
        None if multiple matches / no organization is found.
    """
    found_organization = search_organization_by_label(query_string)

    if found_organization is None:
        return None

    extracted_organization = transform_wikidata_organization_to_extracted_organization(
        found_organization, wikidata_primary_source
    )

    if extracted_organization is None:
        return None

    return extracted_organization
