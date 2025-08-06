from mex.common.organigram.helpers import find_descendants
from mex.common.organigram.models import OrganigramUnit


def test_find_descendants(
    child_unit: OrganigramUnit, parent_unit: OrganigramUnit
) -> None:
    child_ids = find_descendants(
        [child_unit, child_unit, child_unit, parent_unit, parent_unit],
        str(parent_unit.identifier),
    )

    assert child_ids == [child_unit.identifier]
