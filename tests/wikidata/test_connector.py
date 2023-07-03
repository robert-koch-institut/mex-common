from unittest.mock import MagicMock, Mock

import pytest
import requests

from mex.common.exceptions import MExError
from mex.common.wikidata.connector import WikidataConnector


def test_initialization_mocked_server_error(
    mocked_session: MagicMock,
) -> None:
    """Test if server is intialized and availability throws an error."""
    connector = WikidataConnector.get()
    mocked_session.get.return_value = Mock(
        spec=requests.Response, ok=0, status_code=500, text="Internal Server Error"
    )
    with pytest.raises(MExError, match="Internal Server Error"):
        connector._check_availability()


def test_initialization_mocked_server(
    mocked_session: MagicMock,
) -> None:
    """Test if server is intialized and available."""
    mocked_session.get.return_value = Mock(
        spec=requests.Response, ok=1, status_code=200
    )
    connector = WikidataConnector.get()
    assert connector._check_availability() == None


@pytest.mark.integration
def test_get_data_by_query() -> None:
    """Test if items can be searched providing a label."""
    expected = [
        {
            "item": {"type": "uri", "value": "http://www.wikidata.org/entity/Q26678"},
            "itemDescription": {
                "type": "literal",
                "value": "German automotive manufacturer, and " "conglomerate",
                "xml:lang": "en",
            },
            "itemLabel": {"type": "literal", "value": "BMW", "xml:lang": "en"},
        },
        {
            "item": {"type": "uri", "value": "http://www.wikidata.org/entity/Q821937"},
            "itemDescription": {
                "type": "literal",
                "value": "rap group from Berlin",
                "xml:lang": "en",
            },
            "itemLabel": {
                "type": "literal",
                "value": "Berlins Most Wanted",
                "xml:lang": "en",
            },
        },
    ]
    query_string = (
        "SELECT distinct ?item ?itemLabel ?itemDescription "
        "WHERE{"
        "?item (wdt:P31/wdt:P8225*/wdt:P279*) wd:Q43229."
        '?item ?label "BMW"@en.'
        "?article schema:about ?item ."
        'SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }'
        "}"
    )
    connector = WikidataConnector.get()

    response = connector.get_data_by_query(query_string)

    assert response == expected


def test_get_data_by_query_mocked(mocked_session: MagicMock) -> None:
    """Test(mock) if items can be searched providing a label."""
    expected = [
        {
            "item": {"type": "uri", "value": "http://www.wikidata.org/entity/Q26678"},
            "itemDescription": {
                "type": "literal",
                "value": "German automotive manufacturer, and " "conglomerate",
                "xml:lang": "en",
            },
            "itemLabel": {"type": "literal", "value": "BMW", "xml:lang": "en"},
        },
    ]

    mocked_session.get = MagicMock(
        return_value=Mock(
            spec=requests.Response,
            json=MagicMock(return_value={"results": {"bindings": expected}}),
        )
    )

    connector = WikidataConnector.get()

    response = connector.get_data_by_query("SELECT foo;")

    assert response == expected


@pytest.mark.integration
def test_get_wikidata_item_details_by_id() -> None:
    """Test if items details can be fetched by its ID."""
    connector = WikidataConnector.get()
    response = connector.get_wikidata_item_details_by_id("Q26678")

    assert list(response.keys()) == [
        "pageid",
        "ns",
        "title",
        "lastrevid",
        "modified",
        "type",
        "id",
        "labels",
        "descriptions",
        "aliases",
        "claims",
        "sitelinks",
    ]
    assert response.get("title") == "Q26678"
    assert response.get("type") == "item"


def test_get_wikidata_items_details_by_id_mocked(
    mocked_session: MagicMock,
) -> None:
    """Test(mock) if items details can be fetched by its ID."""
    expected = {
        "entities": {
            "Q26678": {
                "pageid": 30097,
                "ns": 0,
                "title": "Q26678",
                "lastrevid": 1817510361,
                "modified": "2023-01-23T09:14:17Z",
                "type": "item",
                "id": "Q26678",
                "descriptions": {
                    "en": {
                        "language": "en",
                        "value": "German automotive manufacturer, and conglomerate",
                    },
                    "de": {
                        "language": "de",
                        "value": "deutscher Automobil- und Motorradhersteller",
                    },
                },
            }
        },
        "success": 1,
    }

    mocked_session.get = MagicMock(
        return_value=Mock(
            spec=requests.Response,
            json=MagicMock(return_value={"entities": {"Q26678": expected}}),
        )
    )

    connector = WikidataConnector.get()

    response = connector.get_wikidata_item_details_by_id("Q26678")

    assert response == expected
