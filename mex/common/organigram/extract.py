import json
from collections.abc import Iterable
from functools import lru_cache
from pathlib import Path

from mex.common.exceptions import MExError
from mex.common.logging import logger
from mex.common.models import ExtractedOrganizationalUnit
from mex.common.organigram.models import OrganigramUnit
from mex.common.settings import BaseSettings
from mex.common.types import MergedOrganizationalUnitIdentifier


@lru_cache(maxsize=1)
def extract_organigram_units() -> list[OrganigramUnit]:
    """Extract organizational units from the organigram JSON file.

    Settings:
        organigram_path: Resolved path to the organigram file

    Returns:
        List of organigram units
    """
    settings = BaseSettings.get()
    with Path(settings.organigram_path).open() as fh:
        raw_units = json.load(fh)
    logger.info("extracted %s organigram units", len(raw_units))
    return [OrganigramUnit.model_validate(raw) for raw in raw_units]


def get_unit_synonyms(extracted_unit: ExtractedOrganizationalUnit) -> list[str]:
    """Generate synonyms for a unit using its name fields.

    Args:
        extracted_unit: Extracted organizational unit

    Returns:
        Sorted list of unique unit synonyms
    """
    return sorted(
        {
            extracted_unit.identifierInPrimarySource,
            *(
                text.value
                for texts in [
                    extracted_unit.name,
                    extracted_unit.shortName,
                    extracted_unit.alternativeName,
                ]
                for text in texts
            ),
        }
    )


def get_unit_merged_ids_by_synonyms(
    extracted_units: Iterable[ExtractedOrganizationalUnit],
) -> dict[str, MergedOrganizationalUnitIdentifier]:
    """Return a mapping from unit alt_label and label to their merged IDs.

    There will be multiple entries per unit mapping to the same merged ID.

    Args:
        extracted_units: Iterable of extracted units

    Raises:
        MExError: If the same entry maps to different merged IDs

    Returns:
        Mapping from unit synonyms to stableTargetIds
    """
    synonym_dict: dict[str, MergedOrganizationalUnitIdentifier] = {}
    for extracted_unit in extracted_units:
        for synonym in get_unit_synonyms(extracted_unit):
            if (
                synonym in synonym_dict
                and synonym_dict[synonym] != extracted_unit.stableTargetId
            ):
                msg = (
                    f"Conflict: label '{synonym}' is associated with merged unit IDs "
                    f"{synonym_dict[synonym]} and {extracted_unit.stableTargetId}."
                )
                raise MExError(msg)
            synonym_dict[synonym] = extracted_unit.stableTargetId
    return synonym_dict


def get_unit_merged_ids_by_emails(
    extracted_units: Iterable[ExtractedOrganizationalUnit],
) -> dict[str, MergedOrganizationalUnitIdentifier]:
    """Return a mapping from unit emails to their merged IDs.

    There may be multiple emails per unit mapping to the same merged ID.

    Args:
        extracted_units: Iterable of extracted units

    Raises:
        MExError: If the same entry maps to different merged IDs

    Returns:
        Mapping from lowercased `email` to stableTargetIds
    """
    email_dict: dict[str, MergedOrganizationalUnitIdentifier] = {}
    for extracted_unit in extracted_units:
        for email in extracted_unit.email:
            lower_email = email.lower()
            if (
                lower_email in email_dict
                and email_dict[lower_email] != extracted_unit.stableTargetId
            ):
                msg = (
                    f"Conflict: email '{email}' is associated with merged unit IDs "
                    f"{email_dict[lower_email]} and {extracted_unit.stableTargetId}."
                )
                raise MExError(msg)
            email_dict[lower_email] = extracted_unit.stableTargetId
    return email_dict
