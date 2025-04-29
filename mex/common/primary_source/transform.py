from collections.abc import Iterable

from mex.common.logging import logger
from mex.common.models import (
    MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
    ExtractedPrimarySource,
)
from mex.common.primary_source.models import SeedPrimarySource


def transform_seed_primary_source_to_extracted_primary_source(
    primary_source: SeedPrimarySource,
) -> ExtractedPrimarySource:
    """Transform a seed primary source into an ExtractedPrimarySource.

    Args:
        primary_source: Primary source coming from raw-data file

    Returns:
        ExtractedPrimarySource
    """
    return ExtractedPrimarySource(
        identifierInPrimarySource=primary_source.identifier,
        title=primary_source.title,
        hadPrimarySource=MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
    )


def transform_seed_primary_sources_to_extracted_primary_sources(
    seed_primary_sources: Iterable[SeedPrimarySource],
) -> list[ExtractedPrimarySource]:
    """Transform seed primary sources into ExtractedPrimarySources.

    Args:
        seed_primary_sources: Iterable of primary sources coming from raw-data file

    Returns:
        List of ExtractedPrimarySource
    """
    extracted_primary_sources = [
        transform_seed_primary_source_to_extracted_primary_source(primary_source)
        for primary_source in seed_primary_sources
    ]
    logger.info("transformed %s primary sources", len(extracted_primary_sources))
    return extracted_primary_sources


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
