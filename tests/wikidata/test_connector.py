from unittest.mock import MagicMock, Mock

import pytest
import requests

from mex.common.wikidata.connector import WikidataAPIConnector


@pytest.mark.integration
def test_get_wikidata_item_details_by_id() -> None:
    """Test if items details can be fetched by its ID."""
    connector = WikidataAPIConnector.get()
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
    mocked_session_wikidata_api: MagicMock,
) -> None:
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
                        "value": "German automobile manufacturer, and conglomerate",
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

    mocked_session_wikidata_api.request = MagicMock(
        return_value=Mock(
            spec=requests.Response,
            json=MagicMock(return_value={"entities": {"Q26678": expected}}),
            status_code=200,
        )
    )

    connector = WikidataAPIConnector.get()

    response = connector.get_wikidata_item_details_by_id("Q26678")

    assert response == expected
