from mex.common.exceptions import MExError
from mex.common.wikidata.connector import (
    WikidataAPIConnector,
    WikidataQueryServiceConnector,
)
from mex.common.wikidata.models.organization import WikidataOrganization


def search_organization_by_label(
    item_label: str,
) -> WikidataOrganization | None:
    """Search for an item in wikidata. Only organizations are fetched.

    Args:
        item_label: Item title or label to be searched

    Returns:
        WikidataOrganization if only one organization is found
        None if no or multiple organizations are found
    """
    connector = WikidataQueryServiceConnector.get()
    item_label = item_label.replace('"', "")
    query_string = (
        "SELECT distinct ?item ?itemLabel ?itemDescription "
        "WHERE{"
        "?item (wdt:P31/wdt:P8225*/wdt:P279*) wd:Q43229."
        f'?item ?label "{item_label}"@en.'
        "?article schema:about ?item ."
        'SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }'
        "}"
    )

    results = connector.get_data_by_query(query_string)
    if len(results) > 1:
        return None

    try:
        wd_item_id = results[0]["item"]["value"].split("/")[-1]
    except KeyError as exc:
        raise MExError(f"KeyError: Error processing results for {item_label}") from exc
    except IndexError as exc:
        raise MExError(
            f"IndexError: Error processing results for {item_label}"
        ) from exc

    return _get_organization_details(wd_item_id)


def _get_organization_details(item_id: str) -> WikidataOrganization:
    """Get a wikidata item details by its ID.

    Args:
        item_id: Item ID to get info

    Returns:
        WikidataOrganization object
    """
    connector = WikidataAPIConnector.get()

    item = connector.get_wikidata_item_details_by_id(item_id)

    return WikidataOrganization.model_validate(item)
