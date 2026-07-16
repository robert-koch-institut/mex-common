from mex.common.models import ExtractedOrganizationalUnit
from mex.common.organigram.helpers import (
    build_child_unit_map,
    get_all_descendant_unit_ids,
    get_extracted_organizational_unit_with_parents,
    get_first_level_child_unit_ids,
)
from mex.common.organigram.models import OrganigramUnit
from mex.common.types import MergedOrganizationIdentifier, MergedPrimarySourceIdentifier


def test_build_child_unit_map(
    child_unit: OrganigramUnit, parent_unit: OrganigramUnit
) -> None:
    test_map = build_child_unit_map(
        [child_unit, child_unit, parent_unit, child_unit, parent_unit]
    )

    assert test_map == {"parent-unit": ["child-unit", "child-unit", "child-unit"]}


def test_get_all_descendant_unit_ids(
    child_unit: OrganigramUnit, parent_unit: OrganigramUnit
) -> None:
    child_ids = get_all_descendant_unit_ids(
        [child_unit, child_unit, child_unit, parent_unit, parent_unit],
        str(parent_unit.identifier),
    )

    assert child_ids == [child_unit.identifier]


def test_get_first_level_child_unit_ids(
    child_unit: OrganigramUnit, parent_unit: OrganigramUnit
) -> None:
    child_ids = get_first_level_child_unit_ids(
        [child_unit, child_unit, child_unit, parent_unit, parent_unit],
        str(parent_unit.identifier),
    )

    assert child_ids == [child_unit.identifier]


def test_get_extracted_organizational_unit_with_parents(
    extracted_child_unit: ExtractedOrganizationalUnit,
    extracted_parent_unit: ExtractedOrganizationalUnit,
    extracted_primary_source_ids: dict[str, MergedPrimarySourceIdentifier],
    rki_organization_id: MergedOrganizationIdentifier,
) -> None:
    expected = {extracted_child_unit, extracted_parent_unit}
    returned = get_extracted_organizational_unit_with_parents(
        "CHLD Unterabteilung",
        extracted_primary_source_ids["organigram"],
        rki_organization_id,
    )
    assert set(returned) == expected
