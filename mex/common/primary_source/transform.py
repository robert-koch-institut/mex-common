from collections.abc import Generator, Iterable

from mex.common.logging import watch
from mex.common.models import (
    MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
    ExtractedPrimarySource,
)
from mex.common.primary_source.models import SeedPrimarySource


@watch()
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
        yield ExtractedPrimarySource(
            identifierInPrimarySource=primary_source.identifier,
            title=primary_source.title,
            hadPrimarySource=MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
        )


# TODO(EH): Remove this in MX-1698
def get_primary_sources_by_name(
    extracted_primary_sources: Iterable[ExtractedPrimarySource], *names: str
) -> tuple[ExtractedPrimarySource, ...]:
    """Pick the extracted primary sources with the given name and return as a tuple.

    Args:
        extracted_primary_sources: Iterable of extracted primary sources
        names: Names (`identifierInPrimarySource`) to pick

    Returns:
        Tuple of picked primary sources of the same length as `names`
    """
    primary_sources_by_name = {
        p.identifierInPrimarySource: p for p in extracted_primary_sources
    }
    return tuple(primary_sources_by_name[n] for n in names)
