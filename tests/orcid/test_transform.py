import pytest

from mex.common.orcid.extract import get_data_by_id
from mex.common.orcid.models.person import FamilyName, GivenNames, OrcidPerson
from mex.common.orcid.transform import (
    map_to_orcid_person,
    reduce_metadata,
    transform_orcid_person_to_mex_person,
)


@pytest.mark.parametrize(
    ("orcid_id", "reduced_data"),
    [
        (
            "0000-0002-1825-0097",
            {
                "orcid-identifier": {"path": "0000-0002-1825-0097"},
                "person": {
                    "name": {
                        "given-names": {"value": "Josiah"},
                        "family-name": {"value": "Carberry"},
                        "visibility": "public",
                    },
                    "emails": {
                        "last-modified-date": None,
                        "email": [],
                        "path": "/0000-0002-1825-0097/email",
                    },
                },
            },
        ),
        ("0009-0004-3041-576", {"result": None, "num-found": 0}),
        (
            "invalid-orcid-id",
            {"result": None, "num-found": 0},
        ),
    ],
    ids=["existing person", "non-existing person", "invalid characters"],
)
def test_reduce_metadata(orcid_id, reduced_data):
    orcid_data = get_data_by_id(orcid_id)
    result = reduce_metadata(orcid_data)
    assert result == reduced_data


@pytest.mark.parametrize(
    ("orcid_person", "expected_mex_person"),
    [
        (
            OrcidPerson(
                orcid_identifier="0000-0002-1825-0097",
                email=["test@example.com"],
                given_names=GivenNames(given_names="Josiah", visibility="public"),
                family_name=FamilyName(family_name="Carberry", visibility="public"),
            ),
            {
                "hadPrimarySource": "Naj2hOJq9FNRkkMWa5Qd0",
                "identifierInPrimarySource": "0000-0002-1825-0097",
                "email": ["test@example.com"],
                "familyName": ["Carberry"],
                "givenName": ["Josiah"],
                "orcidId": ["https://orcid.org/0000-0002-1825-0097"],
                "identifier": "YpTEbqCI50OzL4Nmqtla2",
                "stableTargetId": "VsesmNpZUOi6dklUaXWMv",
            },
        ),
        (
            OrcidPerson(
                orcid_identifier="0000-0002-9876-5432",
                email=[],
                given_names=GivenNames(given_names="John", visibility="public"),
                family_name=FamilyName(family_name="Doe", visibility="public"),
            ),
            {
                "hadPrimarySource": "Naj2hOJq9FNRkkMWa5Qd0",
                "identifierInPrimarySource": "0000-0002-9876-5432",
                "familyName": ["Doe"],
                "givenName": ["John"],
                "orcidId": ["https://orcid.org/0000-0002-9876-5432"],
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
    assert (
        mex_person.model_dump(exclude_none=True, exclude_defaults=True)
        == expected_mex_person
    )


@pytest.mark.parametrize(
    ("orcid_data", "expected_result"),
    [
        (
            {
                "orcid-identifier": {"path": "0000-0002-1825-0097"},
                "person": {
                    "name": {
                        "given-names": {"value": "Josiah"},
                        "family-name": {"value": "Carberry"},
                        "visibility": "public",
                    },
                    "emails": {
                        "email": ["test@example.com"],
                    },
                },
            },
            OrcidPerson(
                orcid_identifier="0000-0002-1825-0097",
                email=["test@example.com"],
                given_names=GivenNames(given_names="Josiah", visibility="public"),
                family_name=FamilyName(family_name="Carberry", visibility="public"),
            ),
        ),
        (
            {
                "orcid-identifier": {"path": "0000-0002-1825-0097"},
                "person": {
                    "name": {
                        "given-names": {"value": "Josiah"},
                        "family-name": {"value": "Carberry"},
                        "visibility": "public",
                    },
                    "emails": {},
                },
            },
            OrcidPerson(
                orcid_identifier="0000-0002-1825-0097",
                email=[],
                given_names=GivenNames(given_names="Josiah", visibility="public"),
                family_name=FamilyName(family_name="Carberry", visibility="public"),
            ),
        ),
        (
            {
                "orcid-identifier": {"path": "0000-0002-1825-0097"},
                "person": {
                    "name": {
                        "given-names": {"value": "Josiah"},
                        "family-name": {"value": "Carberry"},
                        "visibility": "private",
                    },
                    "emails": {
                        "email": ["test@example.com"],
                    },
                },
            },
            OrcidPerson(
                orcid_identifier="0000-0002-1825-0097",
                email=["test@example.com"],
                given_names=GivenNames(given_names="Josiah", visibility="private"),
                family_name=FamilyName(family_name="Carberry", visibility="private"),
            ),
        ),
    ],
    ids=["valid data", "missing email field", "visibility is private"],
)
def test_map_to_orcid_person(orcid_data, expected_result):
    result = map_to_orcid_person(orcid_data)
    assert result == expected_result
