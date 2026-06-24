from mex.common.models import ExtractedPrimarySource
from mex.common.primary_source.extract import extract_seed_primary_sources
from mex.common.primary_source.transform import (
    transform_seed_primary_source_to_extracted_primary_source,
)


def get_extracted_primary_source_by_name(name: str) -> ExtractedPrimarySource | None:
    """Pick the seed primary source with the given name, transform and return it.

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
