from mex.common.models import ExtractedPrimarySource
from mex.common.primary_source.extract import extract_seed_primary_sources
from mex.common.primary_source.transform import (
    transform_seed_primary_source_to_extracted_primary_source,
    transform_seed_primary_sources_to_extracted_primary_sources,
)


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


def get_extracted_primary_source_by_name(name: str) -> ExtractedPrimarySource | None:
    """Pick the extracted primary source with the given name and return it.

    Args:
        name: Name (`identifierInPrimarySource`) of the primary source

    Returns:
        Extracted primary source if it was found, else None
    """
    for seed_primary_source in extract_seed_primary_sources():
        if seed_primary_source.identifier == name:
            return transform_seed_primary_source_to_extracted_primary_source(
                seed_primary_source
            )
    return None
