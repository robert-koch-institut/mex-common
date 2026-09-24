import re
from functools import lru_cache

from mex.common.wikidata.connector import WikidataAPIConnector
from mex.common.wikidata.models import WikidataLocation, WikidataOrganization

_WIKIDATA_ID_PATTERN = re.compile(
    r"(?:(?:https?://)?(?:www\.)?wikidata\.org/entity/)?"
    r"([A-Z0-9]{2,64})/?"
)


def _get_wikidata_raw_item(item_id_or_url: str) -> dict[str, str]:
    """Get a wikidata item details by its ID.

    Args:
        item_id_or_url: Wikidata item ID or full URL

    Raises:
        ValueError: when item_id_or_url does not match pattern

    Returns:
        wikidata response dict
    """
    if not (match := _WIKIDATA_ID_PATTERN.fullmatch(item_id_or_url)):
        msg = f"malformed wikidata url: {item_id_or_url}"
        raise ValueError(msg)
    item_id = match.group(1)
    connector = WikidataAPIConnector.get()
    return connector.get_wikidata_item_details_by_id(item_id)


@lru_cache(maxsize=128)
def get_wikidata_organization(item_id_or_url: str) -> WikidataOrganization:
    """Get wikidata item details by its ID and validate WikidataOrganization model.

    Args:
        item_id_or_url: Wikidata item ID or full URL

    Returns:
        WikidataOrganization object
    """
    item = _get_wikidata_raw_item(item_id_or_url)
    return WikidataOrganization.model_validate(item)


@lru_cache(maxsize=128)
def get_wikidata_location(item_id_or_url: str) -> WikidataLocation:
    """Get wikidata item details by its ID and validate WikidataLocation model.

    Args:
        item_id_or_url: Wikidata item ID or full URL

    Returns:
        WikidataLocation object
    """
    item = _get_wikidata_raw_item(item_id_or_url)
    return WikidataLocation.model_validate(item)
