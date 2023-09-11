import json
from operator import attrgetter, itemgetter

from mex.common.models import ExtractedPrimarySource
from mex.common.testing import Joker
from mex.common.types import Text, TextLanguage
from mex.common.wikidata.models.organization import (
    Aliases,
    Claim,
    Labels,
    WikidataOrganization,
)
from mex.common.wikidata.transform import (
    get_alternative_names,
    get_clean_labels,
    get_clean_short_names,
    transform_wikidata_organizations_to_extracted_organizations,
)
from tests.wikidata.conftest import TESTDATA_DIR


def test_transform_wikidata_organization_to_organization(
    extracted_primary_sources: dict[str, ExtractedPrimarySource],
) -> None:
    """Test wikidata organization transformation to extracted organization."""
    expected = {
        "identifier": Joker(),
        "hadPrimarySource": Joker(),
        "identifierInPrimarySource": "Q26678",
        "stableTargetId": Joker(),
        "alternativeName": [
            {"value": "alias_en_3", "language": None},
            {"value": "alias_de_2", "language": None},
            {"value": "alias_en_1", "language": None},
            {"value": "alias_en_2", "language": None},
            {"value": "alias_de_1", "language": None},
            {"value": "test_native_name", "language": TextLanguage.DE},
            {"value": "alias_de_3", "language": None},
            {"value": "alias_en_4", "language": None},
        ],
        "geprisId": [],
        "gndId": ["https://d-nb.info/gnd/2005475-0"],
        "isniId": ["https://isni.org/isni/000000012308257X"],
        "officialName": [
            Text(value="TEST", language=TextLanguage.EN),
            Text(value="TEST", language=TextLanguage.DE),
        ],
        "rorId": ["https://ror.org/05vs9tj88", "https://ror.org/044kkbh92"],
        "shortName": [],
        "viafId": ["https://viaf.org/viaf/129013645"],
        "wikidataId": "https://www.wikidata.org/entity/Q26678",
    }

    with open(TESTDATA_DIR / "items_details.json", "r", encoding="utf-8") as f:
        wikidata_organizations = [
            WikidataOrganization.parse_obj(item) for item in json.load(f)
        ]

    extracted_organizations = list(
        transform_wikidata_organizations_to_extracted_organizations(
            wikidata_organizations, extracted_primary_sources["wikidata"]
        )
    )

    assert len(extracted_organizations) == 1

    assert sorted(
        extracted_organizations[0].dict()["alternativeName"], key=itemgetter("value")
    ) == sorted(expected["alternativeName"], key=itemgetter("value"))

    assert (
        extracted_organizations[0].dict()["identifierInPrimarySource"]
        == expected["identifierInPrimarySource"]
    )
    assert extracted_organizations[0].dict()["rorId"] == expected["rorId"]
    assert extracted_organizations[0].dict()["wikidataId"] == expected["wikidataId"]
    assert extracted_organizations[0].dict()["gndId"] == expected["gndId"]
    assert extracted_organizations[0].dict()["isniId"] == expected["isniId"]
    assert extracted_organizations[0].dict()["viafId"] == expected["viafId"]


def test_get_alternative_names() -> None:
    """Test if all the alternative names are being transformed."""
    raw_aliases = Aliases.parse_obj(
        {
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
        }
    )

    raw_native_labels = [
        Claim.parse_obj(
            {
                "mainsnak": {
                    "datavalue": {
                        "value": {"language": "de", "text": "test_native_name"}
                    }
                }
            }
        )
    ]
    expected = [
        Text(value="alias_de_1", language=None),
        Text(value="alias_de_2", language=None),
        Text(value="alias_de_3", language=None),
        Text(value="alias_en_1", language=None),
        Text(value="alias_en_2", language=None),
        Text(value="alias_en_3", language=None),
        Text(value="alias_en_4", language=None),
        Text(value="test_native_name", language=TextLanguage.DE),
    ]

    alternative_names = get_alternative_names(raw_native_labels, raw_aliases)

    assert sorted(alternative_names, key=attrgetter("value")) == sorted(
        expected, key=attrgetter("value")
    )


def test_get_clean_short_names() -> None:
    """Test if clean acronyms are being returned as expected."""
    expected = [
        Text(value="ABCEN", language=TextLanguage.EN),
        Text(value="ABCDE", language=TextLanguage.DE),
    ]
    short_names = [
        {
            "mainsnak": {
                "snaktype": "value",
                "property": "P1813",
                "hash": "6cd9c230521797cef15c529e5bb006a0c51e801e",
                "datavalue": {
                    "value": {"text": "ABCEN", "language": "en"},
                    "type": "monolingualtext",
                },
                "datatype": "monolingualtext",
            },
            "type": "statement",
            "id": "Q679041$AAE01E9A-03EA-424E-A51A-222A4858C4DD",
            "rank": "normal",
        },
        {
            "mainsnak": {
                "snaktype": "value",
                "property": "P1813",
                "hash": "03dcb3e47ca24e8ab90a1b11eb7602ceca2d07ad",
                "datavalue": {
                    "value": {"text": "ABCDE", "language": "de"},
                    "type": "monolingualtext",
                },
                "datatype": "monolingualtext",
            },
        },
    ]

    for short_name in short_names:
        Claim.parse_obj(short_name)

    clean_short_names = get_clean_short_names(
        [Claim.parse_obj(acronym) for acronym in short_names]
    )

    assert sorted(clean_short_names, key=attrgetter("value")) == sorted(
        expected, key=attrgetter("value")
    )


def test_get_clean_labels() -> None:
    """Test if clean labels are being returned as expected."""
    expected = [
        Text(value="Test Label 1 EN", language=TextLanguage.EN),
        Text(value="Test Label 1 DE", language=TextLanguage.DE),
    ]
    raw_labels = {
        "de": {"language": "de", "value": "Test Label 1 DE"},
        "en": {"language": "en", "value": "Test Label 1 EN"},
    }

    clean_labels = get_clean_labels(Labels.parse_obj(raw_labels))

    assert clean_labels == expected
