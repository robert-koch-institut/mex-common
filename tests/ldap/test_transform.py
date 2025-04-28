from uuid import UUID

import pytest

from mex.common.ldap.models import LDAPActor, LDAPPerson
from mex.common.ldap.transform import (
    PersonName,
    analyse_person_string,
    transform_ldap_actors_to_mex_contact_points,
    transform_ldap_persons_to_mex_persons,
)
from mex.common.models import ExtractedOrganizationalUnit, ExtractedPrimarySource
from mex.common.testing import Joker


@pytest.fixture
def extracted_unit(
    extracted_primary_sources: dict[str, ExtractedPrimarySource],
) -> ExtractedOrganizationalUnit:
    return ExtractedOrganizationalUnit(
        name=["MF"],
        hadPrimarySource=extracted_primary_sources["ldap"].stableTargetId,
        identifierInPrimarySource="mf",
    )


def test_transform_ldap_actors_to_mex_contact_points(
    extracted_primary_sources: dict[str, ExtractedPrimarySource],
) -> None:
    ldap_actor = LDAPActor(
        mail=["mail@example3.com"],
        objectGUID=UUID(int=42, version=4),
        sAMAccountName="samples",
    )

    extracted_contact_points = transform_ldap_actors_to_mex_contact_points(
        [ldap_actor], extracted_primary_sources["ldap"]
    )
    extracted_contact_point = extracted_contact_points[0]

    expected = {
        "email": ["mail@example3.com"],
        "hadPrimarySource": extracted_primary_sources["ldap"].stableTargetId,
        "identifier": Joker(),
        "identifierInPrimarySource": "00000000-0000-4000-8000-00000000002a",
        "stableTargetId": Joker(),
    }

    assert (
        extracted_contact_point.model_dump(exclude_none=True, exclude_defaults=True)
        == expected
    )


def test_transform_ldap_persons_to_mex_persons(
    extracted_unit: ExtractedOrganizationalUnit,
    extracted_primary_sources: dict[str, ExtractedPrimarySource],
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

    extracted_persons = transform_ldap_persons_to_mex_persons(
        [ldap_person], extracted_primary_sources["ldap"], [extracted_unit]
    )
    extracted_person = extracted_persons[0]

    expected = {
        "email": ["mail@example2.com"],
        "familyName": ["Sample"],
        "fullName": ["Sample, Sam, Dr."],
        "givenName": ["Sam"],
        "hadPrimarySource": extracted_primary_sources["ldap"].stableTargetId,
        "identifier": Joker(),
        "identifierInPrimarySource": "00000000-0000-4000-8000-00000000002a",
        "memberOf": [extracted_unit.stableTargetId],
        "stableTargetId": Joker(),
    }

    assert (
        extracted_person.model_dump(exclude_none=True, exclude_defaults=True)
        == expected
    )


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
