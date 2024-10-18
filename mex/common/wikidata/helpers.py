from functools import cache

from mex.common.exceptions import MExError
from mex.common.models.organization import ExtractedOrganization
from mex.common.primary_source.helpers import get_extracted_primary_source_by_name
from mex.common.wikidata.extract import search_organization_by_label
from mex.common.wikidata.transform import (
    transform_wikidata_organization_to_extracted_organization,
)


@cache
def get_extracted_organization_from_wikidata(
    query_string: str,
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

    wikidata_primary_source = get_extracted_primary_source_by_name("wikidata")
    if not wikidata_primary_source:
        msg = "Primary source for wikidata not found"
        raise MExError(msg)

    return transform_wikidata_organization_to_extracted_organization(
        found_organization, wikidata_primary_source
    )
