from typing import Generator, Iterable

from mex.common.logging import watch
from mex.common.models import ExtractedOrganizationalUnit
from mex.common.organigram.models import OrganigramUnit
from mex.common.types import Identifier, OrganizationalUnitID, Text, TextLanguage


@watch
def transform_organigram_units_to_organizational_units(
    units: Iterable[OrganigramUnit],
) -> Generator[ExtractedOrganizationalUnit, None, None]:
    """Transform organigram units into ExtractedOrganizationalUnit .

    Args:
        units: Iterable of organigram units coming from the JSON file

    Returns:
        Generator for ExtractedOrganizationalUnit
    """
    extracted_unit_by_id_in_primary_source: dict[str, ExtractedOrganizationalUnit] = {}
    parent_id_in_primary_source_by_id_in_primary_source: dict[str, str] = {}

    for unit in units:
        extracted_unit = ExtractedOrganizationalUnit(
            identifierInPrimarySource=unit.identifier,
            hadPrimarySource=Identifier.generate(seed=0),  # TODO stopgap mx-603
            alternativeName=unit.alternativeName,
            email=unit.email,
            name=[
                Text(value=unit.name.de, language=TextLanguage.DE),
                Text(value=unit.name.en, language=TextLanguage.EN),
            ],
            shortName=unit.shortName,
            website=unit.website.url if unit.website else None,  # XXX ignore title
        )
        extracted_unit_by_id_in_primary_source[unit.identifier] = extracted_unit
        if parent_identifier_in_primary_source := unit.parentUnit:
            parent_id_in_primary_source_by_id_in_primary_source[
                unit.identifier
            ] = parent_identifier_in_primary_source

    for extracted_unit in extracted_unit_by_id_in_primary_source.values():
        identifier_in_primary_source = extracted_unit.identifierInPrimarySource
        if parent_identifier_in_primary_source := parent_id_in_primary_source_by_id_in_primary_source.get(
            identifier_in_primary_source
        ):
            if parent_unit := extracted_unit_by_id_in_primary_source.get(
                parent_identifier_in_primary_source
            ):
                extracted_unit.parentUnit = OrganizationalUnitID(
                    parent_unit.stableTargetId
                )
        yield extracted_unit
