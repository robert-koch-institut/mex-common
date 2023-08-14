from mex.common.models.extracted_data import MEX_PRIMARY_SOURCE_STABLE_TARGET_ID
from mex.common.primary_source.extract import extract_seed_primary_sources
from mex.common.primary_source.transform import (
    transform_seed_primary_source_to_extracted_primary_sources,
)
from mex.common.testing import Joker
from mex.common.types import TextLanguage


def test_transform_mex_db_primary_source_to_extracted_primary_source() -> None:
    extracted_primary_source = next(
        transform_seed_primary_source_to_extracted_primary_sources(
            extract_seed_primary_sources()
        )
    )
    assert extracted_primary_source.dict(exclude_none=True, exclude_defaults=True) == {
        "hadPrimarySource": MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
        "identifier": Joker(),
        "identifierInPrimarySource": "mex",
        "stableTargetId": MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
        "title": [{"language": TextLanguage.EN, "value": "Metadata Exchange"}],
    }
