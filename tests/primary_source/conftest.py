import pytest

from mex.common.organigram.extract import (
    extract_oranigram_units,
    get_unit_merged_ids_by_synonyms,
)
from mex.common.organigram.transform import (
    transform_organigram_units_to_organizational_units,
)
from mex.common.testing import insert_test_primary_sources_into_db
from mex.common.types import OrganizationalUnitID


@pytest.fixture()
def seed_test_primary_source() -> None:
    """Seed test primary source data into temp database."""
    insert_test_primary_sources_into_db("test-primary-source")


@pytest.fixture()
def unit_merged_ids_by_synonym() -> dict[str, OrganizationalUnitID]:
    """Extract and return all organigram units."""
    organigram_units = extract_oranigram_units()
    mex_organizational_units = transform_organigram_units_to_organizational_units(
        organigram_units
    )
    return get_unit_merged_ids_by_synonyms(mex_organizational_units)
