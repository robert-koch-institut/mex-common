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


@pytest.mark.parametrize(
    ("string_id", "expected"),
    [
        ("0009-0004-3041-5706", expected_vyvy),
        ("0009-0004-3041-576", {"result": None, "num-found": 0}),
        (
            "Max Mustermann",
            {
                "result": [
                    {
                        "orcid-identifier": {
                            "uri": "https://orcid.org/0000-0002-9056-5667",
                            "path": "0000-0002-9056-5667",
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
                            "uri": "https://orcid.org/0009-0006-0442-1402",
                            "path": "0009-0006-0442-1402",
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
                            "uri": "https://orcid.org/0000-0002-3372-2005",
                            "path": "0000-0002-3372-2005",
                            "host": "orcid.org",
                        }
                    },
                    {
                        "orcid-identifier": {
                            "uri": "https://orcid.org/0000-0002-8130-5791",
                            "path": "0000-0002-8130-5791",
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
                            "uri": "https://orcid.org/0000-0002-8858-5618",
                            "path": "0000-0002-8858-5618",
                            "host": "orcid.org",
                        }
                    },
                    {
                        "orcid-identifier": {
                            "uri": "https://orcid.org/0009-0005-5828-7053",
                            "path": "0009-0005-5828-7053",
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
                            "uri": "https://orcid.org/0009-0004-5716-2091",
                            "path": "0009-0004-5716-2091",
                            "host": "orcid.org",
                        }
                    },
                    {
                        "orcid-identifier": {
                            "uri": "https://orcid.org/0000-0002-5969-8955",
                            "path": "0000-0002-5969-8955",
                            "host": "orcid.org",
                        }
                    },
                ],
                "num-found": 13,
            },
        ),
    ],
    ids=["existing person", "non-existing person", "not an identifier"],
)
def test_get_person_details_by_orcid_id(string_id, expected) -> None:
    orcidapi = OrcidConnector.get()
    result = orcidapi.get_person_details_by_orcid_id(orcid_id=string_id)
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
                ],
                "num-found": 9,
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
    assert result == expected
