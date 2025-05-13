import pytest

from mex.common.orcid.models import (
    OrcidEmail,
    OrcidEmails,
    OrcidFamilyName,
    OrcidGivenNames,
    OrcidIdentifier,
    OrcidName,
    OrcidPerson,
    OrcidRecord,
)


@pytest.mark.parametrize(
    ("orcid_data", "expected_result"),
    [
        (
            {
                "orcid_identifier": {
                    "path": "0009-0004-3041-5706",
                    "uri": "https://orcid.org/0009-0004-3041-5706",
                },
                "person": {
                    "emails": {"email": [{"email": "test@example.com"}]},
                    "name": {
                        "family_name": {"value": "Carberry"},
                        "given_names": {"value": "Josiah"},
                        "visibility": "public",
                    },
                },
            },
            OrcidRecord(
                orcid_identifier=OrcidIdentifier(
                    path="0009-0004-3041-5706",
                    uri="https://orcid.org/0009-0004-3041-5706",
                ),
                person=OrcidPerson(
                    emails=OrcidEmails(email=[OrcidEmail(email="test@example.com")]),
                    name=OrcidName(
                        family_name=OrcidFamilyName(value="Carberry"),
                        given_names=OrcidGivenNames(value="Josiah"),
                        visibility="public",
                    ),
                ),
            ),
        ),
        (
            {
                "orcid-identifier": {
                    "path": "0009-0004-3041-5706",
                    "uri": "https://orcid.org/0009-0004-3041-5706",
                },
                "person": {
                    "name": {
                        "given-names": {"value": "Josiah"},
                        "family-name": {"value": "Carberry"},
                        "visibility": "public",
                    },
                    "emails": {"email": []},
                },
            },
            OrcidRecord(
                orcid_identifier=OrcidIdentifier(
                    path="0009-0004-3041-5706",
                    uri="https://orcid.org/0009-0004-3041-5706",
                ),
                person=OrcidPerson(
                    emails=OrcidEmails(email=[]),
                    name=OrcidName(
                        family_name=OrcidFamilyName(value="Carberry"),
                        given_names=OrcidGivenNames(value="Josiah"),
                        visibility="public",
                    ),
                ),
            ),
        ),
        (
            {
                "orcid-identifier": {
                    "path": "0009-0004-3041-5706",
                    "uri": "https://orcid.org/0009-0004-3041-5706",
                },
                "person": {
                    "name": {
                        "given-names": {"value": "Josiah"},
                        "family-name": {"value": "Carberry"},
                        "visibility": "private",
                    },
                    "emails": {"email": [{"email": "test@example.com"}]},
                },
            },
            OrcidRecord(
                orcid_identifier=OrcidIdentifier(
                    path="0009-0004-3041-5706",
                    uri="https://orcid.org/0009-0004-3041-5706",
                ),
                person=OrcidPerson(
                    emails=OrcidEmails(email=[OrcidEmail(email=["test@example.com"])]),
                    name=OrcidName(
                        given_names=OrcidGivenNames(value="Josiah"),
                        family_name=OrcidFamilyName(value="Carberry"),
                        visibility="private",
                    ),
                ),
            ),
        ),
    ],
    ids=["valid data", "missing email field", "visibility is private"],
)
def test_orcid_record(orcid_data: object, expected_result: OrcidRecord) -> None:
    result = OrcidRecord.model_validate(orcid_data)
    assert result == expected_result
