import pytest
from requests import HTTPError

from mex.common.exceptions import EmptySearchResultError, FoundMoreThanOneError
from mex.common.orcid.connector import OrcidConnector


@pytest.mark.usefixtures("mocked_orcid")
@pytest.mark.parametrize(
    ("filters", "expected"),
    [
        (
            {"given-names": "Josiah", "family-name": "Carberry"},
            "given-names:Josiah AND family-name:Carberry",
        ),
        (
            {"given-and-family-names": '"Jayne Carberry"'},
            'given-and-family-names:"Jayne Carberry"',
        ),
        (
            {"givennames": "Josiah", "familyname": "Carberry"},
            "givennames:Josiah AND familyname:Carberry",
        ),
    ],
    ids=["valid_query", "valid given-and_family-names query", "non_valid_query"],
)
def test_build_query(filters, expected) -> None:
    orcid_api = OrcidConnector.get()
    built_query = orcid_api.build_query(filters=filters)
    assert built_query == expected


@pytest.mark.usefixtures("mocked_orcid")
@pytest.mark.parametrize(
    ("orcidid", "expected"),
    [("0009-0004-3041-5706", True), ("0002-1825-0097", False)],
    ids=["valid_query", "non_valid_query"],
)
@pytest.mark.usefixtures("orcid_person_raw")
@pytest.mark.parametrize(
    ("family_name", "given_names", "expected"),
    [
        (
            "Doe",
            "John",
            {
                "num-found": 1,
                "result": [
                    {
                        "orcid-identifier": {
                            "host": "orcid.org",
                            "path": "0009-0004-3041-5706",
                            "uri": "https://orcid.org/0009-0004-3041-5706",
                        },
                        "path": "/0009-0004-3041-5706",
                        "person": {
                            "emails": {
                                "email": [],
                                "path": "/0009-0004-3041-5706/email",
                            },
                            "name": {
                                "created-date": {"value": 1729001670037},
                                "family-name": {"value": "Doe"},
                                "given-names": {"value": "John"},
                                "last-modified-date": {"value": 1730814244255},
                                "path": "0009-0004-3041-5706",
                                "visibility": "public",
                            },
                            "other-names": {
                                "other-name": [],
                                "path": "/0009-0004-3041-5706/other-names",
                            },
                            "researcher-urls": {
                                "path": "/0009-0004-3041-5706/researcher-urls",
                                "researcher-url": [],
                            },
                        },
                    }
                ],
            },
        ),
        (
            "Doe",
            "Multiple",
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
        ("Doe", "NotExistJohn", {"result": None, "num-found": 0}),
    ],
    ids=["existing person", "multiple results", "non-existing person"],
)
@pytest.mark.usefixtures("mocked_orcid")
def test_fetch_person_by_name(family_name, given_names, expected) -> None:
    orcidapi = OrcidConnector.get()
    filters = {}
    filters["given-names"] = given_names
    filters["family-name"] = family_name
    search_response = orcidapi.fetch(filters=filters)
    num_found = search_response.get("num-found", 0)
    assert num_found == expected["num-found"]
    assert search_response == expected


@pytest.mark.usefixtures("mocked_orcid")
def test_get_data_by_id(orcid_person_raw) -> None:
    expected_data = orcid_person_raw
    result = OrcidConnector.get_data_by_id("0009-0004-3041-5706")
    assert result == expected_data


@pytest.mark.usefixtures("mocked_orcid")
def test_get_data_by_id_not_found():
    with pytest.raises(HTTPError, match="404 Not Found"):
        OrcidConnector.get_data_by_id("0000-0000-0000-0000")


@pytest.mark.usefixtures("mocked_orcid")
def test_get_data_by_name(orcid_person_raw):
    given_names = "John"
    family_name = "Doe"
    result = OrcidConnector.get_data_by_name(
        given_names=given_names, family_name=family_name
    )
    assert result == orcid_person_raw


@pytest.mark.parametrize(
    ("givenname", "familyname", "expected_exception"),
    [
        ("NotExistJohn", "Doe", EmptySearchResultError),
        ("Multiple", "Doe", FoundMoreThanOneError),
    ],
    ids=["Empty Results", "Multiple Responses"],
)
@pytest.mark.usefixtures("mocked_orcid")
def test_get_data_by_name_errors(givenname, familyname, expected_exception):
    """Test get_data_by_name raises appropriate errors for various edge cases."""
    with pytest.raises(expected_exception):
        OrcidConnector.get_data_by_name(given_names=givenname, family_name=familyname)
