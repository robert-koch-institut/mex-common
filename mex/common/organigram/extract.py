import json
from collections.abc import Iterable
from functools import lru_cache
from pathlib import Path

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


def get_extracted_unit_by_synonyms(
    extracted_units: Iterable[ExtractedOrganizationalUnit],
) -> dict[str, list[ExtractedOrganizationalUnit]]:
    """Return a mapping from unit alt_label and label to their organizational units.

    Multiple units can share the same synonym, all will be included in the list.

    Args:
        extracted_units: Iterable of extracted units

    Returns:
        Mapping from unit synonyms to list of extracted units
    """
    synonym_dict: dict[str, list[ExtractedOrganizationalUnit]] = {}
    for extracted_unit in extracted_units:
        for synonym in get_unit_synonyms(extracted_unit):
            if synonym not in synonym_dict:
                synonym_dict[synonym] = []
            if extracted_unit not in synonym_dict[synonym]:
                synonym_dict[synonym].append(extracted_unit)
    return synonym_dict


def get_unit_merged_ids_by_synonyms(
    extracted_units: Iterable[ExtractedOrganizationalUnit],
) -> dict[str, list[MergedOrganizationalUnitIdentifier]]:
    """Return a mapping from unit alt_label and label to their merged IDs.

    Multiple units can share the same synonym, all will be included in the list.

    Args:
        extracted_units: Iterable of extracted units

    Returns:
        Mapping from unit synonyms to list of stableTargetIds
    """
    unit_dict = get_extracted_unit_by_synonyms(extracted_units)
    return {
        key: [unit.stableTargetId for unit in units] for key, units in unit_dict.items()
    }


def get_unit_merged_ids_by_emails(
    extracted_units: Iterable[ExtractedOrganizationalUnit],
) -> dict[str, list[MergedOrganizationalUnitIdentifier]]:
    """Return a mapping from unit emails to their merged IDs.

    Multiple units can share the same email, all will be included in the list.

    Args:
        extracted_units: Iterable of extracted units

    Returns:
        Mapping from lowercased `email` to list of stableTargetIds
    """
    email_dict: dict[str, list[MergedOrganizationalUnitIdentifier]] = {}
    for extracted_unit in extracted_units:
        for email in extracted_unit.email:
            lower_email = email.lower()
            if lower_email not in email_dict:
                email_dict[lower_email] = []
            if extracted_unit.stableTargetId not in email_dict[lower_email]:
                email_dict[lower_email].append(extracted_unit.stableTargetId)
    return email_dict
