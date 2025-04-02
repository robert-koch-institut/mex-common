import pytest
from requests import HTTPError

from mex.common.orcid.connector import OrcidConnector
from mex.common.orcid.models import (
    OrcidIdentifier,
    OrcidSearchItem,
    OrcidSearchResponse,
)


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
def test_build_query(filters: dict[str, str], expected: str) -> None:
    orcid_api = OrcidConnector.get()
    built_query = orcid_api.build_query(filters=filters)
    assert built_query == expected


@pytest.mark.usefixtures("orcid_person_raw")
@pytest.mark.parametrize(
    ("family_name", "given_names", "expected"),
    [
        (
            "Doe",
            "John",
            OrcidSearchResponse(
                num_found=1,
                result=[
                    OrcidSearchItem(
                        orcid_identifier=OrcidIdentifier(
                            path="0009-0004-3041-5706",
                            uri="https://orcid.org/0009-0004-3041-5706",
                        )
                    )
                ],
            ),
        ),
        (
            "Doe",
            "Multiple",
            OrcidSearchResponse(
                num_found=10,
                result=[
                    OrcidSearchItem(
                        orcid_identifier=OrcidIdentifier(
                            path="0009-0005-5828-7053",
                            uri="https://orcid.org/0009-0005-5828-7053",
                        )
                    ),
                    OrcidSearchItem(
                        orcid_identifier=OrcidIdentifier(
                            path="0000-0003-3648-8952",
                            uri="https://orcid.org/0000-0003-3648-8952",
                        )
                    ),
                    OrcidSearchItem(
                        orcid_identifier=OrcidIdentifier(
                            path="0000-0002-7523-2549",
                            uri="https://orcid.org/0000-0002-7523-2549",
                        )
                    ),
                    OrcidSearchItem(
                        orcid_identifier=OrcidIdentifier(
                            path="0000-0002-9056-5667",
                            uri="https://orcid.org/0000-0002-9056-5667",
                        )
                    ),
                    OrcidSearchItem(
                        orcid_identifier=OrcidIdentifier(
                            path="0000-0002-3372-2005",
                            uri="https://orcid.org/0000-0002-3372-2005",
                        )
                    ),
                    OrcidSearchItem(
                        orcid_identifier=OrcidIdentifier(
                            path="0000-0001-7659-8932",
                            uri="https://orcid.org/0000-0001-7659-8932",
                        )
                    ),
                    OrcidSearchItem(
                        orcid_identifier=OrcidIdentifier(
                            path="0009-0005-0959-5447",
                            uri="https://orcid.org/0009-0005-0959-5447",
                        )
                    ),
                    OrcidSearchItem(
                        orcid_identifier=OrcidIdentifier(
                            path="0009-0000-4002-171X",
                            uri="https://orcid.org/0009-0000-4002-171X",
                        )
                    ),
                    OrcidSearchItem(
                        orcid_identifier=OrcidIdentifier(
                            path="0009-0006-0442-1402",
                            uri="https://orcid.org/0009-0006-0442-1402",
                        )
                    ),
                    OrcidSearchItem(
                        orcid_identifier=OrcidIdentifier(
                            path="0009-0006-9954-421X",
                            uri="https://orcid.org/0009-0006-9954-421X",
                        )
                    ),
                ],
            ),
        ),
        ("Doe", "NotExistJohn", OrcidSearchResponse(num_found=0, result=[])),
    ],
    ids=["existing person", "multiple results", "non-existing person"],
)
@pytest.mark.usefixtures("mocked_orcid")
def test_fetch_person_by_name(
    family_name: str, given_names: str, expected: OrcidSearchResponse
) -> None:
    connector = OrcidConnector.get()
    response = connector.search_records_by_name(given_names, family_name)
    assert response == expected


@pytest.mark.usefixtures("mocked_orcid")
def test_get_record_by_id() -> None:
    connector = OrcidConnector.get()
    result = connector.get_record_by_id("0009-0004-3041-5706")
    assert result.model_dump() == {
        "orcid_identifier": {
            "path": "0009-0004-3041-5706",
            "uri": "https://orcid.org/0009-0004-3041-5706",
        },
        "person": {
            "emails": {"email": []},
            "name": {
                "family_name": {"value": "Doe"},
                "given_names": {"value": "John"},
                "visibility": "public",
            },
        },
    }


@pytest.mark.usefixtures("mocked_orcid")
def test_get_record_by_id_not_found() -> None:
    connector = OrcidConnector.get()
    with pytest.raises(HTTPError, match="404 Not Found"):
        connector.get_record_by_id("0000-0000-0000-000")
