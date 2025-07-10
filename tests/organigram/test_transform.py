from mex.common.models import ExtractedPrimarySource
from mex.common.models.organization import ExtractedOrganization
from mex.common.organigram.models import OrganigramUnit
from mex.common.organigram.transform import (
    transform_organigram_units_to_organizational_units,
)
from mex.common.testing import Joker
from mex.common.types import LinkLanguage, Text, TextLanguage


def test_transform_organigram_units_to_organizational_units(
    child_unit: OrganigramUnit,
    parent_unit: OrganigramUnit,
    extracted_primary_sources: dict[str, ExtractedPrimarySource],
    rki_organization: ExtractedOrganization,
) -> None:
    extracted_units = transform_organigram_units_to_organizational_units(
        [child_unit, parent_unit],
        extracted_primary_sources["organigram"],
        rki_organization,
    )

    # look up by ids, because order is not guaranteed
    extracted_units_by_id = {u.identifierInPrimarySource: u for u in extracted_units}
    assert len(extracted_units_by_id) == 2
    child_extracted_unit = extracted_units_by_id["child-unit"]
    parent_extracted_unit = extracted_units_by_id["parent-unit"]

    # check parent relation is resolved
    assert parent_extracted_unit.parentUnit is None
    assert child_extracted_unit.parentUnit is not None
    assert child_extracted_unit.parentUnit == parent_extracted_unit.stableTargetId

    # check name languages are set
    assert child_extracted_unit.name == [
        Text(value="CHLD Unterabteilung", language=TextLanguage.DE),
        Text(value="C1: Sub Unit", language=TextLanguage.EN),
    ]

    # check serialized as expected
    assert parent_extracted_unit.model_dump(exclude_none=True) == {
        "identifier": Joker(),
        "hadPrimarySource": extracted_primary_sources["organigram"].stableTargetId,
        "identifierInPrimarySource": "parent-unit",
        "stableTargetId": Joker(),
        "alternativeName": [
            {"value": "PRNT Abteilung", "language": TextLanguage.DE},
            {"value": "PARENT Dept."},
        ],
        "email": ["pu@example.com", "PARENT@example.com"],
        "name": [
            {"value": "Abteilung", "language": TextLanguage.DE},
            {"value": "Department", "language": TextLanguage.EN},
        ],
        "shortName": [{"value": "PRNT"}],
        "unitOf": ["hDGPcPIlVrQZu9EbokVFmm"],
        "website": [
            {
                "language": LinkLanguage.EN,
                "title": "Example | Parent Department",
                "url": "https://www.example.com/departments/parent.html",
            }
        ],
        "entityType": "ExtractedOrganizationalUnit",
    }
