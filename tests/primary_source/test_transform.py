import pytest

from mex.common.primary_source.extract import extract_mex_db_primary_source_by_id
from mex.common.primary_source.transform import (
    transform_mex_db_primary_source_to_extracted_primary_source,
)
from mex.common.testing import Joker
from mex.common.types import Identifier, LinkLanguage, TextLanguage


@pytest.mark.usefixtures("seed_test_primary_source")
def test_transform_mex_db_primary_source_to_extracted_primary_source(
    unit_merged_ids_by_synonym: dict[str, Identifier]
) -> None:
    mex_db_primary_source = extract_mex_db_primary_source_by_id("test-primary-source")
    extracted_primary_source = (
        transform_mex_db_primary_source_to_extracted_primary_source(
            mex_db_primary_source=mex_db_primary_source,
            unit_merged_ids_by_synonym=unit_merged_ids_by_synonym,
        )
    )

    assert extracted_primary_source.dict(exclude_none=True) == {
        "identifier": Joker(),
        "hadPrimarySource": "bFQoRhcVH5DHUq",
        "identifierInPrimarySource": "test-primary-source",
        "stableTargetId": Joker(),
        "alternativeTitle": [{"value": "PM"}],
        "contact": [],
        "description": [
            {"value": "Probenmaterial Description", "language": TextLanguage.DE}
        ],
        "documentation": [
            {
                "language": LinkLanguage.DE,
                "title": "Probenmaterial Docs",
                "url": "https://probenmaterial.test/docs",
            },
            {
                "language": LinkLanguage.EN,
                "title": "Probenmaterial Docs Eng",
                "url": "https://probenmaterial.test/docs_en",
            },
        ],
        "locatedAt": [
            {
                "language": LinkLanguage.DE,
                "title": "Probenmaterial",
                "url": "https://probenmaterial.test",
            },
            {
                "language": LinkLanguage.EN,
                "title": "Test Material",
                "url": "https://probenmaterial.test/en",
            },
        ],
        "title": [{"value": "Probenmaterial", "language": TextLanguage.DE}],
        "unitInCharge": [Joker()],
        "version": "1.29",
    }
