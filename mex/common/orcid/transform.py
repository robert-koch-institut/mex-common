from collections.abc import Generator, Iterable  # noqa: F401

from mex.common.models import (
    ExtractedPerson,
)
from mex.common.orcid.models.person import OrcidPerson
from mex.common.primary_source.helpers import get_extracted_primary_source_by_name


def transform_orcid_person_to_mex_person(
    orcid_person: OrcidPerson,
) -> ExtractedPerson:
    """Transform a single orcid person to an ExtractedPerson.

    Args:
        orcid_person: Orcid person
        primary_source: Primary source for Orcid

    Returns:
        Extracted person
    """
    primary_source = get_extracted_primary_source_by_name("orcid")
    return ExtractedPerson(
        identifierInPrimarySource=orcid_person.path,
        hadPrimarySource=primary_source.stableTargetId
        if primary_source is not None
        else None,
        givenName=[orcid_person.name.given_names.value]
        if orcid_person.name.given_names
        else [],
        familyName=[orcid_person.name.family_name.value]
        if orcid_person.name.family_name
        else [],
        fullName=[
            f"""{orcid_person.name.given_names.value}
{orcid_person.name.family_name.value}"""
        ]
        if orcid_person.name.given_names and orcid_person.name.family_name
        else [],
        orcidId=[orcid_person.path] if orcid_person.path else [],
        email=[email.value for email in orcid_person.emails.email if email.value],
        isniId=[],
        affiliation=[],
        memberOf=[],
    )
