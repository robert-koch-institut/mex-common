from collections.abc import Generator, Iterable

from mex.common.logging import watch
from mex.common.models import ExtractedOrganizationalUnit, ExtractedPrimarySource
from mex.common.organigram.models import OrganigramUnit
from mex.common.types import Email, MergedOrganizationalUnitIdentifier


@watch
def transform_organigram_units_to_organizational_units(
    units: Iterable[OrganigramUnit], primary_source: ExtractedPrimarySource
) -> Generator[ExtractedOrganizationalUnit, None, None]:
    """Transform organigram units into ExtractedOrganizationalUnits.

    Beware that the order of the output is not necessarily the order of the input.

    Args:
        units: Iterable of organigram units coming from the JSON file
        primary_source: Primary source for organigram

    Returns:
        Generator for ExtractedOrganizationalUnit
    """
    extracted_unit_by_id_in_primary_source: dict[str, ExtractedOrganizationalUnit] = {}
    parent_id_in_primary_source_by_id_in_primary_source: dict[str, str] = {}

    for unit in units:
        extracted_unit = ExtractedOrganizationalUnit(
            identifierInPrimarySource=unit.identifier,
            hadPrimarySource=primary_source.stableTargetId,
            alternativeName=unit.alternativeName if unit.alternativeName else [],
            email=[Email(email) for email in unit.email],
            name=unit.name,
            shortName=unit.shortName,
            website=[unit.website] if unit.website else [],
        )
        extracted_unit_by_id_in_primary_source[unit.identifier] = extracted_unit
        if parent_identifier_in_primary_source := unit.parentUnit:
            parent_id_in_primary_source_by_id_in_primary_source[unit.identifier] = (
                parent_identifier_in_primary_source
            )

    for extracted_unit in extracted_unit_by_id_in_primary_source.values():
        identifier_in_primary_source = extracted_unit.identifierInPrimarySource
        if (
            parent_identifier_in_primary_source
            := parent_id_in_primary_source_by_id_in_primary_source.get(
                identifier_in_primary_source
            )
        ):
            if parent_unit := extracted_unit_by_id_in_primary_source.get(
                parent_identifier_in_primary_source
            ):
                extracted_unit.parentUnit = MergedOrganizationalUnitIdentifier(
                    parent_unit.stableTargetId
                )
        yield extracted_unit
