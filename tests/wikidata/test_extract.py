import json

import pytest
from pytest import MonkeyPatch

from mex.common.exceptions import MExError
from mex.common.wikidata.connector import WikidataConnector
from mex.common.wikidata.extract import (
    get_organization_details,
    search_organization_by_label,
)
from tests.wikidata.conftest import TESTDATA_DIR


@pytest.mark.integration
def test_search_organization_by_label() -> None:
    """Test organization search in wikidata."""
    expected = "Q26678"

    search_results = list(search_organization_by_label(item_label="BMW"))

    assert len(search_results) == 2
    assert search_results[0].identifier == expected


@pytest.mark.usefixtures("mocked_session")
def test_search_organization_by_label_mocked_error(monkeypatch: MonkeyPatch) -> None:
    """Test(mock) organization search in wikidata exceptions."""
    expected_query_response = [
        {
            "item": {"foo": "uri", "bar": "http://www.wikidata.org/entity/Q26678"},
        },
        {
            "item": {"foo": "uri", "bar": "http://www.wikidata.org/entity/Q821937"},
        },
    ]

    def mocked_query_response():
        return expected_query_response

    monkeypatch.setattr(
        WikidataConnector,
        "get_data_by_query",
        lambda self, _: mocked_query_response(),
    )

    with pytest.raises(MExError) as exc:
        _ = list(search_organization_by_label(item_label="BMW"))


@pytest.mark.usefixtures("mocked_session")
def test_search_organization_by_label_mocked(monkeypatch: MonkeyPatch) -> None:
    """Test(mock) organization search in wikidata."""
    expected_item_details_response = {
        "identifier": "Q26678",
        "labels": {
            "de": {"language": "de", "value": "TEST"},
            "en": {"language": "en", "value": "TEST"},
        },
        "claims": {
            "website": [
                {
                    "mainsnak": {
                        "datavalue": {
                            "value": {
                                "text": "https://www.testgroup.com/",
                                "language": None,
                            }
                        }
                    }
                },
                {
                    "mainsnak": {
                        "datavalue": {
                            "value": {"text": "https://www.test.com", "language": None}
                        }
                    }
                },
            ],
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
            "official_name": [
                {
                    "mainsnak": {
                        "datavalue": {
                            "value": {
                                "text": "Bayerische Motoren Werke AG",
                                "language": "de",
                            }
                        }
                    }
                }
            ],
            "short_name": [],
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

    expected_query_response = [
        {
            "item": {"type": "uri", "value": "http://www.wikidata.org/entity/Q26678"},
        },
        {
            "item": {"type": "uri", "value": "http://www.wikidata.org/entity/Q821937"},
        },
    ]

    def mocked_query_response():
        return expected_query_response

    monkeypatch.setattr(
        WikidataConnector,
        "get_data_by_query",
        lambda self, _: mocked_query_response(),
    )

    def mocked_item_details_response():
        with open(TESTDATA_DIR / "items_details.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data[0]

    monkeypatch.setattr(
        WikidataConnector,
        "get_wikidata_item_details_by_id",
        lambda self, _: mocked_item_details_response(),
    )

    search_results = list(search_organization_by_label(item_label="TEST"))

    assert len(search_results) == 2
    assert search_results[0].dict() == expected_item_details_response


@pytest.mark.integration
def test_get_organization_details() -> None:
    """Test organization details fetching from wikidata."""
    expected = {
        "identifier": "Q679041",
        "labels": {
            "de": {"language": "de", "value": "Robert Koch-Institut"},
            "en": {"language": "en", "value": "Robert Koch Institute"},
        },
        "claims": {
            "website": [
                {"mainsnak": {"datavalue": {"value": {"text": "https://www.rki.de/"}}}},
                {
                    "mainsnak": {
                        "datavalue": {
                            "value": {
                                "text": "https://www.rki.de/DE/Home/homepage_node.html"
                            }
                        }
                    }
                },
                {
                    "mainsnak": {
                        "datavalue": {
                            "value": {
                                "text": "https://www.rki.de/EN/Home/homepage_node.html"
                            }
                        }
                    }
                },
            ],
            "isni_id": [
                {"mainsnak": {"datavalue": {"value": {"text": "0000 0001 0940 3744"}}}}
            ],
            "ror_id": [{"mainsnak": {"datavalue": {"value": {"text": "01k5qnb77"}}}}],
            "official_name": [
                {
                    "mainsnak": {
                        "datavalue": {
                            "value": {"text": "Robert-Koch-Institut", "language": "de"}
                        }
                    }
                }
            ],
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
    organization_details = get_organization_details(item_id="Q679041")

    assert organization_details.dict(exclude_none=True) == expected


@pytest.mark.usefixtures("mocked_session")
def test_get_organization_details_mocked(monkeypatch: MonkeyPatch) -> None:
    """Test(mock) organization details fetching from wikidata."""
    expected = {
        "identifier": "Q26678",
        "labels": {
            "de": {"language": "de", "value": "TEST"},
            "en": {"language": "en", "value": "TEST"},
        },
        "claims": {
            "website": [
                {
                    "mainsnak": {
                        "datavalue": {
                            "value": {
                                "text": "https://www.testgroup.com/",
                                "language": None,
                            }
                        }
                    }
                },
                {
                    "mainsnak": {
                        "datavalue": {
                            "value": {"text": "https://www.test.com", "language": None}
                        }
                    }
                },
            ],
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
            "official_name": [
                {
                    "mainsnak": {
                        "datavalue": {
                            "value": {
                                "text": "Bayerische Motoren Werke AG",
                                "language": "de",
                            }
                        }
                    }
                }
            ],
            "short_name": [],
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

    def mocked_item_details_response():
        with open(TESTDATA_DIR / "items_details.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data[0]

    monkeypatch.setattr(
        WikidataConnector,
        "get_wikidata_item_details_by_id",
        lambda self, _: mocked_item_details_response(),
    )

    organization_details = get_organization_details(item_id="Q26678")

    assert organization_details.dict() == expected
