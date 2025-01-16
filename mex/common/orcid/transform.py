from typing import Any

from mex.common.models import (
    ExtractedPerson,
)
from mex.common.orcid.models.person import OrcidRecord
from mex.common.primary_source.helpers import get_all_extracted_primary_sources


def map_orcid_data_to_orcid_record(orcid_data: dict[str, Any]) -> OrcidRecord:
    """Wraps orcid data into an OrcidRecord."""
    return OrcidRecord.model_validate(orcid_data)


def transform_orcid_person_to_mex_person(
    orcid_record: OrcidRecord,
) -> ExtractedPerson:
    """Transforms a single ORCID person to an ExtractedPerson.

    Args:
        orcid_record: OrcidRecord object of a person.

    Returns:
        ExtractedPerson.
    """
    primary_source = get_all_extracted_primary_sources()["orcid"]
    had_primary_source = primary_source.stableTargetId

    id_in_primary_source = orcid_record.orcid_identifier.path
    email = orcid_record.person.emails.email[0].email
    given_names = orcid_record.person.name.given_names.value
    family_name = orcid_record.person.name.family_name.value
    orcid_id = orcid_record.orcid_identifier.uri

    return ExtractedPerson(
        identifierInPrimarySource=id_in_primary_source,
        hadPrimarySource=had_primary_source,
        givenName=given_names,
        familyName=family_name,
        orcidId=orcid_id,
        email=email,
    )
