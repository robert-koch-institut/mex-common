import pytest

from mex.common.models import ExtractedOrganizationalUnit
from mex.common.organigram.models import OrganigramName, OrganigramUnit
from mex.common.organigram.transform import (
    transform_organigram_units_to_organizational_units,
)
from mex.common.types import Link


@pytest.fixture
def child_unit() -> OrganigramUnit:
    """Return a child unit corresponding to the test_data."""
    return OrganigramUnit(
        shortName="C1",
        alternativeName=["CHLD", "C1 Sub-Unit", "C1 Unterabteilung"],
        identifier="child-unit",
        name=OrganigramName(de="CHLD Unterabteilung", en="C1: Sub Unit"),
        parentUnit="parent-unit",
    )


@pytest.fixture
def extracted_child_unit(child_unit: OrganigramUnit) -> ExtractedOrganizationalUnit:
    """Return the child unit transformed to an ExtractedOrganizationalUnit."""
    return next(transform_organigram_units_to_organizational_units([child_unit]))


@pytest.fixture
def parent_unit() -> OrganigramUnit:
    """Return a parent unit corresponding to the test_data."""
    return OrganigramUnit(
        shortName="PRNT",
        alternativeName=["PRNT Abteilung", "PARENT Dept."],
        identifier="parent-unit",
        name=OrganigramName(de="Abteilung", en="Department"),
        email=["pu@example.com", "PARENT@example.com"],
        website=Link(
            language="en",
            title="Example | Parent Department",
            url="https://www.example.com/departments/parent.html",
        ),
    )


@pytest.fixture
def extracted_parent_unit(parent_unit: OrganigramUnit) -> ExtractedOrganizationalUnit:
    """Return the parent unit transformed to an ExtractedOrganizationalUnit."""
    return next(transform_organigram_units_to_organizational_units([parent_unit]))
