import json
from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pytest
from pytest import MonkeyPatch

from mex.common.wikidata.connector import WikidataAPIConnector
from mex.common.wikidata.extract import (
    _get_wikidata_raw_item,
    get_wikidata_location,
    get_wikidata_locations,
    get_wikidata_organization,
)
from tests.wikidata.conftest import TESTDATA_DIR


@pytest.mark.integration
def test_get_wikidata_organization() -> None:
    expected = {
        "identifier": "Q679041",
        "labels": {
            "de": {"language": "de", "value": "Robert Koch-Institut"},
            "en": {"language": "en", "value": "Robert Koch Institute"},
            "multiple": {"language": "mul", "value": "Robert Koch-Institut"},
        },
        "claims": {
            "isni_id": [
                {"mainsnak": {"datavalue": {"value": {"text": "0000000109403744"}}}}
            ],
            "ror_id": [{"mainsnak": {"datavalue": {"value": {"text": "01k5qnb77"}}}}],
            "short_name": [
                {
                    "mainsnak": {
                        "datavalue": {"value": {"text": "RKI", "language": "en"}}
                    }
                },
                {
                    "mainsnak": {
                        "datavalue": {"value": {"text": "RKI", "language": "de"}}
                    }
                },
                {
                    "mainsnak": {
                        "datavalue": {"value": {"text": "IRK", "language": "fr"}}
                    }
                },
            ],
            "native_label": [
                {
                    "mainsnak": {
                        "datavalue": {
                            "value": {"text": "Robert Koch-Institut", "language": "de"}
                        }
                    }
                }
            ],
            "gepris_id": [{"mainsnak": {"datavalue": {"value": {"text": "10179"}}}}],
            "gnd_id": [{"mainsnak": {"datavalue": {"value": {"text": "17690-4"}}}}],
            "viaf_id": [{"mainsnak": {"datavalue": {"value": {"text": "123556639"}}}}],
        },
        "aliases": {
            "de": [
                {"language": "de", "value": "Robert Koch Institut"},
                {"language": "de", "value": "RKI"},
                {"language": "de", "value": "Robert-Koch-Institut"},
                {"language": "de", "value": "Kochsches Institut"},
                {
                    "language": "de",
                    "value": "Robert Koch-Institut",
                },
            ],
            "en": [
                {"language": "en", "value": "RKI"},
                {"language": "en", "value": "Robert Koch-Institut"},
                {"language": "en", "value": "Robert Koch Institut"},
                {"language": "en", "value": "Robert-Koch-Institut"},
                {
                    "language": "en",
                    "value": "Reich Institution for the Combating of Contagious Diseases",
                },
            ],
        },
    }
    organization_details = get_wikidata_organization("Q679041")

    assert organization_details.model_dump(exclude_none=True) == expected


@pytest.mark.usefixtures("mocked_session_wikidata_api")
def test_get_wikidata_organization_mocked(monkeypatch: MonkeyPatch) -> None:
    expected = {
        "identifier": "Q26678",
        "labels": {
            "de": {"language": "de", "value": "TEST"},
            "en": {"language": "en", "value": "TEST"},
            "multiple": None,
        },
        "claims": {
            "isni_id": [
                {
                    "mainsnak": {
                        "datavalue": {
                            "value": {"text": "0000 0001 2308 257X", "language": None}
                        }
                    }
                }
            ],
            "ror_id": [
                {
                    "mainsnak": {
                        "datavalue": {"value": {"text": "05vs9tj88", "language": None}}
                    }
                },
                {
                    "mainsnak": {
                        "datavalue": {"value": {"text": "044kkbh92", "language": None}}
                    }
                },
            ],
            "short_name": [
                {
                    "mainsnak": {
                        "datavalue": {"value": {"language": "de", "text": "BMW"}}
                    }
                }
            ],
            "native_label": [
                {
                    "mainsnak": {
                        "datavalue": {
                            "value": {"text": "test_native_name", "language": "de"}
                        }
                    }
                }
            ],
            "gepris_id": [],
            "gnd_id": [
                {
                    "mainsnak": {
                        "datavalue": {"value": {"text": "2005475-0", "language": None}}
                    }
                }
            ],
            "viaf_id": [
                {
                    "mainsnak": {
                        "datavalue": {"value": {"text": "129013645", "language": None}}
                    }
                }
            ],
        },
        "aliases": {
            "de": [
                {"language": "de", "value": "alias_de_1"},
                {"language": "de", "value": "alias_de_2"},
                {"language": "de", "value": "alias_de_3"},
            ],
            "en": [
                {"language": "en", "value": "alias_en_1"},
                {"language": "en", "value": "alias_en_2"},
                {"language": "en", "value": "alias_en_3"},
                {"language": "en", "value": "alias_en_4"},
            ],
        },
    }

    def mocked_item_details_response() -> Any:  # noqa: ANN401
        with (TESTDATA_DIR / "items_details.json").open(encoding="utf-8") as fh:
            data = json.load(fh)
            return data[0]

    monkeypatch.setattr(
        WikidataAPIConnector,
        "get_wikidata_item_details_by_id",
        lambda self, _: mocked_item_details_response(),
    )

    organization_details = get_wikidata_organization("Q26678")

    assert organization_details.model_dump() == expected


def test_get_wikidata_organization_malformed() -> None:
    with pytest.raises(ValueError, match="malformed wikidata url: foobar"):
        get_wikidata_organization("foobar")


@pytest.mark.parametrize(
    "item_id_or_url",
    [
        "Q183",
        "http://www.wikidata.org/entity/Q183",
        "https://www.wikidata.org/entity/Q183",
        "https://wikidata.org/entity/Q183",
        "www.wikidata.org/entity/Q183",
        "https://www.wikidata.org/entity/Q183/",
    ],
)
def test_get_wikidata_raw_item(
    monkeypatch: MonkeyPatch,
    item_id_or_url: str,
) -> None:
    connector = MagicMock(spec=WikidataAPIConnector)
    connector.get_wikidata_item_details_by_id.return_value = {"id": "Q183"}

    monkeypatch.setattr(WikidataAPIConnector, "get", lambda: connector)

    result = _get_wikidata_raw_item(item_id_or_url)

    assert result == {"id": "Q183"}
    connector.get_wikidata_item_details_by_id.assert_called_once_with("Q183")


@pytest.mark.parametrize(
    "item_id_or_url",
    [
        "",
        "Q",
        "q183",
        "Q183 extra",
        "https://www.wikidata.org/wiki/Q183",
        "https://example.com/entity/Q183",
        "https://www.wikidata.org/entity/Q183?foo=bar",
    ],
)
def test_get_wikidata_raw_item_malformed(
    monkeypatch: MonkeyPatch,
    item_id_or_url: str,
) -> None:
    connector = MagicMock(spec=WikidataAPIConnector)
    monkeypatch.setattr(WikidataAPIConnector, "get", lambda: connector)

    with pytest.raises(ValueError, match="malformed wikidata url"):
        _get_wikidata_raw_item(item_id_or_url)

    connector.get_wikidata_item_details_by_id.assert_not_called()


def test_get_wikidata_location(monkeypatch: MonkeyPatch) -> None:
    raw_location = {
        "id": "Q183",
        "labels": {
            "de": {"language": "de", "value": "Deutschland"},
            "en": {"language": "en", "value": "Germany"},
        },
        "claims": {
            "P1566": [
                {
                    "mainsnak": {
                        "datavalue": {
                            "value": "2921044",
                        }
                    }
                }
            ],
        },
        "aliases": {},
    }

    connector = MagicMock(spec=WikidataAPIConnector)
    connector.get_wikidata_item_details_by_id.return_value = raw_location
    monkeypatch.setattr(WikidataAPIConnector, "get", lambda: connector)

    location = get_wikidata_location("Q183")

    assert location.model_dump() == {
        "aliases": {"de": [], "en": []},
        "claims": {
            "geonames_id": [
                {
                    "mainsnak": {
                        "datavalue": {"value": {"language": None, "text": "2921044"}}
                    }
                }
            ]
        },
        "identifier": "Q183",
        "labels": {
            "de": {"language": "de", "value": "Deutschland"},
            "en": {"language": "en", "value": "Germany"},
            "multiple": None,
        },
    }
    connector.get_wikidata_item_details_by_id.assert_called_once_with("Q183")


def test_get_wikidata_location_is_cached(monkeypatch: MonkeyPatch) -> None:
    raw_location = {
        "id": "Q183",
        "labels": {},
        "claims": {},
        "aliases": {},
    }

    connector = MagicMock(spec=WikidataAPIConnector)
    connector.get_wikidata_item_details_by_id.return_value = raw_location
    monkeypatch.setattr(WikidataAPIConnector, "get", lambda: connector)

    first_result = get_wikidata_location("Q183")
    second_result = get_wikidata_location("Q183")

    assert first_result is second_result
    connector.get_wikidata_item_details_by_id.assert_called_once_with("Q183")


def test_get_wikidata_locations_uses_batches() -> None:
    item_ids = [f"Q{i}" for i in range(100, 220)]

    connector = Mock()

    def get_items(ids: tuple[str, ...]) -> dict[str, Any]:
        return {
            item_id: {
                "id": item_id,
                "labels": {},
                "claims": {},
                "aliases": {},
            }
            for item_id in ids
        }

    connector.get_wikidata_item_details_by_ids.side_effect = get_items

    with patch(
        "mex.common.wikidata.extract.WikidataAPIConnector.get",
        return_value=connector,
    ):
        locations = list(get_wikidata_locations(item_ids))

    assert len(locations) == 120
    assert connector.get_wikidata_item_details_by_ids.call_count == 3

    batches = [
        call.args[0]
        for call in connector.get_wikidata_item_details_by_ids.call_args_list
    ]

    assert [len(batch) for batch in batches] == [50, 50, 20]
    assert [location.identifier for location in locations] == item_ids
