import re
from functools import lru_cache

from mex.common.wikidata.connector import WikidataAPIConnector
from mex.common.wikidata.models import WikidataOrganization


@lru_cache(maxsize=128)
def get_wikidata_organization(item_id_or_url: str) -> WikidataOrganization:
    """Get a wikidata item details by its ID.

    Args:
        item_id_or_url: Wikidata item ID or full URL

    Raises:
        ValueError: when item_id_or_url does not match pattern

    Returns:
        WikidataOrganization object
    """
    if match := re.search(
        r"^(?:http?://)?(?:www\.)?(?:wikidata\.org/entity/)?([A-Z0-9]{2,64})/?$",
        item_id_or_url,
    ):
        item_id = match.group(1)
    else:
        msg = f"malformed wikidata url: {item_id_or_url}"
        raise ValueError(msg)
    connector = WikidataAPIConnector.get()
    item = connector.get_wikidata_item_details_by_id(item_id)
    return WikidataOrganization.model_validate(item)
