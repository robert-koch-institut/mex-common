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

_OrganizationalUnit = TypeVar(
    "_OrganizationalUnit",
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


def find_descendants(items: list[_OrganizationalUnit], parent_id: str) -> list[str]:
    """Finds ids of all descendant (great{n}/grand/child) units for a parent unit id.

    Args:
        items: list of organizational units (Extracted, Merged, or OrganigramUnit)
                in which to search for descendants
        parent_id: identifier of the parent unit

    Returns:
        list of all unique descendant organizational unit ids (children,
                grandchildren, ...), excluding the starting parent_id
    """

    def build_child_map(items: list[_OrganizationalUnit]) -> dict[str, list[str]]:
        """Builds a dictionary with all children per unit from a list of units."""
        child_map: dict[str, list[str]] = {}
        for item in items:
            if item.parentUnit is not None:
                child_map.setdefault(str(item.parentUnit), []).append(
                    str(item.identifier)
                )
        return child_map

    def collect_descendants(
        child_map: dict[str, list[str]],
        node: str,
        descendants: set[str],
    ) -> None:
        """Starting from any parent unit the children are collected.

        This functions collects children and their children and their children ...
        (recursion, depth first).
        """
        for child_id in child_map.get(node, []):
            descendants.add(child_id)
            collect_descendants(child_map, child_id, descendants)

    child_map = build_child_map(items)

    descendants: set[str] = set()
    collect_descendants(child_map, str(parent_id), descendants)
    return list(descendants)
