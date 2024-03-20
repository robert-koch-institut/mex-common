import requests

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
        Generator for WikidataOrganization items
    """
    connector = WikidataQueryServiceConnector.get()
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
    resolved_organizations = []

    for item in results:
        try:
            wd_item_id = item["item"]["value"].split("/")[-1]
        except requests.exceptions.HTTPError as exc:
            raise MExError(
                f"HTTPError: Error processing results for {item_label}"
            ) from exc
        except requests.exceptions.RetryError as exc:
            raise MExError(
                f"RetryError: Max retries exceeded processing results for {item_label}"
            ) from exc
        except KeyError as exc:
            raise MExError(
                f"KeyError: Error processing results for {item_label}"
            ) from exc
        except IndexError as exc:
            raise MExError(
                f"IndexError: Error processing results for {item_label}"
            ) from exc

        resolved_organizations.append(_get_organization_details(wd_item_id))

    if len(resolved_organizations) == 1:
        return resolved_organizations[0]

    return None


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
