import json
from operator import attrgetter, itemgetter
from typing import Any, cast

import pytest

from mex.common.testing import Joker
from mex.common.types import MergedPrimarySourceIdentifier, Text, TextLanguage
from mex.common.wikidata.models import (
    Aliases,
    Claim,
    Label,
    Labels,
    WikidataLocation,
    WikidataOrganization,
)
from mex.common.wikidata.transform import (
    _get_alternative_names,
    _get_clean_short_names,
    _get_preferred_label,
    _get_wikidata_entity_uri,
    transform_wikidata_location_to_extracted_location,
    transform_wikidata_locations_to_extracted_locations,
    transform_wikidata_organization_to_extracted_organization,
    transform_wikidata_organizations_to_extracted_organizations,
)
from tests.wikidata.conftest import TESTDATA_DIR


def test_transform_wikidata_organization_to_extracted_organization(
    extracted_primary_source_ids: dict[str, MergedPrimarySourceIdentifier],
) -> None:
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
        "wikidataId": ["http://www.wikidata.org/entity/Q26678"],
    }
    with (TESTDATA_DIR / "items_details.json").open(encoding="utf-8") as fh:
        wikidata_organization = WikidataOrganization.model_validate(json.load(fh)[0])

    extracted_organization = transform_wikidata_organization_to_extracted_organization(
        wikidata_organization, extracted_primary_source_ids["wikidata"]
    )

    assert extracted_organization

    assert sorted(
        extracted_organization.model_dump()["alternativeName"],
        key=itemgetter("value"),
    ) == sorted(cast("list[Any]", expected["alternativeName"]), key=itemgetter("value"))

    assert (
        extracted_organization.model_dump()["identifierInPrimarySource"]
        == expected["identifierInPrimarySource"]
    )
    assert extracted_organization.model_dump()["rorId"] == expected["rorId"]
    assert extracted_organization.model_dump()["wikidataId"] == expected["wikidataId"]
    assert extracted_organization.model_dump()["gndId"] == expected["gndId"]
    assert extracted_organization.model_dump()["isniId"] == expected["isniId"]
    assert extracted_organization.model_dump()["viafId"] == expected["viafId"]


def test_transform_wikidata_organizations_to_extracted_organizations(
    extracted_primary_source_ids: dict[str, MergedPrimarySourceIdentifier],
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
        "wikidataId": ["http://www.wikidata.org/entity/Q26678"],
    }

    with (TESTDATA_DIR / "items_details.json").open(encoding="utf-8") as fh:
        wikidata_organizations = [
            WikidataOrganization.model_validate(item) for item in json.load(fh)
        ]

    extracted_organizations = list(
        transform_wikidata_organizations_to_extracted_organizations(
            wikidata_organizations, extracted_primary_source_ids["wikidata"]
        )
    )

    assert len(extracted_organizations) == 1

    extracted_organization_dict = extracted_organizations[0].model_dump()

    assert sorted(
        extracted_organization_dict["alternativeName"],
        key=itemgetter("value"),
    ) == sorted(cast("list[Any]", expected["alternativeName"]), key=itemgetter("value"))

    assert (
        extracted_organization_dict["identifierInPrimarySource"]
        == expected["identifierInPrimarySource"]
    )
    assert extracted_organization_dict["rorId"] == expected["rorId"]
    assert extracted_organization_dict["wikidataId"] == expected["wikidataId"]
    assert extracted_organization_dict["gndId"] == expected["gndId"]
    assert extracted_organization_dict["isniId"] == expected["isniId"]
    assert extracted_organization_dict["viafId"] == expected["viafId"]


def test_transform_wikidata_location_to_extracted_location(
    extracted_primary_source_ids: dict[str, MergedPrimarySourceIdentifier],
) -> None:
    wikidata_location = WikidataLocation.model_validate(
        {
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
                ]
            },
            "aliases": {},
        }
    )

    extracted_location = transform_wikidata_location_to_extracted_location(
        wikidata_location,
        extracted_primary_source_ids["wikidata"],
    )

    assert extracted_location
    assert extracted_location.model_dump() == {
        "entityType": "ExtractedLocation",
        "geoNamesId": ["http://www.geonames.org/2921044"],
        "hadPrimarySource": "djbNGb5fLgYHFyMh3fZE2g",
        "identifier": "ciqO3CbUTH05vQrgLfvBHE",
        "identifierInPrimarySource": "Q183",
        "name": [{"language": "de", "value": "Deutschland"}],
        "stableTargetId": "gqP5foiwctLyB9zQbGxj5j",
        "wikidataId": ["http://www.wikidata.org/entity/Q183"],
    }


def test_transform_wikidata_locations_to_extracted_locations(
    extracted_primary_source_ids: dict[str, MergedPrimarySourceIdentifier],
) -> None:
    wikidata_locations = [
        WikidataLocation.model_validate(
            {
                "id": "Q183",
                "labels": {
                    "de": {"language": "de", "value": "Deutschland"},
                },
                "claims": {},
                "aliases": {},
            }
        ),
        WikidataLocation.model_validate(
            {
                "id": "Q142",
                "labels": {},  # should be skipped because of missing labels
                "claims": {},
                "aliases": {},
            }
        ),
        WikidataLocation.model_validate(
            {
                "id": "Q145",
                "labels": {
                    "en": {"language": "en", "value": "United Kingdom"},
                },
                "claims": {},
                "aliases": {},
            }
        ),
    ]

    extracted_locations = list(
        transform_wikidata_locations_to_extracted_locations(
            wikidata_locations,
            extracted_primary_source_ids["wikidata"],
        )
    )

    assert [location.identifierInPrimarySource for location in extracted_locations] == [
        "Q183",
        "Q145",
    ]


def test_get_alternative_names() -> None:
    """Test if all the alternative names are being transformed."""
    raw_aliases = Aliases.model_validate(
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
        Claim.model_validate(
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

    alternative_names = _get_alternative_names(raw_native_labels, raw_aliases)

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
        Claim.model_validate(short_name)

    clean_short_names = _get_clean_short_names(
        [Claim.model_validate(acronym) for acronym in short_names]
    )

    assert sorted(clean_short_names, key=attrgetter("value")) == sorted(
        expected, key=attrgetter("value")
    )


@pytest.mark.parametrize(
    ("labels", "expected"),
    [
        (Labels(), None),
        (
            Labels(en=Label(value="Super cool label")),
            Text(value="Super cool label", language=TextLanguage.EN),
        ),
        (
            Labels(
                de=Label(value="Ein toller Bezeichner"),
                en=Label(value="This does not actually matter"),
            ),
            Text(value="Ein toller Bezeichner", language=TextLanguage.DE),
        ),
    ],
)
def test_get_preferred_label(labels: Labels, expected: Text | None) -> None:
    assert _get_preferred_label(labels) == expected


def test_get_wikidata_entity_uri() -> None:
    assert _get_wikidata_entity_uri("test") == "http://www.wikidata.org/entity/test"
