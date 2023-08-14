from typing import Generator, Iterable

from mex.common.logging import watch
from mex.common.models import (
    MEX_PRIMARY_SOURCE_IDENTIFIER_IN_PRIMARY_SOURCE,
    MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
    ExtractedPrimarySource,
)
from mex.common.primary_source.models import SeedPrimarySource


@watch
def transform_seed_primary_sources_to_extracted_primary_sources(
    primary_sources: Iterable[SeedPrimarySource],
) -> Generator[ExtractedPrimarySource, None, None]:
    """Transform seed primary sources into ExtractedPrimarySources.

    Args:
        primary_sources: Iterable of primary sources coming from raw-data file

    Returns:
        Generator for ExtractedPrimarySource
    """
    for primary_source in primary_sources:
        if primary_source.identifier == MEX_PRIMARY_SOURCE_IDENTIFIER_IN_PRIMARY_SOURCE:
            set_stable_target_id = dict(
                stableTargetId=MEX_PRIMARY_SOURCE_STABLE_TARGET_ID
            )
        else:
            set_stable_target_id = dict()
        yield ExtractedPrimarySource(
            identifierInPrimarySource=primary_source.identifier,
            title=primary_source.title,
            hadPrimarySource=MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
            **set_stable_target_id  # type: ignore[arg-type]
        )
