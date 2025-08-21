from typing import Any

import pytest

from mex.common.models import ExtractedPrimarySource
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
from mex.common.orcid.transform import transform_orcid_person_to_mex_person


@pytest.mark.parametrize(
    ("orcid_person", "expected_mex_person"),
    [
        (
            OrcidRecord(
                orcid_identifier=OrcidIdentifier(
                    path="0009-0004-3041-5706",
                    uri="https://orcid.org/0009-0004-3041-5706",
                ),
                person=OrcidPerson(
                    orcid_identifier="0009-0004-3041-5706",
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
                "identifierInPrimarySource": "0009-0004-3041-5706",
                "affiliation": [],
                "email": ["test@example.com"],
                "familyName": ["Carberry"],
                "fullName": ["Carberry, Josiah"],
                "givenName": ["Josiah"],
                "isniId": [],
                "memberOf": [],
                "orcidId": ["https://orcid.org/0009-0004-3041-5706"],
                "entityType": "ExtractedPerson",
                "identifier": "eLFbvlVkwRgGxLnS8RywZ3",
                "stableTargetId": "ccM55btPUrNtYKSLX8cNQP",
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
                "fullName": ["Doe, John"],
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
def test_transform_orcid_person_to_mex_person(
    orcid_person: OrcidRecord,
    expected_mex_person: dict[str, Any],
    extracted_primary_sources: dict[str, ExtractedPrimarySource],
) -> None:
    orcid_primary_source = extracted_primary_sources["orcid"]
    mex_person = transform_orcid_person_to_mex_person(
        orcid_person, orcid_primary_source
    )
    assert mex_person.model_dump() == expected_mex_person
