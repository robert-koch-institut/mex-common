import pytest

from mex.common.exceptions import MExError
from mex.common.models import ExtractedOrganizationalUnit
from mex.common.organigram.extract import (
    extract_organigram_units,
    get_unit_merged_ids_by_emails,
    get_unit_merged_ids_by_synonyms,
)
from mex.common.organigram.models import OrganigramUnit
from mex.common.types import Email, Text


def test_extract_organigram_units(
    child_unit: OrganigramUnit, parent_unit: OrganigramUnit
) -> None:
    units = list(extract_organigram_units())
    assert units == [child_unit, parent_unit]


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
    erroneus_extracted_child_unit = extracted_child_unit
    erroneus_extracted_child_unit.name.append(Text(value="PARENT Dept."))

    msg = (
        f"MExError: Conflict: label 'PARENT Dept.' is associated with "
        f"merged unit IDs {erroneus_extracted_child_unit.stableTargetId} and "
        f"{extracted_parent_unit.stableTargetId}."
    )
    with pytest.raises(MExError, match=msg):
        get_unit_merged_ids_by_synonyms(
            [erroneus_extracted_child_unit, extracted_parent_unit]
        )


def test_get_unit_merged_ids_by_emails(
    extracted_child_unit: ExtractedOrganizationalUnit,
    extracted_parent_unit: ExtractedOrganizationalUnit,
) -> None:
    mapping = get_unit_merged_ids_by_emails(
        [extracted_child_unit, extracted_parent_unit]
    )
    assert mapping == {
        "parent@example.com": extracted_parent_unit.stableTargetId,
        "pu@example.com": extracted_parent_unit.stableTargetId,
        # child unit has no emails
    }


def test_get_unit_merged_ids_by_emails_error(
    extracted_child_unit: ExtractedOrganizationalUnit,
    extracted_parent_unit: ExtractedOrganizationalUnit,
) -> None:
    erroneus_extracted_child_unit = extracted_child_unit
    erroneus_extracted_child_unit.email.append(Email("PARENT@example.com"))

    msg = (
        f"MExError: Conflict: email 'PARENT@example.com' is associated with "
        f"merged unit IDs {erroneus_extracted_child_unit.stableTargetId} and "
        f"{extracted_parent_unit.stableTargetId}."
    )
    with pytest.raises(MExError, match=msg):
        get_unit_merged_ids_by_emails(
            [erroneus_extracted_child_unit, extracted_parent_unit]
        )
