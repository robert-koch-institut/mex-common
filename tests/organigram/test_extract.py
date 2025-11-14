import pytest

from mex.common.exceptions import MExError
from mex.common.models import ExtractedOrganizationalUnit
from mex.common.organigram.extract import (
    extract_organigram_units,
    get_extracted_unit_by_synonyms,
    get_unit_merged_ids_by_emails,
    get_unit_merged_ids_by_synonyms,
)
from mex.common.organigram.models import OrganigramUnit
from mex.common.types import Text


def test_extract_organigram_units(
    child_unit: OrganigramUnit, parent_unit: OrganigramUnit
) -> None:
    units = list(extract_organigram_units())
    assert units == [child_unit, parent_unit]


def test_get_extracted_unit_by_synonyms(
    extracted_child_unit: ExtractedOrganizationalUnit,
    extracted_parent_unit: ExtractedOrganizationalUnit,
) -> None:
    mapping = get_extracted_unit_by_synonyms(
        [extracted_child_unit, extracted_parent_unit]
    )

    assert mapping["Abteilung"].stableTargetId == extracted_parent_unit.stableTargetId
    assert mapping["C1"].stableTargetId == extracted_child_unit.stableTargetId


def test_get_unit_merged_ids_by_synonyms(
    extracted_child_unit: ExtractedOrganizationalUnit,
    extracted_parent_unit: ExtractedOrganizationalUnit,
) -> None:
    mapping = get_unit_merged_ids_by_synonyms(
        [extracted_child_unit, extracted_parent_unit]
    )
    child_id = extracted_child_unit.stableTargetId
    parent_id = extracted_parent_unit.stableTargetId
    assert mapping == {
        "Abteilung": parent_id,
        "C1": child_id,
        "C1 Sub-Unit": child_id,
        "C1 Unterabteilung": child_id,
        "C1: Sub Unit": child_id,
        "CHLD": child_id,
        "CHLD Unterabteilung": child_id,
        "child-unit": child_id,
        "Department": parent_id,
        "PARENT Dept.": parent_id,
        "PRNT": parent_id,
        "PRNT Abteilung": parent_id,
        "parent-unit": parent_id,
    }


def test_get_unit_merged_ids_by_synonyms_error(
    extracted_child_unit: ExtractedOrganizationalUnit,
    extracted_parent_unit: ExtractedOrganizationalUnit,
) -> None:
    erroneous_extracted_child_unit = extracted_child_unit
    erroneous_extracted_child_unit.name.append(Text(value="PARENT Dept."))

    msg = (
        f"MExError: Conflict: label 'PARENT Dept.' is associated with "
        f"merged unit IDs {erroneous_extracted_child_unit.stableTargetId} and "
        f"{extracted_parent_unit.stableTargetId}."
    )
    with pytest.raises(MExError, match=msg):
        get_extracted_unit_by_synonyms(
            [erroneous_extracted_child_unit, extracted_parent_unit]
        )


def test_get_unit_merged_ids_by_emails(
    extracted_child_unit: ExtractedOrganizationalUnit,
    extracted_parent_unit: ExtractedOrganizationalUnit,
) -> None:
    mapping = get_unit_merged_ids_by_emails(
        [extracted_child_unit, extracted_parent_unit]
    )
    assert mapping == {
        "parent@example.com": [extracted_parent_unit.stableTargetId],
        "pu@example.com": [extracted_parent_unit.stableTargetId],
        # child unit has no emails
    }


def test_get_unit_merged_ids_by_emails_multiple_units_same_email(
    extracted_child_unit: ExtractedOrganizationalUnit,
    extracted_parent_unit: ExtractedOrganizationalUnit,
) -> None:
    """Test that multiple units with the same email are all included in the list."""
    extracted_child_unit.email = ["shared@example.com"]
    extracted_parent_unit.email = ["shared@example.com", "parent@example.com"]

    mapping = get_unit_merged_ids_by_emails(
        [extracted_child_unit, extracted_parent_unit]
    )

    assert "shared@example.com" in mapping
    assert len(mapping["shared@example.com"]) == 2
    assert extracted_child_unit.stableTargetId in mapping["shared@example.com"]
    assert extracted_parent_unit.stableTargetId in mapping["shared@example.com"]

    assert mapping["parent@example.com"] == [extracted_parent_unit.stableTargetId]
