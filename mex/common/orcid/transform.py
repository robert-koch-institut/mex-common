from mex.common.models import ExtractedPerson
from mex.common.orcid.models import OrcidRecord
from mex.common.types import MergedPrimarySourceIdentifier


def transform_orcid_person_to_mex_person(
    orcid_record: OrcidRecord,
    primary_source_id: MergedPrimarySourceIdentifier,
) -> ExtractedPerson:
    """Transforms a single ORCID person to an ExtractedPerson.

    Args:
        orcid_record: OrcidRecord object of a person.
        primary_source_id: Primary source identifier for Orcid.

    Returns:
        ExtractedPerson.
    """
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
        hadPrimarySource=primary_source_id,
        givenName=given_names,
        familyName=family_name,
        fullName=full_name,
        orcidId=orcid_id,
        email=email,
    )
