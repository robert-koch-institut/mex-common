import pytest

from mex.common.models import ExtractedOrganizationalUnit, ExtractedPrimarySource
from mex.common.organigram.models import OrganigramUnit
from mex.common.organigram.transform import (
    transform_organigram_units_to_organizational_units,
)
from mex.common.types import Link, LinkLanguage, Text


@pytest.fixture
def child_unit() -> OrganigramUnit:
    """Return a child unit corresponding to the test_data."""
    return OrganigramUnit(
        shortName=[Text(value="C1")],
        alternativeName=[
            Text(value="CHLD"),
            Text(value="C1 Sub-Unit"),
            Text(value="C1 Unterabteilung"),
        ],
        identifier="child-unit",
        name=[
            Text(value="CHLD Unterabteilung", language="de"),
            Text(value="C1: Sub Unit", language="en"),
        ],
        parentUnit="parent-unit",
        website=None,
    )


@pytest.fixture
def extracted_child_unit(
    child_unit: OrganigramUnit,
    extracted_primary_sources: dict[str, ExtractedPrimarySource],
) -> ExtractedOrganizationalUnit:
    """Return the child unit transformed to an ExtractedOrganizationalUnit."""
    return next(
        transform_organigram_units_to_organizational_units(
            [child_unit], extracted_primary_sources["organigram"]
        )
    )


@pytest.fixture
def parent_unit() -> OrganigramUnit:
    """Return a parent unit corresponding to the test_data."""
    return OrganigramUnit(
        shortName=[Text(value="PRNT")],
        alternativeName=[Text(value="PRNT Abteilung"), Text(value="PARENT Dept.")],
        identifier="parent-unit",
        name=[
            Text(value="Abteilung", language="de"),
            Text(value="Department", language="en"),
        ],
        email=["pu@example.com", "PARENT@example.com"],
        website=Link(
            language=LinkLanguage.EN,
            title="Example | Parent Department",
            url="https://www.example.com/departments/parent.html",
        ),
        parentUnit=None,
    )


@pytest.fixture
def extracted_parent_unit(
    parent_unit: OrganigramUnit,
    extracted_primary_sources: dict[str, ExtractedPrimarySource],
) -> ExtractedOrganizationalUnit:
    """Return the parent unit transformed to an ExtractedOrganizationalUnit."""
    return next(
        transform_organigram_units_to_organizational_units(
            [parent_unit], extracted_primary_sources["organigram"]
        )
    )
