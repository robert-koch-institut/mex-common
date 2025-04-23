from mex.common.models import MEX_PRIMARY_SOURCE_STABLE_TARGET_ID
from mex.common.primary_source.extract import extract_seed_primary_sources
from mex.common.primary_source.transform import (
    transform_seed_primary_sources_to_extracted_primary_sources,
)
from mex.common.testing import Joker
from mex.common.types import TextLanguage


def test_transform_seed_primary_sources_to_extracted_primary_sources() -> None:
    extracted_primary_source = (
        transform_seed_primary_sources_to_extracted_primary_sources(
            extract_seed_primary_sources()
        )[0]
    )
    assert extracted_primary_source.model_dump(
        exclude_none=True, exclude_defaults=True
    ) == {
        "hadPrimarySource": MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
        "identifier": Joker(),
        "identifierInPrimarySource": "mex",
        "stableTargetId": MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
        "title": [{"language": TextLanguage.EN, "value": "Metadata Exchange"}],
    }
