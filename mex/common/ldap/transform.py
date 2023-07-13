import re
from dataclasses import dataclass
from functools import cache
from typing import Generator, Iterable

from mex.common.exceptions import MExError
from mex.common.ldap.models.person import LDAPPerson, LDAPPersonWithQuery
from mex.common.logging import watch
from mex.common.models import (
    ExtractedOrganizationalUnit,
    ExtractedPerson,
    ExtractedPrimarySource,
)


@watch
def transform_ldap_persons_to_mex_persons(
    ldap_persons: Iterable[LDAPPerson],
    primary_source: ExtractedPrimarySource,
    units: Iterable[ExtractedOrganizationalUnit],
) -> Generator[ExtractedPerson, None, None]:
    """Transform LDAP persons to ExtractedPersons.

    Args:
        ldap_persons: LDAP persons
        primary_source: Primary source for LDAP
        units: Extracted organizational units

    Returns:
        Generator for extracted persons
    """
    units_by_identifier_in_primary_source = {
        unit.identifierInPrimarySource: unit for unit in units
    }
    for person in ldap_persons:
        yield transform_ldap_person_to_mex_person(
            person, primary_source, units_by_identifier_in_primary_source
        )


@watch
def transform_ldap_persons_with_query_to_mex_persons(
    ldap_persons_with_query: Iterable[LDAPPersonWithQuery],
    primary_source: ExtractedPrimarySource,
    units: Iterable[ExtractedOrganizationalUnit],
) -> Generator[ExtractedPerson, None, None]:
    """Transform LDAP persons with query to ExtractedPersons.

    Args:
        ldap_persons_with_query: LDAP persons with query
        primary_source: Primary source for LDAP
        units: Extracted organizational units

    Returns:
        Generator for extracted persons
    """
    yield from transform_ldap_persons_to_mex_persons(
        (a.person for a in ldap_persons_with_query), primary_source, units
    )


def transform_ldap_person_to_mex_person(
    ldap_person: LDAPPerson,
    primary_source: ExtractedPrimarySource,
    units_by_identifier_in_primary_source: dict[str, ExtractedOrganizationalUnit],
) -> ExtractedPerson:
    """Transform a single LDAP person to an ExtractedPerson.

    Args:
        ldap_person: LDAP person
        primary_source: Primary source for LDAP
        units_by_identifier_in_primary_source: Mapping to get units by LDAP ID

    Returns:
        Extracted person
    """
    member_of = [
        unit.stableTargetId
        for d in (ldap_person.department, ldap_person.departmentNumber)
        if d and (unit := units_by_identifier_in_primary_source.get(d.lower()))
    ]
    if not member_of:
        raise MExError(
            "No unit or department found for LDAP department "
            f"'{ldap_person.department}' or departmentNumber "
            f"'{ldap_person.departmentNumber}'"
        )
    return ExtractedPerson(
        identifierInPrimarySource=str(ldap_person.objectGUID),
        hadPrimarySource=primary_source.stableTargetId,
        affiliation=None,  # TODO resolve organization for person.company/RKI
        email=ldap_person.mail,
        familyName=ldap_person.sn,
        fullName=ldap_person.displayName,
        givenName=ldap_person.givenName,
        isniId=None,
        memberOf=member_of,
        orcidId=None,
    )


@dataclass
class PersonName:
    """Name of a person split into sur- and given-name."""

    surname: str = "*"
    given_name: str = "*"
    full_name: str = ""


@cache
def analyse_person_string(string: str) -> list[PersonName]:
    """Try to extract a list of given- and surnames from a person string.

    For supported formats of this implementation, check unittest.

    Args:
        string: Person string, containing their name in some form

    Returns:
        List of analyzed person names
    """
    # remove string used to designate no person
    string = string.strip("-")
    # remove everything in brackets
    string = re.sub(r"\([^\)]*[\)$]", "", string)
    # remove tangling brackets
    string = re.sub(r"\(|\)", "", string)
    # remove titles case insensitive
    string = re.sub(r"(hr|fr|dr|med|prof|stellv)\.", "", string, flags=re.IGNORECASE)
    # remove some special keywords
    string = re.sub(r"(Abteilung|Projektleitung|Leitung)", "", string)
    # remove any word with numbers in it
    string = re.sub(r"\b([A-Z][a-zA-Z]*[0-9]+)\b", "", string)
    # remove any word all caps word with dot
    string = re.sub(r"\b([A-Z]+\.)", "", string)
    # remove any remaining numeric characters
    string = re.sub(r"[0-9]", "", string)
    # remove any padding spaces or commas
    string = string.strip(" ,")

    # split on forward slash or semicolon
    if len(split := re.split(r"/|;", string)) > 1:
        return [name for strings in split for name in analyse_person_string(strings)]

    # split on comma if there is more than one
    if len(split := re.split(r",", string)) > 2:
        return [name for strings in split for name in analyse_person_string(strings)]

    # split on single commas only if there are more than three words
    if len(split := re.split(r",", string)) == 2 and string.strip().count(" ") > 2:
        return [name for strings in split for name in analyse_person_string(strings)]

    # split into surname and given name
    if "," in string:
        # if we have a comma, use that to split
        split = list(reversed(string.split(",", maxsplit=1)))
    else:
        # if not, split on whitespace
        split = string.rsplit(maxsplit=1)

    # normalize multiple or padding whitespaces
    split = [" ".join(s.split()) for s in split if s.strip()]
    # re-assemble full name from split
    full_name = " ".join(split)

    # return only surname when given name is missing
    if len(split) == 1:
        return [PersonName(surname=split[0], full_name=full_name)]

    # return surname and given name
    if len(split) == 2:
        return [PersonName(surname=split[1], given_name=split[0], full_name=full_name)]

    # found noone
    return []
