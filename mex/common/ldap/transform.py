import re
from collections.abc import Iterable
from dataclasses import dataclass
from functools import lru_cache

from mex.common.ldap.models import LDAPActor, LDAPPerson, LDAPPersonWithQuery
from mex.common.logging import logger
from mex.common.models import (
    ExtractedContactPoint,
    ExtractedOrganizationalUnit,
    ExtractedPerson,
    ExtractedPrimarySource,
)


def transform_ldap_persons_to_mex_persons(
    ldap_persons: Iterable[LDAPPerson],
    primary_source: ExtractedPrimarySource,
    units: Iterable[ExtractedOrganizationalUnit],
) -> list[ExtractedPerson]:
    """Transform LDAP persons to ExtractedPersons.

    Args:
        ldap_persons: LDAP persons
        primary_source: Primary source for LDAP
        units: Extracted organizational units

    Returns:
        List of extracted persons
    """
    units_by_identifier_in_primary_source = {
        unit.identifierInPrimarySource: unit for unit in units
    }
    extracted_persons = [
        transform_ldap_person_to_mex_person(
            person, primary_source, units_by_identifier_in_primary_source
        )
        for person in ldap_persons
    ]
    logger.info("transformed %s extracted persons from ldap", len(extracted_persons))
    return extracted_persons


def transform_ldap_actors_to_mex_contact_points(
    ldap_actors: Iterable[LDAPActor],
    primary_source: ExtractedPrimarySource,
) -> list[ExtractedContactPoint]:
    """Transform LDAP actors (e.g. functional accounts) to ExtractedContactPoints.

    Args:
        ldap_actors: LDAP actors
        primary_source: Primary source for LDAP

    Returns:
        List of extracted contact points
    """
    extracted_contact_points = [
        transform_ldap_actor_to_mex_contact_point(actor, primary_source)
        for actor in ldap_actors
    ]
    logger.info(
        "transformed %s extracted contact points from ldap",
        len(extracted_contact_points),
    )
    return extracted_contact_points


def transform_ldap_persons_with_query_to_mex_persons(
    ldap_persons_with_query: Iterable[LDAPPersonWithQuery],
    primary_source: ExtractedPrimarySource,
    units: Iterable[ExtractedOrganizationalUnit],
) -> list[ExtractedPerson]:
    """Transform LDAP persons with query to ExtractedPersons.

    Args:
        ldap_persons_with_query: LDAP persons with query
        primary_source: Primary source for LDAP
        units: Extracted organizational units

    Returns:
        List of extracted persons
    """
    return transform_ldap_persons_to_mex_persons(
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
    return ExtractedPerson(
        identifierInPrimarySource=str(ldap_person.objectGUID),
        hadPrimarySource=primary_source.stableTargetId,
        affiliation=[],  # TODO(HS): resolve organization for person.company/RKI
        email=ldap_person.mail,
        familyName=[ldap_person.sn],
        fullName=[ldap_person.displayName] if ldap_person.displayName else [],
        givenName=ldap_person.givenName,
        isniId=[],
        memberOf=[
            unit.stableTargetId
            for d in (ldap_person.department, ldap_person.departmentNumber)
            if d and (unit := units_by_identifier_in_primary_source.get(d.lower()))
        ],
        orcidId=[],
    )


def transform_ldap_actor_to_mex_contact_point(
    ldap_actor: LDAPActor,
    primary_source: ExtractedPrimarySource,
) -> ExtractedContactPoint:
    """Transform a single LDAPActor (a functional account) to an ExtractedContactPoint.

    Args:
        ldap_actor: LDAP actor
        primary_source: Primary source for LDAP

    Returns:
        Extracted contact point
    """
    return ExtractedContactPoint(
        identifierInPrimarySource=str(ldap_actor.objectGUID),
        hadPrimarySource=primary_source.stableTargetId,
        email=ldap_actor.mail,
    )


@dataclass
class PersonName:
    """Name of a person split into sur- and given-name."""

    surname: str = "*"
    given_name: str = "*"
    full_name: str = ""


@lru_cache(maxsize=1024)
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
    if len(split := re.split(r",", string)) > 2:  # noqa: PLR2004
        return [name for strings in split for name in analyse_person_string(strings)]

    # split on single commas only if there are more than three words
    if len(split := re.split(r",", string)) == 2 and string.strip().count(" ") > 2:  # noqa: PLR2004
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
    if len(split) == 2:  # noqa: PLR2004
        return [PersonName(surname=split[1], given_name=split[0], full_name=full_name)]

    # found no one
    return []
