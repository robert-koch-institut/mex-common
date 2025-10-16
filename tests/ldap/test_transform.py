from uuid import UUID

import pytest

from mex.common.ldap.models import (
    AnyLDAPActor,
    LDAPFunctionalAccount,
    LDAPPerson,
    LDAPPersonWithQuery,
)
from mex.common.ldap.transform import (
    PersonName,
    analyse_person_string,
    transform_any_ldap_actor_to_extracted_persons_or_contact_points,
    transform_ldap_functional_accounts_to_extracted_contact_points,
    transform_ldap_persons_to_extracted_persons,
    transform_ldap_persons_with_query_to_extracted_persons,
)
from mex.common.models import (
    ExtractedOrganization,
    ExtractedOrganizationalUnit,
)
from mex.common.testing import Joker
from mex.common.types import MergedPrimarySourceIdentifier
from tests.ldap.conftest import SAMPLE_PERSON_ATTRS


@pytest.fixture
def extracted_unit(
    extracted_primary_source_ids: dict[str, MergedPrimarySourceIdentifier],
) -> ExtractedOrganizationalUnit:
    return ExtractedOrganizationalUnit(
        name=["MF"],
        hadPrimarySource=extracted_primary_source_ids["ldap"],
        identifierInPrimarySource="mf",
    )


def test_transform_ldap_functional_accounts_to_extracted_contact_points(
    extracted_primary_source_ids: dict[str, MergedPrimarySourceIdentifier],
) -> None:
    ldap_functional_account = LDAPFunctionalAccount(
        mail=["mail@example3.com"],
        objectGUID=UUID(int=42, version=4),
        sAMAccountName="samples",
        ou=["Funktion"],
    )

    extracted_contact_points = (
        transform_ldap_functional_accounts_to_extracted_contact_points(
            [ldap_functional_account], extracted_primary_source_ids["ldap"]
        )
    )
    extracted_contact_point = extracted_contact_points[0]

    expected = {
        "email": ["mail@example3.com"],
        "hadPrimarySource": extracted_primary_source_ids["ldap"],
        "identifier": Joker(),
        "identifierInPrimarySource": "00000000-0000-4000-8000-00000000002a",
        "stableTargetId": Joker(),
    }

    assert (
        extracted_contact_point.model_dump(exclude_none=True, exclude_defaults=True)
        == expected
    )


def test_transform_ldap_persons_to_extracted_persons(
    extracted_unit: ExtractedOrganizationalUnit,
    extracted_primary_source_ids: dict[str, MergedPrimarySourceIdentifier],
    extracted_organization_rki: ExtractedOrganization,
) -> None:
    ldap_person = LDAPPerson(
        company="RKI",
        department="MF",
        departmentNumber="MF4",
        displayName="Sample, Sam, Dr.",
        employeeID="SampleS",
        givenName="Sam",
        mail=["mail@example2.com"],
        objectGUID=UUID(int=42, version=4),
        ou="MF",
        sAMAccountName="samples",
        sn="Sample",
    )

    extracted_persons = transform_ldap_persons_to_extracted_persons(
        [ldap_person],
        extracted_primary_source_ids["ldap"],
        [extracted_unit],
        extracted_organization_rki,
    )
    extracted_person = extracted_persons[0]

    expected = {
        "email": ["mail@example2.com"],
        "familyName": ["Sample"],
        "fullName": ["Sample, Sam, Dr."],
        "givenName": ["Sam"],
        "hadPrimarySource": str(extracted_primary_source_ids["ldap"]),
        "identifier": Joker(),
        "identifierInPrimarySource": "00000000-0000-4000-8000-00000000002a",
        "affiliation": [str(extracted_organization_rki.stableTargetId)],
        "memberOf": [str(extracted_unit.stableTargetId)],
        "stableTargetId": Joker(),
    }

    assert (
        extracted_person.model_dump(exclude_none=True, exclude_defaults=True)
        == expected
    )


def test_transform_any_ldap_actor_to_extracted_persons_or_contact_points(
    extracted_primary_source_ids: dict[str, MergedPrimarySourceIdentifier],
    extracted_unit: ExtractedOrganizationalUnit,
    extracted_organization_rki: ExtractedOrganization,
) -> None:
    ldap_actors: list[AnyLDAPActor] = [
        LDAPFunctionalAccount(
            mail=["postfach@example.com"],
            objectGUID=UUID(int=42, version=4),
            sAMAccountName="postfach",
            ou=["Funktion"],
        ),
        LDAPPerson(
            department="MF",
            displayName="Sample, Sam, Dr.",
            employeeID="SampleS",
            givenName="Sam",
            mail=["mail@example.com"],
            objectGUID=UUID(int=43, version=4),
            sAMAccountName="samples",
            sn="Sample",
        ),
    ]

    extracted_actors = transform_any_ldap_actor_to_extracted_persons_or_contact_points(
        ldap_actors,
        [extracted_unit],
        extracted_primary_source_ids["ldap"],
        extracted_organization_rki,
    )

    assert [
        a.model_dump(exclude_none=True, exclude_defaults=True) for a in extracted_actors
    ] == [
        {
            "hadPrimarySource": str(extracted_primary_source_ids["ldap"]),
            "identifierInPrimarySource": "00000000-0000-4000-8000-00000000002a",
            "email": ["postfach@example.com"],
            "identifier": Joker(),
            "stableTargetId": Joker(),
        },
        {
            "hadPrimarySource": extracted_primary_source_ids["ldap"],
            "identifierInPrimarySource": "00000000-0000-4000-8000-00000000002b",
            "email": ["mail@example.com"],
            "familyName": ["Sample"],
            "fullName": ["Sample, Sam, Dr."],
            "givenName": ["Sam"],
            "memberOf": [str(extracted_unit.stableTargetId)],
            "affiliation": [str(extracted_organization_rki.stableTargetId)],
            "identifier": Joker(),
            "stableTargetId": Joker(),
        },
    ]


@pytest.mark.parametrize(
    ("string", "expected"),
    [
        ("", []),
        ("-", []),
        ("Sur", [PersonName("Sur", "*", "Sur")]),
        ("Given Sur", [PersonName("Sur", "Given", "Given Sur")]),
        ("Given M. Sur-Name", [PersonName("Sur-Name", "Given", "Given Sur-Name")]),
        ("Sur, Given", [PersonName("Sur", "Given", "Given Sur")]),
        (
            "Olaf One, Tracy Two, Toni Three",
            [
                PersonName("One", "Olaf", "Olaf One"),
                PersonName("Two", "Tracy", "Tracy Two"),
                PersonName("Three", "Toni", "Toni Three"),
            ],
        ),
        (
            "Olaf One, Tracy Two",
            [
                PersonName("One", "Olaf", "Olaf One"),
                PersonName("Two", "Tracy", "Tracy Two"),
            ],
        ),
        (
            "Olga One / Troy Two",
            [
                PersonName("One", "Olga", "Olga One"),
                PersonName("Two", "Troy", "Troy Two"),
            ],
        ),
        (
            "Lastname; Given Surname",
            [
                PersonName("Lastname", "*", "Lastname"),
                PersonName("Surname", "Given", "Given Surname"),
            ],
        ),
        (
            "Muster, Max; Doe, Jane",
            [
                PersonName("Muster", "Max", "Max Muster"),
                PersonName("Doe", "Jane", "Jane Doe"),
            ],
        ),
        (
            "Mac Fly, Marty",
            [PersonName("Mac Fly", "Marty", "Marty Mac Fly")],
        ),
        (
            "Multiple Given Names Surname",
            [
                PersonName(
                    "Surname", "Multiple Given Names", "Multiple Given Names Surname"
                )
            ],
        ),
        ("Sur, Given (Leitung Unit)", [PersonName("Sur", "Given", "Given Sur")]),
        ("Sur, Given (FG99", [PersonName("Sur", "Given", "Given Sur")]),
        (
            "Prof. Dr. med. Sur stellv. Projektleitung ABC2",
            [PersonName("Sur", "*", "Sur")],
        ),
        ("Given Sur, Abteilung X3 Z.", [PersonName("Sur", "Given", "Given Sur")]),
        ("Fr. Given Sur 3", [PersonName("Sur", "Given", "Given Sur")]),
    ],
)
def test_analyse_person_string(string: str, expected: list[PersonName]) -> None:
    names = analyse_person_string(string)
    assert names == expected


def test_transform_ldap_persons_with_query_to_extracted_persons(
    extracted_primary_source_ids: dict[str, MergedPrimarySourceIdentifier],
    extracted_unit: ExtractedOrganizationalUnit,
    extracted_organization_rki: ExtractedOrganization,
) -> None:
    ldap_person = LDAPPerson.model_validate(SAMPLE_PERSON_ATTRS)
    ldap_persons_with_query = [LDAPPersonWithQuery(person=ldap_person, query="test")]

    extracted_persons = transform_ldap_persons_with_query_to_extracted_persons(
        ldap_persons_with_query,
        extracted_primary_source_ids["ldap"],
        [extracted_unit],
        extracted_organization_rki,
    )

    assert len(extracted_persons) == 1
    assert extracted_persons[0].model_dump() == {
        "hadPrimarySource": extracted_primary_source_ids["ldap"],
        "identifierInPrimarySource": "00000000-0000-4000-8000-000000000000",
        "affiliation": [extracted_organization_rki.stableTargetId],
        "email": ["SampleS@mail.tld"],
        "familyName": ["Sample"],
        "fullName": ["Sample, Sam"],
        "givenName": ["Sam"],
        "isniId": [],
        "memberOf": [],
        "orcidId": [],
        "entityType": "ExtractedPerson",
        "identifier": "cXTehc7a4YxNw6j7UpSq0b",
        "stableTargetId": "fWYZKuwfymRj0ItP1CfTO4",
    }
