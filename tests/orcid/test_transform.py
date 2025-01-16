import pytest

from mex.common.orcid.models.person import (
    OrcidEmail,
    OrcidEmails,
    OrcidFamilyName,
    OrcidGivenNames,
    OrcidIdentifier,
    OrcidName,
    OrcidPerson,
    OrcidRecord,
)
from mex.common.orcid.transform import (
    map_orcid_data_to_orcid_record,
    transform_orcid_person_to_mex_person,
)


@pytest.mark.parametrize(
    ("orcid_person", "expected_mex_person"),
    [
        (
            OrcidRecord(
                orcid_identifier=OrcidIdentifier(
                    path="0000-0002-1825-0097",
                    uri="https://orcid.org/0000-0002-1825-0097",
                ),
                person=OrcidPerson(
                    orcid_identifier="0000-0002-1825-0097",
                    emails=OrcidEmails(email=[OrcidEmail(email=["test@example.com"])]),
                    name=OrcidName(
                        given_names=OrcidGivenNames(value="Josiah"),
                        family_name=OrcidFamilyName(value="Carberry"),
                        visibility="public",
                    ),
                ),
            ),
            {
                "hadPrimarySource": "Naj2hOJq9FNRkkMWa5Qd0",
                "identifierInPrimarySource": "0000-0002-1825-0097",
                "affiliation": [],
                "email": ["test@example.com"],
                "familyName": ["Carberry"],
                "fullName": [],
                "givenName": ["Josiah"],
                "isniId": [],
                "memberOf": [],
                "orcidId": ["https://orcid.org/0000-0002-1825-0097"],
                "entityType": "ExtractedPerson",
                "identifier": "YpTEbqCI50OzL4Nmqtla2",
                "stableTargetId": "VsesmNpZUOi6dklUaXWMv",
            },
        ),
        (
            OrcidRecord(
                orcid_identifier=OrcidIdentifier(
                    path="0000-0002-9876-5432",
                    uri="https://orcid.org/0000-0002-9876-5432",
                ),
                person=OrcidPerson(
                    orcid_identifier="0000-0002-9876-5432",
                    emails=OrcidEmails(email=[OrcidEmail(email=[])]),
                    name=OrcidName(
                        given_names=OrcidGivenNames(value="John"),
                        family_name=OrcidFamilyName(value="Doe"),
                        visibility="public",
                    ),
                ),
            ),
            {
                "hadPrimarySource": "Naj2hOJq9FNRkkMWa5Qd0",
                "identifierInPrimarySource": "0000-0002-9876-5432",
                "affiliation": [],
                "email": [],
                "familyName": ["Doe"],
                "fullName": [],
                "givenName": ["John"],
                "isniId": [],
                "memberOf": [],
                "orcidId": ["https://orcid.org/0000-0002-9876-5432"],
                "entityType": "ExtractedPerson",
                "identifier": "cwOd1omDQ8ePMflUVfXmH6",
                "stableTargetId": "cPgmFF42nbFoEMWtuHaQw7",
            },
        ),
    ],
    ids=[
        "existing person with email",
        "existing person with no email",
    ],
)
def test_transform_orcid_person_to_mex_person(orcid_person, expected_mex_person):
    mex_person = transform_orcid_person_to_mex_person(orcid_person)
    assert mex_person.model_dump() == expected_mex_person


@pytest.mark.parametrize(
    ("orcid_data", "expected_result"),
    [
        (
            {
                "orcid_identifier": {
                    "path": "0000-0002-1825-0097",
                    "uri": "https://orcid.org/0000-0002-1825-0097",
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
                    path="0000-0002-1825-0097",
                    uri="https://orcid.org/0000-0002-1825-0097",
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
                    "path": "0000-0002-1825-0097",
                    "uri": "https://orcid.org/0000-0002-1825-0097",
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
                    path="0000-0002-1825-0097",
                    uri="https://orcid.org/0000-0002-1825-0097",
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
                    "path": "0000-0002-1825-0097",
                    "uri": "https://orcid.org/0000-0002-1825-0097",
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
                    path="0000-0002-1825-0097",
                    uri="https://orcid.org/0000-0002-1825-0097",
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
def test_map_orcid_data_to_orcid_record(orcid_data, expected_result):
    result = map_orcid_data_to_orcid_record(orcid_data)
    assert result == expected_result
