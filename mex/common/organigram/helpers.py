from collections.abc import Generator
from typing import TypeVar

from mex.common.exceptions import MExError
from mex.common.logging import logger
from mex.common.models import (
    ExtractedOrganizationalUnit,
    ExtractedPrimarySource,
    MergedOrganizationalUnit,
)
from mex.common.models.organization import ExtractedOrganization
from mex.common.organigram.extract import extract_organigram_units
from mex.common.organigram.models import OrganigramUnit
from mex.common.organigram.transform import (
    transform_organigram_unit_to_extracted_organizational_unit,
)
from mex.common.types import MergedOrganizationalUnitIdentifier

_TOrganizationalUnit = TypeVar(
    "_TOrganizationalUnit",
    MergedOrganizationalUnit,
    ExtractedOrganizationalUnit,
    OrganigramUnit,
)


def get_extracted_organizational_unit_with_parents(
    name: str,
    primary_source: ExtractedPrimarySource,
    rki_organization: ExtractedOrganization,
) -> list[ExtractedOrganizationalUnit]:
    """Pick the unit with the given name and transform it along with its parents.

    Args:
        name: Name (`identifierInPrimarySource`) of the organigram unit
        primary_source: Extracted primary source for the organigram
        rki_organization: RKI organization to which the unit belongs

    Returns:
        ExtractedOrganizationalUnit with its parents
    """
    organigram_units = extract_organigram_units()

    def with_parents(n: str) -> Generator[OrganigramUnit, None, None]:
        for unit in organigram_units:
            if n == unit.identifier or n in (
                t.value
                for texts in (unit.name, unit.shortName, unit.alternativeName)
                for t in texts
            ):
                yield unit
                if unit.parentUnit:
                    yield from with_parents(unit.parentUnit)
                break
        else:
            msg = f"could not find unit for {name}"
            raise MExError(msg)

    organigram_unit_with_parents = list(with_parents(name))
    extracted_unit_by_id_in_primary_source: dict[str, ExtractedOrganizationalUnit] = {}
    parent_id_in_primary_source_by_id_in_primary_source: dict[str, str] = {}

    for unit in organigram_unit_with_parents:
        extracted_unit = transform_organigram_unit_to_extracted_organizational_unit(
            unit, primary_source, rki_organization
        )
        extracted_unit_by_id_in_primary_source[unit.identifier] = extracted_unit
        if parent_identifier_in_primary_source := unit.parentUnit:
            parent_id_in_primary_source_by_id_in_primary_source[unit.identifier] = (
                parent_identifier_in_primary_source
            )

    for extracted_unit in extracted_unit_by_id_in_primary_source.values():
        identifier_in_primary_source = extracted_unit.identifierInPrimarySource
        if (  # noqa: SIM102
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
    logger.info(
        "transformed %s organizational units",
        len(extracted_unit_by_id_in_primary_source),
    )
    return list(extracted_unit_by_id_in_primary_source.values())


def build_child_map(units: list[_TOrganizationalUnit]) -> dict[str, list[str]]:
    """Builds a dictionary with all children per unit from a list of units.

    Args:
        units: list of organizational units (Extracted, Merged, or OrganigramUnit)

    Returns:
        dict[str, list[str]]: Dictionary with a list of all child unit ids by unit id
    """
    child_map: dict[str, list[str]] = {}
    for unit in units:
        if unit.parentUnit is not None:
            child_map.setdefault(str(unit.parentUnit), []).append(str(unit.identifier))
    return child_map


def _collect_descendants(
    child_map: dict[str, list[str]],
    unit_id: str,
    descendant_ids: set[str],
) -> None:
    """Recursion to collect all children and their children, etc., depth first.

    Args:
        child_map: Dictionary with all child units of a unit by unit id
        unit_id: Unit identifier
        descendant_ids: Set of all descendant units

    Returns:
        None, the set descendant_ids is mutated in-place
    """
    for child_id in child_map.get(unit_id, []):
        descendant_ids.add(child_id)
        _collect_descendants(child_map, child_id, descendant_ids)


def find_descendants(units: list[_TOrganizationalUnit], parent_id: str) -> list[str]:
    """Find ids of all descendant (great{n}/grand/child) units for any parent unit id.

    Args:
        units: list of organizational units (Extracted, Merged, or OrganigramUnit)
                in which to search for descendants
        parent_id: identifier of the parent unit

    Returns:
        list of all unique descendant organizational unit ids (children,
                grandchildren, ...), excluding the starting parent_id
    """
    child_map = build_child_map(units)
    descendant_ids: set[str] = set()

    _collect_descendants(child_map, str(parent_id), descendant_ids)
    return list(descendant_ids)
