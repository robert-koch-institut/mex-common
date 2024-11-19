from collections.abc import Generator, Iterable  # noqa: F401

from mex.common.models import (
    ExtractedPerson,  # noqa: F401
    ExtractedPrimarySource,  # noqa: F401
)
from mex.common.orcid.models.person import OrcidPerson  # noqa: F401

'''def transform_orcid_persons_to_extracted_persons(
    orcid_persons: Iterable[OrcidPerson],
    primary_source: ExtractedPrimarySource,
) -> Generator[ExtractedPerson, None, None]:
    """Transform OrcidPersons to ExtractedPersons.

    Args:
        orcid_persons: OrcidPersons to transform
        primary_source: Primary source for Orcid data

    Returns:
        Generator for ExtractedPersons
    """
    for person in orcid_persons:
        yield transform_orcid_person_to_extracted_person(person, primary_source)'''


'''def transform_orcid_person_to_extracted_person(
    orcid_person: OrcidPerson,
    primary_source: ExtractedPrimarySource,  # noqa: ARG001
) -> ExtractedPerson:
    """Transform a single OrcidPerson to an ExtractedPerson.

    Args:
        orcid_person: OrcidPerson object
        primary_source: Primary source for Orcid data

    Returns:
        ExtractedPerson object
    """
    # Get the member of organization (e.g., company or organizational unit)
    extract_member_of(orcid_person)

    # Create an ExtractedPerson instance
    return ExtractedPerson(
        identifierInPrimarySource=orcid_person.name.created_date.value,
        hadPrimarySource=primary_source.stableTargetId,
        affiliation=[orcid_person.biography.value] if orcid_person.biography else [],
        email=[email.email for email in orcid_person.emails.email] ,
        familyName=[orcid_person.name.family_name.value],
        fullName=[orcid_person.name.full_name],
        givenName=[orcid_person.name.given_names.value],
        isniId=[],
        memberOf=member_of,
        orcidId=[orcid_person.path] if orcid_person.path else []
    )'''


'''def extract_member_of(orcid_person: OrcidPerson) -> list[str]:
    """Helper function to extract organizational unit information for memberOf.

    Args:
        orcid_person: OrcidPerson object

    Returns:
        List of organization identifiers or names
    """
    # This is just an example; adjust it as needed based on the OrcidPerson structure
    # Here we're assuming that the OrcidPerson might have some organizational data
    member_of = []
    if orcid_person.researcher_urls.researcher_url:
        member_of = [url.value for url in orcid_person.researcher_urls.researcher_url]
    return member_of'''
