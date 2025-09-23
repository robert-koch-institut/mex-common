from functools import lru_cache

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.logging import logger
from mex.common.types.identifier import MergedOrganizationIdentifier


@lru_cache(maxsize=1)
def get_wikidata_rki_organization() -> MergedOrganizationIdentifier | None:
    """Get the wikidata RKI organization stableTargetID.

    Returns:
        MergedOrganizationIdentifier for RKI or None if not found
    """
    connector = BackendApiConnector.get()
    response = connector.fetch_extracted_items(
        entity_type=["ExtractedOrganization"], query_string="RKI"
    )
    if (
        response.total > 0
        and type(response.items[0].stableTargetId) is MergedOrganizationIdentifier
    ):
        return response.items[0].stableTargetId
    logger.warning("StableTargetId for RKI organization not found in backend response.")
    return None
