from collections.abc import Generator

from mex.common.exceptions import MExError
from mex.common.types import TextLanguage
from mex.common.wikidata.connector import (
    WikidataAPIConnector,
    WikidataQueryServiceConnector,
)
from mex.common.wikidata.models import WikidataOrganization


def search_organization_by_label(
    item_label: str,
    lang: TextLanguage = TextLanguage.EN,
) -> WikidataOrganization | None:
    """Search for an item in wikidata. Only organizations are searched.

    Args:
        item_label: Item title or label to be searched
        lang: lang in which item should be searched. Default: TextLanguage.EN

    Returns:
        WikidataOrganization if organization is found
        None if no organization is found
    """
    connector = WikidataQueryServiceConnector.get()
    item_label = item_label.replace('"', "")
    query_string = (
        "SELECT distinct ?item ?itemLabel ?itemDescription "
        "WHERE { "
        "SERVICE wikibase:mwapi { "
        'bd:serviceParam wikibase:api "EntitySearch" . '
        'bd:serviceParam wikibase:endpoint "www.wikidata.org" . '
        f'bd:serviceParam mwapi:search "{item_label}" . '
        f'bd:serviceParam mwapi:language "{lang}" . '
        "?item wikibase:apiOutputItem mwapi:item . "
        "?num wikibase:apiOrdinal true . "
        "} "
        "?item (wdt:P31/wdt:P8225*/wdt:P279*) wd:Q43229. "
        'SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en,de". } '  # noqa: E501
        "} "
        "ORDER BY ASC(?num) "
        "LIMIT 1 "
    )

    results = connector.get_data_by_query(query_string)

    if not results:
        return None

    try:
        wd_item_id = results[0]["item"]["value"].split("/")[-1]
    except KeyError as error:
        msg = f"KeyError: Error processing results for {item_label}"
        raise MExError(msg) from error

    return get_organization_details(wd_item_id)


def get_count_of_found_organizations_by_label(
    item_label: str,
    lang: TextLanguage,
) -> int:
    """Get total count of searched organizations in wikidata.

    Args:
        item_label: Item title or label to be counted
        lang: language of the label. Example: en, de

    Returns:
        count of found organizations
    """
    connector = WikidataQueryServiceConnector.get()
    item_label = item_label.replace('"', "")
    query_string = (
        "SELECT (COUNT(distinct ?item) AS ?count) "
        "WHERE { "
        "SERVICE wikibase:mwapi { "
        'bd:serviceParam wikibase:api "EntitySearch" . '
        'bd:serviceParam wikibase:endpoint "www.wikidata.org" . '
        f'bd:serviceParam mwapi:search "{item_label}" . '
        f'bd:serviceParam mwapi:language "{lang}" . '
        "?item wikibase:apiOutputItem mwapi:item . "
        "?num wikibase:apiOrdinal true . "
        "} "
        "?item (wdt:P31/wdt:P8225*/wdt:P279*) wd:Q43229. "
        'SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en,de". } '  # noqa: E501
        "} "
        "ORDER BY ASC(?num) "
    )

    result = connector.get_data_by_query(query_string)
    return int(result[0]["count"]["value"])


def search_organizations_by_label(
    item_label: str,
    offset: int,
    limit: int,
    lang: TextLanguage,
) -> Generator[WikidataOrganization, None, None]:
    """Search for organizations in wikidata.

    Args:
        item_label: Item title or label to be searched
        offset: start page number
        limit: end page number
        lang: language of the label. Example: en, de

    Returns:
        list of WikidataOrganization
    """
    connector = WikidataQueryServiceConnector.get()
    item_label = item_label.replace('"', "")
    query_string = (
        "SELECT distinct ?item ?itemLabel ?itemDescription "
        "WHERE { "
        "SERVICE wikibase:mwapi { "
        'bd:serviceParam wikibase:api "EntitySearch" . '
        'bd:serviceParam wikibase:endpoint "www.wikidata.org" . '
        f'bd:serviceParam mwapi:search "{item_label}" . '
        f'bd:serviceParam mwapi:language "{lang}" . '
        "?item wikibase:apiOutputItem mwapi:item . "
        "?num wikibase:apiOrdinal true . "
        "} "
        "?item (wdt:P31/wdt:P8225*/wdt:P279*) wd:Q43229. "
        'SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en,de". } '  # noqa: E501
        "} "
        "ORDER BY ASC(?num) "
        f"OFFSET {offset} "
        f"LIMIT {limit} "
    )

    results = connector.get_data_by_query(query_string)
    for item in results:
        try:
            wd_item_id = item["item"]["value"].split("/")[-1]
        except KeyError as error:
            msg = f"KeyError: Error processing results for {item_label}"
            raise MExError(msg) from error
        except IndexError as error:
            msg = f"IndexError: Error processing results for {item_label}"
            raise MExError(msg) from error

        yield get_organization_details(wd_item_id)


def get_organization_details(item_id: str) -> WikidataOrganization:
    """Get a wikidata item details by its ID.

    Args:
        item_id: Item ID to get info

    Returns:
        WikidataOrganization object
    """
    connector = WikidataAPIConnector.get()

    item = connector.get_wikidata_item_details_by_id(item_id)

    return WikidataOrganization.model_validate(item)
