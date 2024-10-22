from functools import cache

from mex.common.models import (
    ExtractedPrimarySource,
)
from mex.common.primary_source.extract import extract_seed_primary_sources
from mex.common.primary_source.transform import (
    transform_seed_primary_sources_to_extracted_primary_sources,
)


@cache
def get_all_extracted_primary_sources() -> dict[str, ExtractedPrimarySource]:
    """Extract and transform all primary sources.

    Extract the primary sources from the raw-data JSON file and transform them into
    a dictionary of ExtractedPrimarySources.

    Returns:
        dictionary of all ExtractedPrimarySources
    """
    seed_primary_sources = extract_seed_primary_sources()
    extracted_primary_sources = (
        transform_seed_primary_sources_to_extracted_primary_sources(
            seed_primary_sources
        )
    )
    return {p.identifierInPrimarySource: p for p in extracted_primary_sources}


@cache
def get_extracted_primary_source_by_name(name: str) -> ExtractedPrimarySource | None:
    """Pick the extracted primary source with the given name and return it.

    Args:
        name: Name (`identifierInPrimarySource`) of the primary source

    Returns:
        Extracted primary source if it was found, else None
    """
    try:
        extracted_primary_source = get_all_extracted_primary_sources()[name]
    except KeyError:
        return None

    return extracted_primary_source
