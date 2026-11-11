import re
from collections.abc import Iterator
from functools import lru_cache

from mex.common.logging import logger
from mex.common.wikidata.connector import WIKIDATA_MAX_BATCH_SIZE, WikidataAPIConnector
from mex.common.wikidata.models import WikidataLocation, WikidataOrganization

_WIKIDATA_QID = r"Q[1-9][0-9]{2,64}"

_WIKIDATA_QID_PATTERN = re.compile(rf"({_WIKIDATA_QID})")
_WIKIDATA_QID_OR_URL_PATTERN = re.compile(
    rf"(?:https?://(?:www\.)?wikidata\.org/entity/)?({_WIKIDATA_QID})/?"
)


def _get_wikidata_raw_item(item_id_or_url: str) -> dict[str, str]:
    """Get a wikidata item as dictionary from wikidata by its id or url.

    Args:
        item_id_or_url: Wikidata item ID or full URL

    Raises:
        ValueError: when item_id_or_url does not match pattern

    Returns:
        wikidata response dict
    """
    item_id = _validate_wikidata_id(item_id_or_url, _WIKIDATA_QID_OR_URL_PATTERN)
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


def get_wikidata_locations(
    item_ids: list[str],
    batch_size: int = WIKIDATA_MAX_BATCH_SIZE,
) -> Iterator[WikidataLocation]:
    """Get Wikidata locations using batched API requests."""
    if not 1 <= batch_size <= WIKIDATA_MAX_BATCH_SIZE:
        msg = f"batch_size must be between 1 and {WIKIDATA_MAX_BATCH_SIZE}."
        raise ValueError(msg)

    connector = WikidataAPIConnector.get()

    validated_ids = [
        _validate_wikidata_id(item_id, _WIKIDATA_QID_PATTERN) for item_id in item_ids
    ]

    for batch_start in range(0, len(validated_ids), batch_size):
        batch = validated_ids[batch_start : (batch_start + batch_size)]
        if batch_start % 1000 == 0:
            logger.info(
                f"getting wikidata locations for {batch_start}/{len(validated_ids)} "
                f"items."
            )
        entities = connector.get_wikidata_item_details_by_ids(batch)

        for item_id in batch:
            yield WikidataLocation.model_validate(entities[item_id])


def _validate_wikidata_id(id_str: str, accepted_pattern: re.Pattern[str]) -> str:
    """Validate a Wikidata identifier and return its Q-ID."""
    if not (match := accepted_pattern.fullmatch(id_str)):
        msg = f"Malformed Wikidata ID or URL: {id_str}"
        raise ValueError(msg)
    return match.group(1)
