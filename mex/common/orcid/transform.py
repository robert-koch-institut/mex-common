from mex.common.models import ExtractedPerson, ExtractedPrimarySource
from mex.common.orcid.models import OrcidRecord


def transform_orcid_person_to_mex_person(
    orcid_record: OrcidRecord,
    primary_source: ExtractedPrimarySource,
) -> ExtractedPerson:
    """Transforms a single ORCID person to an ExtractedPerson.

    Args:
        orcid_record: OrcidRecord object of a person.
        primary_source: Primary source for Orcid.

    Returns:
        ExtractedPerson.
    """
    had_primary_source = primary_source.stableTargetId
    id_in_primary_source = orcid_record.orcid_identifier.path
    orcid_id = orcid_record.orcid_identifier.uri
    email = [e for emails in orcid_record.person.emails.email for e in emails.email]
    name = orcid_record.person.name
    given_names = None
    family_name = None
    full_name = None
    if name.visibility == "public":
        if name.given_names:
            given_names = name.given_names.value
        if name.family_name:
            family_name = name.family_name.value
    if family_name and given_names:
        full_name = f"{family_name}, {given_names}"
    else:
        full_name = family_name or given_names

    return ExtractedPerson(
        identifierInPrimarySource=id_in_primary_source,
        hadPrimarySource=had_primary_source,
        givenName=given_names,
        familyName=family_name,
        fullName=full_name,
        orcidId=orcid_id,
        email=email,
    )
