import json
from typing import Any

import pytest
from pytest import MonkeyPatch

from mex.common.exceptions import MExError
from mex.common.types import TextLanguage
from mex.common.wikidata.connector import (
    WikidataAPIConnector,
    WikidataQueryServiceConnector,
)
from mex.common.wikidata.extract import (
    get_count_of_found_organizations_by_label,
    get_organization_details,
    search_organization_by_label,
    search_organizations_by_label,
)
from tests.wikidata.conftest import TESTDATA_DIR


@pytest.mark.integration
def test_search_organization_by_label() -> None:
    expected = "Q679041"

    search_result = search_organization_by_label(item_label='Robert Koch Institute"')

    assert search_result, f"No organizations were found for id: {expected}"
    assert search_result.identifier == expected


@pytest.mark.integration
def test_search_organizations_by_label() -> None:
    search_result = list(
        search_organizations_by_label(
            item_label='Robert Koch Institute"',
            offset=0,
            limit=10,
            lang=TextLanguage.EN,
        )
    )
    identifier = "Q679041"
    labels = {
        "de": {"language": "de", "value": "Robert Koch-Institut"},
        "en": {"language": "en", "value": "Robert Koch Institute"},
    }

    assert len(search_result) == 3
    assert search_result[0].identifier == identifier
    assert search_result[0].labels.model_dump() == labels


@pytest.mark.integration
def test_get_count_of_found_organizations_by_label() -> None:
    total_found_orgs = get_count_of_found_organizations_by_label(
        item_label='Robert Koch Institute"',
        lang=TextLanguage.EN,
    )

    assert total_found_orgs == 3


@pytest.mark.integration
def test_search_organization_by_label_for_none() -> None:
    """Test if None is returned when multiple organizations are found."""
    search_result = search_organization_by_label(
        item_label="Blah-test128%3h2 .1 12 bus"
    )
    assert search_result is None


@pytest.mark.usefixtures("mocked_session_wikidata_query_service")
def test_search_organization_by_label_mocked_error(monkeypatch: MonkeyPatch) -> None:
    """Test(mock) organization search in wikidata exceptions."""
    expected_query_response = [
        {
            "item": {"foo": "uri", "bar": "http://www.wikidata.org/entity/Q26678"},
        },
    ]

    def mocked_query_response() -> list[dict[str, dict[str, str]]]:
        return expected_query_response

    monkeypatch.setattr(
        WikidataQueryServiceConnector,
        "get_data_by_query",
        lambda self, _: mocked_query_response(),
    )

    with pytest.raises(MExError):
        _ = search_organization_by_label(item_label="BMW")


@pytest.mark.usefixtures(
    "mocked_session_wikidata_query_service", "mocked_session_wikidata_api"
)
def test_search_organization_by_label_mocked(monkeypatch: MonkeyPatch) -> None:
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
    ]

    def mocked_query_response() -> list[dict[str, dict[str, str]]]:
        return expected_query_response

    monkeypatch.setattr(
        WikidataQueryServiceConnector,
        "get_data_by_query",
        lambda self, _: mocked_query_response(),
    )

    def mocked_item_details_response() -> Any:
        with open(TESTDATA_DIR / "items_details.json", encoding="utf-8") as f:
            data = json.load(f)
            return data[0]

    monkeypatch.setattr(
        WikidataAPIConnector,
        "get_wikidata_item_details_by_id",
        lambda self, _: mocked_item_details_response(),
    )

    search_result = search_organization_by_label(item_label="TEST")

    assert search_result
    assert search_result.model_dump() == expected_item_details_response


@pytest.mark.usefixtures(
    "mocked_session_wikidata_query_service", "mocked_session_wikidata_api"
)
def test_search_organization_by_label_for_none_mocked(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(
        WikidataQueryServiceConnector,
        "get_data_by_query",
        lambda self, _: [],
    )

    def mocked_item_details_response() -> Any:
        with open(TESTDATA_DIR / "items_details.json", encoding="utf-8") as f:
            data = json.load(f)
            return data[0]

    monkeypatch.setattr(
        WikidataAPIConnector,
        "get_wikidata_item_details_by_id",
        lambda self, _: mocked_item_details_response(),
    )

    search_result = search_organization_by_label(item_label="TEST")

    assert search_result is None


@pytest.mark.usefixtures(
    "mocked_session_wikidata_query_service", "mocked_session_wikidata_api"
)
def test_search_organizations_by_label_mocked(monkeypatch: MonkeyPatch) -> None:
    expected_query_response = [
        {"item": {"type": "uri", "value": "http://www.wikidata.org/entity/Q26678"}},
        {"item": {"type": "uri", "value": "http://www.wikidata.org/entity/Q821937"}},
        {"item": {"type": "uri", "value": "http://www.wikidata.org/entity/Q125698083"}},
    ]

    expected_organization = {
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

    def mocked_query_response() -> list[dict[str, dict[str, str]]]:
        return expected_query_response

    monkeypatch.setattr(
        WikidataQueryServiceConnector,
        "get_data_by_query",
        lambda self, _: mocked_query_response(),
    )

    def mocked_item_details_response() -> Any:
        with open(TESTDATA_DIR / "items_details.json", encoding="utf-8") as f:
            data = json.load(f)
            return data[0]

    monkeypatch.setattr(
        WikidataAPIConnector,
        "get_wikidata_item_details_by_id",
        lambda self, _: mocked_item_details_response(),
    )

    search_result = list(
        search_organizations_by_label(
            item_label="TEST", offset=0, limit=10, lang=TextLanguage.EN
        )
    )

    assert len(search_result) == 3
    assert search_result[0].model_dump() == expected_organization


@pytest.mark.usefixtures(
    "mocked_session_wikidata_query_service", "mocked_session_wikidata_api"
)
def test_get_count_of_found_organizations_by_label_mocked(
    monkeypatch: MonkeyPatch,
) -> None:
    expected_query_response = [
        {
            "count": {
                "datatype": "http://www.w3.org/2001/XMLSchema#integer",
                "type": "literal",
                "value": "3",
            }
        }
    ]

    def mocked_query_response() -> list[dict[str, dict[str, str]]]:
        return expected_query_response

    monkeypatch.setattr(
        WikidataQueryServiceConnector,
        "get_data_by_query",
        lambda self, _: mocked_query_response(),
    )

    search_result = get_count_of_found_organizations_by_label(
        item_label="TEST", lang=TextLanguage.EN
    )

    assert search_result == 3


@pytest.mark.integration
def test_get_organization_details() -> None:
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
                {"mainsnak": {"datavalue": {"value": {"text": "0000000109403744"}}}}
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

    assert organization_details.model_dump(exclude_none=True) == expected


@pytest.mark.usefixtures(
    "mocked_session_wikidata_query_service", "mocked_session_wikidata_api"
)
def test_get_organization_details_mocked(monkeypatch: MonkeyPatch) -> None:
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

    def mocked_item_details_response() -> Any:
        with open(TESTDATA_DIR / "items_details.json", encoding="utf-8") as f:
            data = json.load(f)
            return data[0]

    monkeypatch.setattr(
        WikidataAPIConnector,
        "get_wikidata_item_details_by_id",
        lambda self, _: mocked_item_details_response(),
    )

    organization_details = get_organization_details(item_id="Q26678")

    assert organization_details.model_dump() == expected
