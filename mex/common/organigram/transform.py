from collections.abc import Iterable

from mex.common.identity import get_provider
from mex.common.logging import logger
from mex.common.models import (
    ExtractedOrganizationalUnit,
)
from mex.common.organigram.models import OrganigramUnit
from mex.common.types import (
    MergedOrganizationalUnitIdentifier,
    MergedOrganizationIdentifier,
    MergedPrimarySourceIdentifier,
)


def transform_organigram_unit_to_extracted_organizational_unit(
    organigram_unit: OrganigramUnit,
    primary_source_id: MergedPrimarySourceIdentifier,
    rki_organization_id: MergedOrganizationIdentifier,
    parent_unit: MergedOrganizationalUnitIdentifier | None = None,
) -> ExtractedOrganizationalUnit:
    """Transform an organigram unit into an ExtractedOrganizationalUnit.

    Args:
        organigram_unit: Iterable of organigram units coming from the JSON file
        primary_source_id: Primary source identifier for organigram
        rki_organization_id: identifier of RKI organization to which the unit belongs
        parent_unit: stable target id of the parent unit, if any

    Returns:
        ExtractedOrganizationalUnit
    """
    return ExtractedOrganizationalUnit(
        identifierInPrimarySource=organigram_unit.identifier,
        hadPrimarySource=primary_source_id,
        alternativeName=organigram_unit.alternativeName,
        unitOf=[rki_organization_id],
        email=organigram_unit.email,
        name=organigram_unit.name,
        parentUnit=parent_unit,
        shortName=organigram_unit.shortName,
        website=[organigram_unit.website] if organigram_unit.website else [],
    )


def transform_organigram_units_to_organizational_units(
    organigram_units: Iterable[OrganigramUnit],
    primary_source_id: MergedPrimarySourceIdentifier,
    rki_organization_id: MergedOrganizationIdentifier,
) -> list[ExtractedOrganizationalUnit]:
    """Transform organigram units into ExtractedOrganizationalUnits.

    Beware that the order of the output is not necessarily the order of the input.

    Args:
        organigram_units: Iterable of organigram units coming from the JSON file
        primary_source_id: Primary source for organigram
        rki_organization_id: identifier of RKI organization to which the units belong

    Returns:
        List of ExtractedOrganizationalUnit
    """
    organigram_unit_by_id_in_primary_source = {
        unit.identifier: unit for unit in organigram_units
    }
    identity_provider = get_provider()
    extracted_units = [
        transform_organigram_unit_to_extracted_organizational_unit(
            unit,
            primary_source_id,
            rki_organization_id,
            parent_unit=MergedOrganizationalUnitIdentifier(
                identity_provider.assign(
                    primary_source_id, unit.parentUnit
                ).stableTargetId
            )
            if unit.parentUnit in organigram_unit_by_id_in_primary_source
            else None,
        )
        for unit in organigram_unit_by_id_in_primary_source.values()
    ]
    logger.info("transformed %s organizational units", len(extracted_units))
    return extracted_units
