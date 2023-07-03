from typing import Generator

from mex.common.exceptions import MExError
from mex.common.logging import watch
from mex.common.public_api.connector import PublicApiConnector
from mex.common.public_api.models import PublicApiItemWithoutValues


@watch
def extract_mex_person_items() -> Generator[PublicApiItemWithoutValues, None, None]:
    """Extract all person items from the Public Api."""
    connector = PublicApiConnector.get()
    offset_item_id = None
    for _ in range(100):
        response = connector.get_all_items(offset_item_id=offset_item_id)
        offset_item_id = response.next
        for item in response.items:
            if item.entityType in ["Person", "ExtractedPerson"]:
                yield item
        if not offset_item_id:
            break
    else:
        raise MExError("Exceeded maximum fetchable amount of persons.")
