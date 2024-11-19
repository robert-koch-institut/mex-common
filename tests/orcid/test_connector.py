import pytest  # noqa: INP001

from mex.common.orcid.connector import OrcidConnector

expected_vyvy = {
    "last-modified-date": None,
    "name": {
        "created-date": {"value": 1729001670037},
        "last-modified-date": {"value": 1730814244255},
        "given-names": {"value": "VyVy"},
        "family-name": {"value": "Tran Ngoc"},
        "credit-name": None,
        "source": None,
        "visibility": "public",
        "path": "0009-0004-3041-5706",
    },
    "other-names": {
        "last-modified-date": None,
        "other-name": [],
        "path": "/0009-0004-3041-5706/other-names",
    },
    "biography": None,
    "researcher-urls": {
        "last-modified-date": None,
        "researcher-url": [],
        "path": "/0009-0004-3041-5706/researcher-urls",
    },
    "emails": {
        "last-modified-date": None,
        "email": [],
        "path": "/0009-0004-3041-5706/email",
    },
    "addresses": {
        "last-modified-date": None,
        "address": [],
        "path": "/0009-0004-3041-5706/address",
    },
    "keywords": {
        "last-modified-date": None,
        "keyword": [],
        "path": "/0009-0004-3041-5706/keywords",
    },
    "external-identifiers": {
        "last-modified-date": None,
        "external-identifier": [],
        "path": "/0009-0004-3041-5706/external-identifiers",
    },
    "path": "/0009-0004-3041-5706/person",
}

expected_john = {
    "last-modified-date": {"value": 1494016313820},
    "name": {
        "created-date": {"value": 1460757617078},
        "last-modified-date": {"value": 1504850007188},
        "given-names": {"value": "Josiah"},
        "family-name": {"value": "Carberry"},
        "credit-name": None,
        "source": None,
        "visibility": "public",
        "path": "0000-0002-1825-0097",
    },
    "other-names": {
        "last-modified-date": {"value": 1462157547720},
        "other-name": [
            {
                "created-date": {"value": 1462157351411},
                "last-modified-date": {"value": 1462157547720},
                "source": {
                    "source-orcid": {
                        "uri": "https://orcid.org/0000-0002-1825-0097",
                        "path": "0000-0002-1825-0097",
                        "host": "orcid.org",
                    },
                    "source-client-id": None,
                    "source-name": {"value": "Josiah Carberry"},
                    "assertion-origin-orcid": None,
                    "assertion-origin-client-id": None,
                    "assertion-origin-name": None,
                },
                "content": "Josiah Stinkney Carberry",
                "visibility": "public",
                "path": "/0000-0002-1825-0097/other-names/732317",
                "put-code": 732317,
                "display-index": 3,
            },
            {
                "created-date": {"value": 1446663146889},
                "last-modified-date": {"value": 1462157547720},
                "source": {
                    "source-orcid": {
                        "uri": "https://orcid.org/0000-0002-1825-0097",
                        "path": "0000-0002-1825-0097",
                        "host": "orcid.org",
                    },
                    "source-client-id": None,
                    "source-name": {"value": "Josiah Carberry"},
                    "assertion-origin-orcid": None,
                    "assertion-origin-client-id": None,
                    "assertion-origin-name": None,
                },
                "content": "J. Carberry",
                "visibility": "public",
                "path": "/0000-0002-1825-0097/other-names/565981",
                "put-code": 565981,
                "display-index": 2,
            },
            {
                "created-date": {"value": 1462157351418},
                "last-modified-date": {"value": 1462157547720},
                "source": {
                    "source-orcid": {
                        "uri": "https://orcid.org/0000-0002-1825-0097",
                        "path": "0000-0002-1825-0097",
                        "host": "orcid.org",
                    },
                    "source-client-id": None,
                    "source-name": {"value": "Josiah Carberry"},
                    "assertion-origin-orcid": None,
                    "assertion-origin-client-id": None,
                    "assertion-origin-name": None,
                },
                "content": "J. S. Carberry",
                "visibility": "public",
                "path": "/0000-0002-1825-0097/other-names/732318",
                "put-code": 732318,
                "display-index": 1,
            },
        ],
        "path": "/0000-0002-1825-0097/other-names",
    },
    "biography": {
        "created-date": {"value": 1460757617080},
        "last-modified-date": {"value": 1460757617080},
        "content": 'Josiah Carberry is a fictitious person. This account is used as a demonstration account by ORCID, CrossRef and others who wish to demonstrate the interaction of ORCID with other scholarly communication systems without having to use a real-person\'s account.\r\n\r\nJosiah Stinkney Carberry is a fictional professor, created as a joke in 1929. He is said to still teach at Brown University, and to be known for his work in "psychoceramics", the supposed study of "cracked pots". See his Wikipedia entry for more details.',
        "visibility": "public",
        "path": "/0000-0002-1825-0097/biography",
    },
    "researcher-urls": {
        "last-modified-date": {"value": 1462157645967},
        "researcher-url": [
            {
                "created-date": {"value": 1446663146890},
                "last-modified-date": {"value": 1462157645967},
                "source": {
                    "source-orcid": {
                        "uri": "https://orcid.org/0000-0002-1825-0097",
                        "path": "0000-0002-1825-0097",
                        "host": "orcid.org",
                    },
                    "source-client-id": None,
                    "source-name": {"value": "Josiah Carberry"},
                    "assertion-origin-orcid": None,
                    "assertion-origin-client-id": None,
                    "assertion-origin-name": None,
                },
                "url-name": "Brown University Page",
                "url": {"value": "http://library.brown.edu/about/hay/carberry.php"},
                "visibility": "public",
                "path": "/0000-0002-1825-0097/researcher-urls/568395",
                "put-code": 568395,
                "display-index": 2,
            },
            {
                "created-date": {"value": 1446663146889},
                "last-modified-date": {"value": 1462157645967},
                "source": {
                    "source-orcid": {
                        "uri": "https://orcid.org/0000-0002-1825-0097",
                        "path": "0000-0002-1825-0097",
                        "host": "orcid.org",
                    },
                    "source-client-id": None,
                    "source-name": {"value": "Josiah Carberry"},
                    "assertion-origin-orcid": None,
                    "assertion-origin-client-id": None,
                    "assertion-origin-name": None,
                },
                "url-name": "Wikipedia Entry",
                "url": {"value": "http://en.wikipedia.org/wiki/Josiah_Carberry"},
                "visibility": "public",
                "path": "/0000-0002-1825-0097/researcher-urls/568394",
                "put-code": 568394,
                "display-index": 1,
            },
        ],
        "path": "/0000-0002-1825-0097/researcher-urls",
    },
    "emails": {
        "last-modified-date": None,
        "email": [],
        "path": "/0000-0002-1825-0097/email",
    },
    "addresses": {
        "last-modified-date": None,
        "address": [],
        "path": "/0000-0002-1825-0097/address",
    },
    "keywords": {
        "last-modified-date": {"value": 1462157635636},
        "keyword": [
            {
                "created-date": {"value": 1462157617244},
                "last-modified-date": {"value": 1462157635636},
                "source": {
                    "source-orcid": {
                        "uri": "https://orcid.org/0000-0002-1825-0097",
                        "path": "0000-0002-1825-0097",
                        "host": "orcid.org",
                    },
                    "source-client-id": None,
                    "source-name": {"value": "Josiah Carberry"},
                    "assertion-origin-orcid": None,
                    "assertion-origin-client-id": None,
                    "assertion-origin-name": None,
                },
                "content": "psychoceramics",
                "visibility": "public",
                "path": "/0000-0002-1825-0097/keywords/434187",
                "put-code": 434187,
                "display-index": 3,
            },
            {
                "created-date": {"value": 1462157414545},
                "last-modified-date": {"value": 1462157635636},
                "source": {
                    "source-orcid": {
                        "uri": "https://orcid.org/0000-0002-1825-0097",
                        "path": "0000-0002-1825-0097",
                        "host": "orcid.org",
                    },
                    "source-client-id": None,
                    "source-name": {"value": "Josiah Carberry"},
                    "assertion-origin-orcid": None,
                    "assertion-origin-client-id": None,
                    "assertion-origin-name": None,
                },
                "content": "ionian philology",
                "visibility": "public",
                "path": "/0000-0002-1825-0097/keywords/434184",
                "put-code": 434184,
                "display-index": 2,
            },
        ],
        "path": "/0000-0002-1825-0097/keywords",
    },
    "external-identifiers": {
        "last-modified-date": {"value": 1494016313820},
        "external-identifier": [
            {
                "created-date": {"value": 1494016313820},
                "last-modified-date": {"value": 1494016313820},
                "source": {
                    "source-orcid": None,
                    "source-client-id": {
                        "uri": "https://orcid.org/client/0000-0002-5982-8983",
                        "path": "0000-0002-5982-8983",
                        "host": "orcid.org",
                    },
                    "source-name": {"value": "Scopus - Elsevier"},
                    "assertion-origin-orcid": {
                        "uri": "https://orcid.org/0000-0002-1825-0097",
                        "path": "0000-0002-1825-0097",
                        "host": "orcid.org",
                    },
                    "assertion-origin-client-id": None,
                    "assertion-origin-name": {"value": "Josiah Carberry"},
                },
                "external-id-type": "Scopus Author ID",
                "external-id-value": "7007156898",
                "external-id-url": {
                    "value": "http://www.scopus.com/inward/authorDetails.url?authorID=7007156898&partnerID=MN8TOARS"
                },
                "external-id-relationship": "self",
                "visibility": "public",
                "path": "/0000-0002-1825-0097/external-identifiers/698979",
                "put-code": 698979,
                "display-index": 0,
            }
        ],
        "path": "/0000-0002-1825-0097/external-identifiers",
    },
    "path": "/0000-0002-1825-0097/person",
}


@pytest.mark.parametrize(
    ("string_id", "expected"),
    [
        ("0000-0002-1825-0097", expected_john),
        ("0009-0004-3041-576", {"result": None, "num-found": 0}),
        ("invalid-orcid-id", {"result": None, "num-found": 0}),
    ],
    ids=["existing person", "non-existing person", "invalid characters"],
)
def test_get_person_details_by_orcid_id(string_id, expected) -> None:
    orcidapi = OrcidConnector.get()
    result = orcidapi.get_person_details_by_id(orcid_id=string_id)
    if result.get("num-found"):
        assert result.get("num-found") == expected.get("num-found")
    assert result == expected


@pytest.mark.parametrize(
    ("family_name", "given_names", "expected"),
    [
        ("Tran Ngoc", "Vyvy", expected_vyvy),
        (
            "Mustermann",
            "Max",
            {
                "result": [
                    {
                        "orcid-identifier": {
                            "uri": "https://orcid.org/0009-0005-5828-7053",
                            "path": "0009-0005-5828-7053",
                            "host": "orcid.org",
                        }
                    },
                    {
                        "orcid-identifier": {
                            "uri": "https://orcid.org/0000-0003-3648-8952",
                            "path": "0000-0003-3648-8952",
                            "host": "orcid.org",
                        }
                    },
                    {
                        "orcid-identifier": {
                            "uri": "https://orcid.org/0000-0002-7523-2549",
                            "path": "0000-0002-7523-2549",
                            "host": "orcid.org",
                        }
                    },
                    {
                        "orcid-identifier": {
                            "uri": "https://orcid.org/0000-0002-9056-5667",
                            "path": "0000-0002-9056-5667",
                            "host": "orcid.org",
                        }
                    },
                    {
                        "orcid-identifier": {
                            "uri": "https://orcid.org/0000-0002-3372-2005",
                            "path": "0000-0002-3372-2005",
                            "host": "orcid.org",
                        }
                    },
                    {
                        "orcid-identifier": {
                            "uri": "https://orcid.org/0000-0001-7659-8932",
                            "path": "0000-0001-7659-8932",
                            "host": "orcid.org",
                        }
                    },
                    {
                        "orcid-identifier": {
                            "uri": "https://orcid.org/0009-0005-0959-5447",
                            "path": "0009-0005-0959-5447",
                            "host": "orcid.org",
                        }
                    },
                    {
                        "orcid-identifier": {
                            "uri": "https://orcid.org/0009-0000-4002-171X",
                            "path": "0009-0000-4002-171X",
                            "host": "orcid.org",
                        }
                    },
                    {
                        "orcid-identifier": {
                            "uri": "https://orcid.org/0009-0006-0442-1402",
                            "path": "0009-0006-0442-1402",
                            "host": "orcid.org",
                        }
                    },
                    {
                        "orcid-identifier": {
                            "uri": "https://orcid.org/0009-0006-9954-421X",
                            "path": "0009-0006-9954-421X",
                            "host": "orcid.org",
                        }
                    },
                ],
                "num-found": 10,
            },
        ),
        ("Defgh", "Abc", {"result": None, "num-found": 0}),
    ],
    ids=["existing person", "multiple results", "non-existing person"],
)
def test_search_person_by_givenname(family_name, given_names, expected) -> None:
    orcidapi = OrcidConnector.get()
    result = orcidapi.get_person_details_by_name(
        given_names=given_names, family_name=family_name
    )
    if result.get("num-found"):
        assert result["num-found"] == expected["num-found"]
    assert result == expected
