import json
from typing import Any

import pytest
from pytest import MonkeyPatch

from mex.common.wikidata.connector import WikidataAPIConnector
from mex.common.wikidata.extract import get_wikidata_organization
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
