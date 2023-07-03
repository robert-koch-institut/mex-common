import pytest

from mex.common.primary_source.extract import (
    extract_mex_db_primary_source_by_id,
    insert_primary_source_into_db,
)
from mex.common.primary_source.models import SeedPrimarySource


def test_insert_primary_source_into_db() -> None:
    seed_primary_source = SeedPrimarySource(
        identifier="test-primary-source",
        alternative_title=['{"value": "PM"}'],
        contact=["baakXOQk23Yerq"],
        description=['{"language": "de", "value": "Probenmaterial Description"}'],
        documentation=[
            '{"language": "de", "title": "Probenmaterial Docs", "url": "https://probenmaterial.test/docs"}'
        ],
        located_at=[
            '{"language": "de", "title": "Probenmaterial", "url": "https://probenmaterial.test"}'
        ],
        title=['{"language": "de", "value": "Probenmaterial"}'],
        unit_in_charge=["PRNT"],
        version="1.29",
    )

    insert_primary_source_into_db(seed_primary_source)

    dummy_primary_source = extract_mex_db_primary_source_by_id("test-primary-source")

    assert dummy_primary_source.identifier == seed_primary_source.identifier


@pytest.mark.usefixtures("seed_test_primary_source")
def test_extract_mex_db_primary_source_by_id() -> None:
    mex_db_primary_source = extract_mex_db_primary_source_by_id("test-primary-source")

    assert mex_db_primary_source.identifier == "test-primary-source"
    assert len(mex_db_primary_source.contacts) == 1
