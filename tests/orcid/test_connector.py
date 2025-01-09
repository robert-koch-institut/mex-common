import pytest

from mex.common.orcid.connector import OrcidConnector


@pytest.mark.parametrize(
    ("family_name", "given_names", "expected"),
    [
        (
            "Tran Ngoc",
            "Vyvy",
            {
                "result": [
                    {
                        "orcid-identifier": {
                            "uri": "https://orcid.org/0009-0004-3041-5706",
                            "path": "0009-0004-3041-5706",
                            "host": "orcid.org",
                        }
                    }
                ],
                "num-found": 1,
            },
        ),
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
                            "uri": "https://orcid.org/0009-0006-9954-421X",
                            "path": "0009-0006-9954-421X",
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
                "num-found": 10,
            },
        ),
        ("Defgh", "Abc", {"result": None, "num-found": 0}),
    ],
    ids=["existing person", "multiple results", "non-existing person"],
)
def test_fetch_person_by_name(family_name, given_names, expected) -> None:
    orcidapi = OrcidConnector.get()
    filters = {}
    filters["given-names"] = given_names
    filters["family-name"] = family_name
    search_response = orcidapi.fetch(OrcidConnector.build_query(filters))
    num_found = search_response.get("num-found", 0)
    assert num_found == expected["num-found"]
    assert search_response == expected


@pytest.mark.parametrize(
    ("filters", "expected"),
    [
        (
            {"given-names": "Josiah", "family-name": "Carberry"},
            "given-names:Josiah AND family-name:Carberry",
        ),
        (
            {"givennames": "Josiah", "familyname": "Carberry"},
            "givennames:Josiah AND familyname:Carberry",
        ),
    ],
    ids=["valid_query", "non_valid_query"],
)
def test_build_query(filters, expected) -> None:
    orcid_api = OrcidConnector.get()
    built_query = orcid_api.build_query(filters=filters)
    assert built_query == expected


@pytest.mark.parametrize(
    ("orcidid", "expected"),
    [("0000-0002-1825-0097", True), ("1000-0002-1825-0097", False)],
    ids=["valid_query", "non_valid_query"],
)
def test_check_id_exists(orcidid, expected) -> None:
    orcidapi = OrcidConnector.get()
    id_exists = orcidapi.check_orcid_id_exists(orcidid)
    assert id_exists == expected
