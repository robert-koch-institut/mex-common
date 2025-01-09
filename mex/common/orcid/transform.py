from typing import Any

from pydantic import ValidationError

from mex.common.models import (
    ExtractedPerson,
)
from mex.common.orcid.models.person import FamilyName, GivenNames, OrcidPerson
from mex.common.primary_source.helpers import get_all_extracted_primary_sources


def reduce_metadata(orcid_data: dict[str, Any]) -> dict[str, Any]:
    """Reduces metadata based on mex assets mapping.

    If the ORCID person's name visibility is "public", returns the email, full name
    and ORCID ID.
    If the name is not public, returns only the email and ORCID ID.
    Returns None dict when orcid person is not exising.

    Args:
        orcid_data: Retrieved data from orcid.

    Returns:
        dict: Simplified metadata with email, name and ORCID ID.
    """
    if orcid_data == {"result": None, "num-found": 0}:
        return orcid_data
    is_public = orcid_data["person"]["name"]["visibility"]
    return {
        "orcid-identifier": {
            "path": orcid_data["orcid-identifier"]["path"],
        },
        "person": {
            "name": {
                "given-names": orcid_data["person"]["name"]["given-names"]
                if is_public
                else None,
                "family-name": orcid_data["person"]["name"]["family-name"]
                if is_public
                else None,
                "visibility": orcid_data["person"]["name"]["visibility"],
            },
            "emails": orcid_data["person"]["emails"],
        },
    }


def map_to_orcid_person(orcid_data: dict[str, Any]) -> OrcidPerson:
    """Maps retrieved orcid data to OrcidPerson model.

    Args:
        orcid_data: Input data containing ORCID data by a single person.

    Returns:
        Mapped OrcidPerson.
    """
    try:
        orcid_person = OrcidPerson(
            orcid_identifier=orcid_data["orcid-identifier"]["path"],
            email=orcid_data["person"].get("emails", {}).get("email", []),
            given_names=GivenNames(
                given_names=orcid_data["person"]["name"]["given-names"]["value"],
                visibility=orcid_data["person"]["name"].get("visibility"),
            ),
            family_name=FamilyName(
                family_name=orcid_data["person"]["name"]["family-name"]["value"],
                visibility=orcid_data["person"]["name"].get("visibility"),
            ),
        )
    except (KeyError, ValidationError) as e:
        msg = f"Error mapping data to OrcidPerson: {e}"
        raise ValueError(msg) from e
    return orcid_person


def transform_orcid_person_to_mex_person(
    orcid_person: OrcidPerson,
) -> ExtractedPerson:
    """Transforms a single ORCID person to an ExtractedPerson.

    Args:
        orcid_person: OrcidPerson.

    Returns:
        ExtractedPerson.
    """
    primary_source = get_all_extracted_primary_sources()["orcid"]
    had_primary_source = primary_source.stableTargetId

    id_in_primary_source = orcid_person.orcid_identifier
    email = orcid_person.email
    given_names = orcid_person.given_names.given_names
    family_name = orcid_person.family_name.family_name
    orcid_id = f"https://orcid.org/{orcid_person.orcid_identifier}"

    return ExtractedPerson(
        identifierInPrimarySource=id_in_primary_source,
        hadPrimarySource=had_primary_source,
        givenName=given_names,
        familyName=family_name,
        orcidId=orcid_id,
        email=email,
    )
