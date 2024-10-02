from functools import cache

from mex.common.models import (
    ExtractedPrimarySource,
)
from mex.common.primary_source.extract import extract_seed_primary_sources
from mex.common.primary_source.transform import (
    transform_seed_primary_sources_to_extracted_primary_sources,
)


@cache
def get_all_extracted_primary_sources() -> list[ExtractedPrimarySource]:
    """Extract and transform all primary sources.

    Extract the primary sources from the raw-data JSON file and transform them into
    a list of ExtractedPrimarySources.

    Returns:
        List of all ExtractedPrimarySources
    """
    seed_primary_sources = extract_seed_primary_sources()
    return list(
        transform_seed_primary_sources_to_extracted_primary_sources(
            seed_primary_sources
        )
    )


@cache
def get_extracted_primary_source_by_name(name: str) -> ExtractedPrimarySource | None:
    """Pick the extracted primary source with the given name and return it.

    Args:
        name: Name (`identifierInPrimarySource`) of the primary source

    Returns:
        Extracted primary source if it was found, else None
    """
    primary_sources_by_name = {
        p.identifierInPrimarySource: p for p in get_all_extracted_primary_sources()
    }
    return primary_sources_by_name.get(name)
